# Processed Datasets Directory

This directory stores cleaned, scaled, and split Parquet / CSV datasets ready for model training and evaluation:

- `train_flows.parquet`: Training partition (typically baseline Monday benign flows + stratified portion of Tuesday-Friday attack profiles).
- `test_flows.parquet`: Unseen evaluation partition for computing Precision, Recall, F1, and False Positive Rate (FPR).
- `baseline_reference_sample.parquet`: Reference distribution snapshot used by the Drift Monitoring module (KS-Test and PSI calculation).
- `feature_scaler.joblib`: Fitted `RobustScaler` / `StandardScaler` artifact preserving scale parameters.
