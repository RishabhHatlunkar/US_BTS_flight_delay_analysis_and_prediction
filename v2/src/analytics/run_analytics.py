"""
Analytical & OLAP Query Execution Engine
Executes verified SQL analytical queries against the local SQLite Gold Data Warehouse.
"""

import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..utils.db import get_db_connection
from ..utils.logger import setup_logger


def execute_sql_query(conn, sql_path: str) -> Dict[str, Any]:
    """Reads and executes a single SELECT query file, returning columns and rows."""
    with open(sql_path, "r", encoding="utf-8") as f:
        query_text = f.read()

    # Filter out empty statements or comments
    cursor = conn.cursor()
    cursor.execute(query_text)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description] if cursor.description else []

    # Convert sqlite3.Row to dict
    dict_rows = [dict(zip(cols, r)) for r in rows]
    return {
        "file": os.path.basename(sql_path),
        "columns": cols,
        "row_count": len(dict_rows),
        "data": dict_rows
    }


def execute_all_analytics(config: dict, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Discovers and executes all 10 verified analytical SQL queries in v2/sql/analytics/.
    Prints formatted summaries and returns results dictionary.
    """
    log = logger or setup_logger(
        "v2_analytics",
        log_file=config.get("logging", {}).get("log_file"),
        level=config.get("logging", {}).get("log_level", "INFO")
    )

    db_path = config["database"]["path"]
    conn = get_db_connection(db_path)

    project_root = Path(__file__).resolve().parent.parent.parent
    sql_dir = project_root / "sql" / "analytics"

    results = {}
    sql_files = sorted(list(sql_dir.glob("*.sql")))
    log.info(f"Executing {len(sql_files)} verified analytical SQL queries against Gold warehouse...")

    start_all = time.time()
    for sf in sql_files:
        try:
            q_res = execute_sql_query(conn, str(sf))
            results[sf.name] = q_res
            log.info(f"Query [{sf.name}] SUCCESS -> {q_res['row_count']} rows returned.")
        except Exception as e:
            log.error(f"Query [{sf.name}] FAILED: {e}")
            results[sf.name] = {"file": sf.name, "error": str(e), "status": "FAILED"}

    conn.close()
    elapsed = time.time() - start_all
    log.info(f"Analytics run complete: {len(results)} queries executed in {elapsed:.2f}s.")
    return results
