-- ==============================================================================
-- V2 SQLite Silver Layer Schema
-- Cleaned, validated, and standardized flight records derived from Bronze
-- ==============================================================================

CREATE TABLE IF NOT EXISTS silver_flights (
    silver_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bronze_id INTEGER,
    source_file TEXT,
    source_year INTEGER,
    source_row_hash TEXT NOT NULL,
    
    -- Temporal attributes
    flight_date TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    
    -- Airline identifiers
    reporting_airline TEXT NOT NULL,
    dot_id_reporting_airline INTEGER,
    iata_code_reporting_airline TEXT,
    flight_number TEXT,
    tail_number TEXT,
    
    -- Origin Airport
    origin_airport_id INTEGER NOT NULL,
    origin_airport_seq_id INTEGER,
    origin_city_market_id INTEGER,
    origin_airport_code TEXT NOT NULL,
    origin_city TEXT,
    origin_state TEXT,
    origin_state_fips TEXT,
    origin_state_name TEXT,
    origin_wac INTEGER,
    
    -- Destination Airport
    destination_airport_id INTEGER NOT NULL,
    destination_airport_seq_id INTEGER,
    destination_city_market_id INTEGER,
    destination_airport_code TEXT NOT NULL,
    destination_city TEXT,
    destination_state TEXT,
    destination_state_fips TEXT,
    destination_state_name TEXT,
    destination_wac INTEGER,
    
    -- Operational Times (HH:MM format) and Delays (minutes)
    scheduled_departure_time TEXT,
    actual_departure_time TEXT,
    departure_delay_minutes REAL,
    scheduled_arrival_time TEXT,
    actual_arrival_time TEXT,
    arrival_delay_minutes REAL,
    
    -- Flight performance & Taxi
    taxi_out_minutes REAL,
    taxi_in_minutes REAL,
    scheduled_elapsed_minutes REAL,
    actual_elapsed_minutes REAL,
    air_time_minutes REAL,
    flights REAL DEFAULT 1.0,
    distance_miles REAL,
    distance_group INTEGER,
    
    -- Status flags
    cancelled INTEGER NOT NULL DEFAULT 0,
    cancellation_code TEXT,
    diverted INTEGER NOT NULL DEFAULT 0,
    
    -- Delay causes breakdown (semantic NULL when delay < 15 mins)
    carrier_delay_minutes REAL,
    weather_delay_minutes REAL,
    nas_delay_minutes REAL,
    security_delay_minutes REAL,
    late_aircraft_delay_minutes REAL,
    
    -- Derived metrics
    departure_hour INTEGER,
    arrival_hour INTEGER,
    route_code TEXT NOT NULL,
    arrival_delay_flag INTEGER  -- 1 = Delayed >=15m, 0 = On-time (<15m), NULL = Unknown/Cancelled/Diverted
);

CREATE TABLE IF NOT EXISTS silver_rejected_rows (
    rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bronze_id INTEGER,
    source_file TEXT,
    source_row_hash TEXT,
    rejection_reason TEXT NOT NULL,
    raw_data TEXT,
    rejected_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_silver_flight_date ON silver_flights(flight_date);
CREATE INDEX IF NOT EXISTS idx_silver_airline ON silver_flights(reporting_airline);
CREATE INDEX IF NOT EXISTS idx_silver_origin ON silver_flights(origin_airport_id);
CREATE INDEX IF NOT EXISTS idx_silver_dest ON silver_flights(destination_airport_id);
CREATE INDEX IF NOT EXISTS idx_silver_route ON silver_flights(route_code);
CREATE INDEX IF NOT EXISTS idx_silver_source_hash ON silver_flights(source_row_hash);
