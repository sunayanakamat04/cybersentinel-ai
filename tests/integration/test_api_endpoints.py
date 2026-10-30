"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_predict_single_flow(client: TestClient, sample_attack_flow):
    response = client.post("/api/v1/predict/single", json=sample_attack_flow)
    assert response.status_code == 200
    data = response.json()
    assert "is_alert" in data
    assert "priority" in data
    assert "prediction" in data
    assert "inference_latency_ms" in data


def test_predict_batch_flows(client: TestClient, sample_benign_flow, sample_attack_flow):
    batch = [sample_benign_flow, sample_attack_flow]
    response = client.post("/api/v1/predict/batch", json=batch)
    assert response.status_code == 200
    data = response.json()
    assert data["total_records_processed"] == 2
    assert "breakdown_by_priority" in data


def test_list_alerts(client: TestClient):
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data


def test_drift_status_endpoint(client: TestClient):
    response = client.get("/api/v1/drift/status")
    assert response.status_code == 200
    data = response.json()
    assert "drift_detected" in data


def test_dashboard_ui_html(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "CyberSentinel AI" in response.text
