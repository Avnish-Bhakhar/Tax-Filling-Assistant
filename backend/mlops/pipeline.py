"""
MLOps — Training Pipeline
Orchestrates the full model lifecycle: data → train → evaluate → deploy
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TrainingPipeline:
    """
    ML Training Pipeline implementing the model lifecycle:
    1. Data Validation
    2. Feature Engineering
    3. Model Training
    4. Evaluation
    5. Registration
    6. Deployment
    """

    def __init__(self):
        self.pipeline_log = []

    def _log(self, stage: str, message: str, status: str = "info"):
        entry = {
            "stage": stage,
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        self.pipeline_log.append(entry)
        icon = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}.get(status, "•")
        print(f"  {icon} [{stage}] {message}")

    def validate_data(self, data_path: str) -> bool:
        """Stage 1: Validate training data."""
        self._log("data_validation", f"Validating data at {data_path}")

        import pandas as pd
        try:
            df = pd.read_csv(data_path)
            n_rows = len(df)
            n_cols = len(df.columns)
            null_counts = df.isnull().sum().sum()

            self._log("data_validation",
                      f"Data loaded: {n_rows} rows, {n_cols} columns, {null_counts} nulls",
                      "success")

            if n_rows < 50:
                self._log("data_validation", "WARNING: Small dataset may lead to overfitting", "warning")

            return True
        except Exception as e:
            self._log("data_validation", f"Data validation failed: {e}", "error")
            return False

    def run_pipeline(self, model_name: str, data_path: str, model_path: str) -> Dict:
        """Run the complete training pipeline for a model."""
        self._log("pipeline", f"Starting pipeline for: {model_name}")

        # Stage 1: Data Validation
        if not self.validate_data(data_path):
            return {"status": "failed", "stage": "data_validation"}

        # Stage 2-4: Train & Evaluate
        self._log("training", "Training model...")

        from app.config import Config

        metrics = {}
        if model_name == "regime_classifier":
            from app.models.tax_regime_classifier import TaxRegimeClassifier
            model = TaxRegimeClassifier()
            metrics = model.train(data_path, model_path)
        elif model_name == "liability_predictor":
            from app.models.liability_predictor import TaxLiabilityPredictor
            model = TaxLiabilityPredictor()
            metrics = model.train(data_path, model_path)

        if 'error' in metrics:
            self._log("training", f"Training failed: {metrics['error']}", "error")
            return {"status": "failed", "stage": "training"}

        self._log("evaluation", f"Model metrics: {metrics}", "success")

        # Stage 5: Register
        from mlops.model_registry import model_registry
        model_registry.register_model(
            name=model_name,
            version=f"1.0.{datetime.now().strftime('%Y%m%d%H%M')}",
            metrics=metrics,
            model_path=model_path,
            model_type=metrics.get('model_type', 'ML Model')
        )
        self._log("registration", "Model registered in registry", "success")

        # Stage 6: Deploy (simulate)
        model_registry.log_deployment(model_name, "latest", "local")
        self._log("deployment", "Model deployed to local environment", "success")

        return {
            "status": "success",
            "model": model_name,
            "metrics": metrics,
            "pipeline_log": self.pipeline_log
        }


pipeline = TrainingPipeline()
