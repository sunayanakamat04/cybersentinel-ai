"""Unit tests for traffic drift monitoring."""

import numpy as np
from cybersentinel.drift.detector import TrafficDriftMonitor, calculate_psi


def test_calculate_psi_identical_distributions():
    np.random.seed(42)
    dist = np.random.normal(loc=100.0, scale=15.0, size=500)
    psi = calculate_psi(dist, dist)
    assert psi < 0.05  # Virtually zero drift


def test_calculate_psi_shifted_distribution():
    np.random.seed(42)
    ref = np.random.normal(loc=100.0, scale=15.0, size=500)
    curr = np.random.normal(loc=180.0, scale=25.0, size=500)  # Distinct shift
    psi = calculate_psi(ref, curr)
    assert psi > 0.20  # Significant drift detected


def test_drift_monitor_evaluation():
    monitor = TrafficDriftMonitor(
        sliding_window_size=100,
        feature_names=["feature_0", "feature_1"],
    )
    for _ in range(60):
        vec = np.array([10.0, 20.0])
        monitor.ingest_flow_vector(vec)
    
    result = monitor.evaluate_drift()
    assert "drift_detected" in result
    assert result["sample_count"] == 60
