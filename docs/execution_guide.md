# Execution Guide — Step-by-Step

## Prerequisites

- **Python 3.9+** installed
- **pip** package manager
- **Terminal/Command Prompt** access
- **Web Browser** (Chrome/Firefox recommended)

---

## Step 1: Navigate to Project

```bash
cd /path/to/tax-filing-assistant
```

## Step 2: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- FastAPI + Uvicorn (web server)
- scikit-learn (ML models)
- pandas + NumPy (data processing)
- NLTK (NLP tokenization)
- Plotly (visualization data)

## Step 3: Download NLTK Data (first time only)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

## Step 4: Train All AI Models

```bash
python training/train_all_models.py
```

Expected output:
```
  Training Tax Regime Classifier (ML Classification)
  ✅ Accuracy: 0.85+
  
  Training Tax Liability Predictor (ML Regression)
  ✅ R² Score: 0.95+
  
  Training Document Classifier (Deep Learning)
  ✅ Accuracy: 0.90+
  
  Training Chatbot NLP Engine
  ✅ Intents: 20+
  
  Testing A* State-Space Search
  ✅ Optimal path found!
  
  Testing Bayesian Network
  ✅ Audit Risk Assessment complete!
```

## Step 5: Start the Server

```bash
python -m app.main
```

Server starts at: `http://localhost:8000`

## Step 6: Open in Browser

- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Step 7: Using the Application

### Tax Filing Tab
1. Enter your income and deduction details
2. Click "Calculate Tax" for AI-powered computation
3. Click "AI Regime Recommendation" for ML analysis
4. Click "Smart Deduction Tips" for optimization

### AI Chatbot Tab
1. Type questions like "Which regime should I choose?"
2. The bot uses NLP to classify intent and generate responses
3. Follow-up suggestions appear after each response

### Dashboard Tab
1. Charts auto-populate from your tax filing data
2. See income vs deductions, regime comparison
3. View the A* filing path visualization

### Simulator Tab
1. Adjust sliders for income and deductions
2. See real-time tax impact under both regimes
3. Compare scenarios visually

### Documents Tab
1. Paste or upload document text
2. AI classifies document type using deep learning
3. NLP extracts structured data (PAN, salary, TDS, etc.)

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port 8000 in use | Change port in `config.py` or run with `--port 8001` |
| NLTK data missing | Run the NLTK download command from Step 3 |
| Models not found | Run `python training/train_all_models.py` first |
