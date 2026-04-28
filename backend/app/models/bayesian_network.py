"""
Bayesian Network Module — Probabilistic Reasoning for Tax Analysis
===================================================================
Implements Bayesian inference for:
1. Audit risk assessment: P(Audit | Income, Deductions, Regime)
2. Deduction benefit estimation: P(MaxBenefit | Profile)

Uses Bayes' theorem and conditional probability tables for
transparent probabilistic reasoning.
"""

from typing import Dict, List, Tuple
import math


class BayesianTaxNetwork:
    """
    Bayesian Network for tax-related probabilistic reasoning.

    Implements Bayes' theorem:
    P(A|B) = P(B|A) * P(A) / P(B)

    Nodes in the network:
    - Income Level (Low/Medium/High/VeryHigh)
    - Deduction Level (Low/Medium/High)
    - Regime Choice (Old/New)
    - Filing Accuracy (Accurate/Inaccurate)
    - Audit Risk (Low/Medium/High)
    """

    def __init__(self):
        # Prior probabilities
        self.priors = {
            'income_level': {
                'low': 0.30,       # < 5L
                'medium': 0.35,    # 5L-15L
                'high': 0.25,      # 15L-50L
                'very_high': 0.10  # > 50L
            },
            'deduction_level': {
                'low': 0.35,       # < 1.5L
                'medium': 0.40,    # 1.5L-4L
                'high': 0.25       # > 4L
            },
            'regime_choice': {
                'old': 0.45,
                'new': 0.55
            },
            'audit_base_rate': 0.02  # 2% general audit rate
        }

        # Conditional Probability Tables (CPTs)
        # P(Audit | Income, Deduction, Regime)
        self.cpt_audit = {
            ('low', 'low', 'new'): 0.005,
            ('low', 'low', 'old'): 0.008,
            ('low', 'medium', 'old'): 0.015,
            ('low', 'medium', 'new'): 0.010,
            ('low', 'high', 'old'): 0.035,
            ('low', 'high', 'new'): 0.025,
            ('medium', 'low', 'new'): 0.010,
            ('medium', 'low', 'old'): 0.012,
            ('medium', 'medium', 'old'): 0.020,
            ('medium', 'medium', 'new'): 0.015,
            ('medium', 'high', 'old'): 0.045,
            ('medium', 'high', 'new'): 0.030,
            ('high', 'low', 'new'): 0.025,
            ('high', 'low', 'old'): 0.030,
            ('high', 'medium', 'old'): 0.040,
            ('high', 'medium', 'new'): 0.035,
            ('high', 'high', 'old'): 0.075,
            ('high', 'high', 'new'): 0.050,
            ('very_high', 'low', 'new'): 0.050,
            ('very_high', 'low', 'old'): 0.060,
            ('very_high', 'medium', 'old'): 0.080,
            ('very_high', 'medium', 'new'): 0.070,
            ('very_high', 'high', 'old'): 0.150,
            ('very_high', 'high', 'new'): 0.100,
        }

        # P(Regime Benefit | Income, Deduction)
        self.cpt_regime_benefit = {
            ('low', 'low'): {'old': 0.35, 'new': 0.65},
            ('low', 'medium'): {'old': 0.50, 'new': 0.50},
            ('low', 'high'): {'old': 0.75, 'new': 0.25},
            ('medium', 'low'): {'old': 0.25, 'new': 0.75},
            ('medium', 'medium'): {'old': 0.45, 'new': 0.55},
            ('medium', 'high'): {'old': 0.80, 'new': 0.20},
            ('high', 'low'): {'old': 0.20, 'new': 0.80},
            ('high', 'medium'): {'old': 0.40, 'new': 0.60},
            ('high', 'high'): {'old': 0.85, 'new': 0.15},
            ('very_high', 'low'): {'old': 0.15, 'new': 0.85},
            ('very_high', 'medium'): {'old': 0.35, 'new': 0.65},
            ('very_high', 'high'): {'old': 0.70, 'new': 0.30},
        }

    def _categorize_income(self, income: float) -> str:
        """Categorize income into levels."""
        if income < 500000:
            return 'low'
        elif income < 1500000:
            return 'medium'
        elif income < 5000000:
            return 'high'
        else:
            return 'very_high'

    def _categorize_deductions(self, total_deductions: float) -> str:
        """Categorize total deductions into levels."""
        if total_deductions < 150000:
            return 'low'
        elif total_deductions < 400000:
            return 'medium'
        else:
            return 'high'

    def calculate_audit_risk(self, user_data: Dict) -> Dict:
        """
        Calculate audit risk using Bayesian inference.

        Applies Bayes' theorem:
        P(Audit | Evidence) = P(Evidence | Audit) * P(Audit) / P(Evidence)

        Additional risk factors are incorporated as likelihood modifiers.
        """
        income = user_data.get('annual_income', 0)
        total_deductions = (
            user_data.get('investments_80c', 0) +
            user_data.get('medical_insurance_80d', 0) +
            user_data.get('home_loan_interest', 0) +
            user_data.get('education_loan_interest', 0) +
            user_data.get('donations_80g', 0) +
            user_data.get('nps_contribution', 0)
        )
        regime = user_data.get('regime_choice', 'new')

        income_level = self._categorize_income(income)
        deduction_level = self._categorize_deductions(total_deductions)

        # Base probability from CPT
        key = (income_level, deduction_level, regime)
        base_prob = self.cpt_audit.get(key, 0.02)

        # Apply additional risk factor modifiers using Bayes' theorem
        risk_factors = []
        likelihood_modifier = 1.0

        # High deduction-to-income ratio increases audit risk
        if income > 0:
            deduction_ratio = total_deductions / income
            if deduction_ratio > 0.5:
                likelihood_modifier *= 1.8
                risk_factors.append(
                    f"High deduction-to-income ratio ({deduction_ratio:.1%})"
                )
            elif deduction_ratio > 0.35:
                likelihood_modifier *= 1.3
                risk_factors.append(
                    f"Moderate deduction-to-income ratio ({deduction_ratio:.1%})"
                )

        # Maxed-out 80C with low income
        if user_data.get('investments_80c', 0) >= 150000 and income < 600000:
            likelihood_modifier *= 1.4
            risk_factors.append("80C maxed at ₹1.5L despite income below ₹6L")

        # Large donations relative to income
        donations = user_data.get('donations_80g', 0)
        if donations > 0 and income > 0 and donations / income > 0.1:
            likelihood_modifier *= 1.5
            risk_factors.append(
                f"Donations ({donations/income:.1%} of income) are high"
            )

        # Very high income
        if income > 5000000:
            likelihood_modifier *= 1.6
            risk_factors.append("Income above ₹50 lakhs attracts higher scrutiny")

        # Old regime with minimal deductions (suspicious)
        if regime == 'old' and deduction_level == 'low' and income > 1000000:
            likelihood_modifier *= 1.2
            risk_factors.append("Old regime chosen with low deductions — unusual pattern")

        # Calculate posterior probability
        # P(Audit | Evidence) ∝ P(Evidence | Audit) * P(Audit)
        posterior = min(1.0, base_prob * likelihood_modifier)
        probability_percent = posterior * 100

        # Determine risk level
        if probability_percent < 3:
            risk_level = 'low'
        elif probability_percent < 8:
            risk_level = 'medium'
        else:
            risk_level = 'high'

        return {
            'audit_probability': round(probability_percent, 2),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'base_probability': round(base_prob * 100, 2),
            'likelihood_modifier': round(likelihood_modifier, 2),
            'bayesian_analysis': {
                'income_level': income_level,
                'deduction_level': deduction_level,
                'regime': regime,
                'prior_P_audit': round(self.priors['audit_base_rate'] * 100, 2),
                'conditional_P': round(base_prob * 100, 2),
                'posterior_P': round(probability_percent, 2)
            },
            'recommendations': self._get_audit_recommendations(risk_level, risk_factors),
            'methodology': 'Bayesian Network with conditional probability tables and likelihood modifiers'
        }

    def _get_audit_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Generate recommendations based on audit risk."""
        recommendations = []

        if risk_level == 'low':
            recommendations.append("Your profile looks clean. Continue maintaining proper documentation.")
        elif risk_level == 'medium':
            recommendations.append("Keep all investment proofs and receipts organized.")
            recommendations.append("Ensure Form 26AS matches your TDS claims.")
            if any("deduction" in rf.lower() for rf in risk_factors):
                recommendations.append("Ensure all claimed deductions have valid proof.")
        else:
            recommendations.append("IMPORTANT: Consult a Chartered Accountant before filing.")
            recommendations.append("Maintain detailed documentation for all deductions.")
            recommendations.append("Cross-verify all TDS entries with Form 26AS and AIS.")
            recommendations.append("Consider reviewing claimed deductions for accuracy.")

        return recommendations

    def calculate_regime_probability(self, user_data: Dict) -> Dict:
        """
        Calculate probability of each regime being optimal using Bayesian inference.

        P(OldBetter | Data) = P(Data | OldBetter) * P(OldBetter) / P(Data)
        """
        income = user_data.get('annual_income', 0)
        total_deductions = (
            user_data.get('investments_80c', 0) +
            user_data.get('medical_insurance_80d', 0) +
            user_data.get('home_loan_interest', 0) +
            user_data.get('education_loan_interest', 0) +
            user_data.get('donations_80g', 0) +
            user_data.get('nps_contribution', 0)
        )

        income_level = self._categorize_income(income)
        deduction_level = self._categorize_deductions(total_deductions)

        key = (income_level, deduction_level)
        regime_probs = self.cpt_regime_benefit.get(key, {'old': 0.5, 'new': 0.5})

        # Apply Bayesian update with HRA data
        hra = user_data.get('hra_received', 0)
        if hra > 0 and user_data.get('rent_paid', 0) > 0:
            # HRA is a strong signal for old regime
            regime_probs['old'] = min(0.95, regime_probs['old'] * 1.3)
            regime_probs['new'] = 1 - regime_probs['old']

        # Home loan is strong signal for old regime
        if user_data.get('home_loan_interest', 0) > 100000:
            regime_probs['old'] = min(0.95, regime_probs['old'] * 1.2)
            regime_probs['new'] = 1 - regime_probs['old']

        # Normalize
        total = sum(regime_probs.values())
        regime_probs = {k: v/total for k, v in regime_probs.items()}

        recommended = 'old' if regime_probs['old'] > regime_probs['new'] else 'new'

        return {
            'probabilities': {k: round(v * 100, 2) for k, v in regime_probs.items()},
            'recommended_regime': recommended,
            'confidence': round(max(regime_probs.values()) * 100, 2),
            'analysis': {
                'income_level': income_level,
                'deduction_level': deduction_level,
                'hra_impact': hra > 0,
                'home_loan_impact': user_data.get('home_loan_interest', 0) > 100000
            },
            'methodology': "Bayesian inference with conditional probability tables"
        }


# Module-level instance
bayesian_network = BayesianTaxNetwork()
