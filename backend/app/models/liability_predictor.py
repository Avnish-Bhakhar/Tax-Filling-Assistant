"""
Tax Liability Predictor — Machine Learning Regression Model
============================================================
Predicts the expected tax liability amount using XGBoost-style
Gradient Boosting Regression with feature engineering.

Uses taxpayer financial profile to estimate the tax amount,
providing both point estimates and confidence intervals.
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Optional

try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class TaxLiabilityPredictor:
    """
    ML Regression model to predict tax liability amount.

    Uses Gradient Boosting Regression (XGBoost-style) to predict
    the expected tax amount based on income and deductions profile.
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
        self.is_trained = False
        self.training_metrics = {}
        self.feature_importance = {}

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features with engineering."""
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
        features['taxable_income_approx'] = (
            features['annual_income'] - features['total_deductions'] - 50000  # std deduction
        ).clip(lower=0)
        features['deduction_ratio'] = (
            features['total_deductions'] / features['annual_income'].clip(lower=1)
        )
        features['income_log'] = np.log1p(features['annual_income'])
        features['income_squared'] = features['annual_income'] ** 2 / 1e12  # Scaled

        return features.values

    def train(self, data_path: str, save_path: Optional[str] = None) -> Dict:
        """Train the liability prediction model."""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not installed"}

        df = pd.read_csv(data_path)

        X = self.prepare_features(df)
        y = df['actual_tax_paid'].values

        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        # Gradient Boosting Regressor
        self.model = GradientBoostingRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            min_samples_split=5, min_samples_leaf=3,
            subsample=0.8, random_state=42,
            loss='huber'  # Robust to outliers
        )

        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred = np.maximum(y_pred, 0)  # Tax can't be negative

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_scaled, y, cv=5, scoring='r2'
        )

        # Feature importance
        feature_names = self.FEATURE_COLUMNS + [
            'total_deductions', 'taxable_income_approx',
            'deduction_ratio', 'income_log', 'income_squared'
        ]
        self.feature_importance = dict(zip(
            feature_names, self.model.feature_importances_
        ))

        self.is_trained = True
        self.training_metrics = {
            'mae': round(mae, 2),
            'rmse': round(rmse, 2),
            'r2_score': round(r2, 4),
            'cv_r2_mean': round(cv_scores.mean(), 4),
            'cv_r2_std': round(cv_scores.std(), 4),
            'feature_importance': {k: round(v, 4) for k, v in
                                   sorted(self.feature_importance.items(),
                                          key=lambda x: x[1], reverse=True)[:10]},
            'train_size': len(X_train),
            'test_size': len(X_test)
        }

        if save_path:
            self.save_model(save_path)

        return self.training_metrics

    def predict(self, user_data: Dict) -> Dict:
        """
        Predict tax liability for a user.

        Returns point estimate and confidence interval.
        """
        if not self.is_trained:
            return self._formula_based_prediction(user_data)

        df = pd.DataFrame([user_data])
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)

        prediction = max(0, float(self.model.predict(X_scaled)[0]))

        # Estimate confidence interval using training error
        mae = self.training_metrics.get('mae', prediction * 0.1)
        lower = max(0, prediction - 1.96 * mae)
        upper = prediction + 1.96 * mae

        return {
            'predicted_liability': round(prediction, 0),
            'confidence_interval': {
                'lower': round(lower, 0),
                'upper': round(upper, 0)
            },
            'feature_importance': self.feature_importance,
            'model_type': 'Gradient Boosting Regressor',
            'metrics': {
                'r2_score': self.training_metrics.get('r2_score', 'N/A'),
                'mae': self.training_metrics.get('mae', 'N/A')
            }
        }

    def _formula_based_prediction(self, user_data: Dict) -> Dict:
        """Fallback formula-based prediction using actual tax slab calculation."""
        income = user_data.get('annual_income', 0)
        deductions = (
            min(user_data.get('investments_80c', 0), 150000) +
            min(user_data.get('medical_insurance_80d', 0), 100000) +
            min(user_data.get('home_loan_interest', 0), 200000) +
            user_data.get('education_loan_interest', 0) +
            user_data.get('donations_80g', 0) * 0.5 +
            min(user_data.get('nps_contribution', 0), 50000)
        )

        # Old regime calculation
        taxable_old = max(0, income - 50000 - deductions)
        tax_old = self._calculate_slab_tax(taxable_old, 'old')

        # New regime calculation
        taxable_new = max(0, income - 75000)
        tax_new = self._calculate_slab_tax(taxable_new, 'new')

        predicted = min(tax_old, tax_new)

        return {
            'predicted_liability': round(predicted, 0),
            'confidence_interval': {
                'lower': round(predicted * 0.9, 0),
                'upper': round(predicted * 1.1, 0)
            },
            'old_regime_tax': round(tax_old, 0),
            'new_regime_tax': round(tax_new, 0),
            'feature_importance': {},
            'model_type': 'Formula-based (ML model not trained)'
        }

    def _calculate_slab_tax(self, taxable_income: float, regime: str) -> float:
        """Calculate tax using slab rates."""
        tax = 0
        if regime == 'old':
            if taxable_income > 1000000:
                tax += (taxable_income - 1000000) * 0.30
                taxable_income = 1000000
            if taxable_income > 500000:
                tax += (taxable_income - 500000) * 0.20
                taxable_income = 500000
            if taxable_income > 250000:
                tax += (taxable_income - 250000) * 0.05
        else:  # new
            if taxable_income > 1500000:
                tax += (taxable_income - 1500000) * 0.30
                taxable_income = 1500000
            if taxable_income > 1200000:
                tax += (taxable_income - 1200000) * 0.20
                taxable_income = 1200000
            if taxable_income > 1000000:
                tax += (taxable_income - 1000000) * 0.15
                taxable_income = 1000000
            if taxable_income > 700000:
                tax += (taxable_income - 700000) * 0.10
                taxable_income = 700000
            if taxable_income > 300000:
                tax += (taxable_income - 300000) * 0.05

        # Add cess
        tax = tax * 1.04
        return tax

    def save_model(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance,
            'training_metrics': self.training_metrics
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

    def load_model(self, path: str) -> bool:
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_importance = model_data['feature_importance']
            self.training_metrics = model_data.get('training_metrics', {})
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


# Module-level instance
liability_predictor = TaxLiabilityPredictor()
