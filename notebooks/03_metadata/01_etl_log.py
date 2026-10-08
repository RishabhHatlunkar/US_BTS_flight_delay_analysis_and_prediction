# Databricks notebook source
# MAGIC %md
# MAGIC # Stage 2: 01_etl_log
# MAGIC ## ETL Run Audit Logs & Data Quality Validation Report

# COMMAND --------------

# MAGIC %sql
# MAGIC SELECT * FROM flight_delay_dwm.metadata.etl_run_log ORDER BY start_time DESC;
