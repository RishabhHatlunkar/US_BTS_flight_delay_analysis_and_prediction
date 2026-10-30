"""
Silver Transformation and Data Quality Engine
Reads raw records from bronze_bts_flights, standardises schemas, performs rigorous
validation, and writes cleaned records to silver_flights with quarantine for rejects.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from ..utils.db import get_db_connection, execute_sql_file, db_transaction
from ..utils.time_utils import parse_hhmm_time, extract_hour, parse_iso_date
from ..utils.logger import setup_logger


def to_str(val: Any) -> Optional[str]:
    """Converts value to stripped string or None if empty."""
    if val is None:
        return None
    s = str(val).strip()
    return s if s and s.lower() not in ("none", "null") else None


def to_int(val: Any) -> Optional[int]:
    """Safely converts string/float to integer, handling decimal strings like '1.00'."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("none", "null"):
        return None
    try:
        if "." in s:
            return int(float(s))
        return int(s)
    except (ValueError, TypeError):
        return None


def to_float(val: Any) -> Optional[float]:
    """Safely converts value to float, preserving negative delays and exact zeros."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("none", "null"):
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def derive_arrival_delay_flag(
    cancelled: int,
    diverted: int,
    arr_del15: Optional[float],
    arr_delay: Optional[float]
) -> Optional[int]:
    """
    Deterministic target label logic for arrival delay:
    - 1: Delay >= 15 minutes
    - 0: On-time (Delay < 15 minutes)
    - NULL: Cancelled or Diverted with unknown outcome, or missing arrival metrics
    """
    if cancelled == 1:
        return None

    if diverted == 1:
        if arr_delay is not None:
            return 1 if arr_delay >= 15.0 else 0
        return None

    if arr_del15 == 1.0 or (arr_delay is not None and arr_delay >= 15.0):
        return 1

    if arr_del15 == 0.0 or (arr_delay is not None and arr_delay < 15.0):
        return 0

    return None


def clean_row(row: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Cleans, types, and validates a single Bronze record.
    Returns (cleaned_dict, None) on success, or (None, rejection_reason) on failure.
    """
    # Critical Validation 1: FlightDate
    raw_date = row.get("FlightDate")
    flight_date = parse_iso_date(raw_date)
    if not flight_date:
        return None, f"Invalid or missing FlightDate: '{raw_date}'"

    # Critical Validation 2: Origin & Destination Airport Identifiers
    origin_code = to_str(row.get("Origin"))
    origin_id = to_int(row.get("OriginAirportID"))
    dest_code = to_str(row.get("Dest"))
    dest_id = to_int(row.get("DestAirportID"))

    if not origin_code or not origin_id:
        return None, f"Missing origin airport identifiers (Origin='{origin_code}', ID='{origin_id}')"
    if not dest_code or not dest_id:
        return None, f"Missing destination airport identifiers (Dest='{dest_code}', ID='{dest_id}')"

    # Critical Validation 3: Reporting Airline
    airline = to_str(row.get("Reporting_Airline"))
    if not airline:
        return None, "Missing Reporting_Airline"

    # Parse Calendar attributes
    dt_parts = [int(p) for p in flight_date.split("-")]
    year = to_int(row.get("Year")) or dt_parts[0]
    month = to_int(row.get("Month")) or dt_parts[1]
    day_of_month = to_int(row.get("DayofMonth")) or dt_parts[2]
    quarter = to_int(row.get("Quarter")) or ((month - 1) // 3 + 1)
    day_of_week = to_int(row.get("DayOfWeek"))

    # Operational Times (HH:MM)
    crs_dep_time = parse_hhmm_time(row.get("CRSDepTime"))
    actual_dep_time = parse_hhmm_time(row.get("DepTime"))
    crs_arr_time = parse_hhmm_time(row.get("CRSArrTime"))
    actual_arr_time = parse_hhmm_time(row.get("ArrTime"))

    departure_hour = extract_hour(crs_dep_time)
    arrival_hour = extract_hour(crs_arr_time)

    # Delays (minutes) - preserve negative values
    dep_delay = to_float(row.get("DepDelay"))
    arr_delay = to_float(row.get("ArrDelay"))
    arr_del15 = to_float(row.get("ArrDel15"))

    # Status Flags
    cancelled = to_int(row.get("Cancelled")) or 0
    cancellation_code = to_str(row.get("CancellationCode"))
    diverted = to_int(row.get("Diverted")) or 0

    # Arrival delay flag target
    arrival_delay_flag = derive_arrival_delay_flag(cancelled, diverted, arr_del15, arr_delay)

    # Route Code
    route_code = f"{origin_code}-{dest_code}"

    # Delay Breakdown Causes (preserve semantic NULLs when delay < 15 mins)
    carrier_delay = to_float(row.get("CarrierDelay"))
    weather_delay = to_float(row.get("WeatherDelay"))
    nas_delay = to_float(row.get("NASDelay"))
    security_delay = to_float(row.get("SecurityDelay"))
    late_aircraft_delay = to_float(row.get("LateAircraftDelay"))

    cleaned = {
        "bronze_id": row.get("bronze_id"),
        "source_file": row.get("source_file"),
        "source_year": row.get("source_year"),
        "source_row_hash": row.get("source_row_hash"),
        "flight_date": flight_date,
        "year": year,
        "quarter": quarter,
        "month": month,
        "day_of_month": day_of_month,
        "day_of_week": day_of_week,
        "reporting_airline": airline,
        "dot_id_reporting_airline": to_int(row.get("DOT_ID_Reporting_Airline")),
        "iata_code_reporting_airline": to_str(row.get("IATA_CODE_Reporting_Airline")),
        "flight_number": to_str(row.get("Flight_Number_Reporting_Airline")),
        "tail_number": to_str(row.get("Tail_Number")),
        "origin_airport_id": origin_id,
        "origin_airport_seq_id": to_int(row.get("OriginAirportSeqID")),
        "origin_city_market_id": to_int(row.get("OriginCityMarketID")),
        "origin_airport_code": origin_code,
        "origin_city": to_str(row.get("OriginCityName")),
        "origin_state": to_str(row.get("OriginState")),
        "origin_state_fips": to_str(row.get("OriginStateFips")),
        "origin_state_name": to_str(row.get("OriginStateName")),
        "origin_wac": to_int(row.get("OriginWac")),
        "destination_airport_id": dest_id,
        "destination_airport_seq_id": to_int(row.get("DestAirportSeqID")),
        "destination_city_market_id": to_int(row.get("DestCityMarketID")),
        "destination_airport_code": dest_code,
        "destination_city": to_str(row.get("DestCityName")),
        "destination_state": to_str(row.get("DestState")),
        "destination_state_fips": to_str(row.get("DestStateFips")),
        "destination_state_name": to_str(row.get("DestStateName")),
        "destination_wac": to_int(row.get("DestWac")),
        "scheduled_departure_time": crs_dep_time,
        "actual_departure_time": actual_dep_time,
        "departure_delay_minutes": dep_delay,
        "scheduled_arrival_time": crs_arr_time,
        "actual_arrival_time": actual_arr_time,
        "arrival_delay_minutes": arr_delay,
        "taxi_out_minutes": to_float(row.get("TaxiOut")),
        "taxi_in_minutes": to_float(row.get("TaxiIn")),
        "scheduled_elapsed_minutes": to_float(row.get("CRSElapsedTime")),
        "actual_elapsed_minutes": to_float(row.get("ActualElapsedTime")),
        "air_time_minutes": to_float(row.get("AirTime")),
        "flights": to_float(row.get("Flights")) or 1.0,
        "distance_miles": to_float(row.get("Distance")),
        "distance_group": to_int(row.get("DistanceGroup")),
        "cancelled": cancelled,
        "cancellation_code": cancellation_code,
        "diverted": diverted,
        "carrier_delay_minutes": carrier_delay,
        "weather_delay_minutes": weather_delay,
        "nas_delay_minutes": nas_delay,
        "security_delay_minutes": security_delay,
        "late_aircraft_delay_minutes": late_aircraft_delay,
        "departure_hour": departure_hour,
        "arrival_hour": arrival_hour,
        "route_code": route_code,
        "arrival_delay_flag": arrival_delay_flag
    }

    return cleaned, None


def transform_bronze_to_silver(
    config: dict,
    force: bool = False,
    batch_size: int = 50000,
    logger: Optional[logging.Logger] = None
) -> Dict[str, Any]:
    """
    Transforms records from bronze_bts_flights into silver_flights.
    Extracts, types, standardises, validates, and populates data quality report.
    """
    log = logger or setup_logger(
        "v2_silver",
        log_file=config.get("logging", {}).get("log_file"),
        level=config.get("logging", {}).get("log_level", "INFO")
    )

    db_path = config["database"]["path"]
    conn = get_db_connection(db_path)

    # Initialize Silver DDL
    project_root = Path(__file__).resolve().parent.parent.parent
    silver_sql_path = project_root / "sql" / "schema" / "02_silver.sql"
    if silver_sql_path.exists():
        execute_sql_file(conn, str(silver_sql_path))

    bronze_table = config.get("tables", {}).get("bronze", "bronze_bts_flights")
    silver_table = config.get("tables", {}).get("silver", "silver_flights")
    rejected_table = config.get("tables", {}).get("silver_rejected", "silver_rejected_rows")

    if force:
        log.info(f"Rebuilding Silver layer (force=True): clearing {silver_table} and {rejected_table}...")
        conn.execute(f"DELETE FROM {silver_table};")
        conn.execute(f"DELETE FROM {rejected_table};")
        conn.commit()

    # Find which bronze rows to process (incremental or full)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT b.* FROM {bronze_table} b
        LEFT JOIN {silver_table} s ON b.source_row_hash = s.source_row_hash
        WHERE s.source_row_hash IS NULL
    """)

    log.info("Streaming un-transformed Bronze records into Silver...")
    start_time = time.time()

    silver_cols = [
        "bronze_id", "source_file", "source_year", "source_row_hash",
        "flight_date", "year", "quarter", "month", "day_of_month", "day_of_week",
        "reporting_airline", "dot_id_reporting_airline", "iata_code_reporting_airline",
        "flight_number", "tail_number",
        "origin_airport_id", "origin_airport_seq_id", "origin_city_market_id",
        "origin_airport_code", "origin_city", "origin_state", "origin_state_fips", "origin_state_name", "origin_wac",
        "destination_airport_id", "destination_airport_seq_id", "destination_city_market_id",
        "destination_airport_code", "destination_city", "destination_state", "destination_state_fips", "destination_state_name", "destination_wac",
        "scheduled_departure_time", "actual_departure_time", "departure_delay_minutes",
        "scheduled_arrival_time", "actual_arrival_time", "arrival_delay_minutes",
        "taxi_out_minutes", "taxi_in_minutes",
        "scheduled_elapsed_minutes", "actual_elapsed_minutes", "air_time_minutes",
        "flights", "distance_miles", "distance_group",
        "cancelled", "cancellation_code", "diverted",
        "carrier_delay_minutes", "weather_delay_minutes", "nas_delay_minutes", "security_delay_minutes", "late_aircraft_delay_minutes",
        "departure_hour", "arrival_hour", "route_code", "arrival_delay_flag"
    ]
    silver_placeholders = ", ".join(["?"] * len(silver_cols))
    insert_silver_sql = f"INSERT INTO {silver_table} ({', '.join(silver_cols)}) VALUES ({silver_placeholders})"

    reject_cols = ["bronze_id", "source_file", "source_row_hash", "rejection_reason", "raw_data", "rejected_at"]
    reject_placeholders = ", ".join(["?"] * len(reject_cols))
    insert_reject_sql = f"INSERT INTO {rejected_table} ({', '.join(reject_cols)}) VALUES ({reject_placeholders})"

    silver_batch = []
    reject_batch = []
    total_bronze_read = 0
    total_silver_inserted = 0
    total_rejected = 0

    cancelled_count = 0
    diverted_count = 0
    null_delay_outcomes = 0
    invalid_time_count = 0

    seen_hashes = set()

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break

        for r in rows:
            total_bronze_read += 1
            row_dict = dict(r)
            row_hash = row_dict.get("source_row_hash")

            # Check in-batch duplicate hash
            if row_hash in seen_hashes:
                total_rejected += 1
                reject_batch.append((
                    row_dict.get("bronze_id"),
                    row_dict.get("source_file"),
                    row_hash,
                    "Duplicate source_row_hash in current ingestion",
                    json.dumps(row_dict, default=str),
                    datetime.now(timezone.utc).isoformat()
                ))
                continue

            cleaned, reason = clean_row(row_dict)
            if cleaned:
                seen_hashes.add(row_hash)
                vals = [cleaned.get(c) for c in silver_cols]
                silver_batch.append(vals)

                if cleaned["cancelled"] == 1:
                    cancelled_count += 1
                if cleaned["diverted"] == 1:
                    diverted_count += 1
                if cleaned["arrival_delay_flag"] is None:
                    null_delay_outcomes += 1
                if cleaned["scheduled_departure_time"] is None and row_dict.get("CRSDepTime"):
                    invalid_time_count += 1
            else:
                total_rejected += 1
                reject_batch.append((
                    row_dict.get("bronze_id"),
                    row_dict.get("source_file"),
                    row_hash,
                    reason,
                    json.dumps(row_dict, default=str),
                    datetime.now(timezone.utc).isoformat()
                ))

        if len(silver_batch) >= batch_size:
            conn.executemany(insert_silver_sql, silver_batch)
            conn.commit()
            total_silver_inserted += len(silver_batch)
            log.info(f"Silver progress: {total_silver_inserted:,} clean records inserted...")
            silver_batch = []

        if len(reject_batch) >= 1000:
            conn.executemany(insert_reject_sql, reject_batch)
            conn.commit()
            reject_batch = []

    # Final flush
    if silver_batch:
        conn.executemany(insert_silver_sql, silver_batch)
        conn.commit()
        total_silver_inserted += len(silver_batch)

    if reject_batch:
        conn.executemany(insert_reject_sql, reject_batch)
        conn.commit()

    elapsed = time.time() - start_time
    log.info(f"Silver transformation complete: {total_silver_inserted:,} clean rows inserted, {total_rejected} quarantined in {elapsed:.2f}s.")

    # Quality Report
    quality_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_bronze_rows": total_bronze_read,
        "output_silver_rows": total_silver_inserted,
        "rejected_rows": total_rejected,
        "metrics": {
            "cancellation_count": cancelled_count,
            "diversion_count": diverted_count,
            "null_arrival_delay_outcome_count": null_delay_outcomes,
            "invalid_time_format_count": invalid_time_count
        },
        "duration_seconds": round(elapsed, 2),
        "status": "SUCCESS"
    }

    report_path = config.get("reports", {}).get("silver_quality_report", "v2/reports/silver_quality_report.json")
    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(quality_report, rf, indent=2)

    conn.close()
    return quality_report
