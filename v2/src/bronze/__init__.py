"""Bronze Ingestion Layer for V2 Local SQLite Data Warehouse."""
from .ingest import ingest_bronze_files

__all__ = ["ingest_bronze_files"]
