"""
ETL Pipeline Run Metadata Logger
Stores execution metrics in flight_delay_dwm.metadata.etl_run_log
"""

import json
import uuid
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType, LongType, DoubleType
)

LOG_SCHEMA = StructType([
    StructField("run_id", StringType(), False),
    StructField("pipeline_stage", StringType(), False),
    StructField("start_time", TimestampType(), False),
    StructField("end_time", TimestampType(), True),
    StructField("status", StringType(), False),
    StructField("source_files", StringType(), True),
    StructField("source_rows", LongType(), True),
    StructField("bronze_rows", LongType(), True),
    StructField("silver_rows", LongType(), True),
    StructField("duplicates", LongType(), True),
    StructField("rejected_rows", LongType(), True),
    StructField("execution_seconds", DoubleType(), True),
    StructField("error_message", StringType(), True)
])


def log_etl_run(spark: SparkSession, metrics: dict, target_table="flight_delay_dwm.metadata.etl_run_log", is_delta_available=True):
    """
    Logs an ETL pipeline execution record to the metadata table.
    """
    run_id = str(uuid.uuid4())
    now = datetime.now()
    
    source_files_str = json.dumps(metrics.get("source_files", []))
    
    row_data = [(
        run_id,
        metrics.get("pipeline_stage", "STAGE2_ETL"),
        now,
        now,
        metrics.get("status", "SUCCESS"),
        source_files_str,
        metrics.get("source_rows", 0),
        metrics.get("bronze_rows", 0),
        metrics.get("silver_rows", 0),
        metrics.get("duplicate_source_row_hashes", metrics.get("duplicate_rows_removed", 0)),
        metrics.get("rejected_rows", 0),
        metrics.get("execution_seconds", 0.0),
        metrics.get("error_message", None)
    )]
    
    df_log = spark.createDataFrame(row_data, schema=LOG_SCHEMA)
    print(f"[METADATA LOGGER] Recording ETL run log ({run_id}) to {target_table}")
    
    if is_delta_available:
        try:
            df_log.write.format("delta").mode("append").saveAsTable(target_table)
        except Exception as e:
            print(f"[METADATA LOGGER] Delta write fallback: {e}")
            df_log.write.format("parquet").mode("append").save(target_table.replace(".", "_"))
    else:
        df_log.write.format("parquet").mode("append").save(target_table.replace(".", "_"))
        
    return run_id
