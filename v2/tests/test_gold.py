"""
Unit Tests for V2 Gold Star Schema Layer
Tests dimension surrogate keys, shared airport dimension, directional routes,
fact foreign-key integrity, and safe rebuilding.
"""

import pytest
from v2.src.bronze.ingest import ingest_bronze_files
from v2.src.silver.clean import transform_bronze_to_silver
from v2.src.gold.dimensions import populate_gold_dimensions
from v2.src.gold.facts import load_gold_fact_flights
from v2.src.gold.validator import validate_gold_warehouse
from v2.src.utils.db import get_db_connection


def test_gold_warehouse_pipeline_and_integrity(test_env):
    """Tests that Gold dimensions and fact table load with 100% referential integrity."""
    config = test_env["config"]
    ingest_bronze_files(config, force=True)
    transform_bronze_to_silver(config, force=True)

    # Populate Gold
    dim_counts = populate_gold_dimensions(config, force=True)
    assert dim_counts["gold_dim_date"] >= 1
    assert dim_counts["gold_dim_airline"] >= 3
    assert dim_counts["gold_dim_airport"] >= 4
    assert dim_counts["gold_dim_route"] >= 4

    # Load Fact
    f_res = load_gold_fact_flights(config, force=True)
    assert f_res["inserted_rows"] == 5

    # Run Validator
    v_report = validate_gold_warehouse(config)
    assert v_report["is_valid"] is True
    assert v_report["total_unresolved_foreign_keys"] == 0
    assert v_report["duplicate_fact_grain_count"] == 0

    conn = get_db_connection(test_env["db_path"])
    cursor = conn.cursor()

    # Test Directional Route Uniqueness: LGA-OMA and OMA-LGA must be two distinct route rows
    cursor.execute("""
        SELECT route_code, origin_airport_key, destination_airport_key
        FROM gold_dim_route
        WHERE route_code IN ('LGA-OMA', 'OMA-LGA')
    """)
    routes = {r["route_code"]: r for r in cursor.fetchall()}
    assert len(routes) == 2
    assert routes["LGA-OMA"]["origin_airport_key"] == routes["OMA-LGA"]["destination_airport_key"]
    assert routes["LGA-OMA"]["destination_airport_key"] == routes["OMA-LGA"]["origin_airport_key"]

    conn.close()


def test_gold_rebuild_does_not_affect_silver_or_bronze(test_env):
    """Tests that rebuilding Gold layer preserves Bronze and Silver data intact."""
    config = test_env["config"]
    ingest_bronze_files(config, force=True)
    transform_bronze_to_silver(config, force=True)

    # Rebuild Gold twice
    populate_gold_dimensions(config, force=True)
    load_gold_fact_flights(config, force=True)

    conn = get_db_connection(test_env["db_path"])
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bronze_bts_flights")
    assert cursor.fetchone()[0] == 6
    cursor.execute("SELECT COUNT(*) FROM silver_flights")
    assert cursor.fetchone()[0] == 5
    conn.close()
