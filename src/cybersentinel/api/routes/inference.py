"""Inference API endpoints for batch and streaming flow evaluation."""

import time
import uuid
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from cybersentinel.database.connection import get_db
from cybersentinel.database.models import Alert, ExplanationFeature, FlowRecord
from cybersentinel.drift.detector import TrafficDriftMonitor
from cybersentinel.explainability.explainer import ExplainabilityEngine
from cybersentinel.ingestion.preprocessor import FlowPreprocessor
from cybersentinel.ingestion.schema import FlowRecordSchema
from cybersentinel.models.anomaly import UnsupervisedAnomalyDetector
from cybersentinel.models.classifier import SupervisedClassifier
from cybersentinel.prioritization.engine import AlertTriageEngine

router = APIRouter()

# Singleton pipeline instances
preprocessor = FlowPreprocessor()
classifier = SupervisedClassifier()
anomaly_detector = UnsupervisedAnomalyDetector()
triage_engine = AlertTriageEngine()
explainer = ExplainabilityEngine(feature_names=preprocessor.DEFAULT_FEATURES)
drift_monitor = TrafficDriftMonitor(feature_names=preprocessor.DEFAULT_FEATURES)


@router.post("/predict/single", tags=["Inference"])
async def predict_single_flow(
    flow: FlowRecordSchema,
    db: Session = Depends(get_db),
):
    """Evaluates a single network flow in streaming mode, triaging priority and generating SHAP explanations."""
    start_time = time.perf_counter()

    # 1. Transform flow to feature vector
    raw_vector = preprocessor.schema_to_vector(flow)
    norm_vector = preprocessor.transform(raw_vector.reshape(1, -1))

    # 2. Parallel ML Evaluations
    pred_classes, confidences = classifier.predict(norm_vector)
    sup_class = pred_classes[0]
    sup_conf = float(confidences[0])

    anomaly_scores, is_anom_flags = anomaly_detector.predict(norm_vector)
    anom_score = float(anomaly_scores[0])
    is_anomaly = bool(is_anom_flags[0])

    # 3. Triage Priority Level
    triage = triage_engine.triage(
        supervised_class=sup_class,
        supervised_confidence=sup_conf,
        anomaly_score=anom_score,
        is_anomaly=is_anomaly,
    )

    # 4. Generate SHAP feature explanations if alert triggered
    explanations = []
    if triage.is_alert:
        explanations = explainer.explain_flow(
            flow_vector=norm_vector,
            raw_feature_values=flow.model_dump(),
        )

    # 5. Persist Flow & Alert in Database
    flow_rec = FlowRecord(
        flow_id=flow.flow_id or f"FLOW-{uuid.uuid4().hex[:8].upper()}",
        src_ip=flow.src_ip or "0.0.0.0",
        src_port=flow.src_port,
        dst_ip=flow.dst_ip or "0.0.0.0",
        dst_port=flow.dst_port,
        protocol=flow.protocol,
        flow_duration=flow.flow_duration,
        total_fwd_packets=flow.total_fwd_packets,
        total_bwd_packets=flow.total_bwd_packets,
        flow_bytes_per_sec=flow.flow_bytes_per_sec,
        flow_packets_per_sec=flow.flow_packets_per_sec,
        raw_features=flow.model_dump(),
    )
    db.add(flow_rec)
    db.flush()

    alert_id = None
    if triage.is_alert:
        new_alert = Alert(
            flow_record_id=flow_rec.id,
            priority=triage.priority.value,
            attack_class=triage.attack_class,
            supervised_confidence=sup_conf,
            anomaly_score=anom_score,
            is_anomaly=is_anomaly,
            rule_matched=triage.rule_matched,
            status="OPEN",
        )
        db.add(new_alert)
        db.flush()
        alert_id = new_alert.id

        # Persist explanation features
        for rank, exp in enumerate(explanations, start=1):
            feat_rec = ExplanationFeature(
                alert_id=new_alert.id,
                feature_name=exp.get("feature", "unknown"),
                feature_value=float(exp.get("value", 0.0)),
                shap_attribution=float(exp.get("shap_attribution", 0.0)),
                rank=rank,
                impact_description=exp.get("impact", ""),
            )
            db.add(feat_rec)

    db.commit()

    # 6. Update Drift Buffer
    drift_monitor.ingest_flow_vector(norm_vector)

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "flow_id": flow_rec.flow_id,
        "is_alert": triage.is_alert,
        "priority": triage.priority.value,
        "prediction": {
            "supervised_class": sup_class,
            "supervised_confidence": round(sup_conf, 4),
            "anomaly_score": round(anom_score, 4),
            "is_anomaly": is_anomaly,
        },
        "rule_matched": triage.rule_matched,
        "action_recommendation": triage.action_recommendation,
        "explanations": explanations,
        "alert_id": alert_id,
        "inference_latency_ms": round(latency_ms, 2),
    }


@router.post("/predict/batch", tags=["Inference"])
async def predict_batch_flows(
    flows: List[FlowRecordSchema],
    db: Session = Depends(get_db),
):
    """Processes an array of network flow records in high-throughput batch mode."""
    if len(flows) > 5000:
        raise HTTPException(status_code=400, detail="Batch size exceeds maximum limit of 5,000 records.")

    start_time = time.perf_counter()
    alert_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    total_alerts = 0

    for flow in flows:
        raw_vector = preprocessor.schema_to_vector(flow)
        norm_vector = preprocessor.transform(raw_vector.reshape(1, -1))
        
        pred_classes, confidences = classifier.predict(norm_vector)
        anomaly_scores, is_anom_flags = anomaly_detector.predict(norm_vector)

        triage = triage_engine.triage(
            supervised_class=pred_classes[0],
            supervised_confidence=float(confidences[0]),
            anomaly_score=float(anomaly_scores[0]),
            is_anomaly=bool(is_anom_flags[0]),
        )

        alert_counts[triage.priority.value] = alert_counts.get(triage.priority.value, 0) + 1
        if triage.is_alert:
            total_alerts += 1

        drift_monitor.ingest_flow_vector(norm_vector)

    duration = time.perf_counter() - start_time

    return {
        "total_records_processed": len(flows),
        "total_alerts_generated": total_alerts,
        "breakdown_by_priority": alert_counts,
        "processing_duration_sec": round(duration, 3),
        "throughput_records_per_sec": round(len(flows) / max(duration, 0.001), 1),
    }
