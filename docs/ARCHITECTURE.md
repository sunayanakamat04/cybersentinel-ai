# CyberSentinel AI: System Architecture & Technical Blueprint

---

## 1. High-Level System Architecture

CyberSentinel AI adopts an asynchronous, modular microservice-style architecture designed to ingest network flow records, execute parallel machine learning inferences (supervised classification + unsupervised anomaly detection), compute SHAP-based feature attributions, triage alert priorities, and surface actionable telemetry to security analysts.

```mermaid
flowchart TD
    subgraph INGESTION["1. Ingestion and Preprocessing Layer"]
        DS1["Raw PCAP / NetFlow Sources"] --> INGEST["Flow Validator and Sanitizer"]
        DS2["CIC-IDS2017 / 2018 CSV Dumps"] --> INGEST
        DS3["Live Streaming Flow Events (FastAPI REST)"] --> INGEST
        INGEST --> CLEAN["Missing Value Imputation and Inf Replacer"]
        CLEAN --> SCALE["RobustScaler / StandardScaler Transform"]
    end

    subgraph DUAL_ENGINE["2. Dual-Engine Detection Core"]
        SCALE --> SUP_PIPE["Supervised Classifier (XGBoost Multiclass)"]
        SCALE --> UNSUP_PIPE["Unsupervised Detector (Isolation Forest / OC-SVM)"]
        
        SUP_PIPE -->|"Attack Probabilities and Class Prediction"| FUSION["Alert Prioritization and Triage Engine"]
        UNSUP_PIPE -->|"Anomaly Score (0 to 1)"| FUSION
    end

    subgraph XAI_LAYER["3. Explainable AI (XAI) Engine"]
        FUSION -->|"If Malicious or Anomaly"| SHAP_EXEC["SHAP TreeExplainer"]
        SCALE -.->|"Feature Matrix"| SHAP_EXEC
        SHAP_EXEC -->|"Top-K Attributions and Base Value"| ATTR_RECORD["Local Feature Importance Vector"]
    end

    subgraph PERSISTENCE["4. Data and State Persistence Layer"]
        FUSION --> DB_SAVE["Alert and Flow Record Ingestion"]
        ATTR_RECORD --> DB_SAVE
        DB_SAVE --> PG_DB[("PostgreSQL / SQLite Database")]
        PG_DB --> REPO["Alert Repository and Historical Audit Log"]
    end

    subgraph DRIFT_ENGINE["5. Continuous Drift Monitoring"]
        SCALE --> DRIFT_WIN["Sliding Window Buffer (N=1000)"]
        REF_DATA[("Baseline Reference Distribution")] --> DRIFT_CALC["KS-Test and PSI Estimator"]
        DRIFT_WIN --> DRIFT_CALC
        DRIFT_CALC -->|"Drift Metrics and Status"| DRIFT_LOG["Drift Alerts and Metric Store"]
    end

    subgraph PRESENTATION["6. Web Dashboard and Analyst Cockpit"]
        REPO --> REST_API["FastAPI REST and WebSocket Endpoints"]
        DRIFT_LOG --> REST_API
        REST_API --> UI_DASH["Interactive Web Dashboard (HTML5 / Bootstrap 5 / Chart.js)"]
        UI_DASH --> ANALYST["Security Operations Center (SOC) Analyst"]
    end
```

---

## 2. End-to-End Data Flow Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Sensor as Network Sensor / Client
    participant API as FastAPI Ingestion Gateway
    participant Pre as Preprocessing Pipeline
    participant Super as XGBoost Classifier
    participant Anom as Isolation Forest
    participant Triage as Prioritization Engine
    participant XAI as SHAP TreeExplainer
    participant DB as PostgreSQL Store
    actor Analyst as SOC Analyst Dashboard

    Sensor->>API: POST /api/v1/predict/single (Flow Record JSON)
    API->>Pre: Validate schema and clean values
    Pre->>Pre: Transform with fitted Scaler
    
    par Parallel ML Evaluation
        Pre->>Super: Predict class probabilities
        Super-->>Triage: Return Top Class and Probability
    and
        Pre->>Anom: Compute Isolation Path Depth
        Anom-->>Triage: Return Anomaly Score
    end

    Triage->>Triage: Apply Severity Matrix Rules
    
    opt Priority Elevated
        Triage->>XAI: Compute local Shapley contributions
        XAI-->>Triage: Return Top-5 influential features
    end

    Triage->>DB: Persist Flow, Alert, Explanations, and Timestamp
    DB-->>API: Persisted Alert UUID
    API-->>Sensor: Return 200 OK Response
    
    Analyst->>API: GET /api/v1/alerts
    API-->>Analyst: Real-time Alert Feed with Feature Explanations
```

---

## 3. Dual-Engine Decision Fusion Logic

The system does not rely on a single classifier. Instead, it fuses supervised predictions (for recognized attacks) and unsupervised scores (for deviations from the benign baseline) through a rule-based priority state machine:

```mermaid
flowchart TD
    START(["Incoming Flow Feature Vector x"]) --> SUP_TEST{"Supervised XGBoost Prediction"}
    
    SUP_TEST -->|"Class is Not BENIGN"| CHECK_CONF{"Supervised Probability >= 0.80?"}
    CHECK_CONF -->|"Yes"| HIGH_IMPACT{"Is Attack High Impact? (DDoS, Infiltration, Botnet)"}
    HIGH_IMPACT -->|"Yes"| CRIT["Priority 1: CRITICAL (Immediate Escalation)"]
    HIGH_IMPACT -->|"No"| HIGH_KNOWN["Priority 2: HIGH (Brute Force, Exploits)"]
    
    CHECK_CONF -->|"No: 0.50 to 0.80"| RECON{"Is Recon or Scanning (PortScan)?"}
    RECON -->|"Yes"| MED_KNOWN["Priority 3: MEDIUM (Port Scan / Probing)"]
    RECON -->|"No"| LOW_CONF["Priority 4: LOW (Low-Confidence Alert)"]

    SUP_TEST -->|"Class is BENIGN"| ANOM_TEST{"Unsupervised Anomaly Score S"}
    ANOM_TEST -->|"S >= 0.85"| ZERO_DAY["Priority 2: HIGH (Potential Zero-Day Novel Threat)"]
    ANOM_TEST -->|"0.65 to 0.85"| MOD_ANOM["Priority 3: MEDIUM (Unusual Flow Variance)"]
    ANOM_TEST -->|"S < 0.65"| PASS_BENIGN["Priority 5: INFO (Normal Benign Traffic)"]

    CRIT --> GEN_ALERT["Generate Prioritized Alert Record"]
    HIGH_KNOWN --> GEN_ALERT
    ZERO_DAY --> GEN_ALERT
    MED_KNOWN --> GEN_ALERT
    MOD_ANOM --> GEN_ALERT
    LOW_CONF --> GEN_ALERT
    PASS_BENIGN --> LOG_TELEMETRY["Log Flow Telemetry (No Alert)"]
```

---

## 4. SHAP Feature Attribution Pipeline

For every prioritized alert, CyberSentinel AI executes a SHAP (SHapley Additive exPlanations) attribution step to convert the model's inner decision into an understandable visual breakdown for the security analyst:

```mermaid
flowchart LR
    INPUT_FLOW["Normalized Flow Features"] --> TREE_EXP["XGBoost TreeExplainer (Tree SHAP)"]
    TREE_EXP --> COND_EXP["Calculate Shapley Values for each feature"]
    COND_EXP --> RANK["Sort by Absolute Contribution"]
    RANK --> TOP5["Extract Top-5 Explaining Features"]
    
    TOP5 --> FORMAT["Render Attribution Card with Feature Impact"]
    FORMAT --> UI_CARD["Dashboard Explanatory Visual (Waterfall / Bar Chart)"]
```

### Interpretation Example:
- **Alert**: `DDoS_Hulk` (Priority: CRITICAL)
- **Top 5 Contributing Features**:
  1. `Flow Packets/s = 193,406` ($\phi_1 = +3.42$ push towards attack)
  2. `Flow Bytes/s = 23,076,923` ($\phi_2 = +2.18$)
  3. `Fwd PSH Flags = 350` ($\phi_3 = +1.89$)
  4. `Average Packet Size = 119.6` ($\phi_4 = +0.74$)
  5. `Init_Win_bytes_forward = 65535` ($\phi_5 = +0.31$)

---

## 5. Traffic Drift Monitoring Architecture

Network distributions shift over time. To prevent undetected model decay, CyberSentinel AI monitors both continuous feature distributions and categorical alert rates:

```mermaid
flowchart TD
    subgraph TRAFFIC_CAPTURE["Sliding Window Buffer"]
        FLOWS["Incoming Live Flows"] --> BUFFER["In-Memory Flow Window (N=1000)"]
    end

    subgraph STATISTICAL_TESTS["Statistical Drift Tests"]
        BUFFER --> KS_TEST["Kolmogorov-Smirnov (KS) Test (Continuous Features)"]
        BASELINE[("Baseline Training Reference (Parquet)")] --> KS_TEST
        
        BUFFER --> PSI_TEST["Population Stability Index (PSI) (Binned Distributions)"]
        BASELINE --> PSI_TEST

        BUFFER --> RATE_TEST["Alert Frequency Ratio Test (Spike Detection)"]
    end

    subgraph TRIAGE_ACTION["Drift Alerting and Governance"]
        KS_TEST --> EVAL_DRIFT{"Is p-value below 0.05 or PSI above 0.20?"}
        PSI_TEST --> EVAL_DRIFT
        RATE_TEST --> EVAL_DRIFT
        
        EVAL_DRIFT -->|"No"| STABLE["System State: STABLE (Normal Operations)"]
        EVAL_DRIFT -->|"Yes"| DRIFT_WARN["System State: DRIFT DETECTED"]
        DRIFT_WARN --> NOTIFY["Notify SOC Lead and Trigger Drift Dashboard Banner"]
        NOTIFY --> MANUAL["Human-in-the-Loop Model Validation and Retraining Review"]
        MANUAL -.->|"Explicit Approval Required"| RETRAIN["Controlled Offline Retraining"]
    end
```

---

## 6. Database Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    FLOW_RECORD ||--o| ALERT : triggers
    ALERT ||--|{ EXPLANATION_FEATURE : contains
    ALERT ||--o{ INVESTIGATION_NOTE : has
    MODEL_RUN ||--o{ ALERT : generated_by
    MODEL_RUN ||--o{ DRIFT_SNAPSHOT : evaluated_in

    FLOW_RECORD {
        uuid id PK
        string flow_id
        timestamp timestamp
        string src_ip
        int src_port
        string dst_ip
        int dst_port
        int protocol
        float flow_duration
        int total_fwd_packets
        int total_bwd_packets
        float flow_bytes_per_sec
        float flow_packets_per_sec
        jsonb raw_features
        timestamp created_at
    }

    ALERT {
        uuid id PK
        uuid flow_record_id FK
        string priority
        string attack_class
        float supervised_confidence
        float anomaly_score
        string status
        string assigned_analyst
        string rule_triggered
        timestamp created_at
        timestamp updated_at
    }

    EXPLANATION_FEATURE {
        uuid id PK
        uuid alert_id FK
        string feature_name
        float feature_value
        float shap_value
        int rank
    }

    INVESTIGATION_NOTE {
        uuid id PK
        uuid alert_id FK
        string author
        text note
        string disposition
        timestamp created_at
    }

    MODEL_RUN {
        uuid id PK
        string model_type
        string model_version
        jsonb hyperparameters
        float precision
        float recall
        float f1_score
        float false_positive_rate
        float latency_ms
        timestamp trained_at
    }

    DRIFT_SNAPSHOT {
        uuid id PK
        uuid model_run_id FK
        timestamp evaluated_at
        string feature_name
        float ks_statistic
        float ks_p_value
        float psi_value
        boolean drift_flagged
    }
```

---

## 7. Component Interaction & Tech Stack Mapping

| Layer / Subsystem | Primary Technologies | Key Responsibilities |
|---|---|---|
| **Data Ingestion** | Python, Pydantic, NumPy, pandas | Flow schema validation, missing value imputation, type casting, batch/stream parsing |
| **Supervised Classifier** | XGBoost, scikit-learn | Multi-class intrusion classification, confidence estimation, model version tracking |
| **Anomaly Detector** | scikit-learn (IsolationForest / OC-SVM) | Baseline profiling, outlier scoring, novel traffic flag generation |
| **Alert Triage** | Python, PyYAML | Severity rule matrix evaluation, hybrid alert prioritization (P1-P5) |
| **Explainable AI (XAI)** | SHAP (`TreeExplainer`) | Fast local feature attribution, waterfall data transformation |
| **Drift Monitoring** | SciPy, NumPy, custom PSI routines | Two-sample KS test, binned PSI distribution shift, anomaly rate tracking |
| **API Backend** | FastAPI, Uvicorn, SQLAlchemy | High-concurrency REST endpoints, async database sessions, OpenAPI docs |
| **Database** | PostgreSQL / SQLite | ACID persistence for flows, alerts, SHAP attributions, investigation notes |
| **Frontend UI** | HTML5, Modern CSS, Bootstrap 5, Chart.js | Real-time security telemetry, interactive alert triage, SHAP visualizations |
