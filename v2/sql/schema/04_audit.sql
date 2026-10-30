-- ==============================================================================
-- V2 SQLite Audit & Observability Schema
-- Tracks pipeline executions, stage durations, and row counts
-- ==============================================================================

CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage TEXT NOT NULL,
    start_timestamp TEXT NOT NULL,
    end_timestamp TEXT NOT NULL,
    status TEXT NOT NULL,
    source_files TEXT,
    input_row_count INTEGER DEFAULT 0,
    inserted_row_count INTEGER DEFAULT 0,
    updated_row_count INTEGER DEFAULT 0,
    rejected_row_count INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds REAL DEFAULT 0.0
);
