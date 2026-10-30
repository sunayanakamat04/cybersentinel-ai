"""Unit tests for ingestion and preprocessing module."""

import numpy as np
from cybersentinel.ingestion.schema import FlowRecordSchema
from cybersentinel.ingestion.validator import sanitize_numerical_value, validate_and_clean_flow_dict
from cybersentinel.ingestion.preprocessor import FlowPreprocessor


def test_sanitize_numerical_value():
    assert sanitize_numerical_value(123.45) == 123.45
    assert sanitize_numerical_value(float("nan"), default=0.0) == 0.0
    assert sanitize_numerical_value(float("inf")) == 1e9
    assert sanitize_numerical_value(float("-inf")) == -1e9
    assert sanitize_numerical_value(None, default=5.0) == 5.0
    assert sanitize_numerical_value("invalid", default=0.0) == 0.0


def test_validate_and_clean_flow_dict():
    raw = {
        " Destination Port ": 443,
        " Flow Bytes/s ": float("inf"),
        "Flow Duration": 1200,
    }
    cleaned = validate_and_clean_flow_dict(raw)
    assert "destination_port" in cleaned
    assert cleaned["destination_port"] == 443
    assert "flow_bytes_per_sec" in cleaned
    assert cleaned["flow_bytes_per_sec"] == 1e9


def test_flow_preprocessor_vector_conversion():
    schema = FlowRecordSchema(
        flow_id="FLOW-UNIT-1",
        flow_duration=5000.0,
        total_fwd_packets=25,
        total_bwd_packets=30,
        flow_bytes_per_sec=15000.0,
        flow_packets_per_sec=110.0,
    )
    prep = FlowPreprocessor()
    vec = prep.schema_to_vector(schema)
    assert isinstance(vec, np.ndarray)
    assert len(vec) == len(prep.DEFAULT_FEATURES)
    # Check that flow duration index matches
    dur_idx = prep.DEFAULT_FEATURES.index("flow_duration")
    assert vec[dur_idx] == 5000.0
