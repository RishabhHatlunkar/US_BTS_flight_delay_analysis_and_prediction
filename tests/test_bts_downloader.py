"""
Unit and Integration tests for BTS Data Ingestion Layer.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from src.data_ingestion.bts_downloader import BTSDownloader, setup_logger


@pytest.fixture
def sample_config_dict():
    return {
        "bts": {
            "source_name": "U.S. Bureau of Transportation Statistics (BTS)",
            "dataset_name": "Reporting Carrier On-Time Performance (1987-present)",
            "portal_url": "https://www.transtats.bts.gov/",
            "form_url": "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr",
        },
        "ingestion": {
            "years": [2024, 2025],
            "months": [1],
            "download_all_fields": True,
            "output_dir": "data/raw/bts",
            "output_filename_pattern": "bts_flights_{year}.csv",
            "metadata_file": "data/raw/bts/metadata.json",
            "overwrite": False,
            "request_timeout": 30,
            "retry_count": 2,
            "retry_backoff_seconds": 1,
            "chunk_size_bytes": 65536,
        },
        "logging": {
            "log_file": "logs/bts_download.log",
            "log_level": "DEBUG",
            "console_output": False,
        },
        "required_fields": {
            "time": ["Year", "Quarter", "Month", "DayofMonth", "DayOfWeek", "FlightDate"],
            "airline": ["Reporting_Airline", "DOT_ID_Reporting_Airline", "IATA_CODE_Reporting_Airline", "Flight_Number_Reporting_Airline", "Tail_Number"],
            "origin": ["OriginAirportID", "OriginAirportSeqID", "Origin", "OriginCityName", "OriginState", "OriginStateName"],
            "destination": ["DestAirportID", "DestAirportSeqID", "Dest", "DestCityName", "DestState", "DestStateName"],
            "departure": ["CRSDepTime", "DepTime", "DepDelay", "DepDelayMinutes", "DepDel15", "DepartureDelayGroups", "DepTimeBlk", "TaxiOut"],
            "arrival": ["CRSArrTime", "ArrTime", "ArrDelay", "ArrDelayMinutes", "ArrDel15", "ArrivalDelayGroups", "ArrTimeBlk", "TaxiIn"],
            "cancellation": ["Cancelled", "CancellationCode", "Diverted"],
            "flight": ["CRSElapsedTime", "ActualElapsedTime", "AirTime", "Distance", "DistanceGroup"],
            "delay_causes": ["CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay"],
        },
    }


@pytest.fixture
def temp_env(tmp_path, sample_config_dict):
    """Sets up a temporary working environment with isolated config and directories."""
    config_file = tmp_path / "config.yaml"
    raw_dir = tmp_path / "data" / "raw" / "bts"
    meta_file = raw_dir / "metadata.json"
    log_file = tmp_path / "logs" / "bts_download.log"

    sample_config_dict["ingestion"]["output_dir"] = str(raw_dir)
    sample_config_dict["ingestion"]["metadata_file"] = str(meta_file)
    sample_config_dict["logging"]["log_file"] = str(log_file)

    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(sample_config_dict, f)

    return {
        "config_file": config_file,
        "raw_dir": raw_dir,
        "meta_file": meta_file,
        "log_file": log_file,
    }


def test_config_loading(temp_env):
    """Test that configuration is loaded and parsed correctly."""
    downloader = BTSDownloader(config_path=str(temp_env["config_file"]))
    assert downloader.years == [2024, 2025]
    assert downloader.output_dir == temp_env["raw_dir"]
    assert downloader.request_timeout == 30
    assert downloader.retry_count == 2
    assert "FlightDate" in downloader.expected_columns_flat
    assert "DepDelay" in downloader.expected_columns_flat


def test_missing_config_raises_error():
    """Test that pointing to a nonexistent config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        BTSDownloader(config_path="nonexistent_config_path.yaml")


def test_output_directory_creation(temp_env):
    """Test that raw output directory and metadata parent directories are created automatically."""
    downloader = BTSDownloader(config_path=str(temp_env["config_file"]))
    assert temp_env["raw_dir"].exists()


def test_expected_output_naming(temp_env):
    """Test that output filepath follows the configured pattern."""
    downloader = BTSDownloader(config_path=str(temp_env["config_file"]))
    p2024 = downloader.get_output_filepath(2024)
    p2025 = downloader.get_output_filepath(2025)
    assert p2024.name == "bts_flights_2024.csv"
    assert p2025.name == "bts_flights_2025.csv"
    assert p2024.parent == temp_env["raw_dir"]


def test_file_validation_and_columns(temp_env):
    """Test file validation, row count, column extraction, and schema verification."""
    downloader = BTSDownloader(config_path=str(temp_env["config_file"]))

    # Create a synthetic valid BTS CSV file
    cols = downloader.expected_columns_flat
    csv_content = '"' + '","'.join(cols) + '"\n'
    # Add 3 dummy flight records
    row_1 = ",".join(["2024", "1", "1", "15", "1", "2024-01-15"] + ["0"] * (len(cols) - 6))
    row_2 = ",".join(["2024", "1", "1", "16", "2", "2024-01-16"] + ["0"] * (len(cols) - 6))
    row_3 = ",".join(["2024", "1", "1", "17", "3", "2024-01-17"] + ["0"] * (len(cols) - 6))
    full_csv = csv_content + row_1 + "\n" + row_2 + "\n" + row_3 + "\n"

    test_file = temp_env["raw_dir"] / "bts_flights_2024.csv"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(full_csv)

    val_res = downloader.validate_file(test_file)
    assert val_res["validation_status"] == "PASSED"
    assert val_res["row_count"] == 3
    assert val_res["column_count"] == len(cols)
    assert val_res["file_size_bytes"] > 0
    assert len(val_res["sha256"]) == 64
    assert len(val_res["missing_required_columns"]) == 0


def test_file_validation_empty_file_fails(temp_env):
    """Test that validating an empty file raises ValueError."""
    downloader = BTSDownloader(config_path=str(temp_env["config_file"]))
    empty_file = temp_env["raw_dir"] / "empty.csv"
    empty_file.touch()

    with pytest.raises(ValueError, match="empty"):
        downloader.validate_file(empty_file)


def test_file_validation_missing_columns_warning(temp_env):
    """Test that a file missing required columns is marked as WARNING."""
    downloader = BTSDownloader(config_path=str(temp_env["config_file"]))

    # CSV with only 3 columns
    csv_content = '"Year","Quarter","Month"\n2024,1,1\n2024,1,2\n'
    test_file = temp_env["raw_dir"] / "bts_flights_2024.csv"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(csv_content)

    val_res = downloader.validate_file(test_file)
    assert val_res["validation_status"] == "WARNING"
    assert val_res["column_count"] == 3
    assert len(val_res["missing_required_columns"]) > 0
    assert "FlightDate" in val_res["missing_required_columns"]


def test_metadata_creation_and_consistency(temp_env):
    """Test that metadata.json is created and records all expected fields."""
    downloader = BTSDownloader(config_path=str(temp_env["config_file"]))

    mock_results = {
        2024: {
            "file": str(temp_env["raw_dir"] / "bts_flights_2024.csv"),
            "filename": "bts_flights_2024.csv",
            "file_size_bytes": 1048576,
            "file_size_mb": 1.0,
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "row_count": 50000,
            "column_count": 58,
            "validation_status": "PASSED",
            "missing_required_columns": [],
        }
    }

    meta_path = downloader.update_metadata(year_results=mock_results, overall_status="SUCCESS")
    assert meta_path.exists()

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["source"] == "U.S. Bureau of Transportation Statistics (BTS)"
    assert meta["overall_status"] == "SUCCESS"
    assert "2024" in meta["years"]
    y24 = meta["years"]["2024"]
    assert y24["row_count"] == 50000
    assert y24["column_count"] == 58
    assert y24["sha256"] == "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    assert y24["validation_status"] == "PASSED"


def test_overwrite_behavior(temp_env):
    """Test that downloader does not re-download if file exists and overwrite=False."""
    downloader = BTSDownloader(config_path=str(temp_env["config_file"]))
    target = downloader.get_output_filepath(2024)
    target.write_text("Year,Month\n2024,1\n")

    with patch.object(downloader, "download_month_zip") as mock_dl:
        res = downloader.download_year(2024)
        assert res == target
        # Should NOT have called download_month_zip
        mock_dl.assert_not_called()
