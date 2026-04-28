"""
MLOps — Model Registry
Tracks model versions, metrics, and deployment status.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ModelRegistry:
    """Model versioning and registry system."""

    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or str(
            Path(__file__).resolve().parent.parent / "trained_models" / "registry.json"
        )
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"models": {}, "deployments": []}

    def _save_registry(self):
        Path(self.registry_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def register_model(self, name: str, version: str, metrics: Dict,
                       model_path: str, model_type: str) -> Dict:
        """Register a trained model in the registry."""
        if name not in self.registry["models"]:
            self.registry["models"][name] = {"versions": []}

        entry = {
            "version": version,
            "registered_at": datetime.now().isoformat(),
            "metrics": metrics,
            "model_path": model_path,
            "model_type": model_type,
            "status": "registered",
            "stage": "staging"
        }

        self.registry["models"][name]["versions"].append(entry)
        self.registry["models"][name]["latest"] = version
        self._save_registry()

        return entry

    def promote_model(self, name: str, version: str, stage: str = "production") -> bool:
        """Promote a model version to production."""
        if name not in self.registry["models"]:
            return False

        for v in self.registry["models"][name]["versions"]:
            if v["version"] == version:
                v["stage"] = stage
                v["promoted_at"] = datetime.now().isoformat()
                self._save_registry()
                return True
        return False

    def get_model_info(self, name: str) -> Optional[Dict]:
        """Get info about a model."""
        return self.registry["models"].get(name)

    def get_all_models(self) -> Dict:
        """Get all registered models."""
        return self.registry["models"]

    def log_deployment(self, model_name: str, version: str, environment: str):
        """Log a model deployment event."""
        self.registry["deployments"].append({
            "model": model_name,
            "version": version,
            "environment": environment,
            "deployed_at": datetime.now().isoformat()
        })
        self._save_registry()


model_registry = ModelRegistry()
