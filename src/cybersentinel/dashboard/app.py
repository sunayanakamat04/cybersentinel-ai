"""Dashboard rendering router integrating Jinja2 templates."""

from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from cybersentinel.database.connection import get_db
from cybersentinel.database.models import Alert, FlowRecord
from cybersentinel.api.routes.inference import drift_monitor

router = APIRouter()

template_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(template_dir))


@router.get("/", tags=["Dashboard"])
async def render_dashboard(request: Request, db: Session = Depends(get_db)):
    """Renders the main SOC operations dashboard."""
    total_flows = db.query(FlowRecord).count()
    alerts_query = db.query(Alert)
    total_alerts = alerts_query.count()
    critical_count = alerts_query.filter(Alert.priority == "CRITICAL").count()
    anomaly_count = alerts_query.filter(Alert.is_anomaly == True).count()

    recent_alerts = (
        db.query(Alert)
        .order_by(desc(Alert.created_at))
        .limit(15)
        .all()
    )

    drift_eval = drift_monitor.evaluate_drift()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "total_flows": total_flows,
            "total_alerts": total_alerts,
            "critical_count": critical_count,
            "anomaly_count": anomaly_count,
            "recent_alerts": recent_alerts,
            "drift_detected": drift_eval.get("drift_detected", False),
        },
    )
