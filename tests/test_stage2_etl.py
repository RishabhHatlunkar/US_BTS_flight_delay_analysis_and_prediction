"""
Unit Tests for Stage 2 Databricks Bronze & Silver ETL
"""

import sys
import os

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.etl.schema import validate_schema, REQUIRED_BTS_FIELDS
from src.etl.bronze_ingestion import generate_source_row_hash
from src.etl.silver_etl import transform_bronze_to_silver, parse_hhmm_time, extract_hour
from src.etl.quality_report import generate_stage2_quality_report
from tests.fixtures.sample_bts_data import create_sample_bts_dataframe


@pytest.fixture(scope="module")
def spark():
    builder = (
        SparkSession.builder
        .appName("Stage2_UnitTests")
        .master("local[2]")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
    )
    session = builder.getOrCreate()
    yield session
    session.stop()


def test_schema_validation():
    """Test schema validation logic."""
    present_cols = REQUIRED_BTS_FIELDS[:10]
    res = validate_schema(present_cols, REQUIRED_BTS_FIELDS)
    assert not res["valid"]
    assert len(res["missing_fields"]) == len(REQUIRED_BTS_FIELDS) - 10

    full_res = validate_schema(REQUIRED_BTS_FIELDS, REQUIRED_BTS_FIELDS)
    assert full_res["valid"]
    assert len(full_res["missing_fields"]) == 0


def test_deterministic_source_row_hash(spark):
    """Test that source_row_hash is deterministic and reproducible."""
    df_sample = create_sample_bts_dataframe(spark)
    df_hashed1 = generate_source_row_hash(df_sample)
    df_hashed2 = generate_source_row_hash(df_sample)
    
    hashes1 = [r["source_row_hash"] for r in df_hashed1.select("source_row_hash").collect()]
    hashes2 = [r["source_row_hash"] for r in df_hashed2.select("source_row_hash").collect()]
    
    assert hashes1 == hashes2
    assert len(hashes1[0]) == 64  # SHA-256 length
    
    # Check that row 0 and row 4 (exact duplicate rows) have the exact same hash
    assert hashes1[0] == hashes1[4]


def test_silver_transformation(spark):
    """Test Silver layer ETL transformations."""
    df_sample = create_sample_bts_dataframe(spark)
    df_bronze = (
        df_sample
        .withColumn("ingestion_timestamp", F.current_timestamp())
        .withColumn("source_file", F.lit("test_bts_2024.csv"))
        .withColumn("source_year", F.col("Year").cast("int"))
    )
    df_bronze = generate_source_row_hash(df_bronze)
    
    # Input has 5 rows (1 exact duplicate)
    assert df_bronze.count() == 5
    
    df_silver, metrics = transform_bronze_to_silver(
        spark, df_bronze, target_table="flight_delay_dwm_test.silver.flights", is_delta_available=False, is_save=False
    )
    
    # 1. Deduplication check: 5 input rows -> 4 Silver rows
    assert df_silver.count() == 4
    assert metrics["duplicate_rows_removed"] == 1
    
    # 2. Date conversion check
    row_list = df_silver.collect()
    for r in row_list:
        assert r["flight_date"] is not None
        assert r["year"] in [2024, 2025]
        assert r["route_code"] in ["LGA-OMA", "LAX-SFO", "ATL-ORD", "IAH-DEN"]
        
    # 3. Cancelled & Diverted preservation check
    cancelled_count = df_silver.filter(F.col("Cancelled") == 1).count()
    diverted_count = df_silver.filter(F.col("Diverted") == 1).count()
    assert cancelled_count == 1
    assert diverted_count == 1

    # 4. Semantic NULL preservation check (CarrierDelay MUST be NULL for on-time/cancelled flights)
    ontime_row = df_silver.filter(F.col("route_code") == "LGA-OMA").first()
    assert ontime_row["CarrierDelay"] is None
    
    delayed_row = df_silver.filter(F.col("route_code") == "LAX-SFO").first()
    assert delayed_row["CarrierDelay"] == 20.0
    assert delayed_row["delay_flag"] == 1
    assert delayed_row["departure_hour"] == 14


def test_hhmm_time_parsing(spark):
    """Test HHMM time parsing helper."""
    test_data = [("0856",), ("1425",), ("0005",), ("2400",), ("invalid",)]
    df_time = spark.createDataFrame(test_data, ["raw_time"])
    
    df_parsed = (
        df_time
        .withColumn("parsed", parse_hhmm_time("raw_time"))
        .withColumn("hour", extract_hour("raw_time"))
    )
    
    rows = df_parsed.collect()
    assert rows[0]["parsed"] == "08:56" and rows[0]["hour"] == 8
    assert rows[1]["parsed"] == "14:25" and rows[1]["hour"] == 14
    assert rows[2]["parsed"] == "00:05" and rows[2]["hour"] == 0
    assert rows[3]["parsed"] == "00:00" and rows[3]["hour"] == 0
    assert rows[4]["parsed"] is None and rows[4]["hour"] is None


def test_idempotency(spark):
    """Test idempotency: re-running Silver transformation yields identical row count."""
    df_sample = create_sample_bts_dataframe(spark)
    df_bronze = generate_source_row_hash(df_sample)
    
    df_silver1, m1 = transform_bronze_to_silver(spark, df_bronze, is_delta_available=False, is_save=False)
    df_silver2, m2 = transform_bronze_to_silver(spark, df_bronze, is_delta_available=False, is_save=False)
    
    assert df_silver1.count() == df_silver2.count()
    assert m1["silver_rows"] == m2["silver_rows"]


def test_quality_report_generation(tmp_path):
    """Test Stage 2 data quality report output."""
    b_metrics = {
        "status": "SUCCESS", "target_table": "bronze.bts_flights", "source_files": ["bts_2024.csv"],
        "source_rows": 100, "bronze_rows": 100, "bronze_columns": 113, "distinct_years": [2024],
        "min_flight_date": "2024-01-01", "max_flight_date": "2024-01-31", "duplicate_source_row_hashes": 0,
        "null_counts": {}
    }
    s_metrics = {
        "status": "SUCCESS", "target_table": "silver.flights", "silver_rows": 100, "silver_columns": 120,
        "duplicate_rows_removed": 0, "min_flight_date": "2024-01-01", "max_flight_date": "2024-01-31",
        "cancelled_flights": 2, "diverted_flights": 1, "delayed_flights": 15,
        "avg_arrival_delay_minutes": 5.4, "avg_departure_delay_minutes": 6.2,
        "invalid_dates": 0, "invalid_times": 0
    }
    
    report_path, report_data = generate_stage2_quality_report(
        b_metrics, s_metrics, 12.5, output_dir=str(tmp_path)
    )
    
    assert report_data["overall_status"] == "SUCCESS"
    assert report_data["silver_layer"]["silver_rows"] == 100
    assert report_data["silver_layer"]["flight_counts"]["delayed_15min_plus"] == 15
