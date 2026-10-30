"""Data validation and hygiene utilities for network flows."""

import math
from typing import Any, Dict


def sanitize_numerical_value(val: Any, default: float = 0.0) -> float:
    """Sanitizes floats, replacing infinite and NaN values with safe bounds."""
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f):
            return default
        if math.isinf(f):
            return 1e9 if f > 0 else -1e9
        return f
    except (ValueError, TypeError):
        return default


def validate_and_clean_flow_dict(raw_flow: Dict[str, Any]) -> Dict[str, Any]:
    """Cleans raw dictionary, normalizing keys and sanitizing numerical fields."""
    cleaned: Dict[str, Any] = {}
    
    # Strip whitespace from keys
    for k, v in raw_flow.items():
        clean_key = k.strip().lower().replace(" ", "_").replace("/", "_per_").replace("-", "_")
        if clean_key.endswith("_per_s"):
            clean_key = clean_key + "ec"
        cleaned[clean_key] = v

    # Ensure critical numerical metrics are valid numbers
    rate_keys = ["flow_bytes_per_sec", "flow_packets_per_sec", "flow_duration"]
    for rk in rate_keys:
        if rk in cleaned:
            cleaned[rk] = sanitize_numerical_value(cleaned[rk])

    return cleaned
