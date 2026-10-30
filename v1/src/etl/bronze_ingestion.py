"""
PySpark Bronze Ingestion Module
Stage 2 - Local BTS CSV -> Unity Catalog Volume -> Bronze Delta Table
"""

import os
import time
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql import SparkSession

from src.etl.schema import validate_schema, REQUIRED_BTS_FIELDS


def generate_source_row_hash(df):
    """
    Generates a deterministic 64-character SHA-256 hash for each row.
    To prevent hash instability due to column ordering differences,
    columns are sorted alphabetically before concatenation.
    """
    source_cols = [c for c in df.columns if c not in (
        "ingestion_timestamp", "source_file", "source_year", "source_row_hash"
    )]
    sorted_cols = sorted(source_cols)
    
    # Concatenate all sorted columns separated by '||', replacing nulls with empty string
    concat_expr = F.concat_ws(
        "||",
        *[F.coalesce(F.col(c).cast("string"), F.lit("")) for c in sorted_cols]
    )
    
    return df.withColumn("source_row_hash", F.sha2(concat_expr, 256))


def ingest_bts_to_bronze(spark: SparkSession, input_files, target_table="flight_delay_dwm.bronze.bts_flights", is_delta_available=True):
    """
    Reads raw BTS CSV files, validates schema, attaches deterministic source_row_hash
    and ingestion metadata, and writes to Bronze Delta table.
    Preserves all raw source values without cleaning or imputing.
    """
    start_time = time.time()
    
    if isinstance(input_files, str):
        input_files = [input_files]
        
    print(f"[BRONZE INGESTION] Reading input files: {input_files}")
    
    # Read raw CSVs preserving original strings
    df_raw = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "false")
        .csv(input_files)
    )

    raw_row_count = df_raw.count()
    raw_col_count = len(df_raw.columns)
    print(f"[BRONZE INGESTION] Read {raw_row_count:,} rows across {raw_col_count} columns.")
    
    # Schema validation
    val_res = validate_schema(df_raw.columns)
    if not val_res["valid"]:
        print(f"[WARNING] Missing required fields in Bronze ingestion: {val_res['missing_fields']}")
    else:
        print("[BRONZE INGESTION] Schema validation PASSED for all required BTS fields.")
        
    # Attach Metadata & Deterministic Source Row Hash
    df_bronze = (
        df_raw
        .withColumn("ingestion_timestamp", F.current_timestamp())
        .withColumn("source_file", F.element_at(F.split(F.input_file_name(), "/"), -1))
        .withColumn("source_year", F.col("Year").cast("int"))
    )
    
    df_bronze = generate_source_row_hash(df_bronze)
    
    # Write to Bronze table
    print(f"[BRONZE INGESTION] Writing to table: {target_table}")
    if is_delta_available:
        try:
            (
                df_bronze.write
                .format("delta")
                .mode("overwrite")
                .option("overwriteSchema", "true")
                .saveAsTable(target_table)
            )
        except Exception as e:
            print(f"[BRONZE INGESTION] Delta table write fallback to path/parquet if needed: {e}")
            # Fallback if table name format or local environment requires path write
            df_bronze.write.format("parquet").mode("overwrite").save(target_table.replace(".", "_"))
    else:
        df_bronze.write.format("parquet").mode("overwrite").save(target_table.replace(".", "_"))
        
    execution_seconds = round(time.time() - start_time, 2)
    
    # Calculate Validation Statistics
    distinct_files = [row[0] for row in df_bronze.select("source_file").distinct().collect()]
    distinct_years = [row[0] for row in df_bronze.select("source_year").distinct().collect()]
    
    dates = df_bronze.select(
        F.min("FlightDate").alias("min_date"),
        F.max("FlightDate").alias("max_date")
    ).collect()[0]
    
    total_bronze_rows = df_bronze.count()
    unique_hashes = df_bronze.select("source_row_hash").distinct().count()
    duplicate_hashes = total_bronze_rows - unique_hashes
    
    null_counts = {}
    for check_col in ["FlightDate", "Reporting_Airline", "Origin", "Dest", "DepTime", "ArrTime"]:
        if check_col in df_bronze.columns:
            null_counts[check_col] = df_bronze.filter(F.col(check_col).isNull() | (F.col(check_col) == "")).count()
            
    metrics = {
        "pipeline_stage": "BRONZE_INGESTION",
        "target_table": target_table,
        "source_files": distinct_files,
        "source_rows": raw_row_count,
        "bronze_rows": total_bronze_rows,
        "bronze_columns": len(df_bronze.columns),
        "distinct_years": sorted([y for y in distinct_years if y is not None]),
        "min_flight_date": dates["min_date"],
        "max_flight_date": dates["max_date"],
        "duplicate_source_row_hashes": duplicate_hashes,
        "null_counts": null_counts,
        "execution_seconds": execution_seconds,
        "status": "SUCCESS"
    }
    
    print(f"[BRONZE INGESTION] Completed in {execution_seconds}s. Rows: {total_bronze_rows:,}, Duplicates: {duplicate_hashes:,}")
    return df_bronze, metrics
