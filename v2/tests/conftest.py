"""
Pytest Fixtures for V2 Local SQLite Pipeline Tests
Provides synthetic BTS CSV data and isolated temporary SQLite database fixtures.
"""

import csv
import os
import tempfile
import pytest
from pathlib import Path

from v2.src.utils.db import get_db_connection, execute_sql_file


@pytest.fixture(scope="session")
def synthetic_bts_rows():
    """Returns comprehensive synthetic BTS flight rows representing all operational scenarios."""
    return [
        # 1. On-time flight with early arrival (negative delay)
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "2024-01-08", "Reporting_Airline": "9E", "DOT_ID_Reporting_Airline": "20363",
            "IATA_CODE_Reporting_Airline": "9E", "Tail_Number": "N485PX", "Flight_Number_Reporting_Airline": "4801",
            "OriginAirportID": "12953", "OriginAirportSeqID": "1295304", "OriginCityMarketID": "31703",
            "Origin": "LGA", "OriginCityName": "New York, NY", "OriginState": "NY", "OriginStateFips": "36",
            "OriginStateName": "New York", "OriginWac": "22",
            "DestAirportID": "13871", "DestAirportSeqID": "1387102", "DestCityMarketID": "33316",
            "Dest": "OMA", "DestCityName": "Omaha, NE", "DestState": "NE", "DestStateFips": "31",
            "DestStateName": "Nebraska", "DestWac": "65",
            "CRSDepTime": "0856", "DepTime": "0851", "DepDelay": "-5.00", "DepDelayMinutes": "0.00", "DepDel15": "0.00",
            "DepartureDelayGroups": "-1", "DepTimeBlk": "0800-0859", "TaxiOut": "25.00", "WheelsOff": "0916",
            "WheelsOn": "1120", "TaxiIn": "4.00", "CRSArrTime": "1135", "ArrTime": "1124", "ArrDelay": "-11.00",
            "ArrDelayMinutes": "0.00", "ArrDel15": "0.00", "ArrivalDelayGroups": "-1", "ArrTimeBlk": "1100-1159",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "0.00",
            "CRSElapsedTime": "219.00", "ActualElapsedTime": "213.00", "AirTime": "184.00", "Flights": "1.00",
            "Distance": "1148.00", "DistanceGroup": "5",
            "CarrierDelay": "", "WeatherDelay": "", "NASDelay": "", "SecurityDelay": "", "LateAircraftDelay": ""
        },
        # 2. Delayed Flight (>15 mins with breakdown causes)
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "2024-01-08", "Reporting_Airline": "AA", "DOT_ID_Reporting_Airline": "19805",
            "IATA_CODE_Reporting_Airline": "AA", "Tail_Number": "N104NN", "Flight_Number_Reporting_Airline": "100",
            "OriginAirportID": "12892", "OriginAirportSeqID": "1289208", "OriginCityMarketID": "32575",
            "Origin": "LAX", "OriginCityName": "Los Angeles, CA", "OriginState": "CA", "OriginStateFips": "06",
            "OriginStateName": "California", "OriginWac": "91",
            "DestAirportID": "14771", "DestAirportSeqID": "1477104", "DestCityMarketID": "32575",
            "Dest": "SFO", "DestCityName": "San Francisco, CA", "DestState": "CA", "DestStateFips": "06",
            "DestStateName": "California", "DestWac": "91",
            "CRSDepTime": "1425", "DepTime": "1450", "DepDelay": "25.00", "DepDelayMinutes": "25.00", "DepDel15": "1.00",
            "DepartureDelayGroups": "1", "DepTimeBlk": "1400-1459", "TaxiOut": "15.00", "WheelsOff": "1505",
            "WheelsOn": "1620", "TaxiIn": "5.00", "CRSArrTime": "1555", "ArrTime": "1625", "ArrDelay": "30.00",
            "ArrDelayMinutes": "30.00", "ArrDel15": "1.00", "ArrivalDelayGroups": "2", "ArrTimeBlk": "1500-1559",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "0.00",
            "CRSElapsedTime": "90.00", "ActualElapsedTime": "95.00", "AirTime": "75.00", "Flights": "1.00",
            "Distance": "337.00", "DistanceGroup": "2",
            "CarrierDelay": "20.00", "WeatherDelay": "0.00", "NASDelay": "10.00", "SecurityDelay": "0.00", "LateAircraftDelay": "0.00"
        },
        # 3. Cancelled Flight (Weather cancellation)
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "2024-01-08", "Reporting_Airline": "DL", "DOT_ID_Reporting_Airline": "19790",
            "IATA_CODE_Reporting_Airline": "DL", "Tail_Number": "N3752", "Flight_Number_Reporting_Airline": "1203",
            "OriginAirportID": "10397", "OriginAirportSeqID": "1039707", "OriginCityMarketID": "30397",
            "Origin": "ATL", "OriginCityName": "Atlanta, GA", "OriginState": "GA", "OriginStateFips": "13",
            "OriginStateName": "Georgia", "OriginWac": "34",
            "DestAirportID": "12953", "DestAirportSeqID": "1295304", "DestCityMarketID": "31703",
            "Dest": "LGA", "DestCityName": "New York, NY", "DestState": "NY", "DestStateFips": "36",
            "DestStateName": "New York", "DestWac": "22",
            "CRSDepTime": "0700", "DepTime": "", "DepDelay": "", "DepDelayMinutes": "", "DepDel15": "",
            "DepartureDelayGroups": "", "DepTimeBlk": "0700-0759", "TaxiOut": "", "WheelsOff": "",
            "WheelsOn": "", "TaxiIn": "", "CRSArrTime": "0915", "ArrTime": "", "ArrDelay": "",
            "ArrDelayMinutes": "", "ArrDel15": "", "ArrivalDelayGroups": "", "ArrTimeBlk": "0900-0959",
            "Cancelled": "1.00", "CancellationCode": "B", "Diverted": "0.00",
            "CRSElapsedTime": "135.00", "ActualElapsedTime": "", "AirTime": "", "Flights": "1.00",
            "Distance": "762.00", "DistanceGroup": "4",
            "CarrierDelay": "", "WeatherDelay": "", "NASDelay": "", "SecurityDelay": "", "LateAircraftDelay": ""
        },
        # 4. Diverted Flight
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "2024-01-08", "Reporting_Airline": "UA", "DOT_ID_Reporting_Airline": "19977",
            "IATA_CODE_Reporting_Airline": "UA", "Tail_Number": "N412UA", "Flight_Number_Reporting_Airline": "450",
            "OriginAirportID": "13930", "OriginAirportSeqID": "1393007", "OriginCityMarketID": "30977",
            "Origin": "ORD", "OriginCityName": "Chicago, IL", "OriginState": "IL", "OriginStateFips": "17",
            "OriginStateName": "Illinois", "OriginWac": "41",
            "DestAirportID": "11292", "DestAirportSeqID": "1129202", "DestCityMarketID": "30325",
            "Dest": "DEN", "DestCityName": "Denver, CO", "DestState": "CO", "DestStateFips": "08",
            "DestStateName": "Colorado", "DestWac": "82",
            "CRSDepTime": "1600", "DepTime": "1605", "DepDelay": "5.00", "DepDelayMinutes": "5.00", "DepDel15": "0.00",
            "DepartureDelayGroups": "0", "DepTimeBlk": "1600-1659", "TaxiOut": "20.00", "WheelsOff": "1625",
            "WheelsOn": "", "TaxiIn": "", "CRSArrTime": "1745", "ArrTime": "", "ArrDelay": "",
            "ArrDelayMinutes": "", "ArrDel15": "", "ArrivalDelayGroups": "", "ArrTimeBlk": "1700-1759",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "1.00",
            "CRSElapsedTime": "165.00", "ActualElapsedTime": "", "AirTime": "", "Flights": "1.00",
            "Distance": "888.00", "DistanceGroup": "4",
            "CarrierDelay": "", "WeatherDelay": "", "NASDelay": "", "SecurityDelay": "", "LateAircraftDelay": ""
        },
        # 5. Reverse Route (OMA -> LGA) to test directional route uniqueness
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "2024-01-08", "Reporting_Airline": "9E", "DOT_ID_Reporting_Airline": "20363",
            "IATA_CODE_Reporting_Airline": "9E", "Tail_Number": "N485PX", "Flight_Number_Reporting_Airline": "4802",
            "OriginAirportID": "13871", "OriginAirportSeqID": "1387102", "OriginCityMarketID": "33316",
            "Origin": "OMA", "OriginCityName": "Omaha, NE", "OriginState": "NE", "OriginStateFips": "31",
            "OriginStateName": "Nebraska", "OriginWac": "65",
            "DestAirportID": "12953", "DestAirportSeqID": "1295304", "DestCityMarketID": "31703",
            "Dest": "LGA", "DestCityName": "New York, NY", "DestState": "NY", "DestStateFips": "36",
            "DestStateName": "New York", "DestWac": "22",
            "CRSDepTime": "1215", "DepTime": "1210", "DepDelay": "-5.00", "DepDelayMinutes": "0.00", "DepDel15": "0.00",
            "DepartureDelayGroups": "-1", "DepTimeBlk": "1200-1259", "TaxiOut": "15.00", "WheelsOff": "1225",
            "WheelsOn": "1545", "TaxiIn": "8.00", "CRSArrTime": "1600", "ArrTime": "1553", "ArrDelay": "-7.00",
            "ArrDelayMinutes": "0.00", "ArrDel15": "0.00", "ArrivalDelayGroups": "-1", "ArrTimeBlk": "1600-1659",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "0.00",
            "CRSElapsedTime": "165.00", "ActualElapsedTime": "163.00", "AirTime": "140.00", "Flights": "1.00",
            "Distance": "1148.00", "DistanceGroup": "5",
            "CarrierDelay": "", "WeatherDelay": "", "NASDelay": "", "SecurityDelay": "", "LateAircraftDelay": ""
        },
        # 6. Invalid Row (Missing FlightDate & Origin - should be quarantined)
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "", "Reporting_Airline": "AA", "DOT_ID_Reporting_Airline": "19805",
            "IATA_CODE_Reporting_Airline": "AA", "Tail_Number": "N999XX", "Flight_Number_Reporting_Airline": "999",
            "OriginAirportID": "", "OriginAirportSeqID": "", "OriginCityMarketID": "",
            "Origin": "", "OriginCityName": "", "OriginState": "", "OriginStateFips": "",
            "OriginStateName": "", "OriginWac": "",
            "DestAirportID": "14771", "DestAirportSeqID": "1477104", "DestCityMarketID": "32575",
            "Dest": "SFO", "DestCityName": "San Francisco, CA", "DestState": "CA", "DestStateFips": "06",
            "DestStateName": "California", "DestWac": "91",
            "CRSDepTime": "1000", "DepTime": "1000", "DepDelay": "0.00", "DepDelayMinutes": "0.00", "DepDel15": "0.00",
            "DepartureDelayGroups": "0", "DepTimeBlk": "1000-1059", "TaxiOut": "", "WheelsOff": "",
            "WheelsOn": "", "TaxiIn": "", "CRSArrTime": "1100", "ArrTime": "1100", "ArrDelay": "0.00",
            "ArrDelayMinutes": "0.00", "ArrDel15": "0.00", "ArrivalDelayGroups": "0", "ArrTimeBlk": "1100-1159",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "0.00",
            "CRSElapsedTime": "60.00", "ActualElapsedTime": "60.00", "AirTime": "50.00", "Flights": "1.00",
            "Distance": "300.00", "DistanceGroup": "2",
            "CarrierDelay": "", "WeatherDelay": "", "NASDelay": "", "SecurityDelay": "", "LateAircraftDelay": ""
        }
    ]


@pytest.fixture
def test_env(tmp_path, synthetic_bts_rows):
    """Sets up temporary raw CSV and SQLite test database environment."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    db_file = tmp_path / "test_flight_delay.db"
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    csv_file = raw_dir / "bts_flights_2024.csv"

    # Write synthetic CSV with trailing comma matching real BTS format using csv.writer for proper quoting
    headers = list(synthetic_bts_rows[0].keys())
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers + [""])
        for row in synthetic_bts_rows:
            writer.writerow([row.get(h, "") for h in headers] + [""])

    config = {
        "database": {
            "path": str(db_file),
            "busy_timeout_ms": 10000,
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "foreign_keys": True
        },
        "raw_data": {
            "dir": str(raw_dir),
            "file_pattern": "bts_flights_{year}.csv",
            "years": [2024],
            "chunk_size": 100,
            "max_rows_per_file": None
        },
        "tables": {
            "bronze": "bronze_bts_flights",
            "silver": "silver_flights",
            "silver_rejected": "silver_rejected_rows",
            "gold_dim_date": "gold_dim_date",
            "gold_dim_airline": "gold_dim_airline",
            "gold_dim_airport": "gold_dim_airport",
            "gold_dim_route": "gold_dim_route",
            "gold_fact_flight": "gold_fact_flight",
            "audit_log": "etl_run_log"
        },
        "reports": {
            "output_dir": str(reports_dir),
            "bronze_report": str(reports_dir / "bronze_report.json"),
            "silver_quality_report": str(reports_dir / "silver_quality_report.json"),
            "gold_validation_report": str(reports_dir / "gold_validation_report.json"),
            "pipeline_summary": str(reports_dir / "pipeline_summary.json")
        },
        "logging": {
            "log_file": str(tmp_path / "test.log"),
            "log_level": "DEBUG",
            "console_output": False
        }
    }

    # Apply all SQL schemas
    conn = get_db_connection(str(db_file))
    schema_dir = Path(__file__).resolve().parent.parent / "sql" / "schema"
    for sql_f in sorted(schema_dir.glob("*.sql")):
        execute_sql_file(conn, str(sql_f))
    conn.close()

    return {
        "config": config,
        "db_path": str(db_file),
        "raw_csv": str(csv_file),
        "reports_dir": str(reports_dir)
    }
