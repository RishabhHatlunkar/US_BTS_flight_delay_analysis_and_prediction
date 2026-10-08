# Databricks notebook source
# MAGIC %md
# MAGIC # Stage 2: 01_bronze_to_silver
# MAGIC ## Bronze Delta Table -> Silver Cleaned & Typed Analytical Layer
# MAGIC
# MAGIC **Source Table:** `flight_delay_dwm.bronze.bts_flights`  
# MAGIC **Target Table:** `flight_delay_dwm.silver.flights`

# COMMAND --------------

# MAGIC %sql
# MAGIC USE CATALOG flight_delay_dwm;
# MAGIC CREATE SCHEMA IF NOT EXISTS flight_delay_dwm.silver;

# COMMAND --------------

from src.etl.silver_etl import transform_bronze_to_silver
from src.etl.metadata_logger import log_etl_run

# 1. Run Silver Transformation & Deduplication
df_silver, silver_metrics = transform_bronze_to_silver(
    spark=spark,
    source_df_or_table="flight_delay_dwm.bronze.bts_flights",
    target_table="flight_delay_dwm.silver.flights"
)

# 2. Log Metadata
log_etl_run(spark, silver_metrics)

# 3. Display Silver Summary
display(spark.table("flight_delay_dwm.silver.flights").limit(10))
