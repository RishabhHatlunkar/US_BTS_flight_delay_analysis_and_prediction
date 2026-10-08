# ANTIGRAVITY.md

# Flight Delay Analytics and Prediction Using Data Warehousing and Data Mining

## 1. PROJECT OVERVIEW

This is a 3-member academic Data Warehousing and Data Mining (DWM) project.

Project Title:

Flight Delay Analytics and Prediction Using Data Warehousing and Data Mining

Primary Data Source:

U.S. Bureau of Transportation Statistics (BTS)
Reporting Carrier On-Time Performance Dataset

Official source:

https://www.transtats.bts.gov/

The project analyzes historical flight data to:

- Identify flight delay patterns
- Analyze factors responsible for delays
- Compare airlines
- Analyze airport and route performance
- Perform OLAP analysis
- Build a dimensional data warehouse
- Apply data mining and machine learning
- Predict flight delays
- Cluster airports/routes
- Build an interactive Power BI dashboard
- Generate business insights

---

# 2. PLATFORM

The project uses:

- Databricks Free Edition
- Unity Catalog
- Delta Lake / Delta tables
- Databricks notebooks
- Databricks SQL
- PySpark
- Python
- SQL
- Power BI
- scikit-learn

Databricks is the centralized data platform for the entire team.

DO NOT use PostgreSQL as the primary warehouse unless explicitly requested later.

DO NOT design the architecture around local PostgreSQL databases.

---

# 3. TEAM STRUCTURE

There are 3 team members.

## Member 1 — Data Engineering / Data Warehouse

Responsibilities:

- Data ingestion
- Bronze layer
- Silver ETL
- Data cleaning
- Data transformation
- Gold dimensional model
- Delta tables
- Data quality
- Pipeline orchestration

## Member 2 — Data Analytics / Business Intelligence

Responsibilities:

- Databricks SQL
- OLAP
- KPI development
- Statistical analysis
- Power BI
- DAX
- Dashboard
- Business insights

## Member 3 — Data Mining / Machine Learning

Responsibilities:

- Feature engineering
- Classification
- Decision Tree
- Random Forest
- Logistic Regression
- K-Means
- Model evaluation
- Optional XGBoost
- Explainability where appropriate

All team members must understand the complete architecture.

---

# 4. CENTRALIZED COLLABORATION MODEL

All 3 members work against the SAME Databricks workspace and SAME Unity Catalog data.

Do not create separate local warehouses.

Architecture:

Member 1 ─┐
Member 2 ─┼──> Databricks Workspace
Member 3 ─┘            │
                       ▼
                 Unity Catalog
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Bronze        Silver        Gold
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
                 Databricks     Python/ML      Power BI
                    SQL

The Gold layer is the project's dimensional data warehouse.

---

# 5. MEDALLION ARCHITECTURE

Use:

BRONZE
  ↓
SILVER
  ↓
GOLD

## Bronze

Purpose:

Store the raw BTS dataset in Delta format.

Characteristics:

- Minimal transformation
- Preserve source information
- Add ingestion metadata if useful
- No analytical cleaning
- No destructive modification

Example:

bronze.bts_flights

---

## Silver

Purpose:

Create a clean and validated analytical flight dataset.

Perform:

- Data type conversion
- Date conversion
- Time conversion
- NULL handling
- Duplicate detection
- Data validation
- Standardization
- Derived analytical fields

Example:

silver.flights

Silver is the primary cleaned analytical layer.

---

## Gold

Purpose:

Create the dimensional data warehouse.

Tables:

gold.dim_date
gold.dim_airline
gold.dim_airport
gold.dim_route
gold.fact_flight

The Gold layer must follow a star-schema design.

---

# 6. STORAGE

Use Unity Catalog managed storage / managed volumes where appropriate.

DO NOT use:

- DBFS root
- DBFS mounts
- Hardcoded cloud storage paths
- Local machine paths as the warehouse source

Use Unity Catalog objects.

Recommended conceptual structure:

Catalog:
flight_delay_dwm

Schemas:

bronze
silver
gold

Optional:

metadata

Example:

flight_delay_dwm.bronze.bts_flights
flight_delay_dwm.silver.flights
flight_delay_dwm.gold.dim_date
flight_delay_dwm.gold.dim_airline
flight_delay_dwm.gold.dim_airport
flight_delay_dwm.gold.dim_route
flight_delay_dwm.gold.fact_flight

---

# 7. SOURCE DATA

The initial raw BTS files are:

2024
2025

Future years such as 2026 must be configurable.

The source CSV files currently contain BTS fields including:

Year
Quarter
Month
DayofMonth
DayOfWeek
FlightDate
Reporting_Airline
DOT_ID_Reporting_Airline
IATA_CODE_Reporting_Airline
Tail_Number
Flight_Number_Reporting_Airline
OriginAirportID
OriginAirportSeqID
OriginCityMarketID
Origin
OriginCityName
OriginState
OriginStateFips
OriginStateName
OriginWac
DestAirportID
DestAirportSeqID
DestCityMarketID
Dest
DestCityName
DestState
DestStateFips
DestStateName
DestWac
CRSDepTime
DepTime
DepDelay
DepDelayMinutes
DepDel15
DepartureDelayGroups
DepTimeBlk
TaxiOut
WheelsOff
WheelsOn
TaxiIn
CRSArrTime
ArrTime
ArrDelay
ArrDelayMinutes
ArrDel15
ArrivalDelayGroups
ArrTimeBlk
Cancelled
CancellationCode
Diverted
CRSElapsedTime
ActualElapsedTime
AirTime
Flights
Distance
DistanceGroup
CarrierDelay
WeatherDelay
NASDelay
SecurityDelay
LateAircraftDelay

along with BTS diversion-related fields.

The actual downloaded schema is ALWAYS the source of truth.

Never assume a field exists without checking.

---

# 8. RAW DATA IMMUTABILITY

The original BTS CSV must never be modified.

Do NOT:

- Delete rows
- Rename columns
- Modify values
- Impute NULLs
- Add analytical columns
- Change data types in the original CSV
- Remove duplicates from the original CSV

All transformations must occur after ingestion.

---

# 9. BRONZE LAYER

Bronze should preserve the source dataset as closely as possible.

Store BTS data as Delta.

Recommended:

flight_delay_dwm.bronze.bts_flights

Add ingestion metadata only if useful:

- ingestion_timestamp
- source_file
- source_year
- source_row_hash

Do not modify source analytical values.

---

# 10. SILVER LAYER

Create:

flight_delay_dwm.silver.flights

Perform:

- Correct data types
- Date parsing
- Time parsing
- NULL handling
- Duplicate handling
- Validation
- Standardization
- Derived fields

Potential derived fields:

- flight_date
- year
- month
- quarter
- day_of_week
- departure_hour
- arrival_hour
- route_code
- delay_flag
- delay_category
- distance_category

Only create fields that have analytical value.

---

# 11. FACT TABLE GRAIN

The fact table grain is:

ONE ROW = ONE BTS FLIGHT RECORD / FLIGHT OCCURRENCE.

Do NOT aggregate flights before loading fact_flight.

Do NOT create monthly or airline-level aggregates inside fact_flight.

Aggregations belong in SQL queries, views, dashboards, or analytical tables.

---

# 12. DIMENSIONAL MODEL

The Gold layer must contain:

## gold.dim_date

Suggested columns:

date_key
full_date
day
month
month_name
quarter
year
day_of_week
day_name
week_of_year
is_weekend

date_key format:

YYYYMMDD

Example:

20240115

---

## gold.dim_airline

Suggested columns:

airline_key
reporting_airline_code
dot_airline_id
iata_airline_code

Use available BTS identifiers.

Do not invent airline names.

If a reliable airline-name mapping is later introduced, document its source.

The dimension must not contain duplicate business keys.

---

## gold.dim_airport

Suggested columns:

airport_key
airport_id
airport_seq_id
airport_code
city_market_id
city_name
state
state_fips
state_name
wac

Use ONE airport dimension.

Do NOT create:

dim_origin_airport
dim_destination_airport

The fact table will reference dim_airport twice.

This is a role-playing dimension.

---

## gold.dim_route

Suggested columns:

route_key
origin_airport_key
destination_airport_key
origin_airport_code
destination_airport_code
route_code

Example:

JFK-LAX

Routes are directional.

JFK-LAX != LAX-JFK

---

# 13. FACT TABLE

Create:

gold.fact_flight

Suggested fields:

flight_key

date_key
airline_key
origin_airport_key
destination_airport_key
route_key

flight_number
tail_number

crs_dep_time
dep_time
crs_arr_time
arr_time

dep_delay
dep_delay_minutes
dep_del15

arr_delay
arr_delay_minutes
arr_del15

departure_delay_groups
arrival_delay_groups

taxi_out
taxi_in

crs_elapsed_time
actual_elapsed_time
air_time

flights
distance
distance_group

cancelled
cancellation_code
diverted

carrier_delay
weather_delay
nas_delay
security_delay
late_aircraft_delay

wheels_off
wheels_on

source_year
source_file
source_row_hash

The final schema may be adjusted after inspecting the actual data.

---

# 14. SOURCE ROW HASH

Generate a deterministic source_row_hash.

Purpose:

- Detect exact duplicate source records
- Support idempotent loading
- Track source records

Do NOT use:

FlightDate + FlightNumber

as the only unique identifier.

Multiple valid flights can share these values.

---

# 15. IDENTITY AND IDEMPOTENCY

The pipeline must be idempotent.

Running the pipeline repeatedly against the same source data must NOT create duplicate records.

Dimensions:

Use deterministic business keys.

Fact:

Use source_row_hash or an equivalent deterministic source identifier.

The pipeline should safely support:

First run
Second run
Third run

without continuously duplicating records.

---

# 16. DATA QUALITY

Every stage must validate:

- Row count
- Column count
- Data types
- NULL percentages
- Duplicate count
- Date range
- Invalid dates
- Invalid times
- Invalid airport IDs
- Invalid airline IDs
- Foreign-key resolution
- Fact/dimension consistency

Never silently ignore validation failures.

---

# 17. NULL HANDLING

Do not blindly replace NULL with zero.

Especially for:

CarrierDelay
WeatherDelay
NASDelay
SecurityDelay
LateAircraftDelay

Distinguish:

- NULL
- zero
- not applicable

based on BTS semantics.

Document the chosen behavior.

---

# 18. CANCELLATIONS

Cancelled flights must NOT be removed.

Preserve:

Cancelled
CancellationCode

Arrival/departure fields may naturally be NULL for cancelled flights.

---

# 19. DIVERTED FLIGHTS

Diverted flights must NOT be removed.

Preserve relevant diversion information.

Do not allow diversion-related NULL values to cause unnecessary row rejection.

---

# 20. TIME HANDLING

BTS time fields can use HHMM-style numeric representations.

Examples may include:

530
1425

Create a robust conversion process.

Inspect actual data before implementing edge-case rules.

Missing time values should remain NULL when appropriate.

Do not invent timestamps.

---

# 21. DATA PROCESSING TECHNOLOGY

Prefer:

PySpark

for large-scale ingestion and transformation.

Use:

Databricks SQL

for warehouse queries and OLAP.

Use:

Python / pandas

only where appropriate, especially for small metadata/configuration operations.

Do not load the entire multi-year dataset into pandas unnecessarily.

---

# 22. FREE EDITION RESOURCE AWARENESS

This project runs on Databricks Free Edition.

Therefore:

- Avoid unnecessary compute-heavy operations.
- Avoid repeatedly scanning huge datasets.
- Avoid unnecessary table duplication.
- Prefer efficient Spark transformations.
- Use Delta tables.
- Use partitioning only when justified.
- Avoid creating dozens of unnecessary tables.
- Avoid unnecessary full-table rewrites.
- Keep development/test datasets small where possible.
- Run expensive operations deliberately.

Never design the system assuming unlimited compute.

If a workload is too large for Free Edition, document the limitation and optimize the implementation.

Do NOT silently reduce the dataset.

---

# 23. CATALOG AND SCHEMA

Use Unity Catalog.

Recommended:

Catalog:

flight_delay_dwm

Schemas:

bronze
silver
gold

The Gold warehouse must be queried using:

flight_delay_dwm.gold.<table>

Do not rely on implicit/default schemas.

---

# 24. NOTEBOOK ORGANIZATION

Recommended Databricks workspace structure:

Flight-Delay-DWM/
│
├── 01_ingestion/
│   └── 01_bts_to_bronze
│
├── 02_etl/
│   ├── 01_bronze_to_silver
│   └── 02_silver_validation
│
├── 03_warehouse/
│   ├── 01_dim_date
│   ├── 02_dim_airline
│   ├── 03_dim_airport
│   ├── 04_dim_route
│   └── 05_fact_flight
│
├── 04_olap/
│
├── 05_data_mining/
│
└── 06_power_bi/
```

The exact Databricks folder structure may be adjusted to match the existing repository.

---

# 25. SOURCE CODE ORGANIZATION

If source code is maintained in Git:

src/

├── ingestion/
├── etl/
├── warehouse/
├── validation/
├── analytics/
└── mining/

Use notebooks for interactive Databricks work and reusable Python modules for logic that benefits from testing/reuse.

---

# 26. TESTING

Implement tests for:

* Schema validation
* Date parsing
* Time parsing
* NULL handling
* Duplicate detection
* Source hash
* Route creation
* Dimension uniqueness
* Fact key resolution
* Idempotency

Use a small test dataset for unit/integration tests.

Do NOT run the full BTS dataset for every unit test.

---

# 27. ETL AUDIT

Maintain ETL metadata.

Track:

* pipeline_run_id
* start_time
* end_time
* status
* source_files
* source_rows
* bronze_rows
* silver_rows
* gold_rows
* duplicates
* rejected_rows
* execution_time
* error_message

This can be stored in:

flight_delay_dwm.metadata.etl_run_log

if a metadata schema is implemented.

---

# 28. DATA QUALITY REPORT

Every full ETL run should produce a data-quality summary.

Include:

* Source rows
* Bronze rows
* Silver rows
* Gold fact rows
* Dimension counts
* Duplicate count
* Rejected rows
* NULL statistics
* Date range
* Execution time
* Status

Do not fabricate statistics.

---

# 29. POWER BI

Power BI should consume the Gold layer.

Preferred source:

Databricks SQL Warehouse

Power BI should NOT consume the raw BTS CSV directly for the final dashboard.

Final dashboard source:

flight_delay_dwm.gold.*

---

# 30. OLAP

The Gold warehouse must support:

* Roll-up
* Drill-down
* Slice
* Dice
* Pivot

Potential analytical dimensions:

* Year
* Quarter
* Month
* Airline
* Airport
* Route
* Day of week
* Time of day

---

# 31. DATA MINING

Data mining will use the Gold/Silver data.

Classification target:

Arrival delay of 15 minutes or more.

Potential algorithms:

* Logistic Regression
* Decision Tree
* Random Forest
* XGBoost if appropriate

Clustering:

* K-Means

Potential clustering entities:

* Airports
* Routes

Do not implement these until the ETL/warehouse stages are complete.

---

# 32. GIT

Commit:

* Python source
* SQL
* Databricks notebooks/code
* Documentation
* Tests
* Configuration templates

Do NOT commit:

* Secrets
* .env
* Credentials
* Large raw CSV files
* Generated temporary files

---

# 33. SECURITY

Never hardcode:

* Passwords
* Tokens
* API keys
* Personal access tokens

Never place credentials inside notebooks committed to Git.

Use Databricks-supported authentication/secrets mechanisms where required.

---

# 34. ANTIGRAVITY DEVELOPMENT RULES

Before modifying anything:

1. Read ANTIGRAVITY.md.
2. Inspect the existing repository.
3. Inspect existing notebooks/code.
4. Reuse existing components.
5. Avoid unnecessary rewrites.
6. Do not create duplicate pipelines.
7. Do not introduce unnecessary dependencies.
8. Validate before proceeding.
9. Test after implementation.
10. Clearly report changes.

Do not silently change architecture.

---

# 35. STAGE CONTROL

Current stage:

STAGE 2 — DATABRICKS BRONZE INGESTION + ETL FOUNDATION

The current goal is:

Raw BTS CSV
↓
Unity Catalog Volume
↓
Bronze Delta Table
↓
Silver Delta Table
↓
Validation

The dimensional Gold warehouse comes AFTER the Silver layer has been validated.

Do not skip directly from CSV to fact_flight.

---

# 36. DEVELOPMENT STAGES

Stage 1:
BTS Data Fetching

Stage 2:
Databricks Bronze + Silver ETL

Stage 3:
Gold Dimensional Data Warehouse

Stage 4:
OLAP / SQL Analytics

Stage 5:
Data Mining / Machine Learning

Stage 6:
Power BI

Stage 7:
Final Integration / Documentation / Presentation

---

# 37. DEFINITION OF DONE

A stage is complete only when:

* Implementation works
* Data is validated
* Tests pass
* Documentation is updated
* No raw data is modified
* Pipeline is reproducible
* Pipeline is idempotent
* Errors are visible
* Results are documented

At the end of every stage report:

## Implementation Summary

### Files/Notebooks Created

...

### Files Modified

...

### Tables Created

...

### Rows Processed

...

### Validation

...

### Tests

...

### Problems

...

### Assumptions

...

### Next Stage

...

Do not automatically implement the next stage.

````

---

# 2. Complete Stage 2 Prompt

Since your **Stage 1 BTS fetching is already completed**, I would make Stage 2 specifically:

> **Local BTS CSV → Unity Catalog Volume → Bronze Delta → Silver Delta + validation**

I would **not create the Gold dimensions/fact yet**. That's Stage 3. This separation will make debugging much easier.

Give Antigravity this:

```text id="5p5p9r"
Read ANTIGRAVITY.md completely before making any changes.

We are now implementing:

============================================================
STAGE 2 — DATABRICKS BRONZE + SILVER ETL
============================================================

The BTS data-fetching stage has already been completed.

The raw BTS CSV files are available locally:

data/raw/bts/

Expected files include:

bts_flights_2024.csv
bts_flights_2025.csv

The objective of this stage is:

LOCAL BTS CSV
      ↓
UNITY CATALOG VOLUME
      ↓
BRONZE DELTA TABLE
      ↓
SILVER DELTA TABLE
      ↓
DATA QUALITY VALIDATION

Do NOT create the Gold dimensional warehouse yet.

Gold tables will be created in STAGE 3.

============================================================
1. FIRST INSPECT THE PROJECT
============================================================

Before writing code:

1. Read ANTIGRAVITY.md.
2. Inspect the repository.
3. Inspect the existing BTS downloader.
4. Inspect the actual CSV files.
5. Determine:
   - files available
   - years
   - row counts
   - columns
   - data types
   - nulls
   - duplicate rows
6. Check whether Databricks notebooks/code already exist.

Do not overwrite existing working components unnecessarily.

============================================================
2. DATABRICKS ARCHITECTURE
============================================================

Use:

Databricks Free Edition
+
Unity Catalog
+
Delta Lake
+
PySpark

Do NOT use:

- PostgreSQL
- DBFS root
- DBFS mounts
- hardcoded cloud storage paths

Use Unity Catalog-managed storage / volumes.

============================================================
3. CREATE / USE CATALOG
============================================================

Use the catalog:

flight_delay_dwm

If it does not exist and the current user has permission:

CREATE CATALOG IF NOT EXISTS flight_delay_dwm;

Then create schemas:

flight_delay_dwm.bronze
flight_delay_dwm.silver
flight_delay_dwm.metadata

Do not create the Gold schema in this stage unless needed as an empty namespace.

If catalog creation is restricted by the Free Edition workspace, inspect the existing Unity Catalog setup and adapt to the available catalog while documenting the decision.

Do not fabricate permissions.

============================================================
4. UNITY CATALOG VOLUME
============================================================

Create/use a managed Unity Catalog volume for raw file ingestion.

Suggested conceptual location:

flight_delay_dwm.bronze.raw_bts

If the platform requires a different supported naming/layout, use the appropriate Unity Catalog Volume structure.

The raw BTS CSV files should be uploaded/copied there.

The original local files must remain untouched.

============================================================
5. RAW FILE INGESTION
============================================================

Create a Databricks notebook:

01_ingestion/01_bts_to_bronze

The notebook must:

1. Locate the BTS CSV files.
2. Read all configured years.
3. Validate that files exist.
4. Validate CSV schema.
5. Add source metadata where appropriate.
6. Write data to Delta.

Do not use pandas for the entire multi-year dataset.

Prefer PySpark:

spark.read.csv(...)

or an equivalent Spark-based reader.

============================================================
6. BRONZE TABLE
============================================================

Create:

flight_delay_dwm.bronze.bts_flights

Use Delta format.

The Bronze table should preserve the BTS source fields as closely as possible.

Do not:

- clean values
- impute missing values
- remove duplicates
- create analytical categories
- aggregate data

Bronze is intended to preserve the source data.

============================================================
7. BRONZE METADATA
============================================================

Add only useful ingestion metadata.

Suggested:

ingestion_timestamp
source_file
source_year
source_row_hash

Do not modify BTS source columns.

Generate source_row_hash deterministically.

The hash must be reproducible.

Do not use random UUIDs for source_row_hash.

============================================================
8. SOURCE ROW HASH
============================================================

Generate a deterministic hash from the source record.

The purpose is:

- duplicate detection
- idempotent ingestion
- traceability

Do NOT use:

FlightDate + Flight_Number

as the only identifier.

Use a robust deterministic representation of the source row.

Avoid accidental hash changes caused by unstable column ordering.

Document the hashing method.

============================================================
9. BRONZE SCHEMA VALIDATION
============================================================

Before writing Bronze:

Validate that important BTS fields exist.

At minimum inspect:

FlightDate
Year
Month
DayofMonth
DayOfWeek

Reporting_Airline

OriginAirportID
Origin

DestAirportID
Dest

CRSDepTime
DepTime
DepDelay
DepDelayMinutes

CRSArrTime
ArrTime
ArrDelay
ArrDelayMinutes

Cancelled
CancellationCode
Diverted

Distance
AirTime

CarrierDelay
WeatherDelay
NASDelay
SecurityDelay
LateAircraftDelay

Do not fail because an optional field is absent unless it is required by the actual project logic.

Report schema differences.

============================================================
10. BRONZE DATA VALIDATION
============================================================

After loading Bronze calculate:

- total rows
- total columns
- distinct source files
- distinct source years
- min FlightDate
- max FlightDate
- duplicate source_row_hash count
- NULL count for major fields

Print/report the results.

Do not fabricate values.

============================================================
11. SILVER ETL
============================================================

Create:

02_etl/01_bronze_to_silver

Read:

flight_delay_dwm.bronze.bts_flights

Create:

flight_delay_dwm.silver.flights

Silver is the cleaned analytical layer.

============================================================
12. SILVER TYPE CONVERSION
============================================================

Convert fields to appropriate types.

Examples:

Year → integer
Quarter → integer
Month → integer
DayofMonth → integer
DayOfWeek → integer

FlightDate → date

Airport IDs → integer where appropriate

Delay values → numeric

Cancelled → numeric/boolean as appropriate

Diverted → numeric/boolean as appropriate

Distance → numeric

Do not make assumptions about fields with inconsistent source values.

Inspect the data before casting.

Handle malformed values safely.

============================================================
13. DATE VALIDATION
============================================================

Convert FlightDate to a proper DATE.

Validate:

- valid date
- year consistency
- month consistency
- day consistency

Calculate:

year
month
quarter
day_of_week

from FlightDate where appropriate.

Do not blindly trust duplicated date fields if inconsistencies exist.

Report inconsistencies.

============================================================
14. TIME CONVERSION
============================================================

Handle:

CRSDepTime
DepTime
CRSArrTime
ArrTime
WheelsOff
WheelsOn

BTS values can be HHMM-style integers.

Implement a robust parser.

Examples:

530 → 05:30
1425 → 14:25

Handle missing values.

Handle malformed values safely.

Do not convert invalid times into misleading timestamps.

Create useful derived fields:

departure_hour
arrival_hour

where appropriate.

Keep the original BTS time fields as well.

============================================================
15. NULL HANDLING
============================================================

Do NOT globally replace NULL with zero.

Especially:

CarrierDelay
WeatherDelay
NASDelay
SecurityDelay
LateAircraftDelay

Preserve semantic NULLs.

Document how each important field is handled.

============================================================
16. DUPLICATE HANDLING
============================================================

Detect exact duplicate source records using:

source_row_hash

Do not silently delete them.

Report:

- total rows
- duplicate rows
- rows retained

The Silver table should contain one logical record per unique source record.

Raw/Bronze data must not be destructively modified.

============================================================
17. CANCELLED FLIGHTS
============================================================

Keep cancelled flights.

Do NOT filter:

Cancelled = 1

out.

Preserve:

Cancelled
CancellationCode

NULL arrival/departure values for cancelled flights are acceptable where logically expected.

============================================================
18. DIVERTED FLIGHTS
============================================================

Keep diverted flights.

Do NOT filter them out.

Preserve:

Diverted

and relevant diversion fields.

============================================================
19. SILVER DERIVED COLUMNS
============================================================

Create only useful analytical columns.

At minimum consider:

flight_date
year
quarter
month
day_of_week
departure_hour
arrival_hour

Create:

delay_flag

Definition:

1 if ArrDel15 indicates arrival delay >= 15 minutes
0 otherwise

IMPORTANT:

Use the BTS definition/actual field semantics.

Do not infer delay_flag from an unrelated field if ArrDel15 is available.

Potentially create:

delay_category

Examples:

On Time
Minor Delay
Moderate Delay
Severe Delay

BUT only implement this if the thresholds are clearly documented.

Do not create arbitrary categories without documentation.

============================================================
20. ROUTE
============================================================

Create:

route_code

Format:

ORIGIN-DESTINATION

Example:

JFK-LAX

Routes are directional.

JFK-LAX != LAX-JFK

Do not create route surrogate keys yet.

Surrogate route keys belong to Stage 3.

============================================================
21. SILVER TABLE DESIGN
============================================================

The Silver table should contain:

- Original useful BTS fields
- Corrected data types
- Derived analytical fields
- Source metadata

Do not reduce the Silver table unnecessarily.

The Gold layer will select only required columns.

============================================================
22. SILVER VALIDATION
============================================================

After creating Silver, calculate:

- row count
- column count
- null statistics
- duplicate source_row_hash count
- min flight date
- max flight date
- cancelled count
- diverted count
- delayed flight count
- average arrival delay
- average departure delay
- invalid dates
- invalid times
- invalid airport codes/IDs where detectable

Report all results.

============================================================
23. IDEMPOTENCY
============================================================

The notebook must be safe to rerun.

If:

bronze.bts_flights

already exists:

Do not blindly append the same files again.

Use a deterministic strategy.

For example:

- MERGE
- overwrite for a controlled full rebuild
- source-file tracking
- source_row_hash-based deduplication

Choose the strategy that is safest for this project.

Document it.

The same source files should not produce duplicate records after repeated execution.

============================================================
24. FREE EDITION OPTIMIZATION
============================================================

Remember:

This project uses Databricks Free Edition.

Avoid:

- unnecessary full-table scans
- unnecessary repartitioning
- repeated full-table overwrites
- excessive caching
- unnecessary copies
- expensive operations inside loops

Use Spark efficiently.

Do not cache large datasets unless there is a demonstrated benefit.

Do not use collect() on the full dataset.

Do not convert the full dataset to pandas.

============================================================
25. ETL METADATA
============================================================

Create:

flight_delay_dwm.metadata.etl_run_log

Suggested columns:

run_id
pipeline_stage
start_time
end_time
status
source_files
source_rows
bronze_rows
silver_rows
duplicates
rejected_rows
execution_seconds
error_message

Record the Stage 2 run.

============================================================
26. DATA QUALITY REPORT
============================================================

Create a report such as:

reports/stage2/

stage2_data_quality_<timestamp>.json

or an equivalent Databricks-managed output.

Include:

Source:
...

Bronze:
...

Silver:
...

Rows:
...

Duplicates:
...

NULL statistics:
...

Date range:
...

Cancelled:
...

Diverted:
...

Delay statistics:
...

Invalid records:
...

Pipeline runtime:
...

Status:
...

Do not generate fake values.

============================================================
27. TEST DATA
============================================================

Create a small test dataset derived from the real BTS schema.

Use it for:

- schema validation
- date parsing
- time parsing
- null handling
- duplicate detection
- route generation
- delay flag
- idempotency

Do not run full BTS data for every test.

============================================================
28. DOCUMENTATION
============================================================

Update README.md with:

## Databricks Architecture

Explain:

CSV
→ Unity Catalog Volume
→ Bronze
→ Silver
→ Gold

Document:

- Databricks Free Edition
- Unity Catalog
- Delta
- Bronze
- Silver
- Gold
- Why raw data is immutable

Also document:

- catalog name
- schemas
- table names
- notebooks
- how to execute Stage 2

============================================================
29. IMPORTANT — DO NOT CREATE GOLD
============================================================

Do NOT create:

gold.dim_date
gold.dim_airline
gold.dim_airport
gold.dim_route
gold.fact_flight

in this stage.

Those belong to:

STAGE 3 — GOLD DIMENSIONAL DATA WAREHOUSE.

The objective of this stage is to make Silver reliable enough that Stage 3 can build the warehouse confidently.

============================================================
30. FINAL VALIDATION
============================================================

Before declaring Stage 2 complete:

[ ] Raw CSV unchanged
[ ] CSV schema validated
[ ] Unity Catalog used
[ ] No DBFS root/mount
[ ] Bronze Delta table created
[ ] Silver Delta table created
[ ] Date conversion validated
[ ] Time conversion validated
[ ] NULL handling implemented
[ ] Duplicate handling implemented
[ ] Source hash implemented
[ ] Cancelled flights preserved
[ ] Diverted flights preserved
[ ] Delay flag implemented
[ ] Route code implemented
[ ] Idempotency tested
[ ] ETL run logged
[ ] Data quality report generated
[ ] Tests pass
[ ] README updated

============================================================
31. FINAL REPORT
============================================================

Return:

STAGE 2 IMPLEMENTATION REPORT

Databricks Catalog:
...

Schemas:
...

Bronze Table:
...

Silver Table:
...

Source Files:
...

Source Rows:
...

Bronze Rows:
...

Silver Rows:
...

Duplicates:
...

Cancelled Flights:
...

Diverted Flights:
...

Date Range:
...

Average Arrival Delay:
...

Average Departure Delay:
...

Pipeline Runtime:
...

Tests:
...

Validation:
...

Files/Notebooks Created:
...

Files Modified:
...

Problems:
...

Assumptions:
...

Next Stage:

STAGE 3 — GOLD DIMENSIONAL DATA WAREHOUSE

STOP after Stage 2.

Do not implement Stage 3 automatically.


