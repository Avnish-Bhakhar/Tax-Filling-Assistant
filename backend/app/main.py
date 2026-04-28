"""
AI-Powered Intelligent Tax Filing Assistant
============================================
Main FastAPI Application Entry Point

This application serves both the REST API backend and the
static frontend files. All AI models, NLP chatbot, and
tax computation services are integrated here.

Author: AI Tax Filing Assistant Team
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import Config
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger("main")

# Create FastAPI application
app = FastAPI(
    title="AI Tax Filing Assistant",
    description="AI-Powered Intelligent Tax Filing Assistant with Conversational Chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
Config.ensure_dirs()

# ─── Register API Routes ────────────────────────────────────
from app.api.tax_routes import router as tax_router
from app.api.chat_routes import router as chat_router
from app.api.analysis_routes import router as analysis_router
from app.api.document_routes import router as document_router
from app.api.simulator_routes import router as simulator_router

app.include_router(tax_router)
app.include_router(chat_router)
app.include_router(analysis_router)
app.include_router(document_router)
app.include_router(simulator_router)

# ─── Load AI Models on Startup ──────────────────────────────
@app.on_event("startup")
async def load_models():
    """Load trained ML models on application startup."""
    logger.info("🚀 Starting AI Tax Filing Assistant v1.0.0")

    # Load tax slabs
    from app.services.tax_calculator import tax_calculator
    tax_calculator.load_slabs(str(Config.TAX_SLABS_JSON))
    logger.info("✅ Tax slabs loaded")

    # Load deduction catalog
    from app.models.deduction_recommender import deduction_recommender
    deduction_recommender.load_catalog(str(Config.DEDUCTIONS_JSON))
    logger.info("✅ Deduction catalog loaded")

    # Try loading trained models
    from app.models.tax_regime_classifier import regime_classifier
    if Config.REGIME_MODEL_PATH.exists():
        regime_classifier.load_model(str(Config.REGIME_MODEL_PATH))
        logger.info("✅ Regime classifier loaded")
    else:
        logger.info("⚠️  Regime classifier not trained yet — using rule-based fallback")

    from app.models.liability_predictor import liability_predictor
    if Config.LIABILITY_MODEL_PATH.exists():
        liability_predictor.load_model(str(Config.LIABILITY_MODEL_PATH))
        logger.info("✅ Liability predictor loaded")
    else:
        logger.info("⚠️  Liability predictor not trained — using formula-based fallback")

    from app.models.document_classifier import document_classifier
    doc_model_path = str(Config.DOCUMENT_MODEL_PATH).replace('.h5', '.pkl')
    if Path(doc_model_path).exists():
        document_classifier.load_model(doc_model_path)
        logger.info("✅ Document classifier loaded")
    else:
        logger.info("⚠️  Document classifier not trained — using rule-based fallback")

    from app.models.chatbot_engine import ChatbotEngine
    if Config.CHATBOT_MODEL_PATH.exists():
        logger.info("✅ Chatbot model available")
    else:
        logger.info("⚠️  Chatbot model not trained — using rule-based intent matching")

    logger.info("🎉 All systems ready! Server is running.")


# ─── Health & Info Endpoints ─────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "AI Tax Filing Assistant"
    }


@app.get("/api/model-status")
async def model_status():
    """Check status of all AI models."""
    from app.models.tax_regime_classifier import regime_classifier
    from app.models.liability_predictor import liability_predictor
    from app.models.document_classifier import document_classifier

    return {
        "status": "success",
        "models": {
            "regime_classifier": {
                "trained": regime_classifier.is_trained,
                "type": "Random Forest + Gradient Boosting Ensemble",
                "metrics": regime_classifier.training_metrics if regime_classifier.is_trained else None
            },
            "liability_predictor": {
                "trained": liability_predictor.is_trained,
                "type": "Gradient Boosting Regressor",
                "metrics": liability_predictor.training_metrics if liability_predictor.is_trained else None
            },
            "document_classifier": {
                "trained": document_classifier.is_trained,
                "type": "Deep Neural Network (MLP 256-128-64)",
                "metrics": document_classifier.training_metrics if document_classifier.is_trained else None
            },
            "chatbot": {
                "trained": Config.CHATBOT_MODEL_PATH.exists(),
                "type": "Attention-Enhanced MLP Intent Classifier"
            },
            "state_space_search": {
                "active": True,
                "type": "A* Search Algorithm"
            },
            "bayesian_network": {
                "active": True,
                "type": "Bayesian Network with CPTs"
            },
            "deduction_recommender": {
                "active": True,
                "type": "Heuristic Optimization"
            }
        }
    }


@app.get("/api/prompt-templates")
async def get_prompt_templates():
    """Get available prompt engineering templates."""
    from app.services.prompt_templates import prompt_engine
    return {
        "status": "success",
        "data": prompt_engine.get_all_templates_info()
    }


@app.get("/api/privacy-notice")
async def get_privacy_notice():
    """Get the privacy notice."""
    from app.utils.privacy import privacy_manager
    return {
        "status": "success",
        "data": {
            "notice": privacy_manager.generate_privacy_notice(),
            "data_categories": {
                "sensitive": list(privacy_manager.SENSITIVE_FIELDS),
                "financial": list(privacy_manager.FINANCIAL_FIELDS)
            }
        }
    }


@app.get("/api/glossary")
async def get_glossary():
    """Get the tax glossary."""
    import json
    try:
        with open(Config.TAX_GLOSSARY_JSON, 'r') as f:
            glossary = json.load(f)
        return {"status": "success", "data": glossary}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ─── Serve Frontend ─────────────────────────────────────────
# Mount static files
frontend_dir = Config.FRONTEND_DIR
if frontend_dir.exists():
    app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")
    if (frontend_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        """Serve the main frontend page."""
        return FileResponse(str(frontend_dir / "index.html"))
else:
    @app.get("/")
    async def no_frontend():
        return {"message": "Frontend not found. API is available at /docs"}


# ─── Global Exception Handler ───────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An unexpected error occurred. Please try again."}
    )


# ─── Run Server ─────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )
