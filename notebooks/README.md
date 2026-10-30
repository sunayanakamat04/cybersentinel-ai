# CyberSentinel AI: Research & Experimentation Notebooks

This directory contains Jupyter notebooks structuring the end-to-end data science lifecycle for CyberSentinel AI:

---

## Notebook Index

### 1. `01_exploratory_data_analysis.ipynb`
- **Objective**: Ingest CIC-IDS2017 / 2018 CSV flow records, inspect missing values, analyze infinite throughput features, compute correlation matrices, and visualize class imbalance.
- **Key Output**: Summary report on feature redundancy and clean Parquet candidate splits.

### 2. `02_supervised_classification_xgboost.ipynb`
- **Objective**: Implement leakage-free train/test partitioning (avoiding session-based flow leakage). Train multi-class XGBoost model with class weight calibration.
- **Key Output**: Evaluated model weights (`models/xgboost_classifier_v1.joblib`), confusion matrix, and multi-class precision/recall metrics.

### 3. `03_unsupervised_anomaly_detection.ipynb`
- **Objective**: Train Isolation Forest and One-Class SVM on benign-only baseline traffic (Monday dataset). Tune contamination parameter to limit false alarm rates on validation data.
- **Key Output**: Calibrated anomaly model weights (`models/isolation_forest_v1.joblib`) and anomaly threshold score.

### 4. `04_explainable_ai_shap.ipynb`
- **Objective**: Apply `shap.TreeExplainer` to the trained XGBoost model. Generate local waterfall attribution plots and global summary beeswarm plots for attack categories.
- **Key Output**: Serialized SHAP explainer (`models/shap_explainer_v1.joblib`) and top-5 influential feature mappings.

### 5. `05_traffic_drift_monitoring.ipynb`
- **Objective**: Simulate temporal distribution shifts and seasonal packet spikes. Benchmark Two-Sample Kolmogorov-Smirnov (KS) test and Population Stability Index (PSI).
- **Key Output**: Validated drift alert thresholds (`config/drift_config.yaml`).
