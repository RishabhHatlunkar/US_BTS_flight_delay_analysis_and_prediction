"""
PySpark Gold Dimensional Warehouse Module
Stage 3 - Silver Delta Table -> Gold Star Schema (dim_date, dim_airline, dim_airport, dim_route, fact_flight)
"""

import time
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DateType, DoubleType
)


def safe_cast_int_field(col_expr):
    """Safely converts string or numeric column to Integer, returning NULL for empty strings."""
    str_col = col_expr.cast("string")
    return F.when((str_col == "") | str_col.isNull(), F.lit(None)).otherwise(col_expr.cast("double").cast("int"))


def build_dim_date(spark: SparkSession, min_date_str="2024-01-01", max_date_str="2025-12-31"):
    """
    Generates a full calendar dimension DataFrame for all dates between min_date and max_date.
    Format: date_key = YYYYMMDD (Integer)
    """
    print(f"[GOLD ETL] Building dim_date from {min_date_str} to {max_date_str}")
    
    df_date_seq = spark.sql(f"""
        SELECT explode(sequence(to_date('{min_date_str}'), to_date('{max_date_str}'), interval 1 day)) as full_date
    """)
    
    df_dim_date = (
        df_date_seq
        .withColumn("date_key", F.date_format(F.col("full_date"), "yyyyMMdd").cast(IntegerType()))
        .withColumn("year", F.year(F.col("full_date")))
        .withColumn("quarter", F.quarter(F.col("full_date")))
        .withColumn("month", F.month(F.col("full_date")))
        .withColumn("month_name", F.date_format(F.col("full_date"), "MMMM"))
        .withColumn("day", F.dayofmonth(F.col("full_date")))
        .withColumn("day_of_week", F.dayofweek(F.col("full_date")))
        .withColumn("day_name", F.date_format(F.col("full_date"), "EEEE"))
        .withColumn("week_of_year", F.weekofyear(F.col("full_date")))
        .withColumn(
            "is_weekend",
            F.when(F.dayofweek(F.col("full_date")).isin([1, 7]), F.lit(1)).otherwise(F.lit(0))
        )
        .select(
            "date_key", "full_date", "year", "quarter", "month", "month_name",
            "day", "day_of_week", "day_name", "week_of_year", "is_weekend"
        )
    )
    
    return df_dim_date


def build_dim_airline(spark: SparkSession, df_silver):
    """
    Extracts distinct airlines and assigns surrogate airline_key.
    """
    print("[GOLD ETL] Building dim_airline")
    
    df_airlines = (
        df_silver
        .select(
            F.col("Reporting_Airline").alias("reporting_airline_code"),
            safe_cast_int_field(F.col("DOT_ID_Reporting_Airline")).alias("dot_airline_id"),
            F.col("IATA_CODE_Reporting_Airline").alias("iata_airline_code")
        )
        .filter(F.col("reporting_airline_code").isNotNull() & (F.col("reporting_airline_code") != ""))
        .distinct()
    )
    
    w = Window.orderBy("reporting_airline_code")
    df_dim_airline = (
        df_airlines
        .withColumn("airline_key", F.row_number().over(w).cast(IntegerType()))
        .select("airline_key", "reporting_airline_code", "dot_airline_id", "iata_airline_code")
    )
    
    return df_dim_airline


def build_dim_airport(spark: SparkSession, df_silver):
    """
    Extracts distinct airports from both Origin and Destination fields (Role-Playing Dimension).
    Assigns surrogate airport_key.
    """
    print("[GOLD ETL] Building dim_airport (Role-Playing Dimension)")
    
    df_origin = (
        df_silver
        .select(
            safe_cast_int_field(F.col("OriginAirportID")).alias("airport_id"),
            safe_cast_int_field(F.col("OriginAirportSeqID")).alias("airport_seq_id"),
            F.col("Origin").alias("airport_code"),
            safe_cast_int_field(F.col("OriginCityMarketID")).alias("city_market_id"),
            F.col("OriginCityName").alias("city_name"),
            F.col("OriginState").alias("state"),
            safe_cast_int_field(F.col("OriginStateFips")).alias("state_fips"),
            F.col("OriginStateName").alias("state_name"),
            safe_cast_int_field(F.col("OriginWac")).alias("wac")
        )
        .filter(F.col("airport_id").isNotNull())
    )
    
    df_dest = (
        df_silver
        .select(
            safe_cast_int_field(F.col("DestAirportID")).alias("airport_id"),
            safe_cast_int_field(F.col("DestAirportSeqID")).alias("airport_seq_id"),
            F.col("Dest").alias("airport_code"),
            safe_cast_int_field(F.col("DestCityMarketID")).alias("city_market_id"),
            F.col("DestCityName").alias("city_name"),
            F.col("DestState").alias("state"),
            safe_cast_int_field(F.col("DestStateFips")).alias("state_fips"),
            F.col("DestStateName").alias("state_name"),
            safe_cast_int_field(F.col("DestWac")).alias("wac")
        )
        .filter(F.col("airport_id").isNotNull())
    )
    
    df_airports_union = df_origin.union(df_dest).distinct()
    
    w = Window.orderBy("airport_id")
    df_dim_airport = (
        df_airports_union
        .withColumn("airport_key", F.row_number().over(w).cast(IntegerType()))
        .select(
            "airport_key", "airport_id", "airport_seq_id", "airport_code",
            "city_market_id", "city_name", "state", "state_fips", "state_name", "wac"
        )
    )
    
    return df_dim_airport


def build_dim_route(spark: SparkSession, df_silver, df_dim_airport):
    """
    Extracts distinct directional routes (Origin-Dest) and links to airport keys.
    """
    print("[GOLD ETL] Building dim_route")
    
    df_routes = (
        df_silver
        .select(
            F.col("route_code"),
            F.col("Origin").alias("origin_airport_code"),
            F.col("Dest").alias("destination_airport_code"),
            safe_cast_int_field(F.col("OriginAirportID")).alias("origin_airport_id"),
            safe_cast_int_field(F.col("DestAirportID")).alias("destination_airport_id")
        )
        .filter(F.col("route_code").isNotNull() & (F.col("route_code") != ""))
        .distinct()
    )
    
    w = Window.orderBy("route_code")
    df_dim_route = (
        df_routes
        .withColumn("route_key", F.row_number().over(w).cast(IntegerType()))
        .select(
            "route_key", "route_code", "origin_airport_code", "destination_airport_code",
            "origin_airport_id", "destination_airport_id"
        )
    )
    
    return df_dim_route


def build_fact_flight(spark: SparkSession, df_silver, df_dim_date, df_dim_airline, df_dim_airport, df_dim_route):
    """
    Constructs the fact_flight table by joining Silver records with dimension tables
    to retrieve foreign keys. Preserves all measures, delay causes, and source lineage.
    """
    print("[GOLD ETL] Building fact_flight")
    
    # Pre-cast join keys in Silver to Integer safely
    df_silver_prepared = (
        df_silver
        .withColumn("orig_ap_id_clean", safe_cast_int_field(F.col("OriginAirportID")))
        .withColumn("dest_ap_id_clean", safe_cast_int_field(F.col("DestAirportID")))
    )

    # 1. Join Date Dimension
    df_fact = (
        df_silver_prepared
        .join(
            df_dim_date.select("date_key", "full_date"),
            df_silver_prepared.flight_date == df_dim_date.full_date,
            "left"
        )
    )
    
    # 2. Join Airline Dimension
    df_fact = (
        df_fact
        .join(
            df_dim_airline.select("airline_key", "reporting_airline_code"),
            df_fact.Reporting_Airline == df_dim_airline.reporting_airline_code,
            "left"
        )
    )
    
    # 3. Join Origin Airport Dimension (Role-Playing)
    df_origin_airport = df_dim_airport.select(
        F.col("airport_key").alias("origin_airport_key"),
        F.col("airport_id").alias("orig_ap_id")
    )
    df_fact = (
        df_fact
        .join(
            df_origin_airport,
            df_fact.orig_ap_id_clean == df_origin_airport.orig_ap_id,
            "left"
        )
    )
    
    # 4. Join Destination Airport Dimension (Role-Playing)
    df_dest_airport = df_dim_airport.select(
        F.col("airport_key").alias("destination_airport_key"),
        F.col("airport_id").alias("dest_ap_id")
    )
    df_fact = (
        df_fact
        .join(
            df_dest_airport,
            df_fact.dest_ap_id_clean == df_dest_airport.dest_ap_id,
            "left"
        )
    )
    
    # 5. Join Route Dimension
    df_fact = (
        df_fact
        .join(
            df_dim_route.select("route_key", "route_code"),
            df_fact.route_code == df_dim_route.route_code,
            "left"
        )
    )
    
    # Select final fact columns matching Gold schema
    df_fact_final = (
        df_fact
        .withColumn("flight_key", F.col("source_row_hash"))
        .select(
            "flight_key",
            "date_key",
            "airline_key",
            "origin_airport_key",
            "destination_airport_key",
            "route_key",
            safe_cast_int_field(F.col("Flight_Number_Reporting_Airline")).alias("flight_number"),
            F.col("Tail_Number").alias("tail_number"),
            safe_cast_int_field(F.col("CRSDepTime")).alias("crs_dep_time"),
            safe_cast_int_field(F.col("DepTime")).alias("dep_time"),
            safe_cast_int_field(F.col("CRSArrTime")).alias("crs_arr_time"),
            safe_cast_int_field(F.col("ArrTime")).alias("arr_time"),
            "departure_hour",
            "arrival_hour",
            safe_cast_int_field(F.col("WheelsOff")).alias("wheels_off"),
            safe_cast_int_field(F.col("WheelsOn")).alias("wheels_on"),
            F.col("DepDelay").alias("dep_delay"),
            F.col("DepDelayMinutes").alias("dep_delay_minutes"),
            F.col("DepDel15").alias("dep_del15"),
            F.col("ArrDelay").alias("arr_delay"),
            F.col("ArrDelayMinutes").alias("arr_delay_minutes"),
            F.col("ArrDel15").alias("arr_del15"),
            "delay_flag",
            F.col("DepartureDelayGroups").alias("departure_delay_groups"),
            F.col("ArrivalDelayGroups").alias("arrival_delay_groups"),
            F.col("TaxiOut").alias("taxi_out"),
            F.col("TaxiIn").alias("taxi_in"),
            F.col("CRSElapsedTime").alias("crs_elapsed_time"),
            F.col("ActualElapsedTime").alias("actual_elapsed_time"),
            F.col("AirTime").alias("air_time"),
            safe_cast_int_field(F.col("Flights")).alias("flights"),
            F.col("Distance").alias("distance"),
            safe_cast_int_field(F.col("DistanceGroup")).alias("distance_group"),
            safe_cast_int_field(F.col("Cancelled")).alias("cancelled"),
            F.col("CancellationCode").alias("cancellation_code"),
            safe_cast_int_field(F.col("Diverted")).alias("diverted"),
            F.col("CarrierDelay").alias("carrier_delay"),
            F.col("WeatherDelay").alias("weather_delay"),
            F.col("NASDelay").alias("nas_delay"),
            F.col("SecurityDelay").alias("security_delay"),
            F.col("LateAircraftDelay").alias("late_aircraft_delay"),
            safe_cast_int_field(F.col("source_year")).alias("source_year"),
            F.col("source_file"),
            "source_row_hash"
        )
    )
    
    return df_fact_final


def transform_silver_to_gold(spark: SparkSession, source_silver_table="flight_delay_dwm.silver.flights", catalog="flight_delay_dwm", is_delta_available=True, is_save=True):
    """
    Transforms Silver analytical data into Gold Star Schema (dim_date, dim_airline, dim_airport, dim_route, fact_flight).
    """
    start_time = time.time()
    
    if isinstance(source_silver_table, str):
        print(f"[GOLD ETL] Reading Silver table: {source_silver_table}")
        df_silver = spark.table(source_silver_table)
    else:
        df_silver = source_silver_table

    silver_row_count = df_silver.count()
    print(f"[GOLD ETL] Processing {silver_row_count:,} Silver records for Gold Star Schema.")
    
    # 1. Build Dimensions
    dates = df_silver.select(
        F.min("flight_date").alias("min_d"),
        F.max("flight_date").alias("max_d")
    ).collect()[0]
    
    min_date_str = str(dates["min_d"]) if dates["min_d"] is not None else "2024-01-01"
    max_date_str = str(dates["max_d"]) if dates["max_d"] is not None else "2025-12-31"

    df_dim_date = build_dim_date(spark, min_date_str, max_date_str)
    df_dim_airline = build_dim_airline(spark, df_silver)
    df_dim_airport = build_dim_airport(spark, df_silver)
    df_dim_route = build_dim_route(spark, df_silver, df_dim_airport)
    
    # 2. Build Fact
    df_fact_flight = build_fact_flight(spark, df_silver, df_dim_date, df_dim_airline, df_dim_airport, df_dim_route)

    # 3. Write Gold Tables
    tables_written = {}
    gold_tables = {
        "dim_date": (df_dim_date, f"{catalog}.gold.dim_date"),
        "dim_airline": (df_dim_airline, f"{catalog}.gold.dim_airline"),
        "dim_airport": (df_dim_airport, f"{catalog}.gold.dim_airport"),
        "dim_route": (df_dim_route, f"{catalog}.gold.dim_route"),
        "fact_flight": (df_fact_flight, f"{catalog}.gold.fact_flight")
    }

    for t_name, (df_tbl, full_t_name) in gold_tables.items():
        cnt = df_tbl.count()
        tables_written[t_name] = {"table_name": full_t_name, "row_count": cnt}
        if is_save:
            print(f"[GOLD ETL] Writing Gold table {full_t_name} ({cnt:,} rows)")
            if is_delta_available:
                try:
                    df_tbl.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(full_t_name)
                except Exception as e:
                    print(f"[GOLD ETL] Delta write fallback for {full_t_name}: {e}")
                    try:
                        df_tbl.write.format("parquet").mode("overwrite").save(full_t_name.replace(".", "_"))
                    except Exception as ex:
                        print(f"[GOLD ETL] Local write skipped: {ex}")
            else:
                try:
                    df_tbl.write.format("parquet").mode("overwrite").save(full_t_name.replace(".", "_"))
                except Exception as ex:
                    print(f"[GOLD ETL] Local write skipped: {ex}")

    execution_seconds = round(time.time() - start_time, 2)

    # 4. Foreign Key Integrity Check
    fk_unresolved = df_fact_flight.filter(
        F.col("date_key").isNull() |
        F.col("airline_key").isNull() |
        F.col("origin_airport_key").isNull() |
        F.col("destination_airport_key").isNull() |
        F.col("route_key").isNull()
    ).count()

    metrics = {
        "pipeline_stage": "GOLD_ETL",
        "catalog": catalog,
        "silver_input_rows": silver_row_count,
        "fact_flight_rows": tables_written["fact_flight"]["row_count"],
        "dim_date_rows": tables_written["dim_date"]["row_count"],
        "dim_airline_rows": tables_written["dim_airline"]["row_count"],
        "dim_airport_rows": tables_written["dim_airport"]["row_count"],
        "dim_route_rows": tables_written["dim_route"]["row_count"],
        "unresolved_foreign_keys": fk_unresolved,
        "foreign_key_integrity_passed": fk_unresolved == 0,
        "execution_seconds": execution_seconds,
        "status": "SUCCESS"
    }

    print(f"[GOLD ETL] Completed in {execution_seconds}s. Foreign Key Integrity: {'PASSED' if fk_unresolved==0 else 'FAILED'}")
    return {
        "dim_date": df_dim_date,
        "dim_airline": df_dim_airline,
        "dim_airport": df_dim_airport,
        "dim_route": df_dim_route,
        "fact_flight": df_fact_flight
    }, metrics
