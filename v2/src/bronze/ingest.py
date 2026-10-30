"""
Bronze Ingestion Engine for Local SQLite Data Warehouse
Streams raw BTS CSV files in chunks into bronze_bts_flights, capturing full provenance.
"""

import csv
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..utils.db import get_db_connection, execute_sql_file, db_transaction
from ..utils.hashing import generate_source_row_hash
from ..utils.logger import setup_logger


# The 109 BTS columns expected from raw files
EXPECTED_BTS_COLUMNS = [
    'Year', 'Quarter', 'Month', 'DayofMonth', 'DayOfWeek', 'FlightDate',
    'Reporting_Airline', 'DOT_ID_Reporting_Airline', 'IATA_CODE_Reporting_Airline',
    'Tail_Number', 'Flight_Number_Reporting_Airline', 'OriginAirportID',
    'OriginAirportSeqID', 'OriginCityMarketID', 'Origin', 'OriginCityName',
    'OriginState', 'OriginStateFips', 'OriginStateName', 'OriginWac',
    'DestAirportID', 'DestAirportSeqID', 'DestCityMarketID', 'Dest',
    'DestCityName', 'DestState', 'DestStateFips', 'DestStateName', 'DestWac',
    'CRSDepTime', 'DepTime', 'DepDelay', 'DepDelayMinutes', 'DepDel15',
    'DepartureDelayGroups', 'DepTimeBlk', 'TaxiOut', 'WheelsOff', 'WheelsOn',
    'TaxiIn', 'CRSArrTime', 'ArrTime', 'ArrDelay', 'ArrDelayMinutes', 'ArrDel15',
    'ArrivalDelayGroups', 'ArrTimeBlk', 'Cancelled', 'CancellationCode', 'Diverted',
    'CRSElapsedTime', 'ActualElapsedTime', 'AirTime', 'Flights', 'Distance',
    'DistanceGroup', 'CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay',
    'LateAircraftDelay', 'FirstDepTime', 'TotalAddGTime', 'LongestAddGTime',
    'DivAirportLandings', 'DivReachedDest', 'DivActualElapsedTime', 'DivArrDelay',
    'DivDistance', 'Div1Airport', 'Div1AirportID', 'Div1AirportSeqID', 'Div1WheelsOn',
    'Div1TotalGTime', 'Div1LongestGTime', 'Div1WheelsOff', 'Div1TailNum',
    'Div2Airport', 'Div2AirportID', 'Div2AirportSeqID', 'Div2WheelsOn',
    'Div2TotalGTime', 'Div2LongestGTime', 'Div2WheelsOff', 'Div2TailNum',
    'Div3Airport', 'Div3AirportID', 'Div3AirportSeqID', 'Div3WheelsOn',
    'Div3TotalGTime', 'Div3LongestGTime', 'Div3WheelsOff', 'Div3TailNum',
    'Div4Airport', 'Div4AirportID', 'Div4AirportSeqID', 'Div4WheelsOn',
    'Div4TotalGTime', 'Div4LongestGTime', 'Div4WheelsOff', 'Div4TailNum',
    'Div5Airport', 'Div5AirportID', 'Div5AirportSeqID', 'Div5WheelsOn',
    'Div5TotalGTime', 'Div5LongestGTime', 'Div5WheelsOff', 'Div5TailNum'
]


def ingest_single_file(
    conn,
    csv_path: str,
    table_name: str = "bronze_bts_flights",
    chunk_size: int = 50000,
    max_rows: Optional[int] = None,
    force: bool = False,
    logger: Optional[logging.Logger] = None
) -> Dict[str, Any]:
    """
    Ingests a single raw BTS CSV file into bronze_bts_flights.
    Supports chunking, idempotency via bronze_manifest, and line-level provenance.
    """
    log = logger or logging.getLogger("v2_bronze")
    filename = os.path.basename(csv_path)

    # Check manifest for idempotency
    cursor = conn.cursor()
    cursor.execute("SELECT row_count, status FROM bronze_manifest WHERE filename = ?", (filename,))
    row = cursor.fetchone()

    if row and row["status"] == "SUCCESS" and not force:
        log.info(f"File {filename} was already ingested ({row['row_count']} rows). Skipping (idempotent).")
        return {
            "filename": filename,
            "status": "SKIPPED",
            "rows_read": row["row_count"],
            "rows_inserted": 0,
            "rejected_rows": 0,
            "message": "Already ingested"
        }

    # If forcing reload, delete existing rows for this file
    if row and force:
        log.info(f"Forced re-ingestion: removing existing records for {filename}...")
        conn.execute(f"DELETE FROM {table_name} WHERE source_file = ?", (filename,))
        conn.execute("DELETE FROM bronze_manifest WHERE filename = ?", (filename,))
        conn.commit()

    start_time = time.time()
    total_read = 0
    total_inserted = 0
    total_rejected = 0

    log.info(f"Starting chunked Bronze ingestion for {filename} (chunk_size={chunk_size}, max_rows={max_rows})...")

    # Inspect header
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header_raw = next(reader, None)
        if not header_raw:
            log.error(f"Empty CSV file: {csv_path}")
            return {
                "filename": filename,
                "status": "FAILED",
                "rows_read": 0,
                "rows_inserted": 0,
                "rejected_rows": 0,
                "error": "Empty file"
            }

        # Filter out trailing empty columns
        clean_header = [c.strip() for c in header_raw if c.strip()]
        header_len = len(clean_header)

        # Detect source year from filename e.g. bts_flights_2024.csv
        source_year = None
        for token in filename.replace(".", "_").split("_"):
            if token.isdigit() and len(token) == 4:
                source_year = int(token)
                break

        # Prepare insert query
        cols_to_insert = ["source_file", "source_year", "ingestion_timestamp", "source_row_hash"] + clean_header
        placeholders = ", ".join(["?"] * len(cols_to_insert))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(cols_to_insert)}) VALUES ({placeholders})"

        chunk = []
        batch_idx = 0

        for line_idx, line in enumerate(reader, start=1):
            total_read += 1

            if len(line) < header_len:
                total_rejected += 1
                continue

            # Map line items to clean_header
            row_dict = {clean_header[i]: line[i] for i in range(header_len)}
            row_year = source_year
            if not row_year and row_dict.get("Year") and row_dict["Year"].isdigit():
                row_year = int(row_dict["Year"])

            now_iso = datetime.now(timezone.utc).isoformat()
            row_hash = generate_source_row_hash(row_dict, source_file=filename, row_idx=line_idx)

            values = [filename, row_year, now_iso, row_hash] + [line[i] for i in range(header_len)]
            chunk.append(values)

            if len(chunk) >= chunk_size:
                cursor.executemany(insert_sql, chunk)
                conn.commit()
                total_inserted += len(chunk)
                batch_idx += 1
                log.info(f"[{filename}] Inserted batch {batch_idx}: {total_inserted:,} rows so far...")
                chunk = []

            if max_rows and total_read >= max_rows:
                log.info(f"Reached max_rows limit ({max_rows}) for {filename}.")
                break

        if chunk:
            cursor.executemany(insert_sql, chunk)
            conn.commit()
            total_inserted += len(chunk)

    elapsed = time.time() - start_time
    log.info(f"Finished {filename}: {total_inserted:,} rows inserted in {elapsed:.2f}s ({total_rejected} rejected).")

    # Record in manifest
    now_ts = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        """
        INSERT INTO bronze_manifest (filename, source_year, row_count, ingested_at, status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(filename) DO UPDATE SET
            row_count = excluded.row_count,
            ingested_at = excluded.ingested_at,
            status = excluded.status
        """,
        (filename, source_year, total_inserted, now_ts, "SUCCESS")
    )
    conn.commit()

    return {
        "filename": filename,
        "status": "SUCCESS",
        "rows_read": total_read,
        "rows_inserted": total_inserted,
        "rejected_rows": total_rejected,
        "duration_seconds": round(elapsed, 2)
    }


def ingest_bronze_files(config: dict, force: bool = False, max_rows: Optional[int] = None, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Main orchestrator for Bronze layer ingestion.
    Loads raw CSV files according to configuration, executes DDL if needed,
    and returns a full execution summary.
    """
    log = logger or setup_logger(
        "v2_bronze",
        log_file=config.get("logging", {}).get("log_file"),
        level=config.get("logging", {}).get("log_level", "INFO")
    )

    db_path = config["database"]["path"]
    conn = get_db_connection(db_path)

    # Initialize bronze DDL
    project_root = Path(__file__).resolve().parent.parent.parent
    bronze_sql_path = project_root / "sql" / "schema" / "01_bronze.sql"
    if bronze_sql_path.exists():
        execute_sql_file(conn, str(bronze_sql_path))

    raw_dir = Path(config["raw_data"]["dir"])
    pattern = config["raw_data"].get("file_pattern", "bts_flights_{year}.csv")
    years = config["raw_data"].get("years", [2024, 2025])
    chunk_size = config["raw_data"].get("chunk_size", 50000)
    effective_max_rows = max_rows if max_rows is not None else config["raw_data"].get("max_rows_per_file")

    files_to_process = []
    for y in years:
        fname = pattern.format(year=y)
        fpath = raw_dir / fname
        if fpath.exists():
            files_to_process.append(str(fpath))
        else:
            log.warning(f"Configured raw file not found: {fpath}")

    # Fallback to any .csv in raw_dir if specific years not found
    if not files_to_process and raw_dir.exists():
        files_to_process = [str(p) for p in raw_dir.glob("*.csv")]

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_files": len(files_to_process),
        "files": [],
        "total_inserted": 0,
        "total_read": 0,
        "total_rejected": 0,
        "overall_status": "SUCCESS"
    }

    start_all = time.time()
    for fp in files_to_process:
        res = ingest_single_file(
            conn=conn,
            csv_path=fp,
            table_name=config.get("tables", {}).get("bronze", "bronze_bts_flights"),
            chunk_size=chunk_size,
            max_rows=effective_max_rows,
            force=force,
            logger=log
        )
        summary["files"].append(res)
        summary["total_inserted"] += res.get("rows_inserted", 0)
        summary["total_read"] += res.get("rows_read", 0)
        summary["total_rejected"] += res.get("rejected_rows", 0)
        if res.get("status") == "FAILED":
            summary["overall_status"] = "PARTIAL_FAILURE"

    summary["duration_seconds"] = round(time.time() - start_all, 2)
    conn.close()

    # Write bronze report
    report_path = config.get("reports", {}).get("bronze_report", "v2/reports/bronze_report.json")
    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(summary, rf, indent=2)

    log.info(f"Bronze ingestion complete: {summary['total_inserted']:,} rows loaded across {len(files_to_process)} files.")
    return summary
