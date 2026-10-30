"""Traffic Drift Monitoring Module implementing KS-test and PSI."""

from typing import Any, Dict, List, Optional
import numpy as np
from scipy import stats


def calculate_psi(
    reference: np.ndarray,
    current: np.ndarray,
    num_bins: int = 10,
    epsilon: float = 1e-4,
) -> float:
    """Calculates Population Stability Index (PSI) between two 1D distributions."""
    if len(reference) == 0 or len(current) == 0:
        return 0.0

    # Determine quantiles based on reference
    percentiles = np.linspace(0, 100, num_bins + 1)
    bin_edges = np.percentile(reference, percentiles)
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    # Bucket counts
    ref_counts, _ = np.histogram(reference, bins=bin_edges)
    curr_counts, _ = np.histogram(current, bins=bin_edges)

    # Fractions
    ref_pct = (ref_counts + epsilon) / (np.sum(ref_counts) + epsilon * num_bins)
    curr_pct = (curr_counts + epsilon) / (np.sum(curr_counts) + epsilon * num_bins)

    # PSI sum
    psi_value = np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct))
    return float(psi_value)


class TrafficDriftMonitor:
    """Monitors live network traffic against baseline for statistical distribution drift."""

    def __init__(
        self,
        reference_data: Optional[np.ndarray] = None,
        feature_names: Optional[List[str]] = None,
        sliding_window_size: int = 1000,
        ks_p_value_threshold: float = 0.05,
        psi_threshold: float = 0.20,
    ):
        self.reference_data = reference_data
        self.feature_names = feature_names or []
        self.sliding_window_size = sliding_window_size
        self.ks_p_value_threshold = ks_p_value_threshold
        self.psi_threshold = psi_threshold
        self.live_buffer: List[np.ndarray] = []

    def ingest_flow_vector(self, flow_vec: np.ndarray) -> None:
        """Appends flow vector to sliding window buffer."""
        self.live_buffer.append(flow_vec.flatten())
        if len(self.live_buffer) > self.sliding_window_size:
            self.live_buffer.pop(0)

    def evaluate_drift(self) -> Dict[str, Any]:
        """Evaluates Kolmogorov-Smirnov test and PSI across monitored features."""
        if len(self.live_buffer) < 50:
            return {
                "drift_detected": False,
                "status": "INSUFFICIENT_DATA",
                "sample_count": len(self.live_buffer),
                "features_summary": [],
                "recommendation": "Collecting more flow samples for statistical significance.",
            }

        live_matrix = np.array(self.live_buffer)
        drift_detected = False
        features_summary = []

        # If reference baseline is provided
        if self.reference_data is not None and self.reference_data.shape[0] > 0:
            ref_matrix = self.reference_data
        else:
            # Self-reference initial window split for baseline
            half = len(live_matrix) // 2
            ref_matrix = live_matrix[:half]
            live_matrix = live_matrix[half:]

        n_features = min(live_matrix.shape[1], ref_matrix.shape[1])

        for col_idx in range(n_features):
            feat_name = self.feature_names[col_idx] if col_idx < len(self.feature_names) else f"feature_{col_idx}"
            ref_col = ref_matrix[:, col_idx]
            live_col = live_matrix[:, col_idx]

            # 1. Two-sample Kolmogorov-Smirnov test
            try:
                ks_stat, p_val = stats.ks_2samp(ref_col, live_col)
            except Exception:
                ks_stat, p_val = 0.0, 1.0

            # 2. Population Stability Index (PSI)
            try:
                psi_val = calculate_psi(ref_col, live_col)
            except Exception:
                psi_val = 0.0

            is_feature_drift = (p_val < self.ks_p_value_threshold) or (psi_val >= self.psi_threshold)
            if is_feature_drift:
                drift_detected = True

            features_summary.append({
                "feature": feat_name,
                "ks_statistic": round(float(ks_stat), 4),
                "ks_p_value": round(float(p_val), 4),
                "psi_value": round(float(psi_val), 4),
                "drift_flag": is_feature_drift,
                "status": "DRIFT_DETECTED" if is_feature_drift else "STABLE",
            })

        return {
            "drift_detected": drift_detected,
            "status": "DRIFT_DETECTED" if drift_detected else "STABLE",
            "sample_count": len(self.live_buffer),
            "features_summary": features_summary,
            "recommendation": (
                "Review drift indicators on dashboard. Model retraining validation required."
                if drift_detected
                else "System stable. Traffic distribution aligns with baseline."
            ),
        }
