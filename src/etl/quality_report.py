"""
Data Quality Validation Report Generator
Stage 2 (Bronze + Silver) & Stage 3 (Gold Warehouse)
"""

import os
import json
from datetime import datetime


def generate_stage2_quality_report(bronze_metrics: dict, silver_metrics: dict, total_runtime_sec: float, output_dir="reports/stage2"):
    """
    Generates and saves the Stage 2 Data Quality JSON Report.
    """
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"stage2_data_quality_{timestamp_str}.json"
    
    report_data = {
        "report_title": "Stage 2 Databricks Bronze + Silver Data Quality Report",
        "generated_at": datetime.now().isoformat(),
        "total_pipeline_runtime_seconds": round(total_runtime_sec, 2),
        "overall_status": "SUCCESS" if (bronze_metrics.get("status") == "SUCCESS" and silver_metrics.get("status") == "SUCCESS") else "FAILED",
        "source": {
            "dataset_name": "U.S. BTS Reporting Carrier On-Time Performance",
            "source_files": bronze_metrics.get("source_files", []),
            "total_source_rows": bronze_metrics.get("source_rows", 0)
        },
        "bronze_layer": {
            "table_name": bronze_metrics.get("target_table"),
            "bronze_rows": bronze_metrics.get("bronze_rows", 0),
            "bronze_columns": bronze_metrics.get("bronze_columns", 0),
            "distinct_years": bronze_metrics.get("distinct_years", []),
            "min_flight_date": bronze_metrics.get("min_flight_date"),
            "max_flight_date": bronze_metrics.get("max_flight_date"),
            "duplicate_source_row_hashes": bronze_metrics.get("duplicate_source_row_hashes", 0),
            "null_counts": bronze_metrics.get("null_counts", {})
        },
        "silver_layer": {
            "table_name": silver_metrics.get("target_table"),
            "silver_rows": silver_metrics.get("silver_rows", 0),
            "silver_columns": silver_metrics.get("silver_columns", 0),
            "duplicates_removed": silver_metrics.get("duplicate_rows_removed", 0),
            "date_range": {
                "min": silver_metrics.get("min_flight_date"),
                "max": silver_metrics.get("max_flight_date")
            },
            "flight_counts": {
                "total": silver_metrics.get("silver_rows", 0),
                "cancelled": silver_metrics.get("cancelled_flights", 0),
                "diverted": silver_metrics.get("diverted_flights", 0),
                "delayed_15min_plus": silver_metrics.get("delayed_flights", 0)
            },
            "delay_statistics": {
                "avg_arrival_delay_minutes": silver_metrics.get("avg_arrival_delay_minutes"),
                "avg_departure_delay_minutes": silver_metrics.get("avg_departure_delay_minutes")
            },
            "integrity_checks": {
                "invalid_dates": silver_metrics.get("invalid_dates", 0),
                "invalid_times": silver_metrics.get("invalid_times", 0)
            }
        }
    }
    
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
        
    print(f"[QUALITY REPORT] Stage 2 Data quality report saved to: {report_path}")
    return report_path, report_data


def generate_stage3_quality_report(gold_metrics: dict, total_runtime_sec: float, output_dir="reports/stage3"):
    """
    Generates and saves the Stage 3 Gold Star Schema Data Quality JSON Report.
    """
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"stage3_data_quality_{timestamp_str}.json"
    
    report_data = {
        "report_title": "Stage 3 Databricks Gold Star Schema Data Quality Report",
        "generated_at": datetime.now().isoformat(),
        "total_pipeline_runtime_seconds": round(total_runtime_sec, 2),
        "overall_status": gold_metrics.get("status", "SUCCESS"),
        "gold_warehouse": {
            "catalog": gold_metrics.get("catalog", "flight_delay_dwm"),
            "schema": "gold",
            "silver_input_rows": gold_metrics.get("silver_input_rows", 0),
            "table_summary": {
                "fact_flight_rows": gold_metrics.get("fact_flight_rows", 0),
                "dim_date_rows": gold_metrics.get("dim_date_rows", 0),
                "dim_airline_rows": gold_metrics.get("dim_airline_rows", 0),
                "dim_airport_rows": gold_metrics.get("dim_airport_rows", 0),
                "dim_route_rows": gold_metrics.get("dim_route_rows", 0)
            },
            "integrity_checks": {
                "unresolved_foreign_keys": gold_metrics.get("unresolved_foreign_keys", 0),
                "foreign_key_integrity_passed": gold_metrics.get("foreign_key_integrity_passed", True)
            }
        }
    }
    
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
        
    print(f"[QUALITY REPORT] Stage 3 Data quality report saved to: {report_path}")
    return report_path, report_data
