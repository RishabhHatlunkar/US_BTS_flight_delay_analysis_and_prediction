"""
Unit Tests for V2 Silver Cleaning & Transformation Layer
Tests date/time parsing, negative delays, cancellation/diversion handling,
arrival delay label logic, and quarantine for rejected rows.
"""

import pytest
from v2.src.bronze.ingest import ingest_bronze_files
from v2.src.silver.clean import transform_bronze_to_silver
from v2.src.utils.time_utils import parse_hhmm_time, extract_hour, parse_iso_date
from v2.src.utils.db import get_db_connection


def test_time_and_date_parsing():
    """Tests individual time and date parsing functions with boundary cases."""
    assert parse_hhmm_time("0856") == "08:56"
    assert parse_hhmm_time("856") == "08:56"
    assert parse_hhmm_time("5") == "00:05"
    assert parse_hhmm_time("30") == "00:30"
    assert parse_hhmm_time("2359") == "23:59"
    assert parse_hhmm_time("2400") == "00:00"
    assert parse_hhmm_time("") is None
    assert parse_hhmm_time(None) is None
    assert parse_hhmm_time("9999") is None

    assert extract_hour("08:56") == 8
    assert extract_hour("23:59") == 23
    assert extract_hour(None) is None

    assert parse_iso_date("2024-01-08") == "2024-01-08"
    assert parse_iso_date("2024/01/08") == "2024-01-08"
    assert parse_iso_date("invalid") is None


def test_silver_transform_and_rejections(test_env):
    """Tests Silver transformation: clean rows populate silver_flights and invalid rows hit silver_rejected_rows."""
    config = test_env["config"]
    ingest_bronze_files(config, force=True)
    q_report = transform_bronze_to_silver(config, force=True)

    assert q_report["input_bronze_rows"] == 6
    assert q_report["output_silver_rows"] == 5  # 5 valid, 1 rejected
    assert q_report["rejected_rows"] == 1

    conn = get_db_connection(test_env["db_path"])
    cursor = conn.cursor()

    # 1. Check rejected rows table
    cursor.execute("SELECT rejection_reason, source_file FROM silver_rejected_rows")
    reject = cursor.fetchone()
    assert "Invalid or missing FlightDate" in reject["rejection_reason"]

    # 2. Check early arrival / negative delay preservation
    cursor.execute("""
        SELECT scheduled_departure_time, departure_delay_minutes, arrival_delay_minutes, arrival_delay_flag
        FROM silver_flights
        WHERE reporting_airline = '9E' AND flight_number = '4801'
    """)
    ontime = cursor.fetchone()
    assert ontime["scheduled_departure_time"] == "08:56"
    assert ontime["departure_delay_minutes"] == -5.0
    assert ontime["arrival_delay_minutes"] == -11.0
    assert ontime["arrival_delay_flag"] == 0  # < 15 mins -> 0

    # 3. Check delayed flight (>15 mins)
    cursor.execute("""
        SELECT arrival_delay_minutes, arrival_delay_flag, carrier_delay_minutes, nas_delay_minutes
        FROM silver_flights
        WHERE reporting_airline = 'AA' AND flight_number = '100'
    """)
    delayed = cursor.fetchone()
    assert delayed["arrival_delay_minutes"] == 30.0
    assert delayed["arrival_delay_flag"] == 1
    assert delayed["carrier_delay_minutes"] == 20.0
    assert delayed["nas_delay_minutes"] == 10.0

    # 4. Check cancelled flight (arrival_delay_flag must be NULL)
    cursor.execute("""
        SELECT cancelled, cancellation_code, arrival_delay_flag, actual_departure_time
        FROM silver_flights
        WHERE reporting_airline = 'DL' AND flight_number = '1203'
    """)
    canc = cursor.fetchone()
    assert canc["cancelled"] == 1
    assert canc["cancellation_code"] == "B"
    assert canc["arrival_delay_flag"] is None
    assert canc["actual_departure_time"] is None

    # 5. Check diverted flight (arrival_delay_flag must be NULL)
    cursor.execute("""
        SELECT diverted, arrival_delay_flag
        FROM silver_flights
        WHERE reporting_airline = 'UA' AND flight_number = '450'
    """)
    div = cursor.fetchone()
    assert div["diverted"] == 1
    assert div["arrival_delay_flag"] is None

    conn.close()
