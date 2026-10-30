"""Alert Prioritization Engine implementing hybrid triage rules."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel


class PriorityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class TriageResult(BaseModel):
    is_alert: bool
    priority: PriorityLevel
    attack_class: str
    confidence: float
    anomaly_score: float
    is_anomaly: bool
    rule_matched: str
    action_recommendation: str


class AlertTriageEngine:
    """Evaluates multi-model outputs against triage rules matrix."""

    HIGH_IMPACT_ATTACKS = {
        "DDoS",
        "DoS_Hulk",
        "DoS_GoldenEye",
        "Infiltration",
        "Botnet",
    }

    CREDENTIAL_ATTACKS = {
        "FTP-Patator",
        "SSH-Patator",
        "Web_Attack_Brute_Force",
        "Web_Attack_XSS",
    }

    RECON_ATTACKS = {
        "PortScan",
    }

    def __init__(self, rules_config: Optional[Dict[str, Any]] = None):
        self.rules_config = rules_config or {}

    def triage(
        self,
        supervised_class: str,
        supervised_confidence: float,
        anomaly_score: float,
        is_anomaly: bool,
    ) -> TriageResult:
        """Evaluates hybrid metrics and returns prioritized alert level."""
        
        # Rule 1: High confidence destructive attacks (Critical)
        if (
            supervised_class in self.HIGH_IMPACT_ATTACKS
            and supervised_confidence >= 0.80
        ):
            return TriageResult(
                is_alert=True,
                priority=PriorityLevel.CRITICAL,
                attack_class=supervised_class,
                confidence=supervised_confidence,
                anomaly_score=anomaly_score,
                is_anomaly=is_anomaly,
                rule_matched="RULE_001_HIGH_IMPACT_EXPLOIT",
                action_recommendation="Immediate SOC intervention required. High-impact destructive exploit detected.",
            )

        # Rule 2: Moderate confidence destructive or credential attacks (High)
        if (
            (supervised_class in self.HIGH_IMPACT_ATTACKS and supervised_confidence >= 0.50 and anomaly_score >= 0.65)
            or (supervised_class in self.CREDENTIAL_ATTACKS and supervised_confidence >= 0.70)
        ):
            return TriageResult(
                is_alert=True,
                priority=PriorityLevel.HIGH,
                attack_class=supervised_class,
                confidence=supervised_confidence,
                anomaly_score=anomaly_score,
                is_anomaly=is_anomaly,
                rule_matched="RULE_002_CREDENTIAL_OR_SEVERE_ATTACK",
                action_recommendation="Escalate for investigation. High confidence brute force or active exploit attempt.",
            )

        # Rule 3: Novel Zero-Day Suspicion (Unsupervised Anomaly on Benign Traffic) (High)
        if supervised_class == "BENIGN" and anomaly_score >= 0.85:
            return TriageResult(
                is_alert=True,
                priority=PriorityLevel.HIGH,
                attack_class="SUSPECTED_ZERO_DAY",
                confidence=supervised_confidence,
                anomaly_score=anomaly_score,
                is_anomaly=True,
                rule_matched="RULE_003_NOVEL_UNSUPERVISED_ANOMALY",
                action_recommendation="Potential zero-day exploit or unprecedented protocol anomaly. Review feature attributions.",
            )

        # Rule 4: Reconnaissance / PortScan or Moderate Unknown Anomaly (Medium)
        if (
            (supervised_class in self.RECON_ATTACKS and supervised_confidence >= 0.60)
            or (supervised_class == "BENIGN" and 0.65 <= anomaly_score < 0.85)
        ):
            return TriageResult(
                is_alert=True,
                priority=PriorityLevel.MEDIUM,
                attack_class=supervised_class if supervised_class != "BENIGN" else "UNUSUAL_TRAFFIC_DEVIATION",
                confidence=supervised_confidence,
                anomaly_score=anomaly_score,
                is_anomaly=is_anomaly,
                rule_matched="RULE_004_MODERATE_ANOMALY_OR_SCAN",
                action_recommendation="Monitor and correlate with host logs. Possible reconnaissance or traffic divergence.",
            )

        # Rule 5: Low confidence attack classification (Low)
        if supervised_class != "BENIGN" and supervised_confidence >= 0.40:
            return TriageResult(
                is_alert=True,
                priority=PriorityLevel.LOW,
                attack_class=supervised_class,
                confidence=supervised_confidence,
                anomaly_score=anomaly_score,
                is_anomaly=is_anomaly,
                rule_matched="RULE_005_LOW_CONFIDENCE_MALICIOUS",
                action_recommendation="Log for trend analysis. Low confidence indicator.",
            )

        # Default: Benign Operational Baseline (Info)
        return TriageResult(
            is_alert=False,
            priority=PriorityLevel.INFO,
            attack_class="BENIGN",
            confidence=supervised_confidence,
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            rule_matched="RULE_BENIGN_BASELINE",
            action_recommendation="Normal baseline operational traffic. No action required.",
        )
