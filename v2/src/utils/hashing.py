"""
Row Hashing Utilities for Deterministic Lineage and Provenance
"""

import hashlib
from typing import Dict, Any


def generate_source_row_hash(row: Dict[str, Any], source_file: str = "", row_idx: int = None) -> str:
    """
    Generates a deterministic SHA-256 hash representing a source row.
    Combines:
    - Source file name
    - Business key fields (Date, Airline, FlightNum, TailNum, Origin, Dest, CRSDepTime)
    - Row index when identical flights operate on same day (to differentiate legitimate duplicate observations)
    """
    def _clean(val):
        if val is None:
            return ""
        s = str(val).strip()
        # Normalise trailing .00 if present
        if s.endswith(".00"):
            s = s[:-3]
        return s

    components = [
        source_file,
        _clean(row.get("FlightDate") or row.get("flight_date")),
        _clean(row.get("Reporting_Airline") or row.get("reporting_airline")),
        _clean(row.get("Flight_Number_Reporting_Airline") or row.get("flight_number")),
        _clean(row.get("Tail_Number") or row.get("tail_number")),
        _clean(row.get("Origin") or row.get("OriginAirportID") or row.get("origin_airport_id")),
        _clean(row.get("Dest") or row.get("DestAirportID") or row.get("destination_airport_id")),
        _clean(row.get("CRSDepTime") or row.get("scheduled_departure_time")),
        _clean(row.get("DepTime") or row.get("actual_departure_time")),
    ]

    if row_idx is not None:
        components.append(str(row_idx))

    payload = "|".join(components)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
