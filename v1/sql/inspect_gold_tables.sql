-- ==============================================================================
-- Stage 3 / 4: Inspect Gold Star Schema Warehouse Tables
-- Catalog: flight_delay_dwm
-- Schema: gold
-- ==============================================================================

USE CATALOG flight_delay_dwm;
USE SCHEMA gold;

-- 1. Check Row Counts Across All Gold Tables
SELECT 'dim_date' AS table_name, COUNT(*) AS total_rows FROM dim_date
UNION ALL
SELECT 'dim_airline' AS table_name, COUNT(*) AS total_rows FROM dim_airline
UNION ALL
SELECT 'dim_airport' AS table_name, COUNT(*) AS total_rows FROM dim_airport
UNION ALL
SELECT 'dim_route' AS table_name, COUNT(*) AS total_rows FROM dim_route
UNION ALL
SELECT 'fact_flight' AS table_name, COUNT(*) AS total_rows FROM fact_flight;

-- 2. Sample records from fact_flight
SELECT 
    f.flight_key,
    f.flight_date,
    f.reporting_airline,
    f.origin_airport_code,
    f.dest_airport_code,
    f.dep_delay,
    f.arr_delay,
    f.dep_del15,
    f.arr_del15,
    f.cancelled,
    f.diverted
FROM fact_flight f
LIMIT 10;

-- 3. Sample records from dim_airline
SELECT * FROM dim_airline LIMIT 10;

-- 4. Sample records from dim_airport
SELECT * FROM dim_airport LIMIT 10;

-- 5. Sample records from dim_route
SELECT * FROM dim_route LIMIT 10;

-- 6. Sample records from dim_date
SELECT * FROM dim_date LIMIT 10;
