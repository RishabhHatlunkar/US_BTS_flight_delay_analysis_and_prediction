"""
Unit Tests for V2 Analytical & OLAP SQL Queries
Executes all 10 verified analytical queries against the Gold warehouse fixture.
"""

import pytest
from v2.src.bronze.ingest import ingest_bronze_files
from v2.src.silver.clean import transform_bronze_to_silver
from v2.src.gold.dimensions import populate_gold_dimensions
from v2.src.gold.facts import load_gold_fact_flights
from v2.src.analytics.run_analytics import execute_all_analytics


def test_analytical_sql_queries_execution(test_env):
    """Tests that all 10 analytical SQL queries execute without syntax errors or runtime exceptions."""
    config = test_env["config"]
    ingest_bronze_files(config, force=True)
    transform_bronze_to_silver(config, force=True)
    populate_gold_dimensions(config, force=True)
    load_gold_fact_flights(config, force=True)

    results = execute_all_analytics(config)

    expected_queries = [
        "01_monthly_delay_summary.sql",
        "02_airline_delay_rate.sql",
        "03_airport_delay_performance.sql",
        "04_top_routes_by_delay.sql",
        "05_cancellation_and_diversion_rates.sql",
        "06_delay_cause_breakdown.sql",
        "07_flights_by_day_and_hour.sql",
        "08_rollup_drilldown.sql",
        "09_slice_dice.sql",
        "10_null_handling_validation.sql"
    ]

    for eq in expected_queries:
        assert eq in results, f"Missing query result for {eq}"
        res = results[eq]
        assert "error" not in res, f"Query {eq} raised error: {res.get('error')}"
        assert res.get("columns") is not None
