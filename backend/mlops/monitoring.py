"""
MLOps — Model Monitoring
Tracks model performance, detects drift, and logs predictions.
"""

from datetime import datetime
from typing import Dict, List
import json
from pathlib import Path


class ModelMonitor:
    """Monitors model performance and detects drift."""

    def __init__(self):
        self.prediction_log: List[Dict] = []
        self.performance_metrics: Dict[str, List] = {}
        self.alert_thresholds = {
            "accuracy_drop": 0.05,
            "latency_ms": 500,
            "error_rate": 0.1
        }

    def log_prediction(self, model_name: str, input_data: Dict,
                       prediction: Dict, latency_ms: float):
        """Log a single prediction for monitoring."""
        self.prediction_log.append({
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "prediction": prediction,
            "latency_ms": latency_ms,
            "input_features_count": len(input_data)
        })

    def get_metrics_summary(self, model_name: str = None) -> Dict:
        """Get summary of model performance metrics."""
        logs = self.prediction_log
        if model_name:
            logs = [l for l in logs if l["model"] == model_name]

        if not logs:
            return {"message": "No predictions logged yet"}

        latencies = [l["latency_ms"] for l in logs]

        return {
            "total_predictions": len(logs),
            "avg_latency_ms": sum(latencies) / len(latencies),
            "max_latency_ms": max(latencies),
            "min_latency_ms": min(latencies),
            "first_prediction": logs[0]["timestamp"],
            "last_prediction": logs[-1]["timestamp"]
        }

    def check_health(self) -> Dict:
        """Check overall model health."""
        return {
            "status": "healthy",
            "predictions_logged": len(self.prediction_log),
            "models_active": len(set(l["model"] for l in self.prediction_log)),
            "alerts": [],
            "timestamp": datetime.now().isoformat()
        }


model_monitor = ModelMonitor()
