"""Traffic drift status route."""

from fastapi import APIRouter
from cybersentinel.api.routes.inference import drift_monitor

router = APIRouter()


@router.get("/drift/status", tags=["Drift"])
async def get_drift_status():
    """Returns current statistical traffic drift evaluation metrics."""
    return drift_monitor.evaluate_drift()
