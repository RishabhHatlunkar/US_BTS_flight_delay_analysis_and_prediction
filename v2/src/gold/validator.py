"""
Gold Warehouse Referential Integrity & Quality Validator
Validates dimension member resolution, foreign keys, row counts, and grain integrity.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from ..utils.db import get_db_connection


def validate_gold_warehouse(config: dict, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Executes automated referential integrity and consistency checks against Gold warehouse.
    Outputs validation report to reports/v2/gold_validation_report.json.
    """
    log = logger or logging.getLogger("v2_gold_validator")
    db_path = config["database"]["path"]
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    log.info("Running Gold warehouse referential integrity checks...")
    start_time = time.time()

    # 1. Table row counts
    table_counts = {}
    for tbl in [
        "gold_dim_date", "gold_dim_airline", "gold_dim_airport",
        "gold_dim_route", "gold_fact_flight", "silver_flights", "bronze_bts_flights"
    ]:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
        table_counts[tbl] = cursor.fetchone()[0]

    # 2. Foreign Key Integrity Checks on Fact table
    fk_checks = {}

    # Check Date FK
    cursor.execute("""
        SELECT COUNT(*) FROM gold_fact_flight f
        LEFT JOIN gold_dim_date d ON f.date_key = d.date_key
        WHERE d.date_key IS NULL
    """)
    fk_checks["unresolved_date_keys"] = cursor.fetchone()[0]

    # Check Airline FK
    cursor.execute("""
        SELECT COUNT(*) FROM gold_fact_flight f
        LEFT JOIN gold_dim_airline a ON f.airline_key = a.airline_key
        WHERE a.airline_key IS NULL
    """)
    fk_checks["unresolved_airline_keys"] = cursor.fetchone()[0]

    # Check Origin Airport FK
    cursor.execute("""
        SELECT COUNT(*) FROM gold_fact_flight f
        LEFT JOIN gold_dim_airport orig ON f.origin_airport_key = orig.airport_key
        WHERE orig.airport_key IS NULL
    """)
    fk_checks["unresolved_origin_airport_keys"] = cursor.fetchone()[0]

    # Check Destination Airport FK
    cursor.execute("""
        SELECT COUNT(*) FROM gold_fact_flight f
        LEFT JOIN gold_dim_airport dest ON f.destination_airport_key = dest.airport_key
        WHERE dest.airport_key IS NULL
    """)
    fk_checks["unresolved_dest_airport_keys"] = cursor.fetchone()[0]

    # Check Route FK
    cursor.execute("""
        SELECT COUNT(*) FROM gold_fact_flight f
        LEFT JOIN gold_dim_route r ON f.route_key = r.route_key
        WHERE r.route_key IS NULL
    """)
    fk_checks["unresolved_route_keys"] = cursor.fetchone()[0]

    total_unresolved = sum(fk_checks.values())

    # 3. Fact grain validation (Check uniqueness of source_row_hash)
    cursor.execute("""
        SELECT COUNT(*) - COUNT(DISTINCT source_row_hash) FROM gold_fact_flight
    """)
    duplicate_fact_hashes = cursor.fetchone()[0]

    # 4. Measure validation
    cursor.execute("""
        SELECT
            COUNT(*) AS total_flights,
            SUM(CASE WHEN cancelled = 1 THEN 1 ELSE 0 END) AS cancelled_flights,
            SUM(CASE WHEN diverted = 1 THEN 1 ELSE 0 END) AS diverted_flights,
            SUM(CASE WHEN arrival_delay_flag = 1 THEN 1 ELSE 0 END) AS delayed_flights,
            SUM(CASE WHEN arrival_delay_flag = 0 THEN 1 ELSE 0 END) AS ontime_flights,
            SUM(CASE WHEN arrival_delay_flag IS NULL THEN 1 ELSE 0 END) AS unknown_delay_flights
        FROM gold_fact_flight
    """)
    measures = dict(cursor.fetchone())

    elapsed = time.time() - start_time
    is_valid = (total_unresolved == 0 and duplicate_fact_hashes == 0)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_valid": is_valid,
        "table_row_counts": table_counts,
        "foreign_key_integrity": fk_checks,
        "total_unresolved_foreign_keys": total_unresolved,
        "duplicate_fact_grain_count": duplicate_fact_hashes,
        "flight_measures_summary": measures,
        "duration_seconds": round(elapsed, 2),
        "status": "PASSED" if is_valid else "FAILED"
    }

    report_path = config.get("reports", {}).get("gold_validation_report", "v2/reports/gold_validation_report.json")
    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2)

    log.info(f"Gold validation {'PASSED' if is_valid else 'FAILED'} (Unresolved FKs: {total_unresolved}) in {elapsed:.2f}s.")
    conn.close()
    return report
