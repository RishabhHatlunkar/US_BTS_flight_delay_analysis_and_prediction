"""
Data Loader module for Databricks Gold Warehouse.
Directly queries Databricks SQL Warehouse via Statements Execution API (2.0)
using credentials from v1/.env.
Caches pre-aggregated OLAP cubes and sample records in v1/data/ for high-performance dashboard rendering.
"""

import os
import sys
import time
import json
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

V1_DIR = Path(__file__).resolve().parent.parent
load_dotenv(V1_DIR / ".env")
load_dotenv(V1_DIR.parent / ".env")

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "").strip().rstrip("/")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "").strip()
DATABRICKS_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "").strip()
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG", "flight_delay_dwm").strip()
DATABRICKS_SCHEMA = os.getenv("DATABRICKS_SCHEMA", "gold").strip()

DATA_DIR = V1_DIR / "data"
SAMPLE_PARQUET = DATA_DIR / "databricks_gold_sample.parquet"
CUBES_JSON = DATA_DIR / "databricks_olap_cubes.json"


def is_databricks_configured() -> bool:
    if not DATABRICKS_HOST or not DATABRICKS_TOKEN or not DATABRICKS_WAREHOUSE_ID:
        return False
    if "your-databricks-instance" in DATABRICKS_HOST or "your_personal_access_token" in DATABRICKS_TOKEN:
        return False
    return True


def fetch_from_databricks(sql_query: str) -> pd.DataFrame:
    """Executes a SQL query against Databricks SQL Warehouse via Statements API."""
    if not is_databricks_configured():
        raise ValueError("Databricks is not properly configured in .env.")

    host = DATABRICKS_HOST if DATABRICKS_HOST.startswith("http") else f"https://{DATABRICKS_HOST}"
    url = f"{host}/api/2.0/sql/statements"
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "statement": sql_query,
        "warehouse_id": DATABRICKS_WAREHOUSE_ID,
        "catalog": DATABRICKS_CATALOG,
        "schema": DATABRICKS_SCHEMA,
        "wait_timeout": "50s",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    if resp.status_code != 200:
        raise RuntimeError(f"Databricks SQL API returned HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    status = data.get("status", {}).get("state", "UNKNOWN")
    statement_id = data.get("statement_id")

    while status in ["PENDING", "RUNNING"] and statement_id:
        time.sleep(2)
        poll_resp = requests.get(f"{url}/{statement_id}", headers=headers, timeout=30)
        data = poll_resp.json()
        status = data.get("status", {}).get("state", "UNKNOWN")

    if status != "SUCCEEDED":
        err_msg = data.get("status", {}).get("error", {}).get("message", "Unknown error")
        raise RuntimeError(f"Databricks query failed with state {status}: {err_msg}")

    manifest = data.get("manifest", {})
    columns = [c.get("name") for c in manifest.get("schema", {}).get("columns", [])]
    rows = data.get("result", {}).get("data_array", [])

    df = pd.DataFrame(rows, columns=columns)
    # Automatic numeric conversion where applicable
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
    return df


def build_and_cache_olap_cubes() -> dict:
    """
    Executes all primary OLAP aggregations across the 30.7M records on Databricks
    and caches them in v1/data/ for sub-second dashboard performance.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cubes = {}

    print("[DATABRICKS ETL] Querying Executive KPIs & Outcomes across 30.7M flights...")
    # 1. Executive KPIs (Q1, Q3)
    q1_q3_query = f"""
        SELECT 
            count(*) as total_flights,
            sum(case when cancelled = 0 and arr_delay is not null then 1 else 0 end) as eligible_arrivals,
            sum(case when cancelled = 0 and arr_del15 = 1 then 1 else 0 end) as delayed_arrivals,
            sum(case when cancelled = 0 and arr_del15 = 0 then 1 else 0 end) as ontime_early_arrivals,
            sum(case when cancelled = 1 then 1 else 0 end) as cancelled_flights,
            sum(case when diverted = 1 then 1 else 0 end) as diverted_flights,
            round(sum(case when cancelled = 0 and arr_del15 = 1 then 1 else 0 end) * 100.0 / 
                  nullif(sum(case when cancelled = 0 and arr_delay is not null then 1 else 0 end), 0), 2) as arr_delay_rate,
            round(avg(case when cancelled = 0 then arr_delay else null end), 2) as avg_arrival_delay_signed,
            round(avg(case when cancelled = 0 and arr_delay > 0 then arr_delay else null end), 2) as avg_arrival_delay_positive,
            round(sum(case when cancelled = 1 then 1 else 0 end) * 100.0 / count(*), 2) as cancel_rate,
            round(sum(case when diverted = 1 then 1 else 0 end) * 100.0 / count(*), 2) as divert_rate,
            sum(case when cancelled = 0 and arr_delay > 0 then arr_delay else 0 end) as total_delay_burden_minutes
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight
    """
    df_kpi = fetch_from_databricks(q1_q3_query)
    cubes["kpis"] = df_kpi.to_dict(orient="records")[0]

    # 2. Monthly and Yearly Trends (Q2)
    print("[DATABRICKS ETL] Querying Monthly & Yearly Trends...")
    q2_query = f"""
        SELECT 
            d.year,
            d.month,
            d.month_name,
            count(*) as total_flights,
            sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end) as eligible_arrivals,
            sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) as delayed_arrivals,
            round(sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) * 100.0 / 
                  nullif(sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end), 0), 2) as delay_rate,
            round(avg(case when f.cancelled = 0 then f.arr_delay else null end), 2) as avg_arrival_delay,
            round(sum(case when f.cancelled = 1 then 1 else 0 end) * 100.0 / count(*), 2) as cancel_rate,
            round(sum(case when f.diverted = 1 then 1 else 0 end) * 100.0 / count(*), 2) as divert_rate
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_date d ON f.date_key = d.date_key
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
    """
    cubes["monthly_trend"] = fetch_from_databricks(q2_query).to_dict(orient="records")

    # 3. Top Airlines Delay Burden & Performance (Q4, Q5, Q6, Q7, Q8)
    print("[DATABRICKS ETL] Querying Airline Performance...")
    q_airline = f"""
        SELECT 
            a.reporting_airline_code as reporting_airline,
            count(*) as total_flights,
            sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end) as eligible_arrivals,
            sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) as delayed_arrivals,
            round(sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) * 100.0 / 
                  nullif(sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end), 0), 2) as delay_rate,
            round(avg(case when f.cancelled = 0 then f.arr_delay else null end), 2) as avg_arr_delay_signed,
            round(avg(case when f.cancelled = 0 and f.arr_delay > 0 then f.arr_delay else null end), 2) as avg_arr_delay_pos,
            sum(case when f.cancelled = 0 and f.arr_delay > 0 then f.arr_delay else 0 end) as total_delay_minutes_positive,
            sum(case when f.cancelled = 0 then f.arr_delay else 0 end) as total_delay_minutes_signed,
            round(sum(case when f.cancelled = 1 then 1 else 0 end) * 100.0 / count(*), 2) as cancel_rate,
            round(sum(case when f.diverted = 1 then 1 else 0 end) * 100.0 / count(*), 2) as divert_rate
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_airline a ON f.airline_key = a.airline_key
        GROUP BY a.reporting_airline_code
        ORDER BY total_delay_minutes_positive DESC
    """
    cubes["airline_performance"] = fetch_from_databricks(q_airline).to_dict(orient="records")

    # 4. Airport Departure & Arrival Delays (Q10, Q11)
    print("[DATABRICKS ETL] Querying Airport Delays...")
    q_airports_orig = f"""
        SELECT 
            orig.airport_code as origin_airport_code,
            orig.city_name as origin_city_name,
            orig.state as origin_state,
            count(*) as eligible_departures,
            sum(case when f.dep_del15 = 1 then 1 else 0 end) as delayed_departures,
            round(sum(case when f.dep_del15 = 1 then 1 else 0 end) * 100.0 / count(*), 2) as dep_delay_rate,
            round(avg(f.dep_delay), 2) as avg_dep_delay
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_airport orig ON f.origin_airport_key = orig.airport_key
        WHERE f.dep_delay is not null
        GROUP BY orig.airport_code, orig.city_name, orig.state
        HAVING count(*) >= 1000
        ORDER BY dep_delay_rate DESC
        LIMIT 25
    """
    cubes["origin_airports"] = fetch_from_databricks(q_airports_orig).to_dict(orient="records")

    q_airports_dest = f"""
        SELECT 
            dest.airport_code as dest_airport_code,
            dest.city_name as dest_city_name,
            dest.state as dest_state,
            count(*) as eligible_arrivals,
            sum(case when f.arr_del15 = 1 then 1 else 0 end) as delayed_arrivals,
            round(sum(case when f.arr_del15 = 1 then 1 else 0 end) * 100.0 / count(*), 2) as arr_delay_rate,
            round(avg(f.arr_delay), 2) as avg_arr_delay
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_airport dest ON f.destination_airport_key = dest.airport_key
        WHERE f.cancelled = 0 and f.arr_delay is not null
        GROUP BY dest.airport_code, dest.city_name, dest.state
        HAVING count(*) >= 1000
        ORDER BY arr_delay_rate DESC
        LIMIT 25
    """
    cubes["dest_airports"] = fetch_from_databricks(q_airports_dest).to_dict(orient="records")

    # 5. Route Analysis (Q12, Q13)
    print("[DATABRICKS ETL] Querying Top Routes...")
    q_routes = f"""
        SELECT 
            r.route_code,
            r.origin_airport_code,
            r.destination_airport_code,
            count(*) as total_flights,
            sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end) as eligible_arrivals,
            round(sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) * 100.0 / 
                  nullif(sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end), 0), 2) as arr_delay_rate,
            round(avg(case when f.cancelled = 0 then f.arr_delay else null end), 2) as avg_arr_delay,
            sum(case when f.cancelled = 0 and f.arr_delay > 0 then f.arr_delay else 0 end) as total_delay_burden_minutes
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_route r ON f.route_key = r.route_key
        GROUP BY r.route_code, r.origin_airport_code, r.destination_airport_code
        HAVING count(*) >= 2000
        ORDER BY total_delay_burden_minutes DESC
        LIMIT 30
    """
    cubes["routes"] = fetch_from_databricks(q_routes).to_dict(orient="records")

    # 6. Operational & Time Patterns (Q15, Q16, Q17)
    print("[DATABRICKS ETL] Querying Time & Operational Patterns...")
    q_dow = f"""
        SELECT 
            d.day_of_week,
            d.day_name,
            count(*) as total_flights,
            sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end) as eligible_arrivals,
            round(sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) * 100.0 / 
                  nullif(sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end), 0), 2) as delay_rate,
            round(avg(case when f.cancelled = 0 then f.arr_delay else null end), 2) as avg_arrival_delay,
            sum(case when f.cancelled = 0 and f.arr_delay > 0 then f.arr_delay else 0 end) as total_delay_minutes
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_date d ON f.date_key = d.date_key
        GROUP BY d.day_of_week, d.day_name
        ORDER BY d.day_of_week
    """
    cubes["weekday_patterns"] = fetch_from_databricks(q_dow).to_dict(orient="records")

    q_hourly = f"""
        SELECT 
            f.departure_hour,
            count(*) as total_flights,
            round(sum(case when f.dep_del15 = 1 then 1 else 0 end) * 100.0 / nullif(count(f.dep_delay), 0), 2) as dep_delay_rate,
            round(sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) * 100.0 / 
                  nullif(sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end), 0), 2) as arr_delay_rate,
            round(avg(case when f.cancelled = 0 then f.arr_delay else null end), 2) as avg_arrival_delay
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        WHERE f.departure_hour is not null
        GROUP BY f.departure_hour
        ORDER BY f.departure_hour
    """
    cubes["hourly_patterns"] = fetch_from_databricks(q_hourly).to_dict(orient="records")

    # 7. Delay Causes (Q20, Q21, Q22, Q23)
    print("[DATABRICKS ETL] Querying Delay Causes...")
    q_causes = f"""
        SELECT 
            sum(carrier_delay) as carrier_delay,
            sum(late_aircraft_delay) as late_aircraft_delay,
            sum(nas_delay) as nas_delay,
            sum(weather_delay) as weather_delay,
            sum(security_delay) as security_delay
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight
        WHERE arr_del15 = 1
    """
    causes_row = fetch_from_databricks(q_causes).to_dict(orient="records")[0]
    tot_cause = sum(causes_row.values()) or 1.0
    cubes["delay_causes"] = [
        {"Cause": "Carrier Delay", "Minutes": int(causes_row["carrier_delay"]), "Share (%)": round(causes_row["carrier_delay"] / tot_cause * 100, 2)},
        {"Cause": "Late Aircraft Delay", "Minutes": int(causes_row["late_aircraft_delay"]), "Share (%)": round(causes_row["late_aircraft_delay"] / tot_cause * 100, 2)},
        {"Cause": "National Airspace System (NAS)", "Minutes": int(causes_row["nas_delay"]), "Share (%)": round(causes_row["nas_delay"] / tot_cause * 100, 2)},
        {"Cause": "Weather Delay", "Minutes": int(causes_row["weather_delay"]), "Share (%)": round(causes_row["weather_delay"] / tot_cause * 100, 2)},
        {"Cause": "Security Delay", "Minutes": int(causes_row["security_delay"]), "Share (%)": round(causes_row["security_delay"] / tot_cause * 100, 2)},
    ]
    cubes["late_aircraft_share"] = round(causes_row["late_aircraft_delay"] / tot_cause * 100, 2)

    # 8. OLAP Roll-up Hierarchy (Year -> Quarter -> Month) (Q28)
    print("[DATABRICKS ETL] Querying OLAP Rollup Hierarchy...")
    q_rollup = f"""
        SELECT 
            d.year,
            d.quarter,
            d.month,
            d.month_name,
            count(*) as total_flights,
            sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end) as eligible_arrivals,
            round(sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) * 100.0 / 
                  nullif(sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end), 0), 2) as delay_rate,
            round(avg(case when f.cancelled = 0 then f.arr_delay else null end), 2) as avg_arrival_delay,
            sum(case when f.cancelled = 0 and f.arr_delay > 0 then f.arr_delay else 0 end) as total_delay_minutes
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_date d ON f.date_key = d.date_key
        GROUP BY d.year, d.quarter, d.month, d.month_name
        ORDER BY d.year, d.quarter, d.month
    """
    cubes["rollup_hierarchy"] = fetch_from_databricks(q_rollup).to_dict(orient="records")

    # 9. OLAP Pivot Table (Airline x Month Delay Rate %) (Q30)
    print("[DATABRICKS ETL] Querying OLAP Pivot Table...")
    q_pivot = f"""
        SELECT 
            a.reporting_airline_code as reporting_airline,
            d.month_name,
            d.month,
            round(sum(case when f.cancelled = 0 and f.arr_del15 = 1 then 1 else 0 end) * 100.0 / 
                  nullif(sum(case when f.cancelled = 0 and f.arr_delay is not null then 1 else 0 end), 0), 2) as delay_rate
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_airline a ON f.airline_key = a.airline_key
        JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_date d ON f.date_key = d.date_key
        GROUP BY a.reporting_airline_code, d.month_name, d.month
        ORDER BY a.reporting_airline_code, d.month
    """
    cubes["pivot_data"] = fetch_from_databricks(q_pivot).to_dict(orient="records")

    # 10. Sample Granular Records for Scatter, Filters & Drill-Through (Q18, Q31)
    print("[DATABRICKS ETL] Fetching 50,000 granular sample records for drill-through and live filtering...")
    q_sample = f"""
        SELECT 
            f.flight_key, f.flight_number, f.tail_number,
            d.full_date as flight_date, d.year, d.quarter, d.month, d.month_name,
            d.day as day_of_month, d.day_of_week, d.day_name, d.is_weekend,
            a.reporting_airline_code as reporting_airline,
            orig.airport_code as origin_airport_code, orig.city_name as origin_city_name,
            dest.airport_code as dest_airport_code, dest.city_name as dest_city_name,
            r.route_code,
            f.crs_dep_time, f.dep_time, f.departure_hour,
            f.crs_arr_time, f.arr_time, f.arrival_hour,
            f.dep_delay, f.dep_delay_minutes, f.dep_del15,
            f.arr_delay, f.arr_delay_minutes, f.arr_del15,
            f.cancelled, f.cancellation_code, f.diverted,
            f.carrier_delay, f.weather_delay, f.nas_delay, f.security_delay, f.late_aircraft_delay,
            f.distance
        FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.fact_flight f
        LEFT JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_date d ON f.date_key = d.date_key
        LEFT JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_airline a ON f.airline_key = a.airline_key
        LEFT JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_airport orig ON f.origin_airport_key = orig.airport_key
        LEFT JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_airport dest ON f.destination_airport_key = dest.airport_key
        LEFT JOIN {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.dim_route r ON f.route_key = r.route_key
        LIMIT 50000
    """
    df_sample = fetch_from_databricks(q_sample)
    df_sample.to_parquet(SAMPLE_PARQUET, index=False)
    print(f"[DATABRICKS ETL] Saved sample to {SAMPLE_PARQUET}")

    # Write cubes JSON
    with open(CUBES_JSON, "w") as f:
        json.dump(cubes, f, indent=2)
    print(f"[DATABRICKS ETL] Saved OLAP cubes to {CUBES_JSON}")

    return cubes


def get_cached_cubes_and_sample(force_refresh: bool = False):
    """Retrieves cached OLAP cubes and sample DataFrame or generates them from Databricks."""
    if force_refresh or not CUBES_JSON.exists() or not SAMPLE_PARQUET.exists():
        if is_databricks_configured():
            try:
                cubes = build_and_cache_olap_cubes()
                df_sample = pd.read_parquet(SAMPLE_PARQUET)
                return cubes, df_sample, "Databricks Unity Catalog (30.7M flights, live connection)"
            except Exception as e:
                print(f"[ERROR] Failed to fetch from Databricks: {e}")

    if CUBES_JSON.exists() and SAMPLE_PARQUET.exists():
        with open(CUBES_JSON) as f:
            cubes = json.load(f)
        df_sample = pd.read_parquet(SAMPLE_PARQUET)
        return cubes, df_sample, "Databricks Gold Warehouse Cache (30.7M flights aggregated)"

    raise RuntimeError("No cached OLAP cubes available and Databricks is unreachable.")
