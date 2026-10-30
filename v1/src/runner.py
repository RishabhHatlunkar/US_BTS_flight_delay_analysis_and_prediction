"""
CLI Runner for Databricks Bronze, Silver and Gold ETL (Stage 2 and Stage 3)
"""

import os
import sys
import time
import argparse
from pyspark.sql import SparkSession

# Ensure PySpark uses current python executable on Windows
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from src.etl.bronze_ingestion import ingest_bts_to_bronze
from src.etl.silver_etl import transform_bronze_to_silver
from src.etl.gold_etl import transform_silver_to_gold
from src.etl.metadata_logger import log_etl_run
from src.etl.quality_report import generate_stage2_quality_report, generate_stage3_quality_report


def create_spark_session(app_name="Databricks_Flight_Delay_ETL"):
    """
    Creates or retrieves PySpark session.
    """
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master("local[2]")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "2")
    )
    return builder.getOrCreate()


def run_pipeline(raw_files=None, catalog="flight_delay_dwm", reports_dir="reports", stage="all"):
    start_time = time.time()
    spark = create_spark_session()
    
    if raw_files is None:
        raw_dir = os.path.join("data", "raw", "bts")
        if os.path.exists(raw_dir):
            raw_files = [
                os.path.join(raw_dir, f) for f in os.listdir(raw_dir)
                if f.startswith("bts_flights_") and f.endswith(".csv")
            ]
        else:
            raw_files = []
            
    print(f"=== FLIGHT DELAY DATA WAREHOUSE PIPELINE (Stage: {stage.upper()}) ===")
    print(f"Catalog: {catalog}")
    
    # 1. Ingest Bronze
    bronze_table = f"{catalog}.bronze.bts_flights"
    df_bronze, bronze_metrics = ingest_bts_to_bronze(spark, raw_files, target_table=bronze_table)
    log_etl_run(spark, bronze_metrics)
    
    # 2. Transform Silver
    silver_table = f"{catalog}.silver.flights"
    df_silver, silver_metrics = transform_bronze_to_silver(spark, df_bronze, target_table=silver_table)
    log_etl_run(spark, silver_metrics)
    
    stage2_report_path, stage2_report = generate_stage2_quality_report(
        bronze_metrics, silver_metrics, time.time() - start_time, output_dir=os.path.join(reports_dir, "stage2")
    )
    
    # 3. Transform Gold (Star Schema Warehouse)
    if stage.lower() in ["all", "gold", "stage3"]:
        gold_start = time.time()
        gold_dfs, gold_metrics = transform_silver_to_gold(spark, df_silver, catalog=catalog)
        log_etl_run(spark, gold_metrics)
        
        stage3_report_path, stage3_report = generate_stage3_quality_report(
            gold_metrics, time.time() - gold_start, output_dir=os.path.join(reports_dir, "stage3")
        )
        print(f"[GOLD ETL] Star Schema generated successfully. Report: {stage3_report_path}")
    
    total_runtime = time.time() - start_time
    print(f"\n=== PIPELINE COMPLETED IN {total_runtime:.2f} SECONDS ===")
    return stage2_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flight Delay Databricks ETL and Warehouse Runner")
    parser.add_argument("--catalog", default="flight_delay_dwm", help="Databricks Unity Catalog name")
    parser.add_argument("--reports-dir", default="reports", help="Base directory for quality reports")
    parser.add_argument("--stage", default="all", choices=["all", "stage2", "stage3", "gold"], help="Pipeline stage to run")
    args = parser.parse_args()
    
    run_pipeline(catalog=args.catalog, reports_dir=args.reports_dir, stage=args.stage)
