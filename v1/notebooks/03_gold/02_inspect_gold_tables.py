# Databricks notebook source
# MAGIC %md
# MAGIC # Inspect Gold Star Schema Warehouse Tables
# MAGIC 
# MAGIC This notebook fetches and prints records from all Gold warehouse tables in `flight_delay_dwm.gold`.

# COMMAND --------------

# MAGIC %sql
# MAGIC USE CATALOG flight_delay_dwm;
# MAGIC USE SCHEMA gold;

# COMMAND --------------

# MAGIC %md
# MAGIC ### 1. Row counts across all Gold tables

# COMMAND --------------

# MAGIC %sql
# MAGIC SELECT 'dim_date' AS table_name, COUNT(*) AS row_count FROM dim_date
# MAGIC UNION ALL
# MAGIC SELECT 'dim_airline', COUNT(*) FROM dim_airline
# MAGIC UNION ALL
# MAGIC SELECT 'dim_airport', COUNT(*) FROM dim_airport
# MAGIC UNION ALL
# MAGIC SELECT 'dim_route', COUNT(*) FROM dim_route
# MAGIC UNION ALL
# MAGIC SELECT 'fact_flight', COUNT(*) FROM fact_flight;

# COMMAND --------------

# MAGIC %md
# MAGIC ### 2. Sample records from fact_flight

# COMMAND --------------

display(spark.table("flight_delay_dwm.gold.fact_flight").limit(10))

# COMMAND --------------

# MAGIC %md
# MAGIC ### 3. Sample records from dim_airline

# COMMAND --------------

display(spark.table("flight_delay_dwm.gold.dim_airline").limit(10))

# COMMAND --------------

# MAGIC %md
# MAGIC ### 4. Sample records from dim_airport

# COMMAND --------------

display(spark.table("flight_delay_dwm.gold.dim_airport").limit(10))

# COMMAND --------------

# MAGIC %md
# MAGIC ### 5. Sample records from dim_route

# COMMAND --------------

display(spark.table("flight_delay_dwm.gold.dim_route").limit(10))

# COMMAND --------------

# MAGIC %md
# MAGIC ### 6. Sample records from dim_date

# COMMAND --------------

display(spark.table("flight_delay_dwm.gold.dim_date").limit(10))
