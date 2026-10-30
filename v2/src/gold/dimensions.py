"""
Gold Dimension Population Engine
Extracts distinct dimensional entities from silver_flights into:
- gold_dim_date
- gold_dim_airline
- gold_dim_airport (shared role-playing for origin and dest)
- gold_dim_route (directional)
"""

import calendar
from datetime import datetime
import logging
from typing import Dict, Any, Optional

from ..utils.db import get_db_connection


def populate_gold_dimensions(config: dict, force: bool = False, logger: Optional[logging.Logger] = None) -> Dict[str, int]:
    """
    Builds or updates all Gold dimensions from silver_flights.
    """
    from pathlib import Path
    from ..utils.db import execute_sql_file

    log = logger or logging.getLogger("v2_gold_dimensions")
    db_path = config["database"]["path"]
    conn = get_db_connection(db_path)

    # Ensure Gold DDL schema is applied
    project_root = Path(__file__).resolve().parent.parent.parent
    gold_sql_path = project_root / "sql" / "schema" / "03_gold.sql"
    if gold_sql_path.exists():
        execute_sql_file(conn, str(gold_sql_path))

    cursor = conn.cursor()

    if force:
        log.info("Force rebuild of Gold dimensions requested. Note: Fact must also be refreshed to maintain FK integrity.")

    counts = {}

    # 1. Date Dimension
    log.info("Populating gold_dim_date...")
    cursor.execute("""
        SELECT DISTINCT flight_date, year, quarter, month, day_of_month, day_of_week
        FROM silver_flights
        ORDER BY flight_date
    """)
    dates = cursor.fetchall()
    date_rows = []
    for r in dates:
        f_date = r["flight_date"]
        dt = datetime.strptime(f_date, "%Y-%m-%d")
        date_key = int(dt.strftime("%Y%m%d"))
        day_name = calendar.day_name[dt.weekday()]
        month_name = calendar.month_name[dt.month]
        # Python dt.weekday() is 0=Mon, 6=Sun. BTS DayOfWeek is 1=Mon, 7=Sun.
        day_of_week = dt.weekday() + 1
        week_of_year = dt.isocalendar()[1]
        is_weekend = 1 if day_of_week in (6, 7) else 0

        date_rows.append((
            date_key, f_date, dt.day, day_of_week, day_name,
            dt.month, month_name, (dt.month - 1) // 3 + 1, dt.year,
            week_of_year, is_weekend
        ))

    cursor.executemany("""
        INSERT INTO gold_dim_date (
            date_key, full_date, day_of_month, day_of_week, day_name,
            month, month_name, quarter, year, week_of_year, is_weekend
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date_key) DO UPDATE SET
            full_date = excluded.full_date,
            is_weekend = excluded.is_weekend
    """, date_rows)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM gold_dim_date")
    counts["gold_dim_date"] = cursor.fetchone()[0]
    log.info(f"gold_dim_date populated: {counts['gold_dim_date']} distinct dates.")

    # 2. Airline Dimension
    log.info("Populating gold_dim_airline...")
    cursor.execute("""
        INSERT INTO gold_dim_airline (reporting_airline, dot_id_reporting_airline, iata_code_reporting_airline)
        SELECT DISTINCT reporting_airline, dot_id_reporting_airline, iata_code_reporting_airline
        FROM silver_flights
        WHERE reporting_airline IS NOT NULL
        ON CONFLICT(reporting_airline) DO UPDATE SET
            dot_id_reporting_airline = excluded.dot_id_reporting_airline,
            iata_code_reporting_airline = excluded.iata_code_reporting_airline
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM gold_dim_airline")
    counts["gold_dim_airline"] = cursor.fetchone()[0]
    log.info(f"gold_dim_airline populated: {counts['gold_dim_airline']} distinct airlines.")

    # 3. Airport Dimension (Shared role-playing for origin and dest)
    log.info("Populating gold_dim_airport (shared union of origin and destination)...")
    cursor.execute("""
        INSERT INTO gold_dim_airport (
            airport_id, airport_sequence_id, city_market_id, airport_code,
            city_name, state_code, state_fips, state_name, world_area_code
        )
        SELECT 
            airport_id, airport_sequence_id, city_market_id, airport_code,
            city_name, state_code, state_fips, state_name, world_area_code
        FROM (
            SELECT 
                origin_airport_id AS airport_id,
                origin_airport_seq_id AS airport_sequence_id,
                origin_city_market_id AS city_market_id,
                origin_airport_code AS airport_code,
                origin_city AS city_name,
                origin_state AS state_code,
                origin_state_fips AS state_fips,
                origin_state_name AS state_name,
                origin_wac AS world_area_code
            FROM silver_flights
            WHERE origin_airport_id IS NOT NULL
            UNION
            SELECT 
                destination_airport_id AS airport_id,
                destination_airport_seq_id AS airport_sequence_id,
                destination_city_market_id AS city_market_id,
                destination_airport_code AS airport_code,
                destination_city AS city_name,
                destination_state AS state_code,
                destination_state_fips AS state_fips,
                destination_state_name AS state_name,
                destination_wac AS world_area_code
            FROM silver_flights
            WHERE destination_airport_id IS NOT NULL
        ) u
        WHERE airport_id IS NOT NULL
        ON CONFLICT(airport_id) DO UPDATE SET
            airport_code = excluded.airport_code,
            city_name = excluded.city_name,
            state_code = excluded.state_code
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM gold_dim_airport")
    counts["gold_dim_airport"] = cursor.fetchone()[0]
    log.info(f"gold_dim_airport populated: {counts['gold_dim_airport']} distinct airports.")

    # 4. Route Dimension (Directional: AAA-BBB != BBB-AAA)
    log.info("Populating gold_dim_route (directional)...")
    cursor.execute("""
        INSERT INTO gold_dim_route (origin_airport_key, destination_airport_key, route_code)
        SELECT DISTINCT
            orig.airport_key,
            dest.airport_key,
            s.route_code
        FROM silver_flights s
        JOIN gold_dim_airport orig ON s.origin_airport_id = orig.airport_id
        JOIN gold_dim_airport dest ON s.destination_airport_id = dest.airport_id
        WHERE s.route_code IS NOT NULL
        ON CONFLICT(route_code) DO NOTHING
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM gold_dim_route")
    counts["gold_dim_route"] = cursor.fetchone()[0]
    log.info(f"gold_dim_route populated: {counts['gold_dim_route']} distinct routes.")

    conn.close()
    return counts
