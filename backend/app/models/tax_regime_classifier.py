"""
Tax Regime Classifier — Machine Learning Classification Model
=============================================================
Implements a Random Forest + Gradient Boosting ensemble to recommend
the optimal tax regime (Old vs New) based on taxpayer profile.

Features used:
- Income level, age, city tier
- Deductions (80C, 80D, HRA, home loan, education loan)
- Employment type, NPS contribution

The model provides confidence scores and feature importance for explainability.
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class TaxRegimeClassifier:
    """
    ML Classification model to recommend Old vs New tax regime.

    Uses an ensemble of Random Forest and Gradient Boosting classifiers
    to predict the optimal tax regime based on the taxpayer's financial profile.
    """

    FEATURE_COLUMNS = [
        'annual_income', 'age', 'city_tier', 'investments_80c',
        'medical_insurance_80d', 'home_loan_interest', 'education_loan_interest',
        'donations_80g', 'nps_contribution', 'rent_paid', 'metro_city',
        'hra_received', 'savings_interest', 'professional_tax',
        'leave_travel_allowance', 'other_income'
    ]

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.label_encoder = LabelEncoder() if SKLEARN_AVAILABLE else None
        self.feature_importance = {}
        self.is_trained = False
        self.training_metrics = {}

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare and engineer features from raw data."""
        features = pd.DataFrame()

        for col in self.FEATURE_COLUMNS:
            if col in df.columns:
                features[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                features[col] = 0

        # Feature engineering
        features['total_deductions'] = (
            features['investments_80c'] + features['medical_insurance_80d'] +
            features['home_loan_interest'] + features['education_loan_interest'] +
            features['donations_80g'] + features['nps_contribution']
        )
        features['deduction_to_income_ratio'] = (
            features['total_deductions'] / features['annual_income'].clip(lower=1)
        )
        features['effective_hra_benefit'] = features['hra_received'] * features['metro_city'].apply(
            lambda x: 0.5 if x else 0.4
        )
        features['income_bracket'] = pd.cut(
            features['annual_income'],
            bins=[0, 500000, 750000, 1000000, 1500000, 2000000, float('inf')],
            labels=[0, 1, 2, 3, 4, 5]
        ).astype(float)

        return features.values

    def train(self, data_path: str, save_path: Optional[str] = None) -> Dict:
        """
        Train the regime classification model.

        Args:
            data_path: Path to the training CSV file
            save_path: Optional path to save the trained model

        Returns:
            Dictionary with training metrics
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not installed"}

        # Load data
        df = pd.read_csv(data_path)

        # Prepare features and labels
        X = self.prepare_features(df)
        y = self.label_encoder.fit_transform(df['regime_chosen'])

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        # Create ensemble model
        rf = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=5,
            random_state=42, n_jobs=-1
        )
        gb = GradientBoostingClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1,
            random_state=42
        )

        self.model = VotingClassifier(
            estimators=[('rf', rf), ('gb', gb)],
            voting='soft'
        )

        # Train
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        # Cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)

        # Feature importance (from Random Forest component)
        rf_model = self.model.named_estimators_['rf']
        feature_names = self.FEATURE_COLUMNS + [
            'total_deductions', 'deduction_to_income_ratio',
            'effective_hra_benefit', 'income_bracket'
        ]
        self.feature_importance = dict(zip(
            feature_names, rf_model.feature_importances_
        ))

        self.is_trained = True
        self.training_metrics = {
            'accuracy': round(accuracy, 4),
            'cv_mean': round(cv_scores.mean(), 4),
            'cv_std': round(cv_scores.std(), 4),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'feature_importance': {k: round(v, 4) for k, v in
                                   sorted(self.feature_importance.items(),
                                          key=lambda x: x[1], reverse=True)[:10]},
            'classes': list(self.label_encoder.classes_),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }

        # Save model
        if save_path:
            self.save_model(save_path)

        return self.training_metrics

    def predict(self, user_data: Dict) -> Dict:
        """
        Predict the recommended tax regime for a user.

        Args:
            user_data: Dictionary with user's financial details

        Returns:
            Dictionary with prediction, confidence, and explanation
        """
        if not self.is_trained:
            return self._rule_based_prediction(user_data)

        # Prepare input
        df = pd.DataFrame([user_data])
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)

        # Predict with probabilities
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]

        regime = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(max(probabilities) * 100)

        return {
            'recommended_regime': regime,
            'confidence': round(confidence, 2),
            'probabilities': {
                cls: round(float(prob) * 100, 2)
                for cls, prob in zip(self.label_encoder.classes_, probabilities)
            },
            'feature_importance': self.feature_importance,
            'model_type': 'ML Ensemble (Random Forest + Gradient Boosting)'
        }

    def _rule_based_prediction(self, user_data: Dict) -> Dict:
        """Fallback rule-based prediction when model isn't trained."""
        income = user_data.get('annual_income', 0)
        total_deductions = (
            user_data.get('investments_80c', 0) +
            user_data.get('medical_insurance_80d', 0) +
            user_data.get('home_loan_interest', 0) +
            user_data.get('education_loan_interest', 0) +
            user_data.get('donations_80g', 0) +
            user_data.get('nps_contribution', 0) +
            user_data.get('hra_received', 0) * 0.4  # Approximate HRA exemption
        )

        # Rule: If deductions > threshold, old regime is better
        threshold = 375000  # Approximate break-even point
        if total_deductions > threshold:
            regime = 'old'
            confidence = min(95, 60 + (total_deductions - threshold) / 10000)
        else:
            regime = 'new'
            confidence = min(95, 60 + (threshold - total_deductions) / 10000)

        return {
            'recommended_regime': regime,
            'confidence': round(confidence, 2),
            'probabilities': {
                'old': round(confidence if regime == 'old' else 100 - confidence, 2),
                'new': round(confidence if regime == 'new' else 100 - confidence, 2)
            },
            'feature_importance': {
                'total_deductions': 0.35,
                'annual_income': 0.25,
                'hra_received': 0.15,
                'home_loan_interest': 0.10,
                'investments_80c': 0.08,
                'medical_insurance_80d': 0.07
            },
            'model_type': 'Rule-based (ML model not trained)'
        }

    def save_model(self, path: str):
        """Save trained model to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_importance': self.feature_importance,
            'training_metrics': self.training_metrics
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

    def load_model(self, path: str) -> bool:
        """Load trained model from disk."""
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoder = model_data['label_encoder']
            self.feature_importance = model_data['feature_importance']
            self.training_metrics = model_data.get('training_metrics', {})
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


# Module-level instance
regime_classifier = TaxRegimeClassifier()
