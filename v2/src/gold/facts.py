"""
Gold Fact Table Loading Engine
Loads silver_flights into gold_fact_flight resolving all surrogate dimension keys.
"""

import logging
import time
from typing import Dict, Any, Optional

from ..utils.db import get_db_connection


def load_gold_fact_flights(
    config: dict,
    force: bool = False,
    batch_size: int = 50000,
    logger: Optional[logging.Logger] = None
) -> Dict[str, Any]:
    """
    Populates gold_fact_flight from silver_flights.
    Enforces referential integrity by joining all 4 dimensions.
    """
    log = logger or logging.getLogger("v2_gold_facts")
    db_path = config["database"]["path"]
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    fact_table = config.get("tables", {}).get("gold_fact_flight", "gold_fact_flight")

    if force:
        log.info(f"Clearing {fact_table} for full rebuild...")
        conn.execute(f"DELETE FROM {fact_table};")
        conn.commit()

    start_time = time.time()
    log.info(f"Loading {fact_table} with dimension key resolution...")

    # Insert with surrogate key resolution via SQL JOIN
    cursor.execute(f"""
        INSERT INTO {fact_table} (
            date_key,
            airline_key,
            origin_airport_key,
            destination_airport_key,
            route_key,
            flight_number,
            tail_number,
            scheduled_departure_time,
            actual_departure_time,
            departure_delay_minutes,
            scheduled_arrival_time,
            actual_arrival_time,
            arrival_delay_minutes,
            taxi_out_minutes,
            taxi_in_minutes,
            scheduled_elapsed_minutes,
            actual_elapsed_minutes,
            air_time_minutes,
            flights,
            distance_miles,
            cancelled,
            cancellation_code,
            diverted,
            carrier_delay_minutes,
            weather_delay_minutes,
            nas_delay_minutes,
            security_delay_minutes,
            late_aircraft_delay_minutes,
            arrival_delay_flag,
            source_file,
            source_row_hash
        )
        SELECT
            d.date_key,
            a.airline_key,
            orig.airport_key,
            dest.airport_key,
            r.route_key,
            s.flight_number,
            s.tail_number,
            s.scheduled_departure_time,
            s.actual_departure_time,
            s.departure_delay_minutes,
            s.scheduled_arrival_time,
            s.actual_arrival_time,
            s.arrival_delay_minutes,
            s.taxi_out_minutes,
            s.taxi_in_minutes,
            s.scheduled_elapsed_minutes,
            s.actual_elapsed_minutes,
            s.air_time_minutes,
            s.flights,
            s.distance_miles,
            s.cancelled,
            s.cancellation_code,
            s.diverted,
            s.carrier_delay_minutes,
            s.weather_delay_minutes,
            s.nas_delay_minutes,
            s.security_delay_minutes,
            s.late_aircraft_delay_minutes,
            s.arrival_delay_flag,
            s.source_file,
            s.source_row_hash
        FROM silver_flights s
        JOIN gold_dim_date d ON s.flight_date = d.full_date
        JOIN gold_dim_airline a ON s.reporting_airline = a.reporting_airline
        JOIN gold_dim_airport orig ON s.origin_airport_id = orig.airport_id
        JOIN gold_dim_airport dest ON s.destination_airport_id = dest.airport_id
        JOIN gold_dim_route r ON s.route_code = r.route_code
        WHERE NOT EXISTS (
            SELECT 1 FROM {fact_table} f WHERE f.source_row_hash = s.source_row_hash
        );
    """)
    inserted_count = cursor.rowcount
    conn.commit()

    cursor.execute(f"SELECT COUNT(*) FROM {fact_table}")
    total_fact_count = cursor.fetchone()[0]

    elapsed = time.time() - start_time
    log.info(f"{fact_table} loaded: {inserted_count:,} new rows inserted ({total_fact_count:,} total) in {elapsed:.2f}s.")

    conn.close()
    return {
        "inserted_rows": inserted_count,
        "total_rows": total_fact_count,
        "duration_seconds": round(elapsed, 2),
        "status": "SUCCESS"
    }
