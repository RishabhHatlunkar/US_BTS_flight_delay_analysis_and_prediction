"""
Test Data Fixture for Stage 2 Unit Tests
Creates small PySpark DataFrames matching real BTS schema
"""

from pyspark.sql.types import StructType, StructField, StringType


def get_sample_bts_rows():
    """
    Returns sample dictionary rows representing real BTS records,
    including valid flights, delayed flights, cancelled flights, diverted flights,
    missing values, invalid time strings, and exact duplicate rows.
    """
    rows = [
        # 1. Valid On-Time Flight
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "2024-01-08", "Reporting_Airline": "9E", "DOT_ID_Reporting_Airline": "20363",
            "IATA_CODE_Reporting_Airline": "9E", "Tail_Number": "N485PX", "Flight_Number_Reporting_Airline": "4801",
            "OriginAirportID": "12953", "OriginAirportSeqID": "1295304", "OriginCityMarketID": "31703",
            "Origin": "LGA", "OriginCityName": "New York, NY", "OriginState": "NY", "OriginStateFips": "36",
            "OriginStateName": "New York", "OriginWac": "22",
            "DestAirportID": "13871", "DestAirportSeqID": "1387102", "DestCityMarketID": "33316",
            "Dest": "OMA", "DestCityName": "Omaha, NE", "DestState": "NE", "DestStateFips": "31",
            "DestStateName": "Nebraska", "DestWac": "65",
            "CRSDepTime": "0856", "DepTime": "0851", "DepDelay": "-5.00", "DepDelayMinutes": "0.00", "DepDel15": "0.00",
            "DepartureDelayGroups": "-1", "DepTimeBlk": "0800-0859", "TaxiOut": "25.00", "WheelsOff": "0916",
            "WheelsOn": "1120", "TaxiIn": "4.00", "CRSArrTime": "1135", "ArrTime": "1124", "ArrDelay": "-11.00",
            "ArrDelayMinutes": "0.00", "ArrDel15": "0.00", "ArrivalDelayGroups": "-1", "ArrTimeBlk": "1100-1159",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "0.00",
            "CRSElapsedTime": "219.00", "ActualElapsedTime": "213.00", "AirTime": "184.00", "Flights": "1.00",
            "Distance": "1148.00", "DistanceGroup": "5",
            "CarrierDelay": None, "WeatherDelay": None, "NASDelay": None, "SecurityDelay": None, "LateAircraftDelay": None
        },
        # 2. Delayed Flight (>15 mins with delay breakdown causes)
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "2024-01-08", "Reporting_Airline": "AA", "DOT_ID_Reporting_Airline": "19805",
            "IATA_CODE_Reporting_Airline": "AA", "Tail_Number": "N104NN", "Flight_Number_Reporting_Airline": "100",
            "OriginAirportID": "12892", "OriginAirportSeqID": "1289208", "OriginCityMarketID": "32575",
            "Origin": "LAX", "OriginCityName": "Los Angeles, CA", "OriginState": "CA", "OriginStateFips": "06",
            "OriginStateName": "California", "OriginWac": "91",
            "DestAirportID": "14771", "DestAirportSeqID": "1477104", "DestCityMarketID": "32575",
            "Dest": "SFO", "DestCityName": "San Francisco, CA", "DestState": "CA", "DestStateFips": "06",
            "DestStateName": "California", "DestWac": "91",
            "CRSDepTime": "1425", "DepTime": "1450", "DepDelay": "25.00", "DepDelayMinutes": "25.00", "DepDel15": "1.00",
            "DepartureDelayGroups": "1", "DepTimeBlk": "1400-1459", "TaxiOut": "15.00", "WheelsOff": "1505",
            "WheelsOn": "1620", "TaxiIn": "5.00", "CRSArrTime": "1555", "ArrTime": "1625", "ArrDelay": "30.00",
            "ArrDelayMinutes": "30.00", "ArrDel15": "1.00", "ArrivalDelayGroups": "2", "ArrTimeBlk": "1500-1559",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "0.00",
            "CRSElapsedTime": "90.00", "ActualElapsedTime": "95.00", "AirTime": "75.00", "Flights": "1.00",
            "Distance": "337.00", "DistanceGroup": "2",
            "CarrierDelay": "20.00", "WeatherDelay": "0.00", "NASDelay": "10.00", "SecurityDelay": "0.00", "LateAircraftDelay": "0.00"
        },
        # 3. Cancelled Flight (Cancelled = 1, CancellationCode = A)
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "9", "DayOfWeek": "2",
            "FlightDate": "2024-01-09", "Reporting_Airline": "DL", "DOT_ID_Reporting_Airline": "19790",
            "IATA_CODE_Reporting_Airline": "DL", "Tail_Number": "N123DL", "Flight_Number_Reporting_Airline": "202",
            "OriginAirportID": "10397", "OriginAirportSeqID": "1039707", "OriginCityMarketID": "30397",
            "Origin": "ATL", "OriginCityName": "Atlanta, GA", "OriginState": "GA", "OriginStateFips": "13",
            "OriginStateName": "Georgia", "OriginWac": "34",
            "DestAirportID": "13930", "DestAirportSeqID": "1393007", "DestCityMarketID": "30977",
            "Dest": "ORD", "DestCityName": "Chicago, IL", "DestState": "IL", "DestStateFips": "17",
            "DestStateName": "Illinois", "DestWac": "41",
            "CRSDepTime": "1000", "DepTime": "", "DepDelay": "", "DepDelayMinutes": "", "DepDel15": "",
            "DepartureDelayGroups": "", "DepTimeBlk": "1000-1059", "TaxiOut": "", "WheelsOff": "",
            "WheelsOn": "", "TaxiIn": "", "CRSArrTime": "1130", "ArrTime": "", "ArrDelay": "",
            "ArrDelayMinutes": "", "ArrDel15": "", "ArrivalDelayGroups": "", "ArrTimeBlk": "1100-1159",
            "Cancelled": "1.00", "CancellationCode": "A", "Diverted": "0.00",
            "CRSElapsedTime": "150.00", "ActualElapsedTime": "", "AirTime": "", "Flights": "1.00",
            "Distance": "606.00", "DistanceGroup": "3",
            "CarrierDelay": None, "WeatherDelay": None, "NASDelay": None, "SecurityDelay": None, "LateAircraftDelay": None
        },
        # 4. Diverted Flight (Diverted = 1)
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "10", "DayOfWeek": "3",
            "FlightDate": "2024-01-10", "Reporting_Airline": "UA", "DOT_ID_Reporting_Airline": "19977",
            "IATA_CODE_Reporting_Airline": "UA", "Tail_Number": "N567UA", "Flight_Number_Reporting_Airline": "303",
            "OriginAirportID": "12266", "OriginAirportSeqID": "1226603", "OriginCityMarketID": "32249",
            "Origin": "IAH", "OriginCityName": "Houston, TX", "OriginState": "TX", "OriginStateFips": "48",
            "OriginStateName": "Texas", "OriginWac": "74",
            "DestAirportID": "11292", "DestAirportSeqID": "1129202", "DestCityMarketID": "30343",
            "Dest": "DEN", "DestCityName": "Denver, CO", "DestState": "CO", "DestStateFips": "08",
            "DestStateName": "Colorado", "DestWac": "82",
            "CRSDepTime": "1800", "DepTime": "1805", "DepDelay": "5.00", "DepDelayMinutes": "5.00", "DepDel15": "0.00",
            "DepartureDelayGroups": "0", "DepTimeBlk": "1800-1859", "TaxiOut": "20.00", "WheelsOff": "1825",
            "WheelsOn": "", "TaxiIn": "", "CRSArrTime": "1945", "ArrTime": "", "ArrDelay": "",
            "ArrDelayMinutes": "", "ArrDel15": "", "ArrivalDelayGroups": "", "ArrTimeBlk": "1900-1959",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "1.00",
            "CRSElapsedTime": "165.00", "ActualElapsedTime": "", "AirTime": "", "Flights": "1.00",
            "Distance": "862.00", "DistanceGroup": "4",
            "CarrierDelay": None, "WeatherDelay": None, "NASDelay": None, "SecurityDelay": None, "LateAircraftDelay": None
        },
        # 5. Exact Duplicate of Record #1 (for testing deduplication)
        {
            "Year": "2024", "Quarter": "1", "Month": "1", "DayofMonth": "8", "DayOfWeek": "1",
            "FlightDate": "2024-01-08", "Reporting_Airline": "9E", "DOT_ID_Reporting_Airline": "20363",
            "IATA_CODE_Reporting_Airline": "9E", "Tail_Number": "N485PX", "Flight_Number_Reporting_Airline": "4801",
            "OriginAirportID": "12953", "OriginAirportSeqID": "1295304", "OriginCityMarketID": "31703",
            "Origin": "LGA", "OriginCityName": "New York, NY", "OriginState": "NY", "OriginStateFips": "36",
            "OriginStateName": "New York", "OriginWac": "22",
            "DestAirportID": "13871", "DestAirportSeqID": "1387102", "DestCityMarketID": "33316",
            "Dest": "OMA", "DestCityName": "Omaha, NE", "DestState": "NE", "DestStateFips": "31",
            "DestStateName": "Nebraska", "DestWac": "65",
            "CRSDepTime": "0856", "DepTime": "0851", "DepDelay": "-5.00", "DepDelayMinutes": "0.00", "DepDel15": "0.00",
            "DepartureDelayGroups": "-1", "DepTimeBlk": "0800-0859", "TaxiOut": "25.00", "WheelsOff": "0916",
            "WheelsOn": "1120", "TaxiIn": "4.00", "CRSArrTime": "1135", "ArrTime": "1124", "ArrDelay": "-11.00",
            "ArrDelayMinutes": "0.00", "ArrDel15": "0.00", "ArrivalDelayGroups": "-1", "ArrTimeBlk": "1100-1159",
            "Cancelled": "0.00", "CancellationCode": "", "Diverted": "0.00",
            "CRSElapsedTime": "219.00", "ActualElapsedTime": "213.00", "AirTime": "184.00", "Flights": "1.00",
            "Distance": "1148.00", "DistanceGroup": "5",
            "CarrierDelay": None, "WeatherDelay": None, "NASDelay": None, "SecurityDelay": None, "LateAircraftDelay": None
        }
    ]
    return rows


def create_sample_bts_dataframe(spark):
    """Creates a PySpark DataFrame with sample BTS test rows."""
    rows = get_sample_bts_rows()
    schema = StructType([StructField(k, StringType(), True) for k in rows[0].keys()])
    return spark.createDataFrame(rows, schema=schema)
