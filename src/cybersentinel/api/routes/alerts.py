"""Alert management and investigation triage routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from cybersentinel.database.connection import get_db
from cybersentinel.database.models import Alert, ExplanationFeature

router = APIRouter()


class AlertStatusUpdate(BaseModel):
    status: str  # OPEN, UNDER_INVESTIGATION, CONFIRMED_THREAT, FALSE_POSITIVE, RESOLVED
    assigned_analyst: Optional[str] = None
    note: Optional[str] = None


@router.get("/alerts", tags=["Alerts"])
async def list_alerts(
    priority: Optional[str] = Query(None, description="Filter by priority level (CRITICAL, HIGH, etc.)"),
    status: Optional[str] = Query(None, description="Filter by status (OPEN, RESOLVED, etc.)"),
    attack_class: Optional[str] = Query(None, description="Filter by attack category"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Retrieves paginated historical alerts with optional filtering."""
    query = db.query(Alert)
    if priority:
        query = query.filter(Alert.priority == priority.upper())
    if status:
        query = query.filter(Alert.status == status.upper())
    if attack_class:
        query = query.filter(Alert.attack_class == attack_class)

    total_count = query.count()
    alerts = query.order_by(desc(Alert.created_at)).offset(offset).limit(limit).all()

    results = []
    for a in alerts:
        results.append({
            "id": a.id,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "priority": a.priority,
            "attack_class": a.attack_class,
            "supervised_confidence": a.supervised_confidence,
            "anomaly_score": a.anomaly_score,
            "status": a.status,
            "assigned_analyst": a.assigned_analyst,
            "rule_matched": a.rule_matched,
        })

    return {
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "items": results,
    }


@router.get("/alerts/{alert_id}", tags=["Alerts"])
async def get_alert_detail(
    alert_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves detailed information for an alert including SHAP feature explanations and raw flow metrics."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    explanations = (
        db.query(ExplanationFeature)
        .filter(ExplanationFeature.alert_id == alert_id)
        .order_by(ExplanationFeature.rank)
        .all()
    )

    flow_data = None
    if alert.flow_record:
        flow_data = {
            "flow_id": alert.flow_record.flow_id,
            "src_ip": alert.flow_record.src_ip,
            "src_port": alert.flow_record.src_port,
            "dst_ip": alert.flow_record.dst_ip,
            "dst_port": alert.flow_record.dst_port,
            "protocol": alert.flow_record.protocol,
            "flow_duration": alert.flow_record.flow_duration,
            "flow_bytes_per_sec": alert.flow_record.flow_bytes_per_sec,
            "flow_packets_per_sec": alert.flow_record.flow_packets_per_sec,
            "raw_features": alert.flow_record.raw_features,
        }

    return {
        "id": alert.id,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "priority": alert.priority,
        "attack_class": alert.attack_class,
        "supervised_confidence": alert.supervised_confidence,
        "anomaly_score": alert.anomaly_score,
        "is_anomaly": alert.is_anomaly,
        "rule_matched": alert.rule_matched,
        "status": alert.status,
        "assigned_analyst": alert.assigned_analyst,
        "triage_notes": alert.triage_notes,
        "flow_record": flow_data,
        "explanations": [
            {
                "feature": exp.feature_name,
                "value": exp.feature_value,
                "shap_attribution": exp.shap_attribution,
                "rank": exp.rank,
                "impact": exp.impact_description,
            }
            for exp in explanations
        ],
    }


@router.patch("/alerts/{alert_id}/status", tags=["Alerts"])
async def update_alert_status(
    alert_id: str,
    update: AlertStatusUpdate,
    db: Session = Depends(get_db),
):
    """Updates the investigation lifecycle status of an alert and records analyst triage notes."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    valid_statuses = {"OPEN", "UNDER_INVESTIGATION", "CONFIRMED_THREAT", "FALSE_POSITIVE", "RESOLVED"}
    if update.status.upper() not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    alert.status = update.status.upper()
    if update.assigned_analyst is not None:
        alert.assigned_analyst = update.assigned_analyst
    if update.note:
        existing = alert.triage_notes or ""
        alert.triage_notes = (existing + "\n" + update.note).strip()

    db.commit()
    db.refresh(alert)

    return {
        "id": alert.id,
        "status": alert.status,
        "assigned_analyst": alert.assigned_analyst,
        "triage_notes": alert.triage_notes,
        "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
    }
