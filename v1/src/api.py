"""
FastAPI Backend Service for Databricks Gold Star Schema Data Warehouse.
Reuses existing code in v1/src/data_loader.py and v1/src/olap_analytics.py.
Sources all data exclusively from Databricks Unity Catalog (flight_delay_dwm.gold).
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Add v1 to sys.path so existing modules import cleanly
V1_DIR = Path(__file__).resolve().parent.parent
if str(V1_DIR) not in sys.path:
    sys.path.insert(0, str(V1_DIR))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from src.data_loader import (
    get_cached_cubes_and_sample,
    build_and_cache_olap_cubes,
    fetch_from_databricks,
    is_databricks_configured,
    DATABRICKS_HOST,
    DATABRICKS_CATALOG,
    DATABRICKS_SCHEMA,
    DATABRICKS_WAREHOUSE_ID,
)
from src.olap_analytics import OLAPAnalytics

app = FastAPI(
    title="Databricks Flight Delay Gold Warehouse API",
    description="REST API serving analytics from Databricks Unity Catalog Gold star schema across 30.7M BTS flights.",
    version="2.0.0"
)

# Enable CORS for Next.js frontend (default port 3000, 3001, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for loaded cubes and sample dataframe
STATE = {
    "cubes": None,
    "df_sample": None,
    "source_desc": None,
    "olap": None,
}


def ensure_data_loaded(force_refresh: bool = False):
    """Initialises or refreshes data from existing data loader."""
    if STATE["cubes"] is None or force_refresh:
        cubes, df_sample, desc = get_cached_cubes_and_sample(force_refresh=force_refresh)
        STATE["cubes"] = cubes
        STATE["df_sample"] = df_sample
        STATE["source_desc"] = desc
        if df_sample is not None and not df_sample.empty:
            STATE["olap"] = OLAPAnalytics(df_sample)
    return STATE["cubes"]


@app.on_event("startup")
def startup_event():
    print("[API] Initialising Databricks Gold Warehouse data cache...")
    try:
        ensure_data_loaded()
        print(f"[API] Data successfully ready: {STATE['source_desc']}")
    except Exception as e:
        print(f"[API] Warning during startup data load: {e}")


@app.get("/api/health")
def get_health():
    """Returns system and Databricks connection status."""
    ensure_data_loaded()
    kpis = STATE["cubes"].get("kpis", {}) if STATE["cubes"] else {}
    return {
        "status": "healthy",
        "databricks_configured": is_databricks_configured(),
        "databricks_host": DATABRICKS_HOST,
        "databricks_catalog": DATABRICKS_CATALOG,
        "databricks_schema": DATABRICKS_SCHEMA,
        "warehouse_id": DATABRICKS_WAREHOUSE_ID,
        "data_source": STATE.get("source_desc", "Databricks Gold Warehouse"),
        "total_warehouse_flights": kpis.get("total_flights", 30742408),
        "sample_records_cached": len(STATE["df_sample"]) if STATE["df_sample"] is not None else 0,
    }


@app.get("/api/overview")
def get_overview():
    """Returns Executive KPIs and monthly trends."""
    cubes = ensure_data_loaded()
    return {
        "kpis": cubes.get("kpis", {}),
        "monthly_trend": cubes.get("monthly_trend", []),
        "source": STATE.get("source_desc"),
    }


@app.get("/api/airlines")
def get_airlines():
    """Returns airline benchmarking, delay rates, and delay causes by carrier."""
    cubes = ensure_data_loaded()
    airline_perf = cubes.get("airline_performance", [])
    delay_causes = cubes.get("delay_causes", [])
    late_share = cubes.get("late_aircraft_share", [])
    return {
        "airlines": airline_perf,
        "delay_causes": delay_causes,
        "late_aircraft_share": late_share,
    }


@app.get("/api/airports")
def get_airports():
    """Returns origin and destination airport congestion and delay performance."""
    cubes = ensure_data_loaded()
    origin_airports = cubes.get("origin_airports", [])
    dest_airports = cubes.get("dest_airports", [])
    return {
        "origin_airports": origin_airports,
        "dest_airports": dest_airports,
    }


@app.get("/api/routes")
def get_routes(limit: int = 50):
    """Returns directional route performance metrics."""
    cubes = ensure_data_loaded()
    routes = cubes.get("routes", [])
    return {
        "routes": routes[:limit],
        "total_routes_tracked": len(routes),
    }


@app.get("/api/causes")
def get_delay_causes():
    """Returns root-cause breakdown (Carrier, Weather, NAS, Security, Late Aircraft)."""
    cubes = ensure_data_loaded()
    return {
        "delay_causes": cubes.get("delay_causes", []),
        "late_aircraft_share": cubes.get("late_aircraft_share", []),
    }


@app.get("/api/temporal")
def get_temporal():
    """Returns day of week and scheduled departure hour patterns."""
    cubes = ensure_data_loaded()
    return {
        "weekday_patterns": cubes.get("weekday_patterns", []),
        "hourly_patterns": cubes.get("hourly_patterns", []),
    }


class FilterRequest(BaseModel):
    years: Optional[List[int]] = None
    year: Optional[int] = None
    quarters: Optional[List[int]] = None
    quarter: Optional[int] = None
    months: Optional[List[int]] = None
    month: Optional[int] = None
    airlines: Optional[List[str]] = None
    airline: Optional[str] = None
    origins: Optional[List[str]] = None
    origin: Optional[str] = None
    destinations: Optional[List[str]] = None
    destination: Optional[str] = None


@app.post("/api/filter")
def filter_analytics(req: FilterRequest):
    """
    Performs dynamic in-memory OLAP slice-and-dice filtering
    using the existing OLAPAnalytics engine on the representative Gold sample.
    """
    ensure_data_loaded()
    if STATE["olap"] is None:
        raise HTTPException(status_code=500, detail="OLAP engine not initialised.")

    # Normalize singular/plural filters
    years = req.years or ([req.year] if req.year is not None else None)
    quarters = req.quarters or ([req.quarter] if req.quarter is not None else None)
    months = req.months or ([req.month] if req.month is not None else None)
    airlines = req.airlines or ([req.airline] if req.airline is not None else None)
    origins = req.origins or ([req.origin] if req.origin is not None else None)
    destinations = req.destinations or ([req.destination] if req.destination is not None else None)

    filtered_olap = STATE["olap"].apply_filters(
        years=years,
        quarters=quarters,
        months=months,
        airlines=airlines,
        origins=origins,
        destinations=destinations,
    )

    kpis = filtered_olap.get_kpis()
    monthly = filtered_olap.q2_delays_over_time().to_dict(orient="records")
    airlines_data = filtered_olap.q5_airline_delay_rates().to_dict(orient="records")
    top_airports = filtered_olap.q10_origin_departure_delays().head(15).to_dict(orient="records")

    return {
        "kpis": kpis,
        "monthly_trend": monthly,
        "airlines": airlines_data,
        "top_airports": top_airports,
        "active_filters": {
            "years": years,
            "quarters": quarters,
            "months": months,
            "airlines": airlines,
            "origins": origins,
            "destinations": destinations,
        },
    }


class DirectQueryRequest(BaseModel):
    sql: str


@app.post("/api/query-databricks")
def run_direct_databricks_query(req: DirectQueryRequest):
    """Directly executes custom SQL against Databricks SQL Warehouse."""
    if not is_databricks_configured():
        raise HTTPException(status_code=400, detail="Databricks connection is not configured in .env.")

    # Basic safety safeguard: allow only SELECT queries
    sql_clean = req.sql.strip()
    if not sql_clean.upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are permitted.")

    try:
        df = fetch_from_databricks(sql_clean)
        return {
            "columns": list(df.columns),
            "rows": df.to_dict(orient="records"),
            "row_count": len(df),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh")
def refresh_cache():
    """Forces a rebuild of cached OLAP cubes from live Databricks SQL Warehouse."""
    try:
        cubes = build_and_cache_olap_cubes()
        STATE["cubes"] = cubes
        return {"status": "success", "message": "Databricks Gold cache refreshed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh from Databricks: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
