# Flight Delay Analytics and Prediction Using Data Warehousing and Data Mining

## 1. Project Overview

This project implements an end-to-end Data Warehousing and Data Mining (DWM) pipeline for analyzing historical flight delays in the United States, discovering delay factors across airlines, airports, routes, and temporal periods, building a dimensional data warehouse with star schema in PostgreSQL, and applying machine learning models (classification and clustering) with interactive business intelligence reporting.

**Primary Data Source:** U.S. Bureau of Transportation Statistics (BTS) — *Reporting Carrier On-Time Performance (1987-present)*.

---

## 2. Stage 1 — BTS Data Ingestion

### What is BTS and Why It Is Used
The **U.S. Bureau of Transportation Statistics (BTS)** (a division of the U.S. Department of Transportation / Office of the Assistant Secretary for Research and Technology) is the official, authoritative government body publishing operational performance statistics for commercial aviation.

The **Reporting Carrier On-Time Performance** dataset is the industry gold-standard benchmark containing comprehensive flight-level records from certified U.S. air carriers accounting for at least 0.5% of domestic passenger revenues. It includes precise scheduled vs. actual departure/arrival times, delay breakdowns (carrier, weather, NAS, security, late aircraft), taxi times, cancellations, diversions, and aircraft identification.

### Key Dataset Details
- **Dataset Name:** Reporting Carrier On-Time Performance (1987-present)
- **Table ID:** `236` (`T_ONTIME_REPORTING`)
- **Official Source Portal:** [https://www.transtats.bts.gov/](https://www.transtats.bts.gov/)
- **Initial Target Years:** `2024`, `2025` (configurable)
- **Raw Data Directory:** `data/raw/bts/`
- **Output Files:**
  - `data/raw/bts/bts_flights_2024.csv`
  - `data/raw/bts/bts_flights_2025.csv`
  - `data/raw/bts/metadata.json`

---

## 3. Raw Data Immutability Guarantee

As defined in `ANTIGRAVITY.md`:
> **RAW DATA IS IMMUTABLE.**
> Under no circumstances is the raw BTS data modified, cleaned, filtered, renamed, or feature-engineered in Stage 1.

The raw CSV files in `data/raw/bts/` represent the authentic, bit-level historical flight records received from the BTS TranStats portal. All transformations, data cleaning, and feature engineering are strictly deferred to downstream ETL and transformation stages.

---

## 4. Configuration

All ingestion settings are centralized in [`config/config.yaml`](config/config.yaml).

### How to Configure Years
To add additional years (e.g. `2026` or historical years like `2023`), update the `years` list in `config/config.yaml`:

```yaml
ingestion:
  years:
    - 2024
    - 2025
    - 2026
```

No Python code modifications are necessary.

### Configurable Options
- `years`: List of target calendar years.
- `months`: Specific months (1-12) or `null` to fetch all available months for the year.
- `download_all_fields`: Boolean flag (`true` sets `chkAllVars=on` to retrieve all 110 official BTS fields).
- `output_dir`: Directory where raw datasets are stored (`data/raw/bts`).
- `output_filename_pattern`: Template string (e.g. `bts_flights_{year}.csv`).
- `metadata_file`: Path to the metadata catalog (`data/raw/bts/metadata.json`).
- `overwrite`: Set `true` to force re-download; default is `false` to avoid redundant network requests.
- `request_timeout`: HTTP request timeout in seconds (default `120`).
- `retry_count`: Maximum number of retries per request with exponential backoff (default `3`).
- `chunk_size_bytes`: Buffer chunk size for streaming downloads (default `262144` bytes).

---

## 5. How to Run the Downloader

### Prerequisites
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running Ingestion
To run ingestion for all configured years in `config/config.yaml`:
```bash
python -m src.data_ingestion.bts_downloader
```

### CLI Options
- **Specify specific years:**
  ```bash
  python src/data_ingestion/bts_downloader.py --years 2024
  ```
- **Force overwrite existing raw files:**
  ```bash
  python src/data_ingestion/bts_downloader.py --years 2024 --overwrite
  ```
- **Validate existing downloaded files without re-downloading:**
  ```bash
  python src/data_ingestion/bts_downloader.py --validate-only
  ```
- **Custom configuration file:**
  ```bash
  python src/data_ingestion/bts_downloader.py --config path/to/custom_config.yaml
  ```

---

## 6. Validation and Quality Assurance

After each year is retrieved, the validation pipeline automatically verifies:
1. **File Existence & Non-Emptiness:** Ensures the output CSV exists and contains non-zero byte size.
2. **Streaming Row & Column Counts:** Computes the exact number of records and columns.
3. **Analytical Schema Inspection:** Verifies the presence of required analytical fields across dimensions:
   - **Time:** `Year`, `Quarter`, `Month`, `DayofMonth`, `DayOfWeek`, `FlightDate`
   - **Airline:** `Reporting_Airline`, `DOT_ID_Reporting_Airline`, `IATA_CODE_Reporting_Airline`, `Flight_Number_Reporting_Airline`, `Tail_Number`
   - **Origin:** `OriginAirportID`, `OriginAirportSeqID`, `Origin`, `OriginCityName`, `OriginState`, `OriginStateName`
   - **Destination:** `DestAirportID`, `DestAirportSeqID`, `Dest`, `DestCityName`, `DestState`, `DestStateName`
   - **Departure:** `CRSDepTime`, `DepTime`, `DepDelay`, `DepDelayMinutes`, `DepDel15`, `DepartureDelayGroups`, `DepTimeBlk`, `TaxiOut`
   - **Arrival:** `CRSArrTime`, `ArrTime`, `ArrDelay`, `ArrDelayMinutes`, `ArrDel15`, `ArrivalDelayGroups`, `ArrTimeBlk`, `TaxiIn`
   - **Cancellation & Diversion:** `Cancelled`, `CancellationCode`, `Diverted`
   - **Flight Metrics:** `CRSElapsedTime`, `ActualElapsedTime`, `AirTime`, `Distance`, `DistanceGroup`
   - **Delay Causes:** `CarrierDelay`, `WeatherDelay`, `NASDelay`, `SecurityDelay`, `LateAircraftDelay`
4. **Cryptographic Integrity:** Generates a SHA-256 hash for every raw dataset file to guarantee integrity and immutability tracking.

---

## 7. Metadata and Logging

- **Metadata Catalog:** [`data/raw/bts/metadata.json`](data/raw/bts/metadata.json) records the source, dataset name, download timestamp, row counts, column counts, file size, SHA-256 hash, validation status, and error logs.
- **Log File:** [`logs/bts_download.log`](logs/bts_download.log) records timestamped execution traces, HTTP request headers, streaming chunk download progress, retry attempts, and validation outputs.

---

## 8. Running Automated Tests

Run the unit test suite with pytest:
```bash
pytest -v tests/
```
All tests execute against local mock fixtures and sample schemas without requiring multi-gigabyte network downloads during CI runs.
