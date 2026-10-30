"""
Integration Tests for V2 End-to-End Pipeline Execution
Tests end-to-end execution, audit logging, and error handling.
"""

import os
import yaml
import pytest
from v2.src.pipeline.run_pipeline import run_pipeline
from v2.src.utils.db import get_db_connection


def test_pipeline_end_to_end_success(test_env):
    """Tests complete run_pipeline execution with audit logging."""
    config = test_env["config"]
    tmp_cfg_file = os.path.join(test_env["reports_dir"], "test_config.yaml")
    with open(tmp_cfg_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f)

    # Run entire pipeline on test env
    rc = run_pipeline(stage="all", config_path=tmp_cfg_file, force=True, run_queries=True)
    assert rc == 0

    # Verify audit log in etl_run_log table
    conn = get_db_connection(config["database"]["path"])
    cursor = conn.cursor()
    cursor.execute("SELECT stage, status FROM etl_run_log ORDER BY run_id")
    logs = cursor.fetchall()

    stages = [r["stage"] for r in logs]
    assert "bronze" in stages
    assert "silver" in stages
    assert "gold" in stages

    for r in logs:
        assert r["status"] == "SUCCESS"

    conn.close()


def test_pipeline_transaction_rollback_on_failure(test_env):
    """Tests that transaction rollback preserves state when an error occurs."""
    from v2.src.utils.db import get_db_connection, db_transaction
    import sqlite3

    conn = get_db_connection(test_env["db_path"])
    # Record starting count
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bronze_manifest")
    initial_count = cur.fetchone()[0]

    # Attempt a transaction that intentionally raises an error
    with pytest.raises(sqlite3.OperationalError):
        with db_transaction(conn):
            conn.execute("""
                INSERT INTO bronze_manifest (filename, source_year, row_count, ingested_at, status)
                VALUES ('temp_fail.csv', 2024, 10, '2024-01-01', 'SUCCESS')
            """)
            # Force syntax error inside transaction block
            conn.execute("INVALID SQL STATEMENT THAT MUST FAIL;")

    # Verify rollback: temp_fail.csv was NOT committed
    cur.execute("SELECT COUNT(*) FROM bronze_manifest")
    assert cur.fetchone()[0] == initial_count
    conn.close()


def test_legitimate_duplicate_records_handled(test_env):
    """Tests that legitimate flight observations with identical business attributes on same day are preserved via distinct row hashes."""
    from v2.src.utils.hashing import generate_source_row_hash

    row1 = {
        "FlightDate": "2024-01-08", "Reporting_Airline": "AA",
        "Flight_Number_Reporting_Airline": "100", "Tail_Number": "N104NN",
        "Origin": "LAX", "Dest": "SFO", "CRSDepTime": "1425", "DepTime": "1450"
    }
    # Observation 1 at line 10
    hash1 = generate_source_row_hash(row1, source_file="file.csv", row_idx=10)
    # Identical observation 2 at line 50
    hash2 = generate_source_row_hash(row1, source_file="file.csv", row_idx=50)

    # Hashes must be distinct
    assert hash1 != hash2
