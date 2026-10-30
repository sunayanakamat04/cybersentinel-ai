# CyberSentinel AI: Problem Statement & Research Foundation

---

## 1. Executive Summary

Modern enterprise and cloud networks operate at gigabit-to-terabit scale, generating millions of continuous network-flow records every second. Traditional security perimeter defenses predominantly rely on **Signature-Based Intrusion Detection Systems (NIDS)** (such as Snort, Suricata, or Zeek). While signature matching is computationally efficient for cataloged and deterministic threats, it exhibits catastrophic vulnerability against **novel zero-day exploits, polymorphism, evasive port-hopping, and protocol obfuscation**.

Conversely, pure **unsupervised anomaly detection systems** flag any traffic divergence as malicious, overwhelming Security Operations Center (SOC) analysts with a tidal wave of false positives—a phenomenon known as **Alert Fatigue**. Furthermore, complex "black-box" machine learning algorithms frequently fail to gain operational adoption because security analysts cannot decipher *why* an alert was triggered or *which flow metrics* substantiate the threat.

**CyberSentinel AI** addresses this foundational challenge by engineering an **Adaptive, Explainable, Hybrid Network Intrusion Detection System**. By pairing high-precision **supervised gradient boosting (XGBoost)** for cataloged threat vectors with **unsupervised isolation/density estimators** for zero-day divergence, fused through an **automated alert triage matrix** and illuminated by **SHAP (SHapley Additive exPlanations)**, CyberSentinel AI provides a trustworthy, decision-support platform for modern cybersecurity operations.

---

## 2. Formal Problem Statement

> **"To design, develop, and empirically evaluate an AI-based Network Intrusion Detection System that ingests bidirectionally aggregated network-flow records, classifies known malicious traffic with high precision using supervised machine learning, flags novel or statistically abnormal traffic patterns using unsupervised anomaly detection, and generates prioritized security alerts enriched with feature-level SHAP explanations.**
>
> **The system shall support both high-throughput batch auditing and low-latency streaming-style inference via a modern asynchronous FastAPI architecture, maintain persistent historical audit trails in PostgreSQL, continuously monitor statistical traffic distribution drift to mitigate model staleness, and present real-time telemetry through an intuitive, analyst-centric web dashboard."**

---

## 3. The Core Dilemma in Modern Network Security

```
┌────────────────────────────────────────────────────────────────────────┐
│                        THE NIDS TRILEMMA                               │
│                                                                        │
│                    Detection Accuracy                                  │
│                          ▲                                             │
│                         / \                                            │
│                        /   \                                           │
│                       /     \                                          │
│                      /   ★   \  <-- CyberSentinel AI                   │
│                     /         \     (Balanced Hybrid Paradigm)         │
│                    /           \                                       │
│                   ▼─────────────▼                                      │
│      Operational Trust           Zero-Day Adaptability                 │
│      (Explainable XAI)           (Unsupervised Anomaly)                │
└────────────────────────────────────────────────────────────────────────┘
```

### Challenge 1: The Dual-Vector Threat Environment
- **Known Threats**: DoS/DDoS floods, SSH/FTP brute force attacks, reconnaissance port sweeps, and web exploits exhibit recognized statistical distributions (e.g., packet rate spikes, asymmetric forward/backward byte ratios, unusual TCP flag combinations).
- **Novel/Zero-Day Threats**: Emerging cyber campaigns employ novel command-and-control (C2) protocols, low-and-slow exfiltration, or tailored payloads that do not correspond to any labeled training class.

### Challenge 2: The Black-Box Transparency Gap
A prediction stating *"Confidence: 94.2% Malicious"* provides zero operational context. An incident responder must know:
- Did this trigger because of an abnormal SYN/ACK flag ratio?
- Was it caused by a 50,000 packet/sec surge on port 443?
- Or is the flow duration indicative of a Slowloris HTTP starvation attack?
Without feature-level interpretability (SHAP), analysts cannot validate alerts or configure firewall ACLs.

### Challenge 3: Concept & Covariate Traffic Drift
Network traffic distributions are non-stationary:
- Infrastructure updates, OS patches, work-from-home shifts, and seasonal spikes induce benign statistical shifts.
- If an IDS model remains static, false positive rates surge or detection recall decays.
- CyberSentinel AI implements automated drift tracking (Kolmogorov-Smirnov test and Population Stability Index) to alert engineers before performance degrades.

---

## 4. Mathematical Formulation

Let a bidirectional network-flow record be represented as a multidimensional vector:

$$\mathbf{x} = [x_1, x_2, \dots, x_d] \in \mathbb{R}^d$$

where $d \approx 78$ continuous and categorical flow features (flow duration, inter-arrival times, flag counts, byte throughput, header lengths).

### 4.1. Supervised Multiclass Classification
A supervised gradient boosted tree ensemble $f_{\text{sup}}(\mathbf{x})$ maps the input flow $\mathbf{x}$ to a probability distribution over $K$ discrete traffic classes:

$$\hat{\mathbf{p}} = f_{\text{sup}}(\mathbf{x}) = [\hat{p}_0, \hat{p}_1, \dots, \hat{p}_{K-1}], \quad \sum_{k=0}^{K-1} \hat{p}_k = 1$$

where $k=0$ represents `BENIGN`, and $k \in \{1, \dots, K-1\}$ represents recognized attack categories (DDoS, Patator, Botnet, Infiltration, etc.).

The predicted class $\hat{y}_{\text{sup}}$ and confidence $C_{\text{sup}}$ are:

$$\hat{y}_{\text{sup}} = \arg\max_k \hat{p}_k, \quad C_{\text{sup}} = \max_k \hat{p}_k$$

### 4.2. Unsupervised Novelty & Anomaly Detection
An unsupervised isolation estimator $g_{\text{unsup}}(\mathbf{x})$ computes an anomaly score $S_{\text{anomaly}}(\mathbf{x}) \in [0, 1]$ based on path-length isolation depth across random partitioning trees:

$$S_{\text{anomaly}}(\mathbf{x}) = 2^{-\frac{\mathbb{E}[h(\mathbf{x})]}{c(n)}}$$

where $h(\mathbf{x})$ is the tree traversal depth to isolate $\mathbf{x}$, and $c(n)$ is the average path length of an unsuccessful search in a Binary Search Tree (BST) constructed over $n$ baseline normal flows.

### 4.3. Unified Triage & Priority Function
The alert triage function $\mathcal{T}(\hat{y}_{\text{sup}}, C_{\text{sup}}, S_{\text{anomaly}}, \mathcal{R})$ assigns an actionable priority level:

$$\text{Priority} = \mathcal{T}(\hat{y}_{\text{sup}}, C_{\text{sup}}, S_{\text{anomaly}}, \mathcal{R}) \in \{\text{P1: CRITICAL}, \text{P2: HIGH}, \text{P3: MEDIUM}, \text{P4: LOW}, \text{P5: INFO}\}$$

governed by rule matrix $\mathcal{R}$.

### 4.4. Feature Attribution via Shapley Values
For a given prediction, the local contribution $\phi_i$ of feature $x_i$ satisfies efficiency, symmetry, and dummy properties:

$$f_{\text{sup}}(\mathbf{x}) = \phi_0 + \sum_{i=1}^{d} \phi_i(\mathbf{x})$$

where $\phi_0 = \mathbb{E}[f_{\text{sup}}(\mathbf{X})]$ is the expected baseline model output.

---

## 5. Scope, Constraints, and Ethical Boundaries

As specified in the project governance:
1. **Decision Support, Not Autonomic Blocking**: CyberSentinel AI provides high-fidelity decision support for security analysts; it does not automatically execute destructive firewall actions without human review.
2. **Authorized Test Datasets Only**: Training and benchmarking must use public research datasets (CIC-IDS2017, CSE-CIC-IDS2018) or explicitly authorized synthetic test ranges.
3. **Strict Train-Test Leakage Prevention**: Session-level flows generated by the same TCP connection must not be split across train and test partitions to prevent artificial metric inflation.
4. **Controlled Model Retraining**: Traffic drift detection triggers notification and analyst validation; the system **never** triggers unverified automated model retraining in production.
