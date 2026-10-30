"""
Unit Tests for V2 Bronze Ingestion Layer
Tests schema inspection, provenance columns, chunking, and idempotency.
"""

import sqlite3
import pytest
from v2.src.bronze.ingest import ingest_bronze_files
from v2.src.utils.db import get_db_connection


def test_bronze_ingestion_and_provenance(test_env):
    """Tests that CSV data is faithfully ingested into bronze_bts_flights with provenance metadata."""
    config = test_env["config"]
    res = ingest_bronze_files(config, force=False)

    assert res["overall_status"] == "SUCCESS"
    assert res["total_inserted"] == 6

    conn = get_db_connection(test_env["db_path"])
    cursor = conn.cursor()

    # Verify row count
    cursor.execute("SELECT COUNT(*) FROM bronze_bts_flights")
    assert cursor.fetchone()[0] == 6

    # Verify provenance columns
    cursor.execute("""
        SELECT bronze_id, source_file, source_year, ingestion_timestamp, source_row_hash,
               Reporting_Airline, FlightDate, Origin, Dest
        FROM bronze_bts_flights
        LIMIT 1
    """)
    row = cursor.fetchone()
    assert row["bronze_id"] is not None
    assert row["source_file"] == "bts_flights_2024.csv"
    assert row["source_year"] == 2024
    assert len(row["source_row_hash"]) == 64  # SHA-256 length
    assert row["FlightDate"] == "2024-01-08"
    assert row["Reporting_Airline"] == "9E"
    conn.close()


def test_bronze_idempotency_without_duplication(test_env):
    """Tests that repeated ingestion of unchanged source files skips and does not inflate row count."""
    config = test_env["config"]
    # First ingestion
    ingest_bronze_files(config, force=False)

    # Second ingestion without force
    second_res = ingest_bronze_files(config, force=False)
    assert second_res["total_inserted"] == 0
    assert second_res["files"][0]["status"] == "SKIPPED"

    conn = get_db_connection(test_env["db_path"])
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bronze_bts_flights")
    assert cursor.fetchone()[0] == 6  # Count remains exactly 6
    conn.close()


def test_bronze_force_rebuild(test_env):
    """Tests that force=True safely reloads the file without duplicate accumulation."""
    config = test_env["config"]
    ingest_bronze_files(config, force=False)

    # Force rebuild
    re_res = ingest_bronze_files(config, force=True)
    assert re_res["total_inserted"] == 6

    conn = get_db_connection(test_env["db_path"])
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bronze_bts_flights")
    assert cursor.fetchone()[0] == 6
    conn.close()
