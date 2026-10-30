"""Pytest fixtures for CyberSentinel AI."""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from cybersentinel.api.main import app
from cybersentinel.database.connection import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes tables before running tests."""
    init_db()


@pytest.fixture
def client():
    """Provides a TestClient for FastAPI endpoints."""
    return TestClient(app)


@pytest.fixture
def sample_benign_flow():
    """Loads a sample benign flow record dictionary."""
    sample_path = Path("data/samples/sample_benign_flows.json")
    if sample_path.exists():
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[0]
    return {
        "flow_id": "TEST-FLOW-001",
        "flow_duration": 1000,
        "total_fwd_packets": 10,
        "total_bwd_packets": 10,
        "flow_bytes_per_sec": 1000.0,
        "flow_packets_per_sec": 20.0,
    }


@pytest.fixture
def sample_attack_flow():
    """Loads a sample attack flow record dictionary."""
    sample_path = Path("data/samples/sample_attack_flows.json")
    if sample_path.exists():
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[0]
    return {
        "flow_id": "TEST-ATTACK-001",
        "flow_duration": 500,
        "total_fwd_packets": 500,
        "total_bwd_packets": 1,
        "flow_bytes_per_sec": 5000000.0,
        "flow_packets_per_sec": 100000.0,
        "ground_truth_label": "DoS_Hulk",
    }
