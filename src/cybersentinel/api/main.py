"""Main FastAPI application entry point for CyberSentinel AI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from cybersentinel import __version__
from cybersentinel.api.routes import alerts, drift, health, inference
from cybersentinel.config import settings
from cybersentinel.dashboard import app as dashboard_app
from cybersentinel.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    # Initialize SQLite / PostgreSQL tables
    init_db()
    yield


app = FastAPI(
    title="CyberSentinel AI: Adaptive Network Intrusion Detection System",
    description=(
        "Hybrid Machine Learning & Explainable AI (XAI) Platform for Network Flow Security "
        "Analysis, Novelty Detection, and Dynamic Traffic Drift Monitoring."
    ),
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(inference.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(drift.router, prefix="/api/v1")

# Dashboard UI Router
app.include_router(dashboard_app.router)
