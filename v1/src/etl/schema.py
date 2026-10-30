"""
BTS Schema Validation & Definition Module
Stage 2 - Databricks Bronze & Silver ETL
"""

REQUIRED_BTS_FIELDS = [
    "FlightDate", "Year", "Quarter", "Month", "DayofMonth", "DayOfWeek",
    "Reporting_Airline", "DOT_ID_Reporting_Airline", "IATA_CODE_Reporting_Airline",
    "Flight_Number_Reporting_Airline", "Tail_Number",
    "OriginAirportID", "OriginAirportSeqID", "Origin", "OriginCityName", "OriginState", "OriginStateName",
    "DestAirportID", "DestAirportSeqID", "Dest", "DestCityName", "DestState", "DestStateName",
    "CRSDepTime", "DepTime", "DepDelay", "DepDelayMinutes", "DepDel15", "DepartureDelayGroups", "DepTimeBlk", "TaxiOut",
    "CRSArrTime", "ArrTime", "ArrDelay", "ArrDelayMinutes", "ArrDel15", "ArrivalDelayGroups", "ArrTimeBlk", "TaxiIn",
    "Cancelled", "CancellationCode", "Diverted",
    "CRSElapsedTime", "ActualElapsedTime", "AirTime", "Distance", "DistanceGroup",
    "CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay"
]

def validate_schema(existing_columns, required_fields=None):
    """
    Validates that existing columns contain all required BTS fields.
    Returns dict with status, missing_fields, and present_count.
    """
    if required_fields is None:
        required_fields = REQUIRED_BTS_FIELDS
    
    existing_set = set(existing_columns)
    missing = [f for f in required_fields if f not in existing_set]
    
    return {
        "valid": len(missing) == 0,
        "missing_fields": missing,
        "total_required": len(required_fields),
        "present_count": len(required_fields) - len(missing)
    }
