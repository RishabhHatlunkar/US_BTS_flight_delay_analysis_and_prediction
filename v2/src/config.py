"""
Configuration Loader for V2 Local SQLite Pipeline
Loads config from YAML and provides structured settings with default fallbacks.
"""

import os
import yaml
from pathlib import Path


def get_project_root() -> Path:
    """Returns absolute path to project root directory."""
    # Assuming this file is at <root>/v2/src/config.py
    return Path(__file__).resolve().parent.parent.parent


def load_v2_config(config_path: str = None) -> dict:
    """
    Loads V2 pipeline configuration from YAML file.
    If not specified, defaults to v2/config/config.yaml.
    """
    root = get_project_root()
    if config_path is None:
        primary = root / "v2" / "config" / "config.yaml"
        if primary.exists():
            config_path = str(primary)
        else:
            config_path = str(root / "config" / "v2_config.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Unwrap if nested under 'v2' key
    if "v2" in cfg:
        cfg = cfg["v2"]

    # Resolve relative paths against project root
    db_path = cfg.get("database", {}).get("path", "data/warehouse/flight_delay.db")
    if not os.path.isabs(db_path):
        cfg["database"]["path"] = str(root / db_path)

    raw_dir = cfg.get("raw_data", {}).get("dir", "data/raw/bts")
    if not os.path.isabs(raw_dir):
        cfg["raw_data"]["dir"] = str(root / raw_dir)

    # Reports paths
    reports = cfg.get("reports", {})
    for k, v in list(reports.items()):
        if isinstance(v, str) and not os.path.isabs(v):
            reports[k] = str(root / v)

    # Log file
    log_file = cfg.get("logging", {}).get("log_file", "logs/v2_etl.log")
    if not os.path.isabs(log_file):
        cfg["logging"]["log_file"] = str(root / log_file)

    return cfg
