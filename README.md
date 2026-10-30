<div align="center">

# 🛡️ CyberSentinel AI
### Adaptive Network Intrusion Detection System (NIDS)
**A Hybrid Machine Learning, Anomaly Detection & Explainable AI (XAI) Security Operations Platform**

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/API-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Supervised ML](https://img.shields.io/badge/Classifier-XGBoost-orange.svg?logo=xgboost)](https://xgboost.readthedocs.io/)
[![XAI](https://img.shields.io/badge/Explainability-SHAP-brightgreen.svg)](https://shap.readthedocs.io/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Project_Status-Architecture_%26_Scaffolding_Complete-success.svg)]()

[Problem Statement](docs/PROBLEM_STATEMENT.md) • [System Architecture](docs/ARCHITECTURE.md) • [Modules Specification](docs/MODULES_SPECIFICATION.md) • [Dataset Guide](docs/DATASET_GUIDE.md) • [API Specs](docs/API_SPECIFICATION.md) • [Team Roadmap](docs/TEAM_ROADMAP.md)

---

</div>

## 📌 Project Overview

**CyberSentinel AI** is a web-based network security decision-support platform that analyzes bidirectional network-flow records (NetFlow/IPFIX/CICFlowMeter format) to identify malicious and anomalous network traffic. 

Traditional signature-based Network Intrusion Detection Systems (NIDS) fail against zero-day and obfuscated attacks, while naive anomaly detection floods Security Operations Center (SOC) analysts with false alarms. CyberSentinel AI eliminates this trade-off through a **hybrid AI paradigm**:

1. **Supervised Multi-Class Classification (XGBoost)**: Accurately classifies known attack patterns (DDoS, DoS, Brute Force, Port Scans, Botnets, Infiltration).
2. **Unsupervised Anomaly Detection (Isolation Forest)**: Flags novel zero-day traffic diverging from the learned benign baseline.
3. **Automated Alert Prioritization Matrix**: Fuses classification probabilities, anomaly scores, and severity rules into tiered alerts (Critical, High, Medium, Low, Info) to mitigate alert fatigue.
4. **Feature-Level Explainability (SHAP)**: Explains the underlying statistical flow features that triggered each prediction using Shapley additive values.
5. **Continuous Traffic Drift Monitoring**: Monitors feature distribution shifts and alert spikes using the two-sample Kolmogorov-Smirnov (KS) test and Population Stability Index (PSI).
6. **Unified Web Dashboard**: Surfaces real-time alerts, flow metrics, and interactive visualizations built on HTML5, Bootstrap 5, and Chart.js.

> **Operational Principle**: CyberSentinel AI is engineered as an **analyst decision-support system**, not an autonomous blocker. Anomalies and model outputs represent actionable indicators for human investigation rather than definitive proof of malicious activity.

---

## 🎯 Problem Statement & Objectives

### Formal Problem Statement
> *"To design and develop an AI-based Network Intrusion Detection System that processes network-flow records, classifies known malicious traffic using supervised machine learning, identifies previously unseen or unusual traffic patterns using anomaly detection, and presents prioritized security alerts with feature-level explanations. The system shall support batch and streaming-style inference through a web-based interface, maintain historical alert records, and monitor changes in traffic patterns to assist security analysis using a centralized platform."*

### Key Objectives
- **Web-Based Analysis Platform**: Accept flow records from public benchmark datasets or authorized test environments and present telemetry on a modern dashboard.
- **Supervised Model**: Train and benchmark an XGBoost classifier for high-precision detection of known threat classes.
- **Unsupervised Anomaly Detection**: Implement Isolation Forest / density estimation to capture deviations from baseline benign traffic.
- **Intelligent Prioritization**: Merge model confidences and anomaly scores with configurable rules to prioritize alerts.
- **Transparent Explainability**: Provide feature-level explanations via SHAP so security analysts understand *why* an alert fired.
- **Empirical Rigor**: Evaluate against Precision, Recall, F1-Score, Confusion Matrices, False-Positive Rate (FPR), Detection Latency, and statistical drift indicators while strictly avoiding train-test session leakage.

---

## 🏗️ System Architecture

CyberSentinel AI operates on an asynchronous pipeline architecture connecting ingestion, dual-engine ML scoring, explanation synthesis, persistence, and analyst presentation:

```mermaid
flowchart TD
    subgraph INGESTION["1. Ingestion & Preprocessing"]
        CSV["Dataset Files (CIC-IDS2017)"] --> PRE["Flow Sanitizer & RobustScaler"]
        STREAM["Streaming REST API"] --> PRE
    end

    subgraph DUAL_ENGINE["2. Dual-Engine Detection Core"]
        PRE --> SUP["XGBoost Multi-Class Classifier"]
        PRE --> UNSUP["Isolation Forest Anomaly Detector"]
        
        SUP -->|Predicted Class & Confidence| TRIAGE["Priority Triage & Severity Matrix"]
        UNSUP -->|Anomaly Score [0, 1]| TRIAGE
    end

    subgraph EXPLAINABILITY["3. Explainable AI (XAI)"]
        TRIAGE -->|If Alert Prioritized| SHAP_EXP["SHAP TreeExplainer"]
        SHAP_EXP -->|Top-5 Flow Drivers| ENRICH["Enriched Alert Envelope"]
    end

    subgraph PERSISTENCE["4. Database & Drift Tracking"]
        ENRICH --> DB[("PostgreSQL / SQLite Storage")]
        PRE --> DRIFT["Traffic Drift Engine (KS-Test & PSI)"]
        DRIFT --> DB
    end

    subgraph PRESENTATION["5. Web Dashboard & API"]
        DB --> API["FastAPI REST Services"]
        API --> DASH["Web Dashboard (Bootstrap 5 & Chart.js)"]
        DASH --> ANALYST["SOC Security Analyst"]
    end
```

For the complete architectural design, sequence diagrams, and database schemas, see **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## 🧩 Proposed System Modules

The project is structured into eight distinct functional modules as outlined in the technical specification:

| Module | Name | Purpose | Primary Implementation File |
|:---:|---|---|---|
| **M1** | **Flow Ingestion & Preprocessor** | Schema validation, handling infinity/NaNs, RobustScaler transformation | `src/cybersentinel/ingestion/` |
| **M2** | **Supervised Intrusion Classifier** | Multi-class threat classification with probability scoring | `src/cybersentinel/models/classifier.py` |
| **M3** | **Unsupervised Anomaly Detector** | Baseline traffic profiling and novel outlier score estimation | `src/cybersentinel/models/anomaly.py` |
| **M4** | **Alert Prioritization & Management** | Rules-based triage matrix, alert lifecycle, and analyst audit trail | `src/cybersentinel/prioritization/` |
| **M5** | **Explainability Module (SHAP)** | Local feature attribution breakdown for every prioritized alert | `src/cybersentinel/explainability/` |
| **M6** | **Traffic Drift Monitoring** | Two-sample KS test and PSI tracking on continuous flow buffers | `src/cybersentinel/drift/` |
| **M7** | **Dashboard & Reporting** | Responsive web UI, Chart.js visualizations, and report exports | `src/cybersentinel/dashboard/` |
| **M8** | **Evaluation & Experiment Management** | Leakage-free validation, confusion matrices, latency, and FPR metrics | `src/cybersentinel/evaluation/` |

Detailed inputs, algorithms, outputs, and edge cases for each module are documented in **[docs/MODULES_SPECIFICATION.md](docs/MODULES_SPECIFICATION.md)**.

---

## 💡 Dual-Engine Detection & Priority Triage

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DUAL-ENGINE TRIAGE MATRIX                       │
├─────────────────────────┬──────────────────────┬───────────────────────┤
│ Supervised Output       │ Anomaly Score (S)    │ Actionable Priority   │
├─────────────────────────┼──────────────────────┼───────────────────────┤
│ DDoS / Botnet (P >= 0.8)│ Any                  │ 🔴 P1: CRITICAL       │
│ Brute Force (P >= 0.7)  │ Any                  │ 🟠 P2: HIGH           │
│ BENIGN                  │ S >= 0.85 (Zero-Day) │ 🟠 P2: HIGH (Zero-Day)│
│ PortScan (P >= 0.6)     │ Any                  │ 🟡 P3: MEDIUM         │
│ BENIGN                  │ 0.65 <= S < 0.85     │ 🟡 P3: MEDIUM         │
│ Attack (0.4 <= P < 0.6) │ S < 0.65             │ 🔵 P4: LOW            │
│ BENIGN                  │ S < 0.65             │ ⚪ P5: INFO (Log Only) │
└─────────────────────────┴──────────────────────┴───────────────────────┘
```

---

## 🔍 Explainable AI (SHAP) in Action

Black-box predictions undermine operational trust. CyberSentinel AI uses `shap.TreeExplainer` to calculate local Shapley values $\phi_i$ for each prioritized alert:

```
[ALERT #1042] DDoS_Hulk Attack Detected (Confidence: 96.4%, Priority: CRITICAL)
────────────────────────────────────────────────────────────────────────────────
Top Contributing Flow Features:
  1. Flow Packets/s = 193,406.59      [+3.42]  ████████████████████
  2. Flow Bytes/s = 23,076,923.07     [+2.18]  █████████████
  3. PSH Flag Count = 350             [+1.89]  ███████████
  4. Average Packet Size = 119.60     [+0.74]  ████
  5. Init_Win_bytes_forward = 65,535  [+0.31]  ██
────────────────────────────────────────────────────────────────────────────────
Analyst Takeaway: Flow demonstrates massive packet-rate flooding with push flags,
characteristic of HTTP Hulk denial-of-service starvation.
```

---

## 📊 Traffic Drift & Model Stability

To safeguard against performance degradation due to network evolution or seasonality, CyberSentinel AI continuously monitors live flow distributions against the training baseline:
- **Two-Sample Kolmogorov-Smirnov Test**: Tests whether incoming continuous feature distributions match the baseline null hypothesis ($p < 0.05$ indicates drift).
- **Population Stability Index (PSI)**: Quantifies binned population divergence ($\text{PSI} \ge 0.20$ flags significant drift).
- **Governance**: Drift flags alert the security team for validation; **no automatic model retraining is executed without human sign-off**.

---

## 🛠️ Technology Stack

| Layer | Tools & Frameworks |
|---|---|
| **Frontend** | HTML5, CSS3, Bootstrap 5, Chart.js, Jinja2 Templates |
| **Backend & REST API** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 |
| **Persistence & ORM** | PostgreSQL 15, SQLAlchemy 2.0, Alembic, SQLite (Local Dev) |
| **Data Science & ML** | pandas, NumPy, scikit-learn, XGBoost |
| **Explainability (XAI)** | SHAP (TreeExplainer) |
| **Statistical Drift** | SciPy (Kolmogorov-Smirnov test), custom PSI calculator |
| **DevOps & Containers** | Docker, Docker Compose |
| **Datasets** | CIC-IDS2017, CSE-CIC-IDS2018 (Canadian Institute for Cybersecurity) |

---

## 📂 Repository Structure

```
cybersentinel-ai/
├── .github/
│   └── workflows/
│       ├── ci.yml                     # Continuous integration workflow
│       └── docs.yml                   # Markdown link & schema validator
├── config/
│   ├── config.yaml                    # System settings, feature list, hyperparameters
│   ├── severity_rules.yaml            # Configurable alert priority rules
│   └── drift_config.yaml              # Statistical drift test thresholds (KS & PSI)
├── data/
│   ├── raw/                           # Raw CIC-IDS2017 / 2018 CSVs (gitignored)
│   ├── processed/                     # Normalized train/test Parquet partitions
│   └── samples/                       # Lightweight synthetic/sanitized flows for testing
│       ├── sample_benign_flows.json
│       └── sample_attack_flows.json
├── docker/
│   ├── Dockerfile.api                 # FastAPI backend container definition
│   └── docker-compose.yml             # Full stack (FastAPI + PostgreSQL)
├── docs/
│   ├── ARCHITECTURE.md                # System architecture, C4 diagrams, sequence flows
│   ├── PROBLEM_STATEMENT.md           # Formal problem statement & academic background
│   ├── MODULES_SPECIFICATION.md       # Deep technical spec for all 8 system modules
│   ├── DATASET_GUIDE.md               # Flow taxonomy, cleaning, and leakage prevention
│   ├── API_SPECIFICATION.md           # REST API endpoints, schemas, and payloads
│   └── TEAM_ROADMAP.md                # Work breakdown, roles, and sprint schedule
├── notebooks/                         # Research, exploration & modeling notebooks
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_supervised_classification_xgboost.ipynb
│   ├── 03_unsupervised_anomaly_detection.ipynb
│   ├── 04_explainable_ai_shap.ipynb
│   └── 05_traffic_drift_monitoring.ipynb
├── src/
│   └── cybersentinel/                 # Production Python package
│       ├── __init__.py
│       ├── config.py                  # Pydantic configuration loader
│       ├── ingestion/                 # M1: Data ingestion & preprocessor
│       ├── models/                    # M2 & M3: XGBoost & Isolation Forest
│       ├── prioritization/            # M4: Priority triage engine
│       ├── explainability/            # M5: SHAP feature attribution
│       ├── drift/                     # M6: Traffic drift monitor
│       ├── database/                  # PostgreSQL / SQLite models & CRUD
│       ├── api/                       # FastAPI routes & schemas
│       ├── dashboard/                 # M7: Web templates & static assets
│       └── evaluation/                # M8: Model evaluation & experiment tracking
├── tests/
│   ├── conftest.py
│   ├── unit/                          # Unit tests for preprocessor, rules, drift
│   └── integration/                   # API endpoint tests
├── .env.example                       # Environment configuration template
├── .gitignore                         # Comprehensive ignore rules
├── pyproject.toml                     # Python packaging and tool configuration
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Testing & development dependencies
├── LICENSE                            # MIT License
└── README.md                          # Repository overview & setup guide
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git
- Docker & Docker Compose *(optional, for containerized run)*

### 2. Clone the Repository
```bash
git clone https://github.com/your-org/cybersentinel-ai.git
cd cybersentinel-ai
```

### 3. Create a Virtual Environment
```bash
# On Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 5. Configure Environment Variables
```bash
# Copy example environment configuration
cp .env.example .env
```
*(By default, `.env` uses a local SQLite database for instant zero-dependency development. For production, supply PostgreSQL credentials).*

### 6. Run the Application
```bash
# Start FastAPI backend server and dashboard
uvicorn cybersentinel.api.main:app --reload --host 0.0.0.0 --port 8000
```
- **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Web Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 7. Run with Docker Compose
```bash
cd docker
docker-compose up --build
```

---

## 🧪 Testing & Quality Assurance

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run full test suite
pytest -v

# Run with test coverage
pytest --cov=cybersentinel tests/

# Run code linter
ruff check src/ tests/
```

---

## 👥 Team Development Roadmap

Implementation is organized across 5 coordinated sprints:

- **Sprint 0 (Week 1)**: Scaffolding, Dataset Acquisition (CIC-IDS2017), & Exploratory Data Analysis.
- **Sprint 1 (Weeks 2–3)**: Dual-Engine Model Training (XGBoost + Isolation Forest) & SHAP Integration.
- **Sprint 2 (Week 4)**: Asynchronous FastAPI Server, PostgreSQL Models, & Triage Rules Engine.
- **Sprint 3 (Week 5)**: Web Dashboard UI (Bootstrap 5 & Chart.js) & Traffic Drift Engine.
- **Sprint 4 (Week 6)**: Rigorous Benchmarking, Experiment Reporting, Docker Packaging, & Final Presentation.

For individual task allocations and definition-of-done criteria, see **[docs/TEAM_ROADMAP.md](docs/TEAM_ROADMAP.md)**.

---

## ⚖️ Ethical & Responsible Use

CyberSentinel AI is developed solely for defensive security operations, academic research, and authorized network monitoring:
- Datasets used must be publicly licensed benchmarks (e.g., CIC-IDS2017) or collected with explicit administrative authorization.
- Model predictions and anomaly scores are probabilistic decision-support signals designed to assist human analysts and must not be used as autonomous arbiters for punitive actions.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
