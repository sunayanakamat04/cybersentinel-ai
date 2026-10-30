"""Model evaluation and benchmark metrics engine."""

import time
from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


class ModelBenchmarkEvaluator:
    """Evaluates NIDS models against held-out partitions, tracking precision, recall, FPR, and latency."""

    def __init__(self, target_names: Optional[List[str]] = None):
        self.target_names = target_names or []

    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
        benign_label_idx: int = 0,
        inference_durations_sec: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Calculates multi-class classification and operational detection metrics."""
        
        # 1. Standard Multi-Class Metrics
        prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
        rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
        f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

        # 2. Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)

        # 3. False Positive Rate on Benign Traffic
        # Benign is class index benign_label_idx
        benign_mask = (y_true == benign_label_idx)
        total_benign = int(np.sum(benign_mask))
        if total_benign > 0:
            false_positives = int(np.sum(y_pred[benign_mask] != benign_label_idx))
            fpr = float(false_positives / total_benign)
        else:
            false_positives = 0
            fpr = 0.0

        # 4. Latency Benchmarks
        latency_summary = {}
        if inference_durations_sec and len(inference_durations_sec) > 0:
            durations_ms = np.array(inference_durations_sec) * 1000.0
            latency_summary = {
                "mean_latency_ms": round(float(np.mean(durations_ms)), 3),
                "median_latency_ms": round(float(np.median(durations_ms)), 3),
                "p95_latency_ms": round(float(np.percentile(durations_ms, 95)), 3),
                "p99_latency_ms": round(float(np.percentile(durations_ms, 99)), 3),
            }

        return {
            "macro_precision": round(prec_macro, 4),
            "macro_recall": round(rec_macro, 4),
            "macro_f1": round(f1_macro, 4),
            "weighted_f1": round(f1_weighted, 4),
            "benign_false_positive_rate": round(fpr, 5),
            "total_benign_flows_evaluated": total_benign,
            "benign_false_positives_count": false_positives,
            "confusion_matrix": cm.tolist(),
            "latency_benchmarks": latency_summary,
        }
