"""
V2 Local SQLite Medallion Pipeline Orchestrator
Coordinates Bronze ingestion, Silver cleaning, Gold star schema loading,
validation, and observability logging.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import load_v2_config
from ..utils.db import get_db_connection, execute_sql_file
from ..utils.logger import setup_logger
from ..bronze.ingest import ingest_bronze_files
from ..silver.clean import transform_bronze_to_silver
from ..gold.dimensions import populate_gold_dimensions
from ..gold.facts import load_gold_fact_flights
from ..gold.validator import validate_gold_warehouse
from ..analytics.run_analytics import execute_all_analytics


def log_audit_run(
    conn,
    stage: str,
    start_ts: str,
    end_ts: str,
    status: str,
    source_files: str = "",
    input_rows: int = 0,
    inserted_rows: int = 0,
    updated_rows: int = 0,
    rejected_rows: int = 0,
    error_message: Optional[str] = None,
    duration_sec: float = 0.0
) -> None:
    """Records pipeline stage execution details in etl_run_log table."""
    try:
        conn.execute("""
            INSERT INTO etl_run_log (
                stage, start_timestamp, end_timestamp, status, source_files,
                input_row_count, inserted_row_count, updated_row_count,
                rejected_row_count, error_message, duration_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stage, start_ts, end_ts, status, source_files,
            input_rows, inserted_rows, updated_rows, rejected_rows,
            error_message, duration_sec
        ))
        conn.commit()
    except Exception as e:
        logging.getLogger("v2_pipeline").warning(f"Failed to record audit log: {e}")


def run_pipeline(
    stage: str = "all",
    config_path: Optional[str] = None,
    max_rows: Optional[int] = None,
    force: bool = False,
    run_queries: bool = True
) -> int:
    """
    Executes the configured ETL pipeline stages.
    Returns 0 on success, 1 on failure.
    """
    config = load_v2_config(config_path)
    logger = setup_logger(
        "v2_pipeline",
        log_file=config.get("logging", {}).get("log_file"),
        level=config.get("logging", {}).get("log_level", "INFO")
    )

    logger.info("=" * 80)
    logger.info("FLIGHT DELAY ANALYTICS & PREDICTION — V2 LOCAL SQLITE PIPELINE")
    logger.info(f"Target Stage: {stage.upper()} | Force Rebuild: {force} | Max Rows/File: {max_rows}")
    logger.info(f"Database Path: {config['database']['path']}")
    logger.info("=" * 80)

    # Initialize Audit Table
    db_path = config["database"]["path"]
    conn = get_db_connection(db_path)
    project_root = Path(__file__).resolve().parent.parent.parent
    audit_sql_path = project_root / "sql" / "schema" / "04_audit.sql"
    if audit_sql_path.exists():
        execute_sql_file(conn, str(audit_sql_path))

    pipeline_start_ts = datetime.now(timezone.utc).isoformat()
    start_time = time.time()
    summary = {
        "pipeline_version": "v2_sqlite",
        "started_at": pipeline_start_ts,
        "database_path": db_path,
        "stages": {},
        "overall_status": "SUCCESS"
    }

    try:
        # Stage 1: Bronze Ingestion
        if stage in ("all", "bronze"):
            s_start = datetime.now(timezone.utc).isoformat()
            t0 = time.time()
            b_res = ingest_bronze_files(config, force=force, max_rows=max_rows, logger=logger)
            dur = time.time() - t0
            s_end = datetime.now(timezone.utc).isoformat()
            summary["stages"]["bronze"] = b_res

            log_audit_run(
                conn, stage="bronze", start_ts=s_start, end_ts=s_end,
                status=b_res.get("overall_status", "SUCCESS"),
                source_files=", ".join([f["filename"] for f in b_res.get("files", [])]),
                input_rows=b_res.get("total_read", 0),
                inserted_rows=b_res.get("total_inserted", 0),
                rejected_rows=b_res.get("total_rejected", 0),
                duration_sec=dur
            )

        # Stage 2: Silver Cleaning & Transformation
        if stage in ("all", "silver"):
            s_start = datetime.now(timezone.utc).isoformat()
            t0 = time.time()
            s_res = transform_bronze_to_silver(config, force=force, logger=logger)
            dur = time.time() - t0
            s_end = datetime.now(timezone.utc).isoformat()
            summary["stages"]["silver"] = s_res

            log_audit_run(
                conn, stage="silver", start_ts=s_start, end_ts=s_end,
                status=s_res.get("status", "SUCCESS"),
                input_rows=s_res.get("input_bronze_rows", 0),
                inserted_rows=s_res.get("output_silver_rows", 0),
                rejected_rows=s_res.get("rejected_rows", 0),
                duration_sec=dur
            )

        # Stage 3: Gold Warehouse Dimensions & Fact Loading
        if stage in ("all", "gold"):
            # A. Populate Dimensions
            s_start = datetime.now(timezone.utc).isoformat()
            t0 = time.time()
            d_counts = populate_gold_dimensions(config, force=force, logger=logger)

            # B. Load Fact Flight Table
            f_res = load_gold_fact_flights(config, force=force, logger=logger)
            dur = time.time() - t0
            s_end = datetime.now(timezone.utc).isoformat()

            summary["stages"]["gold_dimensions"] = d_counts
            summary["stages"]["gold_facts"] = f_res

            log_audit_run(
                conn, stage="gold", start_ts=s_start, end_ts=s_end,
                status=f_res.get("status", "SUCCESS"),
                inserted_rows=f_res.get("inserted_rows", 0),
                duration_sec=dur
            )

        # Stage 4: Validation
        if stage in ("all", "validate", "gold"):
            v_res = validate_gold_warehouse(config, logger=logger)
            summary["stages"]["validation"] = v_res
            if not v_res.get("is_valid", False):
                summary["overall_status"] = "VALIDATION_FAILED"

        # Stage 5: Analytics & OLAP Verification
        if stage in ("all", "analytics") and run_queries:
            a_res = execute_all_analytics(config, logger=logger)
            summary["stages"]["analytics"] = {
                "total_queries_run": len(a_res),
                "queries": list(a_res.keys())
            }

    except Exception as e:
        logger.exception(f"Pipeline failed with exception: {e}")
        summary["overall_status"] = "FAILED"
        summary["error"] = str(e)
        log_audit_run(
            conn, stage=stage, start_ts=pipeline_start_ts,
            end_ts=datetime.now(timezone.utc).isoformat(),
            status="FAILED", error_message=str(e),
            duration_sec=time.time() - start_time
        )
        conn.close()
        return 1

    summary["completed_at"] = datetime.now(timezone.utc).isoformat()
    summary["duration_seconds"] = round(time.time() - start_time, 2)
    conn.close()

    # Save summary report
    sum_report_path = config.get("reports", {}).get("pipeline_summary", "v2/reports/pipeline_summary.json")
    os.makedirs(os.path.dirname(os.path.abspath(sum_report_path)), exist_ok=True)
    with open(sum_report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 80)
    logger.info(f"PIPELINE COMPLETED: {summary['overall_status']} in {summary['duration_seconds']}s")
    logger.info(f"Summary written to: {sum_report_path}")
    logger.info("=" * 80)

    return 0 if summary["overall_status"] in ("SUCCESS", "PARTIAL_FAILURE") else 1


def main():
    parser = argparse.ArgumentParser(description="V2 Local SQLite Medallion Data Warehouse Pipeline")
    parser.add_argument("--stage", choices=["all", "bronze", "silver", "gold", "validate", "analytics"], default="all", help="Pipeline stage to execute")
    parser.add_argument("--limit", type=int, default=None, help="Maximum rows per CSV file to process (for sampling/testing)")
    parser.add_argument("--rebuild", "--force", dest="force", action="store_true", help="Force rebuild of target stages")
    parser.add_argument("--config", type=str, default=None, help="Path to custom config YAML")
    parser.add_argument("--no-analytics", dest="no_analytics", action="store_true", help="Skip analytics queries run")

    args = parser.parse_args()
    rc = run_pipeline(
        stage=args.stage,
        config_path=args.config,
        max_rows=args.limit,
        force=args.force,
        run_queries=not args.no_analytics
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
