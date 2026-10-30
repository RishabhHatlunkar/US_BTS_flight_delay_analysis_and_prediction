# Flight Delay Analytics and Prediction Using Data Warehousing and Data Mining

## 1. Project Overview

This project implements an end-to-end Data Warehousing and Data Mining (DWM) pipeline for analyzing historical flight delays in the United States, discovering delay factors across airlines, airports, routes, and temporal periods, building a dimensional data warehouse with star schema in Databricks, and applying machine learning models (classification and clustering) with interactive business intelligence reporting.

**Primary Data Source:** U.S. Bureau of Transportation Statistics (BTS) - *Reporting Carrier On-Time Performance (1987-present)*.

---

## 2. Databricks Architecture & Data Pipeline

```
LOCAL BTS CSV / DOWNLOADER
          ↓
UNITY CATALOG VOLUME (/Volumes/flight_delay_dwm/bronze/raw_bts)
          ↓
BRONZE DELTA TABLE (flight_delay_dwm.bronze.bts_flights)
          ↓
SILVER DELTA TABLE (flight_delay_dwm.silver.flights)
          ↓
GOLD STAR SCHEMA DATA WAREHOUSE (flight_delay_dwm.gold.*)
  ├── dim_date (Date Dimension)
  ├── dim_airline (Airline / Carrier Dimension)
  ├── dim_airport (Role-Playing Airport Dimension - Origin & Destination)
  ├── dim_route (Directional Route Dimension)
  └── fact_flight (Flight Performance Fact Table at 1 row = 1 flight grain)
          ↓
DATA QUALITY VALIDATION & METADATA RUN LOG
```

### Storage Layers & Architecture Highlights
- **Platform:** Databricks Free Edition with **Unity Catalog** and **Delta Lake**.
- **Immutable Raw Data:** Local BTS CSV files (`data/raw/bts/`) and Unity Catalog Volume files (`/Volumes/flight_delay_dwm/bronze/raw_bts/`) are strictly immutable.
- **Bronze Layer (`flight_delay_dwm.bronze.bts_flights`):** Preserves source BTS fields with ingestion metadata (`ingestion_timestamp`, `source_file`, `source_year`) and a deterministic 64-character SHA-256 `source_row_hash`.
- **Silver Layer (`flight_delay_dwm.silver.flights`):** Cleaned, typed, deduplicated analytical layer. Converts types (`INTEGER`, `DOUBLE`, `DATE`), parses HHMM times (`departure_hour`, `arrival_hour`), constructs directional `route_code` (e.g. `JFK-LAX`), computes `delay_flag` (1 for delays >= 15 mins), deduplicates exact duplicate records, and preserves cancelled (`Cancelled = 1`) and diverted (`Diverted = 1`) flights while retaining semantic `NULL`s for delay causes.
- **Gold Star Schema Layer (`flight_delay_dwm.gold.*`):** Enterprise Star Schema dimensional model with 4 dimension tables and 1 fact table:
  - **`gold.dim_date`**: Full calendar dimension keyed by `date_key` (`YYYYMMDD`).
  - **`gold.dim_airline`**: Carrier dimension keyed by surrogate `airline_key`.
  - **`gold.dim_airport`**: Role-playing airport dimension keyed by surrogate `airport_key` (referenced twice by fact table for Origin and Destination).
  - **`gold.dim_route`**: Directional route dimension keyed by surrogate `route_key` (`JFK-LAX != LAX-JFK`).
  - **`gold.fact_flight`**: Fact table at the grain of **ONE ROW = ONE FLIGHT OCCURRENCE**. Stores measures (delays, taxi times, distance, cancellation/diversion flags) and foreign keys pointing to all 4 dimensions.
- **Metadata Layer (`flight_delay_dwm.metadata.etl_run_log`):** Audit table recording pipeline execution logs, status, run duration, row counts, duplicate counts, and error traces.

---

## 3. Catalog, Schemas, and Star Schema Tables

| Schema | Table / Asset Name | Type | Description |
| :--- | :--- | :--- | :--- |
| `bronze` | `raw_bts` | UC Volume | Storage volume containing raw `bts_flights_YYYY.csv` files |
| `bronze` | `bts_flights` | Delta Table | Raw ingestion table with source columns + deterministic hash & metadata |
| `silver` | `flights` | Delta Table | Cleaned, typed, deduplicated analytical table with derived time & route features |
| `gold` | `dim_date` | Dimension | Calendar dimension (`date_key`, `full_date`, `year`, `quarter`, `month`, `day`, `day_of_week`, `is_weekend`) |
| `gold` | `dim_airline` | Dimension | Airline carrier dimension (`airline_key`, `reporting_airline_code`, `dot_airline_id`, `iata_airline_code`) |
| `gold` | `dim_airport` | Dimension | Role-playing airport dimension (`airport_key`, `airport_id`, `airport_code`, `city_name`, `state`) |
| `gold` | `dim_route` | Dimension | Directional route dimension (`route_key`, `route_code`, `origin_airport_code`, `destination_airport_code`) |
| `gold` | `fact_flight` | Fact Table | Flight performance fact table at 1 row = 1 flight grain with foreign keys & delay measures |
| `metadata`| `etl_run_log` | Delta Table | Execution audit log table tracking pipeline run metrics and status |

---

## 4. Star Schema ER Diagram

```
         +-----------------------+
         |     gold.dim_date     |
         +-----------------------+
         | PK  date_key (YYYYMMDD)|
         |     full_date         |
         |     year, quarter     |
         |     month, day_name   |
         +-----------+-----------+
                     |
                     | 1:N
                     v
+--------------------+---------------------+
|              gold.fact_flight            |
+------------------------------------------+
| PK  flight_key (source_row_hash)         |
| FK  date_key                             |-----> gold.dim_date (date_key)
| FK  airline_key                          |-----> gold.dim_airline (airline_key)
| FK  origin_airport_key                   |-----> gold.dim_airport (airport_key) [Role: Origin]
| FK  destination_airport_key              |-----> gold.dim_airport (airport_key) [Role: Destination]
| FK  route_key                            |-----> gold.dim_route (route_key)
|     flight_number, tail_number           |
|     crs_dep_time, dep_time, dep_delay    |
|     crs_arr_time, arr_time, arr_delay    |
|     delay_flag, taxi_out, taxi_in        |
|     cancelled, cancellation_code, diverted|
|     carrier_delay, weather_delay, etc.   |
+----+---------------+---------------+-----+
     |               |               |
 1:N |           1:N |           1:N |
     v               v               v
+----+----+    +-----+---+     +-----+-----+
|dim_airline|  |dim_airport|   | dim_route |
+-----------+  +-----------+   +-----------+
|airline_key|  |airport_key|   | route_key |
+-----------+  +-----------+   +-----------+
```

---

## 5. Notebooks and Execution Guide

### Notebook Structure (`notebooks/`)
Available in both `.py` (Databricks Source format) and `.ipynb` (Jupyter format):
- `notebooks/01_ingestion/01_bts_to_bronze`: Ingests raw CSVs into `bronze.bts_flights`.
- `notebooks/02_etl/01_bronze_to_silver`: Cleans and transforms Bronze into `silver.flights`.
- `notebooks/03_gold/01_silver_to_gold`: Builds Star Schema dimensions and fact table in `gold.*`.
- `notebooks/03_metadata/01_etl_log`: Queries execution run log and data quality reports.

### Python Modules (`src/etl/`)
- `src/etl/schema.py`: BTS field definitions & schema validation functions.
- `src/etl/bronze_ingestion.py`: PySpark Bronze ingestion pipeline & deterministic SHA-256 hash generation.
- `src/etl/silver_etl.py`: PySpark Silver ETL pipeline, safe type casting, date/time parsing, semantic NULL preservation, route generation, delay flag, deduplication.
- `src/etl/gold_etl.py`: PySpark Gold ETL pipeline building `dim_date`, `dim_airline`, `dim_airport`, `dim_route`, and `fact_flight` with foreign key integrity checks.
- `src/etl/metadata_logger.py`: ETL run logger writing to `metadata.etl_run_log`.
- `src/etl/quality_report.py`: Data Quality Report generator outputting JSON summaries to `reports/`.
- `src/runner.py`: End-to-end command line execution runner.

### Running the Pipeline

#### 1. In Databricks Workspace:
Import notebooks from `notebooks/` into your Databricks workspace and run `01_bts_to_bronze` → `01_bronze_to_silver` → `01_silver_to_gold`.

#### 2. Locally via CLI Runner:
```bash
# Run all stages end-to-end (Bronze + Silver + Gold)
python -m src.runner --catalog flight_delay_dwm --stage all
```

#### 3. Running Automated Test Suite:
```bash
pytest -v tests/test_stage2_etl.py tests/test_stage3_gold.py
```


---

## Interactive Dashboard (Next.js 16 + FastAPI)

A modern, high-performance web dashboard built with **Next.js 16 (App Router + Tailwind CSS)** and a **FastAPI Python backend** that directly integrates with existing Databricks Gold warehouse pipelines.

### Key Highlights
- **No Separate/Duplicate Backend**: Directly wraps and reuses existing modules (`v1/src/data_loader.py` and `v1/src/olap_analytics.py`).
- **Databricks Unity Catalog Data**: Data is sourced exclusively from Databricks Unity Catalog Gold (`flight_delay_dwm.gold.fact_flight`, representing 30,742,408 processed flight records).
- **Aesthetic Design**: Bright, modern Royal Blue (`#1E3A8A`, `#1E40AF`, `#2563EB`) and Crisp White color scheme with subtle gradients, card styling, and responsive navigation.
- **8 Dedicated Analytics Tabs**:
  1. **Executive Overview**: Punctuality trajectory, 6 core KPIs, and monthly volume vs delay rate.
  2. **Airlines Scorecard**: Punctuality league table for 18 carriers, net delay burden, cancellation and diversion rates.
  3. **Airport Congestion**: Origin departure delays vs. destination arrival bottlenecks across major US hubs.
  4. **Bottleneck Routes**: High-traffic directional city pairs ranked by delay exposure (ATL, ORD, DEN, DFW, LGA, etc.).
  5. **Root Causes & Cascades**: Late aircraft inbound reaction propagation (41.2% primary culprit) alongside carrier, weather, NAS, and security breakdowns.
  6. **Temporal & Seasonality**: 7-day weekday congestion cycle and 24-hour diurnal morning-to-night delay accumulation profile.
  7. **OLAP Slice & Dice**: Interactive multi-dimensional filtering by Airline, Year, Month, Origin, and Destination.
  8. **Stakeholder Insights**: Concrete operational and economic recommendations for Airlines, Airports, ATC/FAA, and Passengers.

### Running the Dashboard

You can start both the backend API and frontend with a single command from the repository root:

```bash
# Using python launcher
python start_dashboard.py

# Or on Windows using batch script
start_dashboard.bat
```

Alternatively, run them in separate terminals:
```bash
# Terminal 1: FastAPI Backend (Port 8000)
python -m uvicorn src.api:app --app-dir v1 --port 8000 --reload

# Terminal 2: Next.js Frontend (Port 3000)
cd frontend
npm run dev
```

Visit **http://localhost:3000** in your browser. Interactive OpenAPI documentation is available at **http://127.0.0.1:8000/docs**.
