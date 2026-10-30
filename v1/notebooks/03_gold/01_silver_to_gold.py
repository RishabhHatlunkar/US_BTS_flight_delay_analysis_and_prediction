# Databricks notebook source
# MAGIC %md
# MAGIC # Stage 3: 01_silver_to_gold
# MAGIC ## Silver Delta Table -> Gold Star Schema Data Warehouse
# MAGIC
# MAGIC **Source Table:** `flight_delay_dwm.silver.flights`  
# MAGIC **Gold Tables:**  
# MAGIC - `flight_delay_dwm.gold.dim_date`  
# MAGIC - `flight_delay_dwm.gold.dim_airline`  
# MAGIC - `flight_delay_dwm.gold.dim_airport` (Role-Playing)  
# MAGIC - `flight_delay_dwm.gold.dim_route`  
# MAGIC - `flight_delay_dwm.gold.fact_flight` (Grain: 1 row = 1 flight)

# COMMAND --------------

# MAGIC %sql
# MAGIC USE CATALOG flight_delay_dwm;
# MAGIC CREATE SCHEMA IF NOT EXISTS flight_delay_dwm.gold;

# COMMAND --------------

from src.etl.gold_etl import transform_silver_to_gold
from src.etl.metadata_logger import log_etl_run

# 1. Run Gold Star Schema Transformation
gold_tables, gold_metrics = transform_silver_to_gold(
    spark=spark,
    source_silver_table="flight_delay_dwm.silver.flights",
    catalog="flight_delay_dwm"
)

# 2. Log Metadata Run Record
log_etl_run(spark, gold_metrics)

# 3. Display Fact Flight Sample
display(spark.table("flight_delay_dwm.gold.fact_flight").limit(10))
