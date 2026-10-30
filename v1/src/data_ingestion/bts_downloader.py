"""
BTS Flight Data Downloader — Stage 1: Data Ingestion.

This module is responsible for retrieving raw historical flight records
from the official U.S. Bureau of Transportation Statistics (BTS)
TranStats 'Reporting Carrier On-Time Performance' dataset.

Core Principles:
1. RAW DATA IMMUTABILITY: Raw CSV files are preserved exactly as delivered by BTS.
   No transformations, feature engineering, filtering, or column renaming.
2. REPRODUCIBILITY & CONFIGURABILITY: Years, paths, timeouts, retries, and overwrite
   policies are driven by config.yaml.
3. DATA INTEGRITY: Validation of file sizes, row counts, schema columns, and SHA-256 hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import os
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
import yaml
from bs4 import BeautifulSoup


def setup_logger(
    log_file: str = "logs/bts_download.log",
    log_level: str = "INFO",
    console_output: bool = True,
) -> logging.Logger:
    """Configures and returns a structured logger for BTS ingestion."""
    logger = logging.getLogger("bts_downloader")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers if re-initializing
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


class BTSDownloader:
    """Downloader and validator for BTS TranStats On-Time Performance data."""

    VERSION = "1.0.0"

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config(self.config_path)

        log_cfg = self.config.get("logging", {})
        self.logger = setup_logger(
            log_file=log_cfg.get("log_file", "logs/bts_download.log"),
            log_level=log_cfg.get("log_level", "INFO"),
            console_output=log_cfg.get("console_output", True),
        )

        ingestion_cfg = self.config.get("ingestion", {})
        self.output_dir = Path(ingestion_cfg.get("output_dir", "data/raw/bts"))
        self.output_filename_pattern = ingestion_cfg.get(
            "output_filename_pattern", "bts_flights_{year}.csv"
        )
        self.metadata_file = Path(
            ingestion_cfg.get("metadata_file", "data/raw/bts/metadata.json")
        )
        self.years: List[int] = ingestion_cfg.get("years", [2024, 2025])
        self.months: Optional[List[int]] = ingestion_cfg.get("months", None)
        self.overwrite: bool = ingestion_cfg.get("overwrite", False)
        self.request_timeout: int = ingestion_cfg.get("request_timeout", 120)
        self.retry_count: int = ingestion_cfg.get("retry_count", 3)
        self.retry_backoff: int = ingestion_cfg.get("retry_backoff_seconds", 5)
        self.chunk_size: int = ingestion_cfg.get("chunk_size_bytes", 262144)
        self.download_all_fields: bool = ingestion_cfg.get("download_all_fields", True)

        bts_cfg = self.config.get("bts", {})
        self.form_url: str = bts_cfg.get(
            "form_url",
            "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr",
        )
        self.source_name: str = bts_cfg.get(
            "source_name", "U.S. Bureau of Transportation Statistics (BTS)"
        )
        self.dataset_name: str = bts_cfg.get(
            "dataset_name", "Reporting Carrier On-Time Performance (1987-present)"
        )

        self.required_fields_map: Dict[str, List[str]] = self.config.get(
            "required_fields", {}
        )
        self.expected_columns_flat: List[str] = [
            col for group in self.required_fields_map.values() for col in group
        ]

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_config(path: Path) -> Dict[str, Any]:
        """Loads YAML configuration safely."""
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def get_output_filepath(self, year: int) -> Path:
        """Returns the destination Path for a given year's raw CSV dataset."""
        filename = self.output_filename_pattern.format(year=year)
        return self.output_dir / filename

    def _init_session(self) -> requests.Session:
        """Initializes a requests Session with standard browser headers."""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Origin": "https://www.transtats.bts.gov",
                "Referer": self.form_url,
            }
        )
        return session

    def _fetch_form_state(
        self, session: requests.Session
    ) -> Tuple[Dict[str, str], Set[str]]:
        """Fetches the ASP.NET form page and extracts viewstate tokens and field checkboxes."""
        self.logger.debug(f"Fetching ASP.NET form state from {self.form_url}")
        resp = session.get(self.form_url, timeout=self.request_timeout)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        form_data: Dict[str, str] = {}
        available_checkboxes: Set[str] = set()

        for inp in soup.find_all("input"):
            name = inp.get("name")
            if not name:
                continue
            inp_type = inp.get("type", "").lower()
            val = inp.get("value", "")
            if inp_type == "checkbox":
                available_checkboxes.add(name)
            else:
                form_data[name] = val

        form_data["__EVENTTARGET"] = ""
        form_data["__EVENTARGUMENT"] = ""
        form_data["__LASTFOCUS"] = ""

        return form_data, available_checkboxes

    def download_month_zip(
        self,
        session: requests.Session,
        year: int,
        month: int,
        base_form_data: Dict[str, str],
        available_checkboxes: Set[str],
    ) -> Optional[bytes]:
        """Submits the BTS download form for a specific Year and Month and returns the zip bytes."""
        payload = dict(base_form_data)
        payload["cboGeography"] = "All"
        payload["cboYear"] = str(year)
        payload["cboPeriod"] = str(month)
        payload["chkDownloadZip"] = "on"
        payload["btnDownload"] = "Download"

        if self.download_all_fields and "chkAllVars" in available_checkboxes:
            payload["chkAllVars"] = "on"
        else:
            # Fallback: check individual requested checkboxes that exist on page
            for cb in available_checkboxes:
                if cb not in (
                    "chkshowNull",
                    "chkMergeSub",
                    "chkDocument",
                    "chkTermDef",
                ):
                    payload[cb] = "on"

        self.logger.info(
            f"Requesting Year {year}, Month {month:02d} from BTS TranStats..."
        )

        for attempt in range(1, self.retry_count + 1):
            try:
                t0 = time.time()
                resp = session.post(
                    self.form_url,
                    data=payload,
                    timeout=self.request_timeout,
                    stream=True,
                )
                resp.raise_for_status()

                content_type = resp.headers.get("Content-Type", "")
                self.logger.debug(
                    f"Response received (attempt {attempt}/{self.retry_count}): "
                    f"status={resp.status_code}, content-type={content_type}"
                )

                # Read stream in chunks
                zip_buffer = io.BytesIO()
                downloaded_bytes = 0

                for chunk in resp.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        zip_buffer.write(chunk)
                        downloaded_bytes += len(chunk)

                zip_bytes = zip_buffer.getvalue()
                elapsed = time.time() - t0

                if zip_bytes.startswith(b"PK"):
                    self.logger.info(
                        f"Successfully downloaded Year {year} Month {month:02d}: "
                        f"{downloaded_bytes / (1024 * 1024):.2f} MB in {elapsed:.1f}s"
                    )
                    return zip_bytes
                else:
                    # Could be an empty result or unreleased month
                    preview = zip_bytes[:300].decode("utf-8", errors="ignore").strip()
                    self.logger.warning(
                        f"Year {year} Month {month:02d} returned non-ZIP response "
                        f"(Size: {len(zip_bytes)} bytes). Content preview: {preview[:120]}"
                    )
                    return None

            except (requests.RequestException, Exception) as exc:
                self.logger.warning(
                    f"Attempt {attempt}/{self.retry_count} failed for Year {year} Month {month:02d}: {exc}"
                )
                if attempt < self.retry_count:
                    time.sleep(self.retry_backoff * attempt)
                else:
                    self.logger.error(
                        f"All {self.retry_count} attempts failed for Year {year} Month {month:02d}."
                    )
                    raise

        return None

    def extract_csv_from_zip(self, zip_bytes: bytes) -> Tuple[str, bytes]:
        """Extracts the primary flight CSV data from the BTS ZIP archive."""
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            csv_names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not csv_names:
                raise ValueError(
                    f"No CSV file found inside BTS ZIP. Contents: {z.namelist()}"
                )
            # Typically named On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_YYYY_M.csv
            primary_csv = csv_names[0]
            data = z.read(primary_csv)
            return primary_csv, data

    def download_year(self, year: int) -> Path:
        """
        Downloads all available months for a given year and saves the exact raw records
        to data/raw/bts/bts_flights_{year}.csv.
        """
        output_file = self.get_output_filepath(year)

        if output_file.exists() and not self.overwrite:
            self.logger.info(
                f"Raw dataset {output_file} already exists and overwrite is disabled. "
                f"Skipping download."
            )
            return output_file

        self.logger.info(
            f"=== Starting BTS Ingestion for Year {year} -> {output_file} ==="
        )
        session = self._init_session()
        base_form_data, available_checkboxes = self._fetch_form_state(session)

        target_months = self.months if self.months else list(range(1, 13))
        months_downloaded: List[int] = []

        temp_output_file = output_file.with_suffix(".tmp")
        if temp_output_file.exists():
            temp_output_file.unlink()

        first_month_written = False

        try:
            with open(temp_output_file, "wb") as out_f:
                for month in target_months:
                    zip_bytes = self.download_month_zip(
                        session=session,
                        year=year,
                        month=month,
                        base_form_data=base_form_data,
                        available_checkboxes=available_checkboxes,
                    )

                    if zip_bytes is None:
                        self.logger.info(
                            f"Skipping Year {year} Month {month:02d} (not available or unreleased)."
                        )
                        continue

                    _, csv_bytes = self.extract_csv_from_zip(zip_bytes)
                    lines = csv_bytes.splitlines(keepends=True)
                    if not lines:
                        continue

                    if not first_month_written:
                        # Write the complete CSV including the original BTS header
                        out_f.write(csv_bytes)
                        first_month_written = True
                    else:
                        # Append data lines only, omitting duplicate header
                        for line in lines[1:]:
                            out_f.write(line)

                    months_downloaded.append(month)

            if not first_month_written or not months_downloaded:
                raise RuntimeError(
                    f"No flight data could be retrieved for Year {year}."
                )

            # Atomically replace final file
            if output_file.exists():
                output_file.unlink()
            temp_output_file.rename(output_file)

            self.logger.info(
                f"Successfully saved raw dataset for Year {year} to {output_file} "
                f"(Months included: {months_downloaded})"
            )
            return output_file

        finally:
            if temp_output_file.exists():
                temp_output_file.unlink()

    def validate_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Validates the raw CSV dataset:
        - Verifies existence and non-empty size.
        - Calculates SHA-256 hash.
        - Counts total rows and columns.
        - Inspects presence of required analytical columns without mutating data.
        """
        if not filepath.exists():
            raise FileNotFoundError(f"File does not exist for validation: {filepath}")

        file_size = filepath.stat().st_size
        if file_size == 0:
            raise ValueError(f"Downloaded file is empty (0 bytes): {filepath}")

        sha256 = hashlib.sha256()
        row_count = 0
        header_line = ""
        columns: List[str] = []

        with open(filepath, "rb") as f:
            # Read first line for header
            header_bytes = f.readline()
            if header_bytes:
                sha256.update(header_bytes)
                header_line = header_bytes.decode("utf-8", errors="ignore").strip()
                # Parse header columns cleanly (handling quotes)
                raw_cols = [
                    c.strip().strip('"')
                    for c in header_line.split(",")
                    if c.strip() != ""
                ]
                columns = raw_cols

            # Read remainder of the file in chunks for row count and hashing
            buf_size = 1024 * 1024  # 1 MB buffer
            while True:
                chunk = f.read(buf_size)
                if not chunk:
                    break
                sha256.update(chunk)
                row_count += chunk.count(b"\n")

        # Check required columns
        header_col_set = set(columns)
        # Also support case-insensitive matching if BTS casing differs
        header_col_lower_map = {c.lower(): c for c in columns}

        matched_columns: List[str] = []
        missing_columns: List[str] = []

        for req in self.expected_columns_flat:
            if req in header_col_set:
                matched_columns.append(req)
            elif req.lower() in header_col_lower_map:
                matched_columns.append(header_col_lower_map[req.lower()])
            else:
                missing_columns.append(req)

        validation_status = "PASSED" if len(missing_columns) == 0 else "WARNING"

        result: Dict[str, Any] = {
            "file": str(filepath.resolve()),
            "filename": filepath.name,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "sha256": sha256.hexdigest(),
            "row_count": row_count,
            "column_count": len(columns),
            "columns": columns,
            "required_columns_total": len(self.expected_columns_flat),
            "required_columns_matched": len(matched_columns),
            "missing_required_columns": missing_columns,
            "validation_status": validation_status,
        }

        self.logger.info(
            f"Validation Results for {filepath.name}: "
            f"Rows={row_count:,}, Columns={len(columns)}, Size={result['file_size_mb']} MB, "
            f"SHA256={result['sha256'][:16]}..., Status={validation_status}"
        )
        if missing_columns:
            self.logger.warning(
                f"Missing required columns ({len(missing_columns)}): {missing_columns}"
            )

        return result

    def update_metadata(
        self,
        year_results: Dict[int, Dict[str, Any]],
        overall_status: str = "SUCCESS",
        errors: Optional[List[str]] = None,
    ) -> Path:
        """Updates and persists the metadata.json catalog."""
        metadata: Dict[str, Any] = {
            "source": self.source_name,
            "dataset_name": self.dataset_name,
            "portal_url": self.form_url,
            "downloader_version": self.VERSION,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "overall_status": overall_status,
            "errors": errors or [],
            "years": {},
        }

        # If existing metadata exists, load and update it
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    existing_meta = json.load(f)
                    if isinstance(existing_meta, dict) and "years" in existing_meta:
                        metadata["years"] = existing_meta["years"]
            except Exception as e:
                self.logger.warning(f"Could not read existing metadata: {e}")

        for year, res in year_results.items():
            metadata["years"][str(year)] = {
                "year": year,
                "filename": res.get("filename"),
                "file_path": res.get("file"),
                "download_timestamp": datetime.now(timezone.utc).isoformat(),
                "file_size_bytes": res.get("file_size_bytes"),
                "file_size_mb": res.get("file_size_mb"),
                "row_count": res.get("row_count"),
                "column_count": res.get("column_count"),
                "sha256": res.get("sha256"),
                "validation_status": res.get("validation_status"),
                "missing_required_columns": res.get("missing_required_columns", []),
            }

        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        self.logger.info(f"Updated metadata catalog at {self.metadata_file}")
        return self.metadata_file

    def run(
        self,
        years: Optional[List[int]] = None,
        overwrite: Optional[bool] = None,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes the Stage 1 BTS Data Ingestion pipeline.
        """
        run_years = years if years is not None else self.years
        if overwrite is not None:
            self.overwrite = overwrite

        self.logger.info("=" * 70)
        self.logger.info(f"Starting BTS Data Ingestion Run (v{self.VERSION})")
        self.logger.info(f"Config: {self.config_path}")
        self.logger.info(f"Target Years: {run_years}")
        self.logger.info(f"Output Directory: {self.output_dir}")
        self.logger.info(f"Overwrite Mode: {self.overwrite}")
        self.logger.info(f"Validate Only: {validate_only}")
        self.logger.info("=" * 70)

        year_results: Dict[int, Dict[str, Any]] = {}
        errors: List[str] = []

        for year in run_years:
            try:
                target_file = self.get_output_filepath(year)
                if not validate_only:
                    target_file = self.download_year(year)

                if target_file.exists():
                    val_res = self.validate_file(target_file)
                    year_results[year] = val_res
                else:
                    msg = f"Dataset file for year {year} not found: {target_file}"
                    self.logger.error(msg)
                    errors.append(msg)

            except Exception as exc:
                err_msg = f"Error processing year {year}: {exc}"
                self.logger.error(err_msg, exc_info=True)
                errors.append(err_msg)

        overall_status = "SUCCESS" if not errors else "PARTIAL_FAILURE"
        if not year_results and errors:
            overall_status = "FAILED"

        self.update_metadata(
            year_results=year_results,
            overall_status=overall_status,
            errors=errors,
        )

        self.logger.info("=" * 70)
        self.logger.info(f"BTS Data Ingestion Finished — Overall Status: {overall_status}")
        self.logger.info("=" * 70)

        return {
            "overall_status": overall_status,
            "year_results": year_results,
            "errors": errors,
        }


def main():
    """Command-line entrypoint for the BTS Downloader."""
    parser = argparse.ArgumentParser(
        description="Fetch and validate historical flight datasets from US BTS TranStats."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to YAML configuration file.",
    )
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        default=None,
        help="Specific years to download (e.g. --years 2024 2025).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=None,
        help="Force overwrite of existing files.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Skip downloading and validate existing files in data/raw/bts/.",
    )

    args = parser.parse_args()

    downloader = BTSDownloader(config_path=args.config)
    downloader.run(
        years=args.years,
        overwrite=args.overwrite,
        validate_only=args.validate_only,
    )


if __name__ == "__main__":
    main()
