# AI-Powered Intelligent Tax Filing Assistant

> 🤖 A production-level, full-stack AI tax filing system with Conversational Chatbot, Machine Learning, NLP, Deep Learning, Bayesian Networks, and Interactive Visualizations.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3-orange) ![Plotly](https://img.shields.io/badge/Plotly-5.18-purple)

---

## 🎯 Project Overview

This system helps Indian taxpayers file their income taxes intelligently using 7+ AI/ML components:

| AI Domain | Implementation | Module |
|-----------|---------------|--------|
| **State-Space Search** | A* algorithm for optimal filing path | `state_space_search.py` |
| **ML Classification** | Random Forest + Gradient Boosting ensemble | `tax_regime_classifier.py` |
| **ML Regression** | Gradient Boosting Regressor (XGBoost-style) | `liability_predictor.py` |
| **Bayesian Network** | Conditional Probability Tables + Bayes' theorem | `bayesian_network.py` |
| **Deep Learning** | Multi-Layer Perceptron (256-128-64) | `document_classifier.py` |
| **NLP + Chatbot** | TF-IDF + Attention + Intent Classification | `chatbot_engine.py` |
| **Generative AI** | Template-based + Chain-of-Thought reasoning | `generative_engine.py` |
| **Heuristic Optimization** | Greedy deduction maximization | `deduction_recommender.py` |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/CSS/JS)                    │
│  ┌──────┐  ┌────────┐  ┌──────────┐  ┌───────┐  ┌──────┐  │
│  │Filing│  │Chatbot │  │Dashboard │  │ Sim.  │  │ Docs │  │
│  └──┬───┘  └───┬────┘  └────┬─────┘  └───┬───┘  └──┬───┘  │
└─────┼──────────┼────────────┼─────────────┼─────────┼───────┘
      │          │            │             │         │
┌─────┴──────────┴────────────┴─────────────┴─────────┴───────┐
│                    FastAPI REST API                           │
│  tax_routes │ chat_routes │ analysis │ simulator │ documents │
├──────────────────────────────────────────────────────────────┤
│                    AI/ML MODEL LAYER                         │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐          │
│  │A* Search│ │ML Classif│ │Bayesian│ │Deep Learn│          │
│  │         │ │ML Regress│ │Network │ │NLP Chat  │          │
│  └─────────┘ └──────────┘ └────────┘ └──────────┘          │
├──────────────────────────────────────────────────────────────┤
│                    SERVICES LAYER                            │
│  Tax Calculator │ Generative AI │ Prompt Engine │ Doc Proc  │
├──────────────────────────────────────────────────────────────┤
│  UTILS: Logger(Privacy) │ Explainability │ Privacy(DPDPA)   │
├──────────────────────────────────────────────────────────────┤
│  DATA: taxpayers.csv │ tax_slabs.json │ intents.json │ etc  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
cd tax-filing-assistant/backend
pip install -r requirements.txt
```

### Step 2: Train AI Models
```bash
python training/train_all_models.py
```
This trains 4 models:
- ✅ Tax Regime Classifier (Random Forest + Gradient Boosting)
- ✅ Tax Liability Predictor (Gradient Boosting Regressor)
- ✅ Document Classifier (Deep Neural Network 256-128-64)
- ✅ Chatbot Intent Classifier (Attention-Enhanced MLP)

### Step 3: Start the Server
```bash
python -m app.main
```

### Step 4: Open in Browser
Navigate to: **http://localhost:8000**

API Docs available at: **http://localhost:8000/docs**

---

## 📁 Project Structure

```
tax-filing-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point
│   │   ├── config.py                   # Configuration
│   │   ├── api/                        # REST API routes
│   │   │   ├── tax_routes.py           # Tax calculation endpoints
│   │   │   ├── chat_routes.py          # Chatbot endpoints
│   │   │   ├── analysis_routes.py      # Dashboard data endpoints
│   │   │   ├── document_routes.py      # Document processing endpoints
│   │   │   └── simulator_routes.py     # What-if simulator endpoints
│   │   ├── models/                     # AI/ML models
│   │   │   ├── state_space_search.py   # A* search algorithm
│   │   │   ├── tax_regime_classifier.py# ML classification
│   │   │   ├── liability_predictor.py  # ML regression
│   │   │   ├── bayesian_network.py     # Probabilistic reasoning
│   │   │   ├── deduction_recommender.py# Heuristic optimization
│   │   │   ├── document_classifier.py  # Deep learning (DNN)
│   │   │   └── chatbot_engine.py       # NLP chatbot
│   │   ├── services/                   # Business logic
│   │   │   ├── tax_calculator.py       # Tax computation engine
│   │   │   ├── generative_engine.py    # GenAI summaries
│   │   │   ├── prompt_templates.py     # Prompt engineering
│   │   │   └── document_processor.py   # Document parsing
│   │   ├── utils/                      # Utilities
│   │   │   ├── logger.py              # Privacy-aware logging
│   │   │   ├── explainability.py      # AI decision explanations
│   │   │   └── privacy.py            # Data protection (DPDPA)
│   │   └── data/                      # Datasets & configs
│   │       ├── sample_taxpayers.csv   # 130+ synthetic records
│   │       ├── tax_slabs_2024.json    # FY 2024-25 tax slabs
│   │       ├── deductions_catalog.json# All deduction sections
│   │       ├── chat_intents.json      # 25+ chatbot intents
│   │       └── tax_glossary.json      # 50+ tax terms
│   ├── training/                      # Model training scripts
│   │   └── train_all_models.py        # Master training pipeline
│   ├── mlops/                         # ML Operations
│   │   ├── model_registry.py          # Model versioning
│   │   ├── pipeline.py                # Training pipeline
│   │   └── monitoring.py              # Performance monitoring
│   ├── trained_models/                # Serialized model files
│   ├── requirements.txt               # Python dependencies
│   └── Dockerfile                     # Container deployment
├── frontend/
│   ├── index.html                     # Main SPA
│   ├── css/
│   │   ├── main.css                   # Design system
│   │   ├── chat.css                   # Chatbot styles
│   │   └── dashboard.css              # Dashboard styles
│   └── js/
│       ├── api.js                     # API client
│       ├── app.js                     # Main controller
│       ├── chat.js                    # Chatbot UI
│       ├── dashboard.js               # Plotly charts
│       ├── simulator.js               # What-if simulator
│       └── document.js                # Document processing
├── docs/                              # Documentation
│   ├── architecture_diagram.md
│   ├── execution_guide.md
│   ├── ethics_statement.md
│   └── prompt_design.md
└── README.md                          # This file
```

---

## 🤖 AI Components Explained

### 1. A* State-Space Search
Models tax filing as a graph where states are filing steps and edges are transitions. Uses an admissible heuristic based on data completeness to find the optimal filing path.

### 2. ML Classification (Tax Regime)
Ensemble of Random Forest and Gradient Boosting classifiers predicts whether Old or New tax regime is optimal. Features include income, deductions, HRA, and investment patterns.

### 3. ML Regression (Tax Liability)
Gradient Boosting Regressor predicts expected tax liability with confidence intervals. Uses feature engineering including log-income and deduction ratios.

### 4. Bayesian Network
Implements Bayes' theorem with Conditional Probability Tables for audit risk assessment. Calculates P(Audit | Income, Deductions, Regime) with likelihood modifiers.

### 5. Deep Learning (Document Classifier)
Multi-Layer Perceptron Neural Network (256→128→64) with ReLU activation, dropout, and early stopping. Classifies tax documents into 7 categories.

### 6. NLP Chatbot Engine
Full pipeline: Tokenization → TF-IDF Embeddings → Attention Mechanism → Neural Intent Classification → Entity Extraction → Response Generation.

### 7. Generative AI
Template-based generation with:
- **Few-shot prompting**: Example Q&A pairs
- **Role-based prompting**: Tax expert persona
- **Chain-of-thought**: Step-by-step reasoning

### 8. Deduction Recommender
Greedy heuristic optimization that maximizes tax savings by identifying unused deductions, ranked by marginal tax rate impact.

---

## 📊 Features

- ✅ **Conversational Chatbot** — NLP-powered tax assistant
- ✅ **Tax Calculator** — Both old & new regime (FY 2024-25)
- ✅ **AI Regime Recommendation** — ML + Bayesian ensemble
- ✅ **Tax Liability Prediction** — ML regression with confidence
- ✅ **Smart Deductions** — AI-optimized deduction recommendations
- ✅ **Audit Risk Assessment** — Bayesian probability analysis
- ✅ **Document Processing** — Deep learning classification + NLP extraction
- ✅ **What-If Simulator** — Interactive tax scenario explorer
- ✅ **Plotly Dashboards** — Income vs deductions, tax breakdown
- ✅ **A* Filing Path** — Optimal step-by-step filing navigation
- ✅ **Generative Summaries** — AI-written tax reports
- ✅ **Explainable AI** — Feature importance, confidence scores
- ✅ **Privacy Protection** — PII redaction, consent management
- ✅ **MLOps Pipeline** — Training, evaluation, registration, monitoring

---

## 🔒 Ethics & Responsible AI

- All AI decisions include transparent explanations
- Feature importance visible for ML recommendations
- Confidence scores accompany all predictions
- PII (PAN, Aadhaar, email) automatically redacted in logs
- Data retention policy with consent management
- Clear disclaimer: AI recommendations supplement, not replace, professional tax advice

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tax/calculate` | Calculate tax liability |
| POST | `/api/tax/recommend-regime` | ML regime recommendation |
| POST | `/api/tax/predict-liability` | Predict tax amount |
| POST | `/api/tax/recommend-deductions` | AI deduction tips |
| POST | `/api/tax/audit-risk` | Bayesian audit assessment |
| POST | `/api/tax/generate-summary` | GenAI tax summary |
| POST | `/api/chat/message` | Send chatbot message |
| POST | `/api/chat/reset` | Reset conversation |
| POST | `/api/analysis/income-vs-deductions` | Chart data |
| POST | `/api/analysis/tax-breakdown` | Tax breakdown data |
| POST | `/api/analysis/filing-path` | A* search path |
| POST | `/api/documents/classify` | DL document classification |
| POST | `/api/documents/extract` | NLP data extraction |
| POST | `/api/simulator/what-if` | What-if scenarios |
| POST | `/api/simulator/compare-regimes` | Regime comparison |
| GET | `/api/model-status` | AI model status |
| GET | `/api/health` | Health check |
| GET | `/api/glossary` | Tax glossary |

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| ML | scikit-learn (RandomForest, GradientBoosting, MLP) |
| NLP | NLTK, TF-IDF, Custom Attention |
| Visualization | Plotly.js |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Data | pandas, NumPy |
| MLOps | Custom pipeline, model registry |
| Deployment | Docker |

---

## 📄 License

This project is developed for academic purposes as part of the AI coursework (Semester 4).

---

*Built with ❤️ and AI*
