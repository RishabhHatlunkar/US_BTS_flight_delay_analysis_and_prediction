-- ==============================================================================
-- Stage 3: Databricks Unity Catalog Gold Schema & Star Schema DDL
-- Catalog: flight_delay_dwm
-- Schema: gold
-- Dimension Tables: dim_date, dim_airline, dim_airport, dim_route
-- Fact Table: fact_flight
-- ==============================================================================

USE CATALOG flight_delay_dwm;

CREATE SCHEMA IF NOT EXISTS flight_delay_dwm.gold
  COMMENT 'Gold layer storing Star Schema dimensional warehouse tables for analytical OLAP and ML';

-- 1. Date Dimension
CREATE TABLE IF NOT EXISTS flight_delay_dwm.gold.dim_date (
  date_key INT NOT NULL COMMENT 'Surrogate Date Key in YYYYMMDD format (e.g. 20240115)',
  full_date DATE NOT NULL COMMENT 'Full Calendar Date',
  year INT NOT NULL COMMENT 'Calendar Year',
  quarter INT NOT NULL COMMENT 'Calendar Quarter (1-4)',
  month INT NOT NULL COMMENT 'Calendar Month (1-12)',
  month_name STRING NOT NULL COMMENT 'Full Month Name (e.g. January)',
  day INT NOT NULL COMMENT 'Day of Month (1-31)',
  day_of_week INT NOT NULL COMMENT 'Day of Week (1=Sunday, 7=Saturday)',
  day_name STRING NOT NULL COMMENT 'Full Day Name (e.g. Monday)',
  week_of_year INT NOT NULL COMMENT 'ISO Week of Year (1-53)',
  is_weekend INT NOT NULL COMMENT 'Flag: 1 if Weekend (Saturday/Sunday), 0 otherwise'
)
USING DELTA
COMMENT 'Date dimension table containing comprehensive calendar attributes';

-- 2. Airline Dimension
CREATE TABLE IF NOT EXISTS flight_delay_dwm.gold.dim_airline (
  airline_key INT NOT NULL COMMENT 'Surrogate Airline Key',
  reporting_airline_code STRING NOT NULL COMMENT 'Natural Business Key: Carrier IATA Code (e.g. AA, DL, UA)',
  dot_airline_id INT COMMENT 'U.S. DOT Unique Airline Identification Number',
  iata_airline_code STRING COMMENT 'IATA Carrier Code'
)
USING DELTA
COMMENT 'Airline / Reporting Carrier dimension table';

-- 3. Airport Dimension (Role-Playing Dimension)
CREATE TABLE IF NOT EXISTS flight_delay_dwm.gold.dim_airport (
  airport_key INT NOT NULL COMMENT 'Surrogate Airport Key',
  airport_id INT NOT NULL COMMENT 'Natural Business Key: U.S. DOT Airport ID',
  airport_seq_id INT COMMENT 'U.S. DOT Airport Sequence ID',
  airport_code STRING NOT NULL COMMENT '3-Letter IATA Airport Code (e.g. LAX, JFK, ORD)',
  city_market_id INT COMMENT 'U.S. DOT City Market ID',
  city_name STRING COMMENT 'Full City Name and State (e.g. Los Angeles, CA)',
  state STRING COMMENT '2-Letter State Abbreviation',
  state_fips INT COMMENT 'State FIPS Code',
  state_name STRING COMMENT 'Full State Name',
  wac INT COMMENT 'World Area Code'
)
USING DELTA
COMMENT 'Role-Playing Airport dimension referenced by fact_flight as Origin and Destination';

-- 4. Route Dimension
CREATE TABLE IF NOT EXISTS flight_delay_dwm.gold.dim_route (
  route_key INT NOT NULL COMMENT 'Surrogate Route Key',
  route_code STRING NOT NULL COMMENT 'Directional Route Code (e.g. JFK-LAX)',
  origin_airport_code STRING NOT NULL COMMENT 'Origin Airport Code',
  destination_airport_code STRING NOT NULL COMMENT 'Destination Airport Code',
  origin_airport_id INT COMMENT 'Origin Airport ID',
  destination_airport_id INT COMMENT 'Destination Airport ID'
)
USING DELTA
COMMENT 'Directional Route dimension table representing unique airport pairs';

-- 5. Flight Fact Table
CREATE TABLE IF NOT EXISTS flight_delay_dwm.gold.fact_flight (
  flight_key STRING NOT NULL COMMENT 'Surrogate Fact Primary Key derived from source_row_hash',
  
  -- Foreign Keys
  date_key INT NOT NULL COMMENT 'Foreign Key -> dim_date.date_key (YYYYMMDD)',
  airline_key INT NOT NULL COMMENT 'Foreign Key -> dim_airline.airline_key',
  origin_airport_key INT NOT NULL COMMENT 'Foreign Key -> dim_airport.airport_key (Origin Role)',
  destination_airport_key INT NOT NULL COMMENT 'Foreign Key -> dim_airport.airport_key (Destination Role)',
  route_key INT NOT NULL COMMENT 'Foreign Key -> dim_route.route_key',

  -- Degenerate / Natural Identifiers
  flight_number INT COMMENT 'Flight Number',
  tail_number STRING COMMENT 'Aircraft Tail Number',

  -- Time Attributes
  crs_dep_time INT COMMENT 'Scheduled Departure Time (HHMM)',
  dep_time INT COMMENT 'Actual Departure Time (HHMM)',
  crs_arr_time INT COMMENT 'Scheduled Arrival Time (HHMM)',
  arr_time INT COMMENT 'Actual Arrival Time (HHMM)',
  departure_hour INT COMMENT 'Derived Scheduled Departure Hour (0-23)',
  arrival_hour INT COMMENT 'Derived Scheduled Arrival Hour (0-23)',
  wheels_off INT COMMENT 'Wheels Off Time (HHMM)',
  wheels_on INT COMMENT 'Wheels On Time (HHMM)',

  -- Performance & Delay Measures
  dep_delay DOUBLE COMMENT 'Departure Delay in Minutes (can be negative)',
  dep_delay_minutes DOUBLE COMMENT 'Departure Delay in Minutes (non-negative)',
  dep_del15 DOUBLE COMMENT 'Departure Delay Indicator (1 if DepDelay >= 15)',
  arr_delay DOUBLE COMMENT 'Arrival Delay in Minutes (can be negative)',
  arr_delay_minutes DOUBLE COMMENT 'Arrival Delay in Minutes (non-negative)',
  arr_del15 DOUBLE COMMENT 'Arrival Delay Indicator (1 if ArrDelay >= 15)',
  delay_flag INT COMMENT 'Analytical Delay Flag (1 if Arrival Delay >= 15 mins)',
  departure_delay_groups DOUBLE COMMENT 'Departure Delay Group (-2 to 12)',
  arrival_delay_groups DOUBLE COMMENT 'Arrival Delay Group (-2 to 12)',
  taxi_out DOUBLE COMMENT 'Taxi Out Time in Minutes',
  taxi_in DOUBLE COMMENT 'Taxi In Time in Minutes',
  crs_elapsed_time DOUBLE COMMENT 'Scheduled Elapsed Flight Time in Minutes',
  actual_elapsed_time DOUBLE COMMENT 'Actual Elapsed Flight Time in Minutes',
  air_time DOUBLE COMMENT 'Air Time in Minutes',
  flights INT COMMENT 'Flight Count (always 1)',
  distance DOUBLE COMMENT 'Flight Distance in Miles',
  distance_group INT COMMENT 'Distance Grouping (1 to 11)',

  -- Cancellation & Diversion Measures
  cancelled INT COMMENT 'Cancellation Flag (1 if Cancelled, 0 otherwise)',
  cancellation_code STRING COMMENT 'Cancellation Cause Code (A=Carrier, B=Weather, C=NAS, D=Security)',
  diverted INT COMMENT 'Diversion Flag (1 if Diverted, 0 otherwise)',

  -- Delay Cause Breakdown Measures (Preserves Semantic NULLs)
  carrier_delay DOUBLE COMMENT 'Delay in Minutes due to Carrier Causes',
  weather_delay DOUBLE COMMENT 'Delay in Minutes due to Weather Causes',
  nas_delay DOUBLE COMMENT 'Delay in Minutes due to National Airspace System Causes',
  security_delay DOUBLE COMMENT 'Delay in Minutes due to Security Causes',
  late_aircraft_delay DOUBLE COMMENT 'Delay in Minutes due to Late Aircraft Arrival',

  -- Lineage Metadata
  source_year INT COMMENT 'Source Calendar Year',
  source_file STRING COMMENT 'Source File Name',
  source_row_hash STRING NOT NULL COMMENT 'Deterministic 64-character SHA-256 Source Hash'
)
USING DELTA
COMMENT 'Flight Performance Fact table at the grain of ONE ROW = ONE FLIGHT OCCURRENCE';
