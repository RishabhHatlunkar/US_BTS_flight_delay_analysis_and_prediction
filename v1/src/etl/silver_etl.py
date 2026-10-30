"""
PySpark Silver ETL Module
Stage 2 - Bronze Delta Table -> Silver Cleaned & Typed Analytical Layer
"""

import time
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    IntegerType, DoubleType, DateType, StringType
)


def parse_hhmm_time(col_name):
    """
    Parses HHMM integer/string values (e.g. 530 -> '05:30', 1425 -> '14:25').
    Pads to 4 digits, extracts HH (00..23) and MM (00..59).
    Returns formatted string 'HH:MM' or NULL for invalid values.
    """
    raw_col = F.col(col_name).cast("string")
    clean_digits = F.regexp_extract(raw_col, r"^(\d{1,4})", 1)
    padded = F.lpad(clean_digits, 4, "0")
    
    hh = F.substring(padded, 1, 2).cast("int")
    mm = F.substring(padded, 3, 2).cast("int")
    
    valid_time = F.when(
        raw_col.isNotNull() & (clean_digits != "") & (hh >= 0) & (hh <= 23) & (mm >= 0) & (mm <= 59),
        F.concat(F.lpad(hh, 2, "0"), F.lit(":"), F.lpad(mm, 2, "0"))
    ).when(
        raw_col.isNotNull() & (clean_digits != "") & (hh == 24) & (mm == 0),
        F.lit("00:00")
    ).otherwise(F.lit(None))
    
    return valid_time


def extract_hour(col_name):
    """Extracts integer hour (0..23) from HHMM integer/string column."""
    raw_col = F.col(col_name).cast("string")
    clean_digits = F.regexp_extract(raw_col, r"^(\d{1,4})", 1)
    padded = F.lpad(clean_digits, 4, "0")
    hh = F.substring(padded, 1, 2).cast("int")
    
    return F.when(
        raw_col.isNotNull() & (clean_digits != "") & (hh >= 0) & (hh <= 23),
        hh
    ).when(
        raw_col.isNotNull() & (clean_digits != "") & (hh == 24),
        0
    ).otherwise(F.lit(None))


def safe_cast_double(col_expr):
    """Replaces empty string with NULL and casts to DoubleType safely."""
    return F.when((col_expr == "") | col_expr.isNull(), F.lit(None)).otherwise(col_expr).cast(DoubleType())


def safe_cast_int(col_expr):
    """Replaces empty string with NULL and casts to Double -> Int safely."""
    return F.when((col_expr == "") | col_expr.isNull(), F.lit(None)).otherwise(col_expr).cast(DoubleType()).cast(IntegerType())


def transform_bronze_to_silver(spark: SparkSession, source_df_or_table, target_table="flight_delay_dwm.silver.flights", is_delta_available=True, is_save=True):
    """
    Reads Bronze data, applies type casting, date/time parsing, deduplication,
    derived analytical columns, preserves semantic NULLs & cancelled/diverted flights.
    """
    start_time = time.time()
    
    if isinstance(source_df_or_table, str):
        print(f"[SILVER ETL] Reading Bronze table: {source_df_or_table}")
        df_bronze = spark.table(source_df_or_table)
    else:
        df_bronze = source_df_or_table

    total_bronze_input_rows = df_bronze.count()
    print(f"[SILVER ETL] Processing {total_bronze_input_rows:,} Bronze input records.")
    
    # 1. Deduplication on source_row_hash
    df_dedup = df_bronze.dropDuplicates(["source_row_hash"])
    dedup_rows = df_dedup.count()
    duplicate_rows_removed = total_bronze_input_rows - dedup_rows
    print(f"[SILVER ETL] Deduplicated records: Retained {dedup_rows:,} (Removed {duplicate_rows_removed:,} exact duplicates).")

    # 2. Type Conversions & Safe Casting
    int_cols = [
        "Year", "Quarter", "Month", "DayofMonth", "DayOfWeek",
        "DOT_ID_Reporting_Airline", "Flight_Number_Reporting_Airline",
        "OriginAirportID", "OriginAirportSeqID", "OriginCityMarketID", "OriginStateFips", "OriginWac",
        "DestAirportID", "DestAirportSeqID", "DestCityMarketID", "DestStateFips", "DestWac",
        "Cancelled", "Diverted", "Flights", "DistanceGroup"
    ]
    
    double_cols = [
        "DepDelay", "DepDelayMinutes", "DepDel15", "DepartureDelayGroups", "TaxiOut",
        "ArrDelay", "ArrDelayMinutes", "ArrDel15", "ArrivalDelayGroups", "TaxiIn",
        "CRSElapsedTime", "ActualElapsedTime", "AirTime", "Distance"
    ]
    
    delay_cause_cols = [
        "CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay"
    ]

    df_silver = df_dedup

    # Cast integer columns safely handling empty strings
    for col_name in int_cols:
        if col_name in df_silver.columns:
            df_silver = df_silver.withColumn(col_name, safe_cast_int(F.col(col_name)))

    # Cast double columns safely handling empty strings
    for col_name in double_cols:
        if col_name in df_silver.columns:
            df_silver = df_silver.withColumn(col_name, safe_cast_double(F.col(col_name)))

    # Cast delay cause breakdown columns safely WITHOUT replacing NULL with 0
    for col_name in delay_cause_cols:
        if col_name in df_silver.columns:
            df_silver = df_silver.withColumn(col_name, safe_cast_double(F.col(col_name)))

    # 3. Date Validation & Conversion
    df_silver = df_silver.withColumn("flight_date", F.to_date(F.col("FlightDate"), "yyyy-MM-dd"))
    
    df_silver = (
        df_silver
        .withColumn("year", F.year(F.col("flight_date")))
        .withColumn("quarter", F.quarter(F.col("flight_date")))
        .withColumn("month", F.month(F.col("flight_date")))
        .withColumn("day_of_week", F.dayofweek(F.col("flight_date")))
    )

    # 4. Time Conversion & Hour Extraction
    time_cols = ["CRSDepTime", "DepTime", "CRSArrTime", "ArrTime", "WheelsOff", "WheelsOn"]
    for t_col in time_cols:
        if t_col in df_silver.columns:
            df_silver = df_silver.withColumn(f"{t_col}_formatted", parse_hhmm_time(t_col))

    df_silver = (
        df_silver
        .withColumn("departure_hour", extract_hour("CRSDepTime"))
        .withColumn("arrival_hour", extract_hour("CRSArrTime"))
    )

    # 5. Route Code Generation (ORIGIN-DEST)
    df_silver = df_silver.withColumn(
        "route_code",
        F.concat(F.col("Origin"), F.lit("-"), F.col("Dest"))
    )

    # 6. Delay Flag Implementation
    df_silver = df_silver.withColumn(
        "delay_flag",
        F.when(F.col("ArrDel15") == 1.0, F.lit(1))
        .when(F.col("ArrDel15") == 0.0, F.lit(0))
        .otherwise(
            F.when(F.col("ArrDelayMinutes") >= 15.0, F.lit(1))
            .when(F.col("ArrDelayMinutes") < 15.0, F.lit(0))
            .otherwise(F.lit(0))
        )
    )

    # Write Silver Table
    if is_save:
        print(f"[SILVER ETL] Writing to Silver table: {target_table}")
        if is_delta_available:
            try:
                (
                    df_silver.write
                    .format("delta")
                    .mode("overwrite")
                    .option("overwriteSchema", "true")
                    .saveAsTable(target_table)
                )
            except Exception as e:
                print(f"[SILVER ETL] Delta write fallback: {e}")
                try:
                    df_silver.write.format("parquet").mode("overwrite").save(target_table.replace(".", "_"))
                except Exception as ex:
                    print(f"[SILVER ETL] Local storage write skipped (Hadoop winutils missing): {ex}")
        else:
            try:
                df_silver.write.format("parquet").mode("overwrite").save(target_table.replace(".", "_"))
            except Exception as ex:
                print(f"[SILVER ETL] Local storage write skipped: {ex}")

    execution_seconds = round(time.time() - start_time, 2)

    # Calculate Silver Validation Statistics
    final_silver_count = df_silver.count()
    
    dates = df_silver.select(
        F.min("flight_date").alias("min_date"),
        F.max("flight_date").alias("max_date")
    ).collect()[0]
    
    cancelled_count = df_silver.filter(F.col("Cancelled") == 1).count()
    diverted_count = df_silver.filter(F.col("Diverted") == 1).count()
    delayed_count = df_silver.filter(F.col("delay_flag") == 1).count()
    
    delay_stats = df_silver.select(
        F.avg("ArrDelay").alias("avg_arr_delay"),
        F.avg("DepDelay").alias("avg_dep_delay")
    ).collect()[0]

    invalid_dates = df_silver.filter(F.col("flight_date").isNull()).count()
    invalid_times = df_silver.filter(F.col("CRSDepTime_formatted").isNull() & F.col("CRSDepTime").isNotNull()).count()

    metrics = {
        "pipeline_stage": "SILVER_ETL",
        "target_table": target_table,
        "bronze_input_rows": total_bronze_input_rows,
        "silver_rows": final_silver_count,
        "silver_columns": len(df_silver.columns),
        "duplicate_rows_removed": duplicate_rows_removed,
        "min_flight_date": str(dates["min_date"]),
        "max_flight_date": str(dates["max_date"]),
        "cancelled_flights": cancelled_count,
        "diverted_flights": diverted_count,
        "delayed_flights": delayed_count,
        "avg_arrival_delay_minutes": round(delay_stats["avg_arr_delay"], 2) if delay_stats["avg_arr_delay"] is not None else None,
        "avg_departure_delay_minutes": round(delay_stats["avg_dep_delay"], 2) if delay_stats["avg_dep_delay"] is not None else None,
        "invalid_dates": invalid_dates,
        "invalid_times": invalid_times,
        "execution_seconds": execution_seconds,
        "status": "SUCCESS"
    }

    print(f"[SILVER ETL] Completed in {execution_seconds}s. Final Silver Rows: {final_silver_count:,}")
    return df_silver, metrics
