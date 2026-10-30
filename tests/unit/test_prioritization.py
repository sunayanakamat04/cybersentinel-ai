"""Unit tests for prioritization triage rules."""

from cybersentinel.prioritization.engine import AlertTriageEngine, PriorityLevel


def test_triage_critical_destructive_attack():
    engine = AlertTriageEngine()
    result = engine.triage(
        supervised_class="DDoS",
        supervised_confidence=0.92,
        anomaly_score=0.75,
        is_anomaly=True,
    )
    assert result.is_alert is True
    assert result.priority == PriorityLevel.CRITICAL
    assert "HIGH_IMPACT" in result.rule_matched


def test_triage_zero_day_unsupervised_anomaly():
    engine = AlertTriageEngine()
    result = engine.triage(
        supervised_class="BENIGN",
        supervised_confidence=0.99,
        anomaly_score=0.91,
        is_anomaly=True,
    )
    assert result.is_alert is True
    assert result.priority == PriorityLevel.HIGH
    assert result.attack_class == "SUSPECTED_ZERO_DAY"
    assert "NOVEL_UNSUPERVISED_ANOMALY" in result.rule_matched


def test_triage_portscan_medium():
    engine = AlertTriageEngine()
    result = engine.triage(
        supervised_class="PortScan",
        supervised_confidence=0.75,
        anomaly_score=0.45,
        is_anomaly=False,
    )
    assert result.is_alert is True
    assert result.priority == PriorityLevel.MEDIUM


def test_triage_benign_info():
    engine = AlertTriageEngine()
    result = engine.triage(
        supervised_class="BENIGN",
        supervised_confidence=0.98,
        anomaly_score=0.20,
        is_anomaly=False,
    )
    assert result.is_alert is False
    assert result.priority == PriorityLevel.INFO
