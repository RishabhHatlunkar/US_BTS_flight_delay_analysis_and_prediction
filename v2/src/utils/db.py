"""
Database Connection and Transaction Management for SQLite
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Generator


def get_db_connection(db_path: str, foreign_keys: bool = True) -> sqlite3.Connection:
    """
    Creates and returns an optimized SQLite connection with:
    - Foreign key constraints enforced
    - WAL journal mode for concurrent read/write performance
    - Busy timeout for concurrency handling
    - Row factory enabled for dictionary-like access
    """
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=60.0)
    conn.row_factory = sqlite3.Row

    if foreign_keys:
        conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 60000;")

    return conn


@contextmanager
def db_transaction(conn: sqlite3.Connection) -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager for safe SQLite transactions.
    Automatically commits on success or rolls back on exception.
    """
    cursor = conn.cursor()
    try:
        conn.execute("BEGIN;")
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def execute_sql_file(conn: sqlite3.Connection, sql_path: str) -> None:
    """Reads and executes a multi-statement SQL script file."""
    if not os.path.exists(sql_path):
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    with open(sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    cursor = conn.cursor()
    try:
        cursor.executescript(sql_script)
        conn.commit()
    finally:
        cursor.close()
