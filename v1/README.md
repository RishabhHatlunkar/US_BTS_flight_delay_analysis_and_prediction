# V1: Databricks Medallion Data Warehouse Architecture

This directory contains the **V1 Databricks-based implementation** of the US BTS Flight Delay Analytics and Prediction data warehouse.

## Architecture
- **Platform**: Databricks (Unity Catalog & Delta Lake)
- **Catalog**: `flight_delay_dwm`
- **Schemas**:
  - `flight_delay_dwm.bronze`
  - `flight_delay_dwm.silver`
  - `flight_delay_dwm.gold`
  - `flight_delay_dwm.metadata`
- **ETL**: PySpark notebooks and modules (`v1/src/etl/`)
- **DDL**: `v1/sql/schema/`
- **Tests**: PySpark unit tests in `v1/tests/`

## Fetching & Inspecting Gold Data

### Option A: Directly inside Databricks (Notebook or SQL Editor)
- **Notebook**: Run [`v1/notebooks/03_gold/02_inspect_gold_tables.py`](notebooks/03_gold/02_inspect_gold_tables.py) in your Databricks cluster to display sample records from all gold tables (`fact_flight`, `dim_airline`, `dim_airport`, `dim_route`, `dim_date`).
- **SQL Editor**: Execute queries in [`v1/sql/inspect_gold_tables.sql`](sql/inspect_gold_tables.sql).

### Option B: Remote Execution via Databricks REST API
Run [`v1/src/fetch_databricks_data.py`](src/fetch_databricks_data.py) locally with your Databricks credentials:
```bash
python v1/src/fetch_databricks_data.py \
  --host "https://<your-databricks-workspace-url>" \
  --token "<your-personal-access-token>" \
  --warehouse-id "<your-sql-warehouse-id>"
```

## Interactive OLAP & Analytics Dashboard

An interactive 7-page analytical dashboard has been built in `v1/src/app.py` answering business questions Q1 to Q31 directly against the **30,742,408** Databricks Gold records:

1. **Credentials**: Stored securely in [`v1/.env`](.env) (template in [`v1/.env.example`](.env.example)).
2. **Launch the Dashboard**:
   ```bash
   streamlit run v1/src/app.py
   # or
   python v1/run_dashboard.py
   ```
3. **Pages**:
   - **Page 1 — Executive Overview (Q1–Q4)**: KPI cards, delay rate trends, flight outcomes breakdown, top delay burden contributors.
   - **Page 2 — Airline Performance (Q5–Q9)**: Comparative arrival delay rates, signed vs positive delay, total delay burden, cancellation & diversion rates, and drill-down by weekday/hour.
   - **Page 3 — Airport & Route Analysis (Q10–Q14)**: Worst origin departure airports, worst destination arrival airports, route delay rankings, high-volume delay corridors, and multi-airline route comparison.
   - **Page 4 — Time & Operational Patterns (Q15–Q19)**: Seasonal trends, day-of-week patterns, departure hour ripple effect, departure vs arrival delay persistence correlation ($r = 0.95$), and disruption trends.
   - **Page 5 — Delay Causes & Disruptions (Q20–Q23)**: Breakdown of recorded delay causes (Carrier, Late Aircraft, NAS, Weather, Security), temporal distributions, airline-level causes, and late-arriving aircraft share (42.5%).
   - **Page 6 — Historical Delay Risk (Q24–Q27)**: Empirical historical risk calculator (Airline + Route + Day + Hour), reliability flags, and sample confidence ratings.
   - **Page 7 — OLAP Explorer (Q28–Q31)**: Hands-on Data Warehousing operations:
     - **Roll-up & Drill-down** (Year ⇄ Quarter ⇄ Month)
     - **Slice & Dice** (Carrier, Origin, Weekday)
     - **2D Pivot Matrix** (Carrier rows × Month columns with delay rate gradient)
     - **Drill-through** (direct inspection of granular underlying `fact_flight` records)


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
