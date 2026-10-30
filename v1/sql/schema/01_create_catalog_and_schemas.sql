-- ==============================================================================
-- Stage 2: Databricks Unity Catalog & Schemas Setup
-- Catalog: flight_delay_dwm
-- Schemas: bronze, silver, metadata
-- Volume: raw_bts
-- ==============================================================================

-- 1. Create Catalog (if permissions allow in Databricks Free Edition)
CREATE CATALOG IF NOT EXISTS flight_delay_dwm;

USE CATALOG flight_delay_dwm;

-- 2. Create Schemas
CREATE SCHEMA IF NOT EXISTS flight_delay_dwm.bronze
  COMMENT 'Raw data ingestion layer preserving source BTS structure with ingestion metadata';

CREATE SCHEMA IF NOT EXISTS flight_delay_dwm.silver
  COMMENT 'Cleaned, typed, deduplicated analytical layer with derived time/route features';

CREATE SCHEMA IF NOT EXISTS flight_delay_dwm.metadata
  COMMENT 'Metadata schema storing ETL pipeline run logs and data quality metrics';

-- 3. Create Unity Catalog Volume for Raw File Ingestion
CREATE VOLUME IF NOT EXISTS flight_delay_dwm.bronze.raw_bts
  COMMENT 'Managed Unity Catalog volume storing raw BTS CSV files (bts_flights_YYYY.csv)';

-- 4. Create Metadata Table for ETL Logging
CREATE TABLE IF NOT EXISTS flight_delay_dwm.metadata.etl_run_log (
  run_id STRING NOT NULL COMMENT 'Unique identifier for the ETL pipeline run',
  pipeline_stage STRING NOT NULL COMMENT 'Stage identifier: BRONZE_INGESTION or SILVER_ETL',
  start_time TIMESTAMP NOT NULL COMMENT 'Stage execution start timestamp',
  end_time TIMESTAMP COMMENT 'Stage execution completion timestamp',
  status STRING NOT NULL COMMENT 'Status: SUCCESS, FAILED, RUNNING',
  source_files STRING COMMENT 'JSON array or comma-separated list of processed files',
  source_rows BIGINT COMMENT 'Count of records read from source',
  bronze_rows BIGINT COMMENT 'Count of records written to Bronze Delta table',
  silver_rows BIGINT COMMENT 'Count of records written to Silver Delta table',
  duplicates BIGINT COMMENT 'Count of duplicate records detected by source_row_hash',
  rejected_rows BIGINT COMMENT 'Count of malformed/rejected rows',
  execution_seconds DOUBLE COMMENT 'Pipeline stage execution time in seconds',
  error_message STRING COMMENT 'Detailed error trace if status is FAILED'
)
USING DELTA
COMMENT 'Audit log recording execution status and metrics for all Stage 2 ETL runs';
