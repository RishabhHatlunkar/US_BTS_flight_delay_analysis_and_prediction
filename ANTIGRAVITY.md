# ANTIGRAVITY.md

# Flight Delay Analytics and Prediction Using Data Warehousing and Data Mining

## 1. PROJECT OVERVIEW

This is a 3-member academic Data Warehousing and Data Mining (DWM) project.

Project Title:

Flight Delay Analytics and Prediction Using Data Warehousing and Data Mining

Project Objective:

Analyze historical flight data to:
- Identify flight delay patterns
- Analyze factors responsible for delays
- Discover relationships between airlines, airports, routes, time periods and delays
- Build a dimensional data warehouse
- Perform OLAP analysis
- Apply data mining and machine learning techniques
- Predict whether a flight will be delayed
- Cluster airports/routes based on delay behavior
- Present insights through an interactive Power BI dashboard

Primary Data Source:

U.S. Bureau of Transportation Statistics (BTS)
Reporting Carrier On-Time Performance Dataset

Official Source:
https://www.transtats.bts.gov/

The BTS dataset is the authoritative primary source for this project.

---

# 2. TEAM STRUCTURE

There are 3 team members.

## Member 1 — Data Engineering / Data Warehouse

Responsibilities:
- Data acquisition
- Raw data management
- Data profiling
- ETL
- Data cleaning
- Data transformation
- PostgreSQL
- Star schema
- Fact and dimension tables
- SQL queries

## Member 2 — Data Analytics / Business Intelligence

Responsibilities:
- Exploratory Data Analysis
- Statistical analysis
- OLAP operations
- KPI development
- Power BI
- DAX
- Dashboard design
- Business insights

## Member 3 — Data Mining / Machine Learning

Responsibilities:
- Feature engineering
- Classification
- Decision Tree
- Random Forest
- Logistic Regression
- Clustering
- K-Means
- Optional association-rule mining
- Model evaluation
- Explainability / SHAP where appropriate

IMPORTANT:

Although responsibilities are divided, all team members must understand the complete project pipeline.

---

# 3. COMPLETE PROJECT ARCHITECTURE

The intended architecture is:

BTS Flight Data
        ↓
Data Ingestion
        ↓
Raw Data
        ↓
Data Profiling
        ↓
ETL / Data Cleaning
        ↓
Data Transformation
        ↓
PostgreSQL Data Warehouse
        ↓
Star Schema
        ↓
OLAP / SQL Analysis
        ↓
Data Mining / Machine Learning
        ↓
Power BI
        ↓
Business Insights

Optional:

BTS Flight Data
        +
Weather Data
        ↓
Enriched Dataset

Weather integration must remain optional unless explicitly requested.

---

# 4. DEVELOPMENT STAGES

The project must be developed in the following order.

## Stage 1 — Data Ingestion

Fetch historical flight data from official BTS.

Initial target years:
- 2024
- 2025

The implementation must allow adding:
- 2026
- Other years

without major code changes.

---

## Stage 2 — Data Profiling

Analyze:
- Number of rows
- Number of columns
- Data types
- Missing values
- Duplicate records
- Unique values
- Outliers
- Invalid values
- Distribution of delay variables
- Cancellation and diversion rates

No destructive modification of raw data.

---

## Stage 3 — ETL / Data Cleaning

Perform:
- Missing-value handling
- Data-type correction
- Duplicate handling
- Invalid-record handling
- Date/time normalization
- Categorical normalization
- Outlier analysis
- Delay-related transformations

Raw data must NEVER be modified.

---

## Stage 4 — Data Transformation

Create analytical features such as:

- FlightDate
- Year
- Month
- Quarter
- DayOfWeek
- DepartureHour
- ArrivalHour
- Route
- DelayFlag
- DelayCategory
- DistanceCategory
- FlightDurationCategory

The exact feature list should be determined after profiling the dataset.

---

## Stage 5 — Data Warehouse

Use PostgreSQL.

Implement a star schema containing:

### FactFlight

Potential measures:
- DepDelay
- ArrDelay
- Distance
- AirTime
- TaxiOut
- TaxiIn
- ActualElapsedTime
- ScheduledElapsedTime

### DimDate

Potential attributes:
- DateKey
- FullDate
- Day
- Month
- MonthName
- Quarter
- Year
- DayOfWeek
- DayName

### DimAirline

Potential attributes:
- AirlineKey
- ReportingAirline
- AirlineCode

### DimAirport

Potential attributes:
- AirportKey
- AirportCode
- AirportID
- City
- State
- AirportName where available

### DimRoute

Potential attributes:
- RouteKey
- OriginAirport
- DestinationAirport
- Route

### DimWeather

Optional.

Only implement if reliable weather data is integrated.

---

# 6. DATA MINING REQUIREMENTS

At minimum, implement:

## Classification

Target:

Arrival delay of 15 minutes or more.

Use:

- Logistic Regression
- Decision Tree
- Random Forest

Optionally:
- XGBoost

Compare models using appropriate metrics.

Metrics may include:
- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix

Do NOT rely only on accuracy.

---

## Clustering

Use K-Means to identify groups of:

- Airports
or
- Routes

based on metrics such as:

- Average delay
- Delay rate
- Cancellation rate
- Flight volume
- Average departure delay

Determine the appropriate number of clusters using:
- Elbow method
- Silhouette score

---

## Optional Association Mining

If the dataset structure supports meaningful categorical transactions, consider:

- Apriori
- FP-Growth

This is optional and should NOT be forced into the project merely to increase the number of algorithms.

---

# 7. POWER BI REQUIREMENTS

Create an interactive dashboard containing approximately:

## Page 1 — Executive Overview

KPIs:
- Total Flights
- Delayed Flights
- Delay Rate
- Average Arrival Delay
- Average Departure Delay
- Cancellation Rate

Visuals:
- Delay trend
- Airline comparison
- Monthly performance
- Top delayed airports

---

## Page 2 — Airport & Route Analysis

Show:
- Origin airport performance
- Destination airport performance
- Worst routes
- Best routes
- Delay rate by airport
- Route-level delay trends

---

## Page 3 — Delay Analysis

Analyze:
- Carrier delays
- Weather delays
- NAS delays
- Security delays
- Late aircraft delays

Also analyze delay behavior by:
- Month
- Day of week
- Time of day
- Airline

---

## Page 4 — Prediction / Data Mining

Show:
- Model performance
- Confusion matrix
- Important features
- Predicted delay probability where appropriate
- Cluster analysis
- Cluster characteristics

---

# 8. IMPORTANT BTS VARIABLES

Potentially useful BTS columns include:

Time:
- Year
- Quarter
- Month
- DayofMonth
- DayOfWeek
- FlightDate

Airline:
- Reporting_Airline
- DOT_ID_Reporting_Airline
- IATA_CODE_Reporting_Airline
- Flight_Number_Reporting_Airline
- Tail_Number

Origin:
- OriginAirportID
- OriginAirportSeqID
- Origin
- OriginCityName
- OriginState
- OriginStateName

Destination:
- DestAirportID
- DestAirportSeqID
- Dest
- DestCityName
- DestState
- DestStateName

Departure:
- CRSDepTime
- DepTime
- DepDelay
- DepDelayMinutes
- DepDel15
- DepartureDelayGroups
- DepTimeBlk
- TaxiOut

Arrival:
- CRSArrTime
- ArrTime
- ArrDelay
- ArrDelayMinutes
- ArrDel15
- ArrivalDelayGroups
- ArrTimeBlk
- TaxiIn

Cancellation:
- Cancelled
- CancellationCode
- Diverted

Flight:
- CRSElapsedTime
- ActualElapsedTime
- AirTime
- Distance
- DistanceGroup

Delay causes:
- CarrierDelay
- WeatherDelay
- NASDelay
- SecurityDelay
- LateAircraftDelay

Do not assume every field is necessary.

First inspect the actual downloaded dataset and determine the final required columns.

---

# 9. RAW DATA RULE

RAW DATA IS IMMUTABLE.

Never:
- Clean raw CSV files
- Rename columns inside raw files
- Delete rows from raw files
- Add derived columns
- Replace missing values
- Modify original BTS values

Instead:

Raw
 ↓
Staging
 ↓
Cleaned
 ↓
Warehouse

Keep every transformation reproducible.

---

# 10. PROJECT DIRECTORY STRUCTURE

Use a clean structure similar to:

flight-delay-dwm/
│
├── ANTIGRAVITY.md
├── README.md
├── requirements.txt
├── .gitignore
│
├── config/
│   └── config.yaml
│
├── data/
│   ├── raw/
│   │   └── bts/
│   ├── staging/
│   ├── processed/
│   └── external/
│
├── src/
│   ├── data_ingestion/
│   ├── profiling/
│   ├── etl/
│   ├── transformation/
│   ├── warehouse/
│   ├── olap/
│   ├── mining/
│   └── visualization/
│
├── sql/
│   ├── schema/
│   ├── staging/
│   ├── dimensions/
│   ├── facts/
│   └── analytics/
│
├── notebooks/
│
├── tests/
│
├── logs/
│
└── docs/
    ├── architecture/
    ├── data_dictionary/
    └── reports/

Do not create unnecessary folders.

---

# 11. TECHNOLOGY STACK

Primary:

Python
Pandas
NumPy
PostgreSQL
SQL
pgAdmin
Power BI
DAX
scikit-learn

Optional:

XGBoost
mlxtend
SHAP
Matplotlib
Seaborn

Use additional libraries only when they provide a clear project benefit.

---

# 12. CODING PRINCIPLES

Write production-quality, understandable academic project code.

Requirements:

- Modular Python code
- Functions with clear responsibilities
- Type hints where useful
- Meaningful variable names
- Docstrings for important functions
- Error handling
- Logging
- Configuration instead of hardcoded values
- Reproducibility
- Avoid unnecessary global variables
- Avoid duplicated code
- Avoid magic numbers
- Validate inputs and outputs

Do not create huge monolithic scripts.

---

# 13. CONFIGURATION

Do not hardcode:

- Dataset years
- Paths
- Database credentials
- Retry counts
- Timeouts
- Model parameters

Use configuration files or environment variables.

Never commit:
- Passwords
- API keys
- Database credentials
- Secrets

---

# 14. DATA QUALITY

Every major stage must validate its output.

Validation should include where applicable:

- Row count
- Column count
- Expected columns
- Data types
- Null percentage
- Duplicate count
- Date range
- Invalid values
- Referential integrity
- Primary-key uniqueness
- Foreign-key integrity

If a validation fails, do not silently continue.

---

# 15. REPRODUCIBILITY

A fresh developer should be able to clone the project and understand:

1. Where data comes from
2. How data is downloaded
3. How data is cleaned
4. How the warehouse is created
5. How analysis is performed
6. How models are trained
7. How Power BI connects to the warehouse

Every important stage should have:
- README documentation
- Reproducible scripts
- Configuration
- Logs
- Validation

---

# 16. GIT RULES

Do not commit:

- Raw BTS datasets
- Large generated datasets
- Database dumps
- Logs
- Virtual environments
- Secrets
- Temporary files

Commit:

- Source code
- SQL
- Configuration templates
- Tests
- Documentation
- Notebooks when useful
- Requirements

---

# 17. ANTIGRAVITY BEHAVIOR

Before implementing a feature:

1. Inspect the existing project structure.
2. Read ANTIGRAVITY.md.
3. Inspect relevant existing files.
4. Reuse existing utilities where possible.
5. Do not unnecessarily rewrite working code.
6. Do not introduce dependencies without justification.
7. Implement the requested stage only.
8. Run appropriate tests.
9. Validate generated outputs.
10. Report exactly what changed.

Never silently make architectural changes.

If a requirement is ambiguous:

- Prefer the existing project architecture.
- Make the smallest reasonable assumption.
- Document the assumption.
- Do not invent external APIs, URLs, dataset schemas, or credentials.

---

# 18. BTS DATA INGESTION RULE

The official BTS source must be inspected before implementation.

Do NOT invent a static CSV download URL.

If BTS uses a form-based download mechanism:

1. Inspect how the official download process works.
2. Determine the reproducible programmatic approach.
3. Implement the downloader based on the actual mechanism.
4. Validate the downloaded data.
5. Record source metadata.

The source should remain configurable.

---

# 19. CURRENT DEVELOPMENT STAGE

Current stage:

STAGE 1 — DATA INGESTION

The immediate goal is:

BTS
 ↓
Download
 ↓
Raw CSV
 ↓
Validation
 ↓
Metadata
 ↓
Logging

Do NOT implement:
- ETL
- Machine learning
- Power BI
- PostgreSQL warehouse
- OLAP

until explicitly requested.

---

# 20. DEFINITION OF DONE

A stage is complete only when:

- Code is implemented
- Code runs successfully
- Output exists
- Output is validated
- Tests pass where applicable
- Errors are handled
- Documentation is updated
- No raw data is accidentally modified
- Changes are clearly reported

At the end of each stage, provide:

## Implementation Summary

### Files Created
...

### Files Modified
...

### Commands Executed
...

### Validation
...

### Tests
...

### Output
...

### Problems / Assumptions
...

### Next Recommended Stage
...
