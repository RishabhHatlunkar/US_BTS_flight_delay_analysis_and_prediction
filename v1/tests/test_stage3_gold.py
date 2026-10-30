"""
Unit Tests for Stage 3 Databricks Gold Star Schema Warehouse ETL
"""

import sys
import os

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.etl.bronze_ingestion import generate_source_row_hash
from src.etl.silver_etl import transform_bronze_to_silver
from src.etl.gold_etl import (
    build_dim_date, build_dim_airline, build_dim_airport, build_dim_route,
    build_fact_flight, transform_silver_to_gold
)
from src.etl.quality_report import generate_stage3_quality_report
from tests.fixtures.sample_bts_data import create_sample_bts_dataframe


@pytest.fixture(scope="module")
def spark():
    builder = (
        SparkSession.builder
        .appName("Stage3_UnitTests")
        .master("local[2]")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
    )
    session = builder.getOrCreate()
    yield session
    session.stop()


def test_dim_date_generation(spark):
    """Test date dimension generator."""
    df_dim_date = build_dim_date(spark, min_date_str="2024-01-01", max_date_str="2024-01-10")
    
    assert df_dim_date.count() == 10
    first_row = df_dim_date.filter(F.col("full_date") == "2024-01-01").first()
    assert first_row["date_key"] == 20240101
    assert first_row["year"] == 2024
    assert first_row["month"] == 1
    assert first_row["month_name"] == "January"


def test_gold_star_schema_transform(spark):
    """Test full Silver to Gold transformation."""
    df_sample = create_sample_bts_dataframe(spark)
    df_bronze = (
        df_sample
        .withColumn("ingestion_timestamp", F.current_timestamp())
        .withColumn("source_file", F.lit("test_bts_2024.csv"))
        .withColumn("source_year", F.col("Year").cast("int"))
    )
    df_bronze = generate_source_row_hash(df_bronze)
    
    df_silver, _ = transform_bronze_to_silver(
        spark, df_bronze, target_table="test_silver.flights", is_delta_available=False, is_save=False
    )
    
    gold_dfs, metrics = transform_silver_to_gold(
        spark, df_silver, catalog="flight_delay_dwm_test", is_delta_available=False, is_save=False
    )
    
    # Check Dimension counts
    assert gold_dfs["dim_airline"].count() > 0
    assert gold_dfs["dim_airport"].count() > 0
    assert gold_dfs["dim_route"].count() > 0
    
    # Check Fact grain (1 row = 1 flight occurrence)
    df_fact = gold_dfs["fact_flight"]
    assert df_fact.count() == df_silver.count()
    
    # Foreign key resolution integrity check (MUST be 0 unresolved)
    assert metrics["unresolved_foreign_keys"] == 0
    assert metrics["foreign_key_integrity_passed"] is True
    
    # Verify semantic NULL preservation in fact table
    ontime_fact = df_fact.filter(F.col("delay_flag") == 0).first()
    assert ontime_fact["carrier_delay"] is None
    
    delayed_fact = df_fact.filter(F.col("delay_flag") == 1).first()
    assert delayed_fact["carrier_delay"] == 20.0


def test_stage3_quality_report_output(tmp_path):
    """Test Stage 3 quality report output."""
    g_metrics = {
        "status": "SUCCESS", "catalog": "flight_delay_dwm", "silver_input_rows": 1000,
        "fact_flight_rows": 1000, "dim_date_rows": 731, "dim_airline_rows": 15,
        "dim_airport_rows": 350, "dim_route_rows": 1200, "unresolved_foreign_keys": 0,
        "foreign_key_integrity_passed": True
    }
    
    report_path, report_data = generate_stage3_quality_report(
        g_metrics, 8.5, output_dir=str(tmp_path)
    )
    
    assert report_data["overall_status"] == "SUCCESS"
    assert report_data["gold_warehouse"]["table_summary"]["fact_flight_rows"] == 1000
    assert report_data["gold_warehouse"]["integrity_checks"]["foreign_key_integrity_passed"] is True
