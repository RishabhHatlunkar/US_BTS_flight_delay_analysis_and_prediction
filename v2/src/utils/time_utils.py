"""
Time and Date Parsing Utilities for BTS Flight Records
"""

import re
from datetime import datetime
from typing import Optional


from typing import Any

def parse_hhmm_time(val: Any) -> Optional[str]:
    """
    Safely parses BTS integer/string HHMM values into standard 'HH:MM'.
    Examples:
      - '0856' -> '08:56'
      - '856'  -> '08:56'
      - '5'    -> '00:05'
      - '30'   -> '00:30'
      - '2359' -> '23:59'
      - '2400' -> '00:00'
      - '' or None -> None
    """
    if val is None:
        return None

    s = str(val).strip()
    if not s or s.lower() == "none" or s.lower() == "null":
        return None

    # Strip decimal part if numeric float string e.g. '856.0' or '856.00'
    if "." in s:
        s = s.split(".")[0].strip()

    # Digits only
    digits = re.sub(r"\D", "", s)
    if not digits:
        return None

    if len(digits) > 4:
        # Unexpected length
        return None

    # Zero-pad up to 4 digits
    padded = digits.zfill(4)
    hh = int(padded[:2])
    mm = int(padded[2:])

    # BTS allows 2400 for midnight
    if hh == 24 and mm == 0:
        return "00:00"

    if 0 <= hh <= 23 and 0 <= mm <= 59:
        return f"{hh:02d}:{mm:02d}"

    return None


def extract_hour(time_val: Any) -> Optional[int]:
    """Extracts the hour (0-23) from a parsed 'HH:MM' string or raw HHMM value."""
    parsed = parse_hhmm_time(time_val)
    if parsed:
        try:
            return int(parsed.split(":")[0])
        except (ValueError, IndexError):
            return None
    return None


def parse_iso_date(val: Any) -> Optional[str]:
    """
    Parses and standardises date into ISO YYYY-MM-DD.
    Validates reasonable calendar bounds.
    """
    if val is None:
        return None

    s = str(val).strip()
    if not s or s.lower() in ("none", "null"):
        return None

    # Handle standard YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            dt = datetime.strptime(s, fmt)
            if 1980 <= dt.year <= 2040:
                return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None
