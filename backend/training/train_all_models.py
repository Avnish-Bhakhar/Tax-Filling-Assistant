"""
Master Training Script — Train All AI Models
"""

import sys
import os
import time
from pathlib import Path

# Setup paths
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import Config
Config.ensure_dirs()


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def train_regime_classifier():
    """Train the tax regime classification model."""
    print_header("Training Tax Regime Classifier (ML Classification)")
    from app.models.tax_regime_classifier import TaxRegimeClassifier

    classifier = TaxRegimeClassifier()
    metrics = classifier.train(
        data_path=str(Config.TAXPAYERS_CSV),
        save_path=str(Config.REGIME_MODEL_PATH)
    )

    if 'error' in metrics:
        print(f"❌ Error: {metrics['error']}")
        return False

    print(f"✅ Accuracy: {metrics['accuracy']}")
    print(f"   CV Score: {metrics['cv_mean']} ± {metrics['cv_std']}")
    print(f"   Train/Test: {metrics['train_size']}/{metrics['test_size']}")
    print(f"   Top features: {list(metrics['feature_importance'].keys())[:5]}")
    print(f"   Saved to: {Config.REGIME_MODEL_PATH}")
    return True


def train_liability_predictor():
    """Train the tax liability prediction model."""
    print_header("Training Tax Liability Predictor (ML Regression)")
    from app.models.liability_predictor import TaxLiabilityPredictor

    predictor = TaxLiabilityPredictor()
    metrics = predictor.train(
        data_path=str(Config.TAXPAYERS_CSV),
        save_path=str(Config.LIABILITY_MODEL_PATH)
    )

    if 'error' in metrics:
        print(f"❌ Error: {metrics['error']}")
        return False

    print(f"✅ R² Score: {metrics['r2_score']}")
    print(f"   MAE: ₹{metrics['mae']:,.0f}")
    print(f"   RMSE: ₹{metrics['rmse']:,.0f}")
    print(f"   CV R²: {metrics['cv_r2_mean']} ± {metrics['cv_r2_std']}")
    print(f"   Saved to: {Config.LIABILITY_MODEL_PATH}")
    return True


def train_document_classifier():
    """Train the document classification neural network."""
    print_header("Training Document Classifier (Deep Learning)")
    from app.models.document_classifier import DocumentClassifier

    classifier = DocumentClassifier()
    save_path = str(Config.DOCUMENT_MODEL_PATH).replace('.h5', '.pkl')
    metrics = classifier.train(save_path=save_path)

    if 'error' in metrics:
        print(f"❌ Error: {metrics['error']}")
        return False

    print(f"✅ Accuracy: {metrics['accuracy']}")
    print(f"   Architecture: {' → '.join(metrics['architecture']['layers'])}")
    print(f"   Iterations: {metrics['n_iterations']}")
    print(f"   Train/Test: {metrics['train_samples']}/{metrics['test_samples']}")
    print(f"   Saved to: {save_path}")
    return True


def train_chatbot():
    """Train the chatbot intent classifier."""
    print_header("Training Chatbot NLP Engine")
    from app.models.chatbot_engine import ChatbotEngine

    chatbot = ChatbotEngine(str(Config.CHAT_INTENTS_JSON))
    metrics = chatbot.train(
        intents_path=str(Config.CHAT_INTENTS_JSON),
        save_path=str(Config.CHATBOT_MODEL_PATH)
    )

    if 'error' in metrics:
        print(f"❌ Error: {metrics['error']}")
        return False

    print(f"✅ Intents: {metrics['n_intents']}")
    print(f"   Patterns: {metrics['n_patterns']}")
    print(f"   Architecture: {metrics['architecture']}")
    print(f"   Saved to: {Config.CHATBOT_MODEL_PATH}")
    return True


def test_state_space_search():
    """Test the A* state space search."""
    print_header("Testing A* State-Space Search")
    from app.models.state_space_search import tax_search

    sample_data = {
        'name': 'Test User',
        'pan': 'ABCPK1234M',
        'annual_income': 1200000,
        'basic_salary': 600000,
        'hra_received': 300000,
        'rent_paid': 20000,
        'metro_city': True
    }

    result = tax_search.a_star_search(sample_data)

    if isinstance(result, dict) and 'optimal_path' in result:
        print(f"✅ Optimal path found!")
        print(f"   Total steps: {result['total_steps']}")
        print(f"   Total cost: {result['total_cost']}")
        print(f"   Nodes explored: {result['nodes_explored']}")
        print(f"   Path: {' → '.join(s['step_name'] for s in result['optimal_path'])}")
        return True
    else:
        print(f"❌ Search failed: {result}")
        return False


def test_bayesian_network():
    """Test the Bayesian network."""
    print_header("Testing Bayesian Network")
    from app.models.bayesian_network import bayesian_network

    sample_data = {
        'annual_income': 1500000,
        'investments_80c': 150000,
        'medical_insurance_80d': 25000,
        'home_loan_interest': 200000,
        'education_loan_interest': 0,
        'donations_80g': 10000,
        'nps_contribution': 50000,
        'regime_choice': 'old'
    }

    result = bayesian_network.calculate_audit_risk(sample_data)
    print(f"✅ Audit Risk Assessment:")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Probability: {result['audit_probability']}%")
    print(f"   Factors: {len(result['risk_factors'])}")
    print(f"   Methodology: {result['methodology']}")
    return True


def main():
    print("\n" + "🤖 " * 20)
    print("  AI TAX FILING ASSISTANT — MODEL TRAINING PIPELINE")
    print("🤖 " * 20)

    start_time = time.time()
    results = {}

    # Train all models
    results['regime_classifier'] = train_regime_classifier()
    results['liability_predictor'] = train_liability_predictor()
    results['document_classifier'] = train_document_classifier()
    results['chatbot'] = train_chatbot()

    # Test non-trainable models
    results['state_space_search'] = test_state_space_search()
    results['bayesian_network'] = test_bayesian_network()

    # Summary
    elapsed = time.time() - start_time
    print_header("TRAINING SUMMARY")

    for name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {status} — {name.replace('_', ' ').title()}")

    print(f"\n  Total time: {elapsed:.1f}s")
    print(f"  Models directory: {Config.MODELS_DIR}")

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    print(f"  Results: {success_count}/{total_count} successful")

    if success_count == total_count:
        print("\n  🎉 All models trained and tested successfully!")
        print("  ▶ Run the server: cd backend && python -m app.main")
    else:
        print("\n  ⚠️  Some models failed. Install dependencies: pip install -r requirements.txt")

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
