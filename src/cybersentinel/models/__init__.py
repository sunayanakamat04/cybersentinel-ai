"""Models Module for Supervised Classification and Unsupervised Anomaly Detection."""

from cybersentinel.models.classifier import SupervisedClassifier
from cybersentinel.models.anomaly import UnsupervisedAnomalyDetector

__all__ = ["SupervisedClassifier", "UnsupervisedAnomalyDetector"]
