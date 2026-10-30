"""Unsupervised Anomaly Detection Module (Isolation Forest)."""

from typing import Any, Optional, Tuple
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest


class UnsupervisedAnomalyDetector:
    """Detects statistical deviations from learned benign network traffic baseline."""

    def __init__(
        self,
        contamination: float = 0.05,
        threshold: float = 0.65,
        model_version: str = "v1.0.0",
    ):
        self.contamination = contamination
        self.threshold = threshold
        self.model_version = model_version
        self.model: Optional[IsolationForest] = None
        self.is_trained = False

    def train(self, X_benign: np.ndarray, **params: Any) -> "UnsupervisedAnomalyDetector":
        """Fits Isolation Forest on baseline benign network flows."""
        default_params = {
            "n_estimators": 100,
            "max_samples": "auto",
            "contamination": self.contamination,
            "random_state": 42,
        }
        default_params.update(params)

        self.model = IsolationForest(**default_params)
        self.model.fit(X_benign)
        self.is_trained = True
        return self

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Computes anomaly scores normalized to [0, 1].

        Higher score implies greater anomalous deviation.
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        if self.model is not None and self.is_trained:
            # IsolationForest score_samples returns negative values (lower = more abnormal)
            raw_scores = self.model.score_samples(X)
            # Normalize to 0 (normal) - 1 (highly anomalous)
            # raw_scores typically range from -0.8 to -0.2
            normalized = np.clip(0.5 - raw_scores, 0.0, 1.0)
            return normalized

        # Scaffolding default baseline
        return np.full(X.shape[0], 0.15, dtype=np.float32)

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Returns anomaly scores and boolean outlier flags."""
        scores = self.score_samples(X)
        is_anomaly = scores >= self.threshold
        return scores, is_anomaly

    def save(self, file_path: str | Path) -> None:
        """Saves model artifact to disk."""
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "threshold": self.threshold, "version": self.model_version}, p)

    def load(self, file_path: str | Path) -> "UnsupervisedAnomalyDetector":
        """Loads model artifact from disk."""
        p = Path(file_path)
        if p.exists():
            data = joblib.load(p)
            self.model = data.get("model")
            self.threshold = data.get("threshold", 0.65)
            self.model_version = data.get("version", "v1.0.0")
            self.is_trained = self.model is not None
        return self
