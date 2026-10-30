-- ==============================================================================
-- V2 SQLite Gold Layer Schema (Star Schema Dimensional Warehouse)
-- Dimensions: Date, Airline, Airport (Shared Role-Playing), Route (Directional)
-- Fact: Fact Flight (Grain: 1 row = 1 BTS Flight Occurrence)
-- ==============================================================================

-- 1. Date Dimension
CREATE TABLE IF NOT EXISTS gold_dim_date (
    date_key INTEGER PRIMARY KEY,           -- Format: YYYYMMDD
    full_date TEXT UNIQUE NOT NULL,         -- Format: YYYY-MM-DD
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,           -- 1 = Monday, 7 = Sunday
    day_name TEXT NOT NULL,                 -- Monday, Tuesday, ...
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,               -- January, February, ...
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL             -- 1 = Weekend (Sat/Sun), 0 = Weekday
);

-- 2. Airline Dimension
CREATE TABLE IF NOT EXISTS gold_dim_airline (
    airline_key INTEGER PRIMARY KEY AUTOINCREMENT,
    reporting_airline TEXT UNIQUE NOT NULL,  -- Natural Key (e.g. 'AA', 'DL', 'UA')
    dot_id_reporting_airline INTEGER,
    iata_code_reporting_airline TEXT
);

-- 3. Airport Dimension (Shared for both Origin and Destination)
CREATE TABLE IF NOT EXISTS gold_dim_airport (
    airport_key INTEGER PRIMARY KEY AUTOINCREMENT,
    airport_id INTEGER UNIQUE NOT NULL,      -- Natural Key (BTS AirportID)
    airport_sequence_id INTEGER,
    city_market_id INTEGER,
    airport_code TEXT NOT NULL,              -- IATA Airport Code (e.g. 'JFK', 'LAX')
    city_name TEXT,
    state_code TEXT,
    state_fips TEXT,
    state_name TEXT,
    world_area_code INTEGER
);

-- 4. Route Dimension (Directional: AAA-BBB != BBB-AAA)
CREATE TABLE IF NOT EXISTS gold_dim_route (
    route_key INTEGER PRIMARY KEY AUTOINCREMENT,
    origin_airport_key INTEGER NOT NULL REFERENCES gold_dim_airport(airport_key),
    destination_airport_key INTEGER NOT NULL REFERENCES gold_dim_airport(airport_key),
    route_code TEXT UNIQUE NOT NULL          -- Format: ORIGIN-DEST (e.g. 'JFK-LAX')
);

-- 5. Flight Fact Table (Grain: 1 row = 1 flight occurrence)
CREATE TABLE IF NOT EXISTS gold_fact_flight (
    flight_key INTEGER PRIMARY KEY AUTOINCREMENT,
    date_key INTEGER NOT NULL REFERENCES gold_dim_date(date_key),
    airline_key INTEGER NOT NULL REFERENCES gold_dim_airline(airline_key),
    origin_airport_key INTEGER NOT NULL REFERENCES gold_dim_airport(airport_key),
    destination_airport_key INTEGER NOT NULL REFERENCES gold_dim_airport(airport_key),
    route_key INTEGER NOT NULL REFERENCES gold_dim_route(route_key),
    
    -- Flight identification
    flight_number TEXT,
    tail_number TEXT,
    
    -- Operational times & delay measures
    scheduled_departure_time TEXT,
    actual_departure_time TEXT,
    departure_delay_minutes REAL,
    scheduled_arrival_time TEXT,
    actual_arrival_time TEXT,
    arrival_delay_minutes REAL,
    
    -- Flight performance & taxi
    taxi_out_minutes REAL,
    taxi_in_minutes REAL,
    scheduled_elapsed_minutes REAL,
    actual_elapsed_minutes REAL,
    air_time_minutes REAL,
    flights REAL DEFAULT 1.0,
    distance_miles REAL,
    
    -- Status flags
    cancelled INTEGER NOT NULL DEFAULT 0,
    cancellation_code TEXT,
    diverted INTEGER NOT NULL DEFAULT 0,
    
    -- Delay breakdown causes (semantic NULL when delay < 15 mins)
    carrier_delay_minutes REAL,
    weather_delay_minutes REAL,
    nas_delay_minutes REAL,
    security_delay_minutes REAL,
    late_aircraft_delay_minutes REAL,
    
    -- Target classification label
    arrival_delay_flag INTEGER,             -- 1 = Delayed >=15m, 0 = On-time, NULL = Cancelled/Diverted
    
    -- Provenance & lineage
    source_file TEXT,
    source_row_hash TEXT UNIQUE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_gold_fact_date ON gold_fact_flight(date_key);
CREATE INDEX IF NOT EXISTS idx_gold_fact_airline ON gold_fact_flight(airline_key);
CREATE INDEX IF NOT EXISTS idx_gold_fact_origin ON gold_fact_flight(origin_airport_key);
CREATE INDEX IF NOT EXISTS idx_gold_fact_dest ON gold_fact_flight(destination_airport_key);
CREATE INDEX IF NOT EXISTS idx_gold_fact_route ON gold_fact_flight(route_key);
CREATE INDEX IF NOT EXISTS idx_gold_fact_hash ON gold_fact_flight(source_row_hash);
