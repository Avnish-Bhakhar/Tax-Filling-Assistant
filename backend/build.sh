#!/usr/bin/env bash
# exit on error
set -o errexit

cd backend

pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Create directories
mkdir -p trained_models logs uploads

# Train all models
python training/train_all_models.py
