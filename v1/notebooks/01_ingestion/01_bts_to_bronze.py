# Databricks notebook source
# MAGIC %md
# MAGIC # Stage 2: 01_bts_to_bronze
# MAGIC ## BTS Raw CSV -> Unity Catalog Volume -> Bronze Delta Table
# MAGIC
# MAGIC **Catalog:** `flight_delay_dwm`  
# MAGIC **Schema:** `bronze`  
# MAGIC **Table:** `flight_delay_dwm.bronze.bts_flights`  
# MAGIC **Volume Location:** `/Volumes/flight_delay_dwm/bronze/raw_bts`

# COMMAND --------------

# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS flight_delay_dwm;
# MAGIC USE CATALOG flight_delay_dwm;
# MAGIC CREATE SCHEMA IF NOT EXISTS flight_delay_dwm.bronze;
# MAGIC CREATE VOLUME IF NOT EXISTS flight_delay_dwm.bronze.raw_bts;

# COMMAND --------------

import os
from pyspark.sql import functions as F
from src.etl.bronze_ingestion import ingest_bts_to_bronze
from src.etl.metadata_logger import log_etl_run

# 1. Locate BTS CSV Files in Unity Catalog Volume (or local fallback)
volume_dir = "/Volumes/flight_delay_dwm/bronze/raw_bts"
if not os.path.exists(volume_dir):
    volume_dir = "data/raw/bts"

csv_files = [
    os.path.join(volume_dir, f) for f in os.listdir(volume_dir)
    if f.startswith("bts_flights_") and f.endswith(".csv")
]

print(f"Target BTS CSV Files: {csv_files}")

# 2. Ingest to Bronze Delta Table
df_bronze, bronze_metrics = ingest_bts_to_bronze(
    spark=spark,
    input_files=csv_files,
    target_table="flight_delay_dwm.bronze.bts_flights"
)

# 3. Log Metadata
log_etl_run(spark, bronze_metrics)

# 4. Display Bronze Summary
display(spark.table("flight_delay_dwm.bronze.bts_flights").limit(10))
