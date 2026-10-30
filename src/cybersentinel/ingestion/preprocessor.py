"""Flow preprocessing and transformation pipeline."""

from typing import List, Optional, Union
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler

from cybersentinel.ingestion.schema import FlowRecordSchema


class FlowPreprocessor:
    """Extracts, cleans, and transforms network flow feature matrices."""

    DEFAULT_FEATURES: List[str] = [
        "flow_duration",
        "total_fwd_packets",
        "total_bwd_packets",
        "total_length_fwd_packets",
        "total_length_bwd_packets",
        "fwd_packet_length_max",
        "fwd_packet_length_min",
        "fwd_packet_length_mean",
        "fwd_packet_length_std",
        "bwd_packet_length_max",
        "bwd_packet_length_min",
        "bwd_packet_length_mean",
        "bwd_packet_length_std",
        "flow_bytes_per_sec",
        "flow_packets_per_sec",
        "flow_iat_mean",
        "flow_iat_std",
        "flow_iat_max",
        "flow_iat_min",
        "fwd_iat_total",
        "bwd_iat_total",
        "fin_flag_count",
        "syn_flag_count",
        "rst_flag_count",
        "psh_flag_count",
        "ack_flag_count",
        "urg_flag_count",
        "fwd_psh_flags",
        "bwd_psh_flags",
        "fwd_urg_flags",
        "bwd_urg_flags",
        "fwd_header_length",
        "bwd_header_length",
        "fwd_packets_per_sec",
        "bwd_packets_per_sec",
        "min_packet_length",
        "max_packet_length",
        "packet_length_mean",
        "packet_length_std",
        "packet_length_variance",
        "down_up_ratio",
        "average_packet_size",
        "init_win_bytes_forward",
        "init_win_bytes_backward",
        "act_data_pkt_fwd",
        "min_seg_size_forward",
        "active_mean",
        "active_std",
        "idle_mean",
        "idle_std",
    ]

    def __init__(self, feature_names: Optional[List[str]] = None):
        self.feature_names = feature_names or self.DEFAULT_FEATURES
        self.scaler = RobustScaler()
        self.is_fitted = False

    def schema_to_vector(self, record: FlowRecordSchema) -> np.ndarray:
        """Converts a FlowRecordSchema into a 1D numerical numpy feature vector."""
        vec = []
        rec_dict = record.model_dump()
        for feat in self.feature_names:
            val = rec_dict.get(feat, 0.0)
            if val is None or np.isnan(val) or np.isinf(val):
                val = 0.0
            vec.append(float(val))
        return np.array(vec, dtype=np.float32)

    def fit(self, X: Union[pd.DataFrame, np.ndarray]) -> "FlowPreprocessor":
        """Fits the RobustScaler on training flows."""
        if isinstance(X, pd.DataFrame):
            X = X[self.feature_names].values
        self.scaler.fit(X)
        self.is_fitted = True
        return self

    def transform(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Applies scaler transformation to feature matrix."""
        if isinstance(X, pd.DataFrame):
            X = X[self.feature_names].values
        if self.is_fitted:
            return self.scaler.transform(X)
        return np.array(X, dtype=np.float32)

    def fit_transform(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Fits scaler and transforms matrix."""
        return self.fit(X).transform(X)
