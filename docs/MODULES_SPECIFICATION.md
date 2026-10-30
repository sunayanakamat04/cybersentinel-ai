# CyberSentinel AI: Technical Modules Specification

This document provides a comprehensive technical specification for all eight proposed system modules in CyberSentinel AI, detailing their purpose, inputs, algorithms, outputs, failure modes, and code structure.

---

## Module 1: Network-Flow Ingestion & Preprocessing Module

- **Implementation Path**: `src/cybersentinel/ingestion/`
  - `schema.py` (Pydantic validation models)
  - `validator.py` (Field checks, range checks, protocol validation)
  - `preprocessor.py` (Imputation, scaling, feature alignment)

### 1.1 Purpose
Ingests raw bidirectional network-flow records from stored benchmark datasets (CSV/Parquet from CIC-IDS2017/2018) or streaming network monitors via REST endpoints. Validates required schema fields, handles edge cases (e.g., division by zero leading to `Infinity` or `NaN`), and transforms continuous features to normalized representations.

### 1.2 Inputs
- High-throughput CSV/Parquet files OR single/batch JSON payloads over HTTP:
  - 5-tuple: `Source IP`, `Source Port`, `Destination IP`, `Destination Port`, `Protocol`
  - Statistical flow aggregates: `Flow Duration`, `Total Fwd Packets`, `Total Bwd Packets`, `Flow Bytes/s`, `Flow Packets/s`, packet length statistics, inter-arrival times (IAT), TCP flag counts, window sizes.

### 1.3 Algorithm & Processing Logic
1. **Schema Validation**: Verify that required 78+ flow fields exist and adhere to type bounds (e.g., ports $\in [0, 65535]$, duration $\ge 0$).
2. **Infinite & NaN Cleansing**:
   $$\text{Flow Bytes/s} = \begin{cases} \text{Max Valid Float} & \text{if } \text{Duration} = 0 \text{ and } \text{Bytes} > 0 \\ 0 & \text{if } \text{Duration} = 0 \text{ and } \text{Bytes} = 0 \\ \frac{\text{Total Bytes}}{\text{Duration}} & \text{otherwise} \end{cases}$$
3. **Scaling**: Transform numerical columns using a pre-fitted `RobustScaler` (resistant to extreme network volume outliers):
   $$x' = \frac{x - Q_2(x)}{Q_3(x) - Q_1(x)}$$

### 1.4 Outputs
- Sanitized, normalized feature matrix $\mathbf{X} \in \mathbb{R}^{B \times d}$ ready for model consumption.
- Flow metadata envelope containing session IDs and timestamp.

---

## Module 2: Supervised Intrusion Classification Module

- **Implementation Path**: `src/cybersentinel/models/classifier.py`

### 2.1 Purpose
Classifies preprocessed flow vectors into recognized network traffic classes (Benign vs. specific attack categories such as DDoS, PortScan, FTP/SSH-Patator, Web Attacks, Botnet, Infiltration). Records confidence scores and model version metadata.

### 2.2 Inputs
- Preprocessed feature vector $\mathbf{x} \in \mathbb{R}^d$ or batch $\mathbf{X} \in \mathbb{R}^{B \times d}$.

### 2.3 Algorithm & Processing Logic
- **Architecture**: Gradient Boosted Decision Tree ensemble using **XGBoost** (`multi:softprob` objective).
- **Inference Pipeline**:
  $$\hat{\mathbf{p}} = \text{Softmax}\left(\sum_{m=1}^{M} f_m(\mathbf{x})\right)$$
- Selects winning class $\hat{y} = \arg\max_k \hat{p}_k$ and confidence $C = \max_k \hat{p}_k$.
- Compares confidence against configurable classification decision boundaries.

### 2.4 Outputs
- Predicted Attack Class Label (e.g., `DDoS_Hulk`, `PortScan`, `BENIGN`).
- Class Probability Distribution Vector $\hat{\mathbf{p}}$.
- Model Lineage Information (`model_version`, `timestamp`).

---

## Module 3: Unsupervised Anomaly Detection Module

- **Implementation Path**: `src/cybersentinel/models/anomaly.py`

### 3.1 Purpose
Detects novel, previously unseen, or zero-day network traffic behaviors that deviate from normal baseline operations without relying on predefined attack signatures. Produces a continuous anomaly score for further investigation.

### 3.2 Inputs
- Preprocessed feature vector $\mathbf{x} \in \mathbb{R}^d$ (or feature subset highlighting behavioral rates and flag distributions).

### 3.3 Algorithm & Processing Logic
- **Primary Algorithm**: **Isolation Forest** (ensemble of extremely randomized trees).
  - Normal traffic requires many splits to isolate; anomalies reside in sparse regions and are isolated at shallow tree depths.
- **Scoring Function**:
  $$S(\mathbf{x}, n) = 2^{-\frac{\mathbb{E}[h(\mathbf{x})]}{c(n)}}$$
  - $S \in [0, 1]$. If $S \to 1$, the instance is flagged as highly anomalous. If $S < 0.5$, the instance exhibits normal baseline structure.
- **Secondary Option**: One-Class Support Vector Machine (OC-SVM) with RBF kernel or DBSCAN clustering for high-density boundary tracking.

### 3.4 Outputs
- Continuous Anomaly Score $S_{\text{anomaly}} \in [0.0, 1.0]$.
- Binary Outlier Flag (`is_anomaly`: boolean, where $S_{\text{anomaly}} \ge \tau_{\text{threshold}}$).

---

## Module 4: Alert Prioritization & Management Module

- **Implementation Path**: `src/cybersentinel/prioritization/` & `src/cybersentinel/database/`

### 4.1 Purpose
Synthesizes the outputs of the supervised classifier, the unsupervised anomaly score, and configurable operational rules into an actionable severity tier (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`). Prevents alert fatigue and tracks alert resolution lifecycles.

### 4.2 Inputs
- Supervised Prediction $\hat{y}_{\text{sup}}$ and Confidence $C_{\text{sup}}$.
- Unsupervised Anomaly Score $S_{\text{anomaly}}$.
- Configurable Rule Matrix (`config/severity_rules.yaml`).

### 4.3 Triage Matrix
| Supervised Class | Confidence $C$ | Anomaly Score $S$ | Assigned Priority | Response SLA |
|---|---|---|---|---|
| Destructive (DDoS, Botnet, Infiltration) | $\ge 0.80$ | Any | **CRITICAL (P1)** | 15 Minutes |
| Destructive | $0.50 \le C < 0.80$ | $\ge 0.65$ | **HIGH (P2)** | 60 Minutes |
| Credential / Exploits (Patator, Web Attack) | $\ge 0.70$ | Any | **HIGH (P2)** | 60 Minutes |
| BENIGN | Any | $\ge 0.85$ (Zero-Day Suspicion) | **HIGH (P2)** | 60 Minutes |
| Reconnaissance (PortScan) | $\ge 0.60$ | Any | **MEDIUM (P3)** | 4 Hours |
| BENIGN | Any | $0.65 \le S < 0.85$ | **MEDIUM (P3)** | 4 Hours |
| Any Attack Class | $0.40 \le C < 0.60$ | $< 0.65$ | **LOW (P4)** | 24 Hours |
| BENIGN | $\ge 0.70$ | $< 0.65$ | **INFO (P5)** | Log Only |

### 4.4 Outputs & State Lifecycle
- Persistent Alert Record with unique UUID in PostgreSQL.
- State Transition Support: `OPEN` $\to$ `UNDER_INVESTIGATION` $\to$ `CONFIRMED_THREAT` / `FALSE_POSITIVE` $\to$ `RESOLVED`.
- Analyst annotation logs and audit trail.

---

## Module 5: Explainability Module (SHAP)

- **Implementation Path**: `src/cybersentinel/explainability/`

### 5.1 Purpose
Demystifies the decisions of the supervised machine learning model by computing localized feature attributions using Shapley Additive Explanations. Displays the exact flow features that drove the prediction to empower analyst verification.

### 5.2 Inputs
- Preprocessed flow instance $\mathbf{x} \in \mathbb{R}^d$.
- Trained XGBoost model artifact.

### 5.3 Algorithm & Processing Logic
- Utilizes `shap.TreeExplainer` optimized for tree-based ensemble models via dynamic programming in $\mathcal{O}(T L D^2)$ time:
  $$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} [f_x(S \cup \{i\}) - f_x(S)]$$
- Extracts top-$K$ positive and negative contributing features for the predicted class.
- Generates structured waterfall payload: Feature Name, Raw Value, Normalized Value, and $\phi$ Attribution Delta.

### 5.4 Outputs
- Structured JSON explanation payload containing Top-5 features and baseline expected value.
- Visual waterfall / bar attribution representation for the web dashboard.

---

## Module 6: Traffic Drift Monitoring Module

- **Implementation Path**: `src/cybersentinel/drift/`

### 6.1 Purpose
Tracks statistical distribution shifts in continuous network flow features and monitors anomalies in alert triggering frequencies over sliding temporal windows. Emits early warnings before model accuracy degrades.

### 6.2 Inputs
- Reference baseline feature sample $\mathbf{X}_{\text{ref}}$ (from training baseline).
- Sliding inference buffer $\mathbf{X}_{\text{live}}$ ($N=1000$ latest flows).

### 6.3 Statistical Methods
1. **Two-Sample Kolmogorov-Smirnov (KS) Test**:
   $$D = \sup_x |F_{\text{live}}(x) - F_{\text{ref}}(x)|$$
   Rejects the null hypothesis (traffic distributions are identical) if $p\text{-value} < \alpha$ (default $\alpha = 0.05$).
2. **Population Stability Index (PSI)**:
   $$\text{PSI} = \sum_{b=1}^{B} \left( \% \text{Live}_b - \% \text{Ref}_b \right) \times \ln\left(\frac{\% \text{Live}_b}{\% \text{Ref}_b}\right)$$
   - $\text{PSI} < 0.10$: No significant shift.
   - $0.10 \le \text{PSI} < 0.20$: Moderate drift detected.
   - $\text{PSI} \ge 0.20$: Significant distribution drift.
3. **Alert Rate Spike Detection**: Compares moving average alert frequencies against historical 95th percentile confidence bands.

### 6.4 Outputs
- Drift Status Payload: `is_drift_detected`, per-feature $p$-values and PSI metrics.
- Visual drift comparison plots for dashboard display.
- System notifications without automated retraining.

---

## Module 7: Dashboard and Reporting Module

- **Implementation Path**: `src/cybersentinel/dashboard/` & `src/cybersentinel/api/`

### 7.1 Purpose
Serves a responsive, web-based security operations dashboard built with HTML5, Bootstrap 5, and Chart.js. Visualizes real-time alert streams, attack category distributions, anomaly trends, SHAP attribution graphs, and downloadable analytical reports.

### 7.2 Key Dashboard Views
1. **Executive SOC Overview**: Total flows ingested, active alerts by severity (P1-P5), current anomaly rate, and system drift status.
2. **Real-Time Alert Feed**: Filterable, searchable table displaying recent alerts with severity badges, timestamps, source/destination 5-tuples, and quick action triage buttons.
3. **Alert Deep-Dive Modal**: Displays complete raw flow metrics alongside the interactive SHAP feature importance breakdown.
4. **Drift & Model Health Tab**: Histograms comparing live flow features against baseline distributions, KS $p$-values, and PSI indicators.
5. **Report Exporter**: Generates formatted JSON and CSV audit reports for incident reviews and compliance.

---

## Module 8: Model Evaluation & Experiment Management Module

- **Implementation Path**: `src/cybersentinel/evaluation/`

### 8.1 Purpose
Provides reproducible benchmarking tools to evaluate supervised and unsupervised models on held-out test partitions. Measures multi-class precision, recall, F1-score, false positive rate (FPR), inference latency, and confusion matrices.

### 8.2 Evaluation Metrics Computed
- **Confusion Matrix**: Multi-class $K \times K$ matrix.
- **Class-Weighted & Macro-Averaged Precision, Recall, and F1**:
  $$\text{Precision}_k = \frac{\text{TP}_k}{\text{TP}_k + \text{FP}_k}, \quad \text{Recall}_k = \frac{\text{TP}_k}{\text{TP}_k + \text{FN}_k}, \quad F1_k = 2 \cdot \frac{\text{Precision}_k \cdot \text{Recall}_k}{\text{Precision}_k + \text{Recall}_k}$$
- **False Positive Rate on Benign Traffic**:
  $$\text{FPR} = \frac{\text{FP}_{\text{benign}}}{\text{FP}_{\text{benign}} + \text{TN}_{\text{benign}}}$$
- **Detection Latency**: Median and 99th percentile inference latency in milliseconds per flow.
- **Experiment Artifact Log**: Persists hyperparameter configurations, test splits, and metric snapshots in JSON format.
