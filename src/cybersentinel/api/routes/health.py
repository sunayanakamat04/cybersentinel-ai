"""Health check and system telemetry route."""

from datetime import datetime, timezone
from fastapi import APIRouter
from cybersentinel import __version__
from cybersentinel.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """Returns service health status, version, and runtime parameters."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": __version__,
        "environment": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "models": {
            "supervised_classifier": "loaded",
            "anomaly_detector": "loaded",
            "explainability_engine": "loaded",
            "drift_monitor": "active",
        },
    }
