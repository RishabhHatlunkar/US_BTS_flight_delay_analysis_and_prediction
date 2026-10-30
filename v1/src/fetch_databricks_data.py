"""
Utility to fetch and print Gold layer data from Databricks.
Supports:
1. Databricks SQL Statements REST API (no extra drivers needed, uses `requests`)
2. Local PySpark session (if querying local Delta or metastore)
"""

import os
import sys
import time
import argparse
import requests


def fetch_via_databricks_rest_api(
    host: str,
    token: str,
    warehouse_id: str,
    catalog: str = "flight_delay_dwm",
    schema: str = "gold",
    limit: int = 10,
):
    """
    Executes queries against Databricks SQL Warehouse using Databricks REST API 2.0 (Statements Execution).
    """
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"https://{host}"
    host = host.rstrip("/")

    url = f"{host}/api/2.0/sql/statements"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    tables = ["dim_date", "dim_airline", "dim_airport", "dim_route", "fact_flight"]

    print("=" * 80)
    print(f"CONNECTING TO DATABRICKS WORKSPACE: {host}")
    print(f"CATALOG: {catalog} | SCHEMA: {schema} | WAREHOUSE ID: {warehouse_id}")
    print("=" * 80)

    for table in tables:
        full_table = f"{catalog}.{schema}.{table}"
        print(f"\n>>> FETCHING: {full_table} (Limit {limit})")
        
        payload = {
            "statement": f"SELECT * FROM {full_table} LIMIT {limit}",
            "warehouse_id": warehouse_id,
            "wait_timeout": "30s",
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code != 200:
                print(f"[ERROR] HTTP {resp.status_code}: {resp.text}")
                continue

            data = resp.json()
            status = data.get("status", {}).get("state", "UNKNOWN")
            
            # Wait if statement is still running
            statement_id = data.get("statement_id")
            while status in ["PENDING", "RUNNING"] and statement_id:
                time.sleep(2)
                poll_resp = requests.get(f"{url}/{statement_id}", headers=headers, timeout=30)
                data = poll_resp.json()
                status = data.get("status", {}).get("state", "UNKNOWN")

            if status != "SUCCEEDED":
                print(f"[ERROR] Statement execution state: {status}")
                if "error" in data.get("status", {}):
                    print("Error message:", data["status"]["error"])
                continue

            manifest = data.get("manifest", {})
            schema_info = manifest.get("schema", {})
            columns = [c.get("name") for c in schema_info.get("columns", [])]
            result_data = data.get("result", {}).get("data_array", [])

            # Print formatted table
            print(f"Total Rows Returned: {len(result_data)}")
            if columns:
                header_str = " | ".join(columns[:8])
                print("-" * len(header_str))
                print(header_str)
                print("-" * len(header_str))
                for row in result_data:
                    row_preview = [str(x) if x is not None else "NULL" for x in row[:8]]
                    print(" | ".join(row_preview))
                if len(columns) > 8:
                    print(f"  ... (+ {len(columns) - 8} more columns: {', '.join(columns[8:])})")

        except Exception as e:
            print(f"[EXCEPTION] Failed to fetch table {table}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Fetch and print Gold data from Databricks")
    parser.add_argument(
        "--host",
        default=os.environ.get("DATABRICKS_HOST", ""),
        help="Databricks Host URL (e.g. https://dbc-xxxx.cloud.databricks.com)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("DATABRICKS_TOKEN", ""),
        help="Databricks Personal Access Token",
    )
    parser.add_argument(
        "--warehouse-id",
        default=os.environ.get("DATABRICKS_WAREHOUSE_ID", ""),
        help="Databricks SQL Warehouse ID (from SQL Warehouse connection details)",
    )
    parser.add_argument(
        "--catalog",
        default="flight_delay_dwm",
        help="Databricks Unity Catalog name",
    )
    parser.add_argument(
        "--schema",
        default="gold",
        help="Target schema (default: gold)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of sample rows to print per table",
    )
    args = parser.parse_args()

    if not args.host or not args.token or not args.warehouse_id:
        print("[!] Databricks connection parameters are missing.")
        print("\nPlease provide them via command-line arguments or environment variables:")
        print("  --host            Databricks workspace URL (or set DATABRICKS_HOST)")
        print("  --token           Databricks Personal Access Token (or set DATABRICKS_TOKEN)")
        print("  --warehouse-id    Databricks SQL Warehouse ID (or set DATABRICKS_WAREHOUSE_ID)")
        print("\nExample command:")
        print("  python v1/src/fetch_databricks_data.py --host https://dbc-xxxx.cloud.databricks.com --token dapi... --warehouse-id abcd1234efgh5678")
        sys.exit(1)

    fetch_via_databricks_rest_api(
        host=args.host,
        token=args.token,
        warehouse_id=args.warehouse_id,
        catalog=args.catalog,
        schema=args.schema,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
