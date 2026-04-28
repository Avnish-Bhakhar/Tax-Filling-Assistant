"""
Application Configuration Module
Centralized configuration for the AI Tax Filing Assistant.
"""

import os
from pathlib import Path


class Config:
    """Application configuration with environment variable support."""

    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    APP_DIR = Path(__file__).resolve().parent
    DATA_DIR = APP_DIR / "data"
    MODELS_DIR = BASE_DIR / "trained_models"
    UPLOAD_DIR = BASE_DIR / "uploads"
    LOG_DIR = BASE_DIR / "logs"

    # Server
    HOST = os.getenv("APP_HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))
    DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"

    # Frontend
    FRONTEND_DIR = BASE_DIR.parent / "frontend"

    # Model settings
    REGIME_MODEL_PATH = MODELS_DIR / "regime_classifier.pkl"
    LIABILITY_MODEL_PATH = MODELS_DIR / "liability_predictor.pkl"
    DOCUMENT_MODEL_PATH = MODELS_DIR / "document_classifier.h5"
    CHATBOT_MODEL_PATH = MODELS_DIR / "chatbot_model.pkl"
    CHATBOT_VECTORIZER_PATH = MODELS_DIR / "chatbot_vectorizer.pkl"

    # Data files
    TAXPAYERS_CSV = DATA_DIR / "sample_taxpayers.csv"
    TAX_SLABS_JSON = DATA_DIR / "tax_slabs_2024.json"
    DEDUCTIONS_JSON = DATA_DIR / "deductions_catalog.json"
    CHAT_INTENTS_JSON = DATA_DIR / "chat_intents.json"
    TAX_GLOSSARY_JSON = DATA_DIR / "tax_glossary.json"

    # AI Settings
    MAX_CHAT_HISTORY = 50
    SEARCH_MAX_DEPTH = 20
    BAYESIAN_THRESHOLD = 0.7

    # Privacy & Ethics
    DATA_RETENTION_DAYS = 30
    ANONYMIZE_LOGS = True
    EXPLAINABILITY_ENABLED = True

    # MLOps
    MODEL_VERSION = "1.0.0"
    MODEL_REGISTRY_PATH = MODELS_DIR / "registry.json"

    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories if they don't exist."""
        for dir_path in [cls.MODELS_DIR, cls.UPLOAD_DIR, cls.LOG_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
