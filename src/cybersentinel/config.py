"""CyberSentinel AI Configuration Management."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application and environment configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = "CyberSentinel AI"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str = "dev-secret-key-change-in-prod"

    # Database
    database_url: str = "sqlite+aiosqlite:///./cybersentinel.db"
    database_sync_url: str = "sqlite:///./cybersentinel.db"

    # Model Artifact Paths
    supervised_model_path: str = "models/xgboost_classifier_v1.joblib"
    anomaly_model_path: str = "models/isolation_forest_v1.joblib"
    preprocessor_path: str = "models/feature_preprocessor_v1.joblib"
    explainer_path: str = "models/shap_explainer_v1.joblib"

    # Detection & Drift Thresholds
    anomaly_threshold: float = 0.65
    alert_probability_threshold: float = 0.50
    drift_p_value_threshold: float = 0.05
    drift_psi_threshold: float = 0.20
    top_k_shap_features: int = 5
    batch_inference_max_size: int = 5000


def load_yaml_config(file_path: str | Path) -> Dict[str, Any]:
    """Helper to load a YAML configuration file safely."""
    p = Path(file_path)
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# Global configuration singleton instances
settings = AppSettings()
core_config = load_yaml_config("config/config.yaml")
severity_rules_config = load_yaml_config("config/severity_rules.yaml")
drift_config = load_yaml_config("config/drift_config.yaml")
