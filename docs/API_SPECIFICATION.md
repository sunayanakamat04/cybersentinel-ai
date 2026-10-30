# CyberSentinel AI: REST API Specification

CyberSentinel AI provides high-performance, asynchronous REST API endpoints built with **FastAPI**. Interactive Swagger/OpenAPI documentation is available at `/docs`, and ReDoc is accessible at `/redoc`.

---

## 1. System Health & Metadata

### `GET /api/v1/health`
Returns system status, active database connectivity, and loaded model lineage versions.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-10-30T15:00:00Z",
  "database_connected": true,
  "loaded_models": {
    "supervised": {
      "type": "xgboost",
      "version": "v1.0.0",
      "classes_count": 13
    },
    "anomaly": {
      "type": "isolation_forest",
      "version": "v1.0.0",
      "contamination": 0.05
    },
    "explainer": {
      "type": "shap.TreeExplainer",
      "status": "ready"
    }
  }
}
```

---

## 2. Real-Time & Streaming Inference

### `POST /api/v1/predict/single`
Ingests a single network flow record in real time, applies preprocessing, evaluates supervised and anomaly models, computes SHAP attributions if anomalous/malicious, and triages alert priority.

**Request Body**:
```json
{
  "flow_id": "FLOW-STREAM-9081",
  "src_ip": "192.168.10.15",
  "src_port": 54210,
  "dst_ip": "192.168.10.50",
  "dst_port": 80,
  "protocol": 6,
  "flow_duration": 1820,
  "total_fwd_packets": 350,
  "total_bwd_packets": 2,
  "total_length_fwd_packets": 42000,
  "total_length_bwd_packets": 0,
  "flow_bytes_per_sec": 23076923.07,
  "flow_packets_per_sec": 193406.59,
  "fwd_packet_length_max": 240,
  "fwd_packet_length_min": 60,
  "fwd_packet_length_mean": 120.0,
  "fwd_packet_length_std": 15.2,
  "bwd_packet_length_max": 0,
  "bwd_packet_length_min": 0,
  "bwd_packet_length_mean": 0.0,
  "bwd_packet_length_std": 0.0,
  "fin_flag_count": 0,
  "syn_flag_count": 1,
  "rst_flag_count": 0,
  "psh_flag_count": 350,
  "ack_flag_count": 0,
  "urg_flag_count": 0,
  "init_win_bytes_forward": 65535,
  "init_win_bytes_backward": 0
}
```

**Response `200 OK`**:
```json
{
  "flow_id": "FLOW-STREAM-9081",
  "is_alert": true,
  "priority": "CRITICAL",
  "prediction": {
    "supervised_class": "DoS_Hulk",
    "supervised_confidence": 0.964,
    "anomaly_score": 0.882,
    "is_anomaly": true
  },
  "triage_reason": "Matched RULE_001_HIGH_IMPACT_EXPLOIT: Destructive DoS attack with confidence >= 0.80",
  "explanations": [
    {
      "feature": "Flow Packets/s",
      "value": 193406.59,
      "shap_attribution": 3.42,
      "impact": "Increases Attack Probability"
    },
    {
      "feature": "Flow Bytes/s",
      "value": 23076923.07,
      "shap_attribution": 2.18,
      "impact": "Increases Attack Probability"
    },
    {
      "feature": "PSH Flag Count",
      "value": 350,
      "shap_attribution": 1.89,
      "impact": "Increases Attack Probability"
    },
    {
      "feature": "Average Packet Size",
      "value": 119.6,
      "shap_attribution": 0.74,
      "impact": "Increases Attack Probability"
    },
    {
      "feature": "Init_Win_bytes_forward",
      "value": 65535,
      "shap_attribution": 0.31,
      "impact": "Increases Attack Probability"
    }
  ],
  "alert_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "inference_latency_ms": 4.12
}
```

---

## 3. Batch Flow Ingestion

### `POST /api/v1/predict/batch`
Processes an array of flow records (up to 5,000 records per batch) or accepts an uploaded CSV dataset.

**Response `200 OK`**:
```json
{
  "total_records_processed": 500,
  "total_alerts_generated": 42,
  "breakdown_by_priority": {
    "CRITICAL": 12,
    "HIGH": 8,
    "MEDIUM": 18,
    "LOW": 4,
    "INFO": 458
  },
  "processing_duration_sec": 1.48,
  "throughput_records_per_sec": 337.8
}
```

---

## 4. Alert Management & SOC Triage

### `GET /api/v1/alerts`
Retrieves paginated alerts with filtering.

**Query Parameters**:
- `priority`: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
- `status`: `OPEN` | `UNDER_INVESTIGATION` | `CONFIRMED_THREAT` | `FALSE_POSITIVE` | `RESOLVED`
- `attack_class`: string
- `limit`: integer (default: 50)
- `offset`: integer (default: 0)

### `GET /api/v1/alerts/{alert_id}`
Retrieves full details of a specific alert, including raw flow parameters, full SHAP values, and investigator notes.

### `PATCH /api/v1/alerts/{alert_id}/status`
Updates alert status and appends investigation notes.

**Request Body**:
```json
{
  "status": "CONFIRMED_THREAT",
  "assigned_analyst": "analyst_jdoe",
  "note": "Confirmed HTTP flood targeting web server VIP. Added temporary ACL rule."
}
```

---

## 5. Traffic Drift Monitoring

### `GET /api/v1/drift/status`
Returns statistical drift test metrics comparing current sliding window to baseline reference.

**Response `200 OK`**:
```json
{
  "drift_detected": false,
  "evaluated_at": "2026-10-30T15:30:00Z",
  "sliding_window_size": 1000,
  "features_drift_summary": [
    {
      "feature": "Flow Bytes/s",
      "ks_p_value": 0.421,
      "psi_value": 0.048,
      "drift_status": "STABLE"
    },
    {
      "feature": "Flow Packets/s",
      "ks_p_value": 0.185,
      "psi_value": 0.082,
      "drift_status": "STABLE"
    },
    {
      "feature": "Packet Length Mean",
      "ks_p_value": 0.038,
      "psi_value": 0.142,
      "drift_status": "MODERATE_SHIFT"
    }
  ],
  "recommendation": "System stable. No retraining required."
}
```
