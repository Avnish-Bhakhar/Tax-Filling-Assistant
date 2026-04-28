"""
Explainability Module
Provides interpretable AI decision explanations for tax recommendations.
Implements SHAP-like feature importance and natural language explanations.
"""

from typing import Dict, List, Tuple
import json


class AIExplainer:
    """
    Generates human-readable explanations for AI model decisions.
    Supports feature importance, decision paths, and confidence breakdowns.
    """

    def __init__(self):
        self.explanation_templates = {
            "regime_recommendation": {
                "high_confidence": "Based on your financial profile, the {regime} regime is recommended with {confidence:.1f}% confidence. {reason}",
                "low_confidence": "Both regimes are close, but the {regime} regime has a slight edge ({confidence:.1f}% confidence). {reason}",
                "factors": "Key factors: {factors}"
            },
            "liability_prediction": {
                "template": "Your estimated tax liability is ₹{amount:,.0f}. This is based on: {breakdown}",
                "comparison": "Under the {regime} regime, you save ₹{savings:,.0f} compared to the other regime."
            },
            "deduction_recommendation": {
                "template": "We recommend claiming {section} deduction. Potential savings: ₹{savings:,.0f}. {reason}"
            },
            "audit_risk": {
                "low": "Your audit risk is LOW ({probability:.1f}%). Your financial profile appears consistent and well-documented.",
                "medium": "Your audit risk is MODERATE ({probability:.1f}%). {reason} Consider reviewing your deduction claims.",
                "high": "Your audit risk is HIGH ({probability:.1f}%). {reason} We recommend consulting a CA before filing."
            }
        }

    def explain_regime_recommendation(
        self, regime: str, confidence: float,
        feature_importance: Dict[str, float], user_data: Dict
    ) -> Dict:
        """Generate explanation for regime recommendation."""
        sorted_features = sorted(
            feature_importance.items(), key=lambda x: abs(x[1]), reverse=True
        )
        top_features = sorted_features[:5]

        # Build reason
        reasons = []
        for feat, importance in top_features:
            direction = "increases" if importance > 0 else "decreases"
            feat_name = feat.replace('_', ' ').title()
            reasons.append(f"{feat_name} {direction} preference for this regime")

        template_key = "high_confidence" if confidence > 70 else "low_confidence"
        main_explanation = self.explanation_templates["regime_recommendation"][template_key].format(
            regime=regime, confidence=confidence, reason=reasons[0]
        )

        factors_str = "; ".join([f"{f[0].replace('_', ' ').title()}: {abs(f[1]):.2f}" for f in top_features])
        factors_explanation = self.explanation_templates["regime_recommendation"]["factors"].format(
            factors=factors_str
        )

        return {
            "summary": main_explanation,
            "factors": factors_explanation,
            "feature_importance": {f[0]: round(f[1], 4) for f in top_features},
            "confidence": round(confidence, 2),
            "recommended_regime": regime,
            "transparency_note": "This recommendation is based on a machine learning model trained on historical taxpayer data. Individual results may vary."
        }

    def explain_liability_prediction(
        self, predicted_amount: float, breakdown: Dict[str, float],
        regime: str, alternative_amount: float = None
    ) -> Dict:
        """Generate explanation for tax liability prediction."""
        breakdown_str = ", ".join([
            f"{k.replace('_', ' ').title()}: ₹{v:,.0f}" for k, v in breakdown.items()
        ])

        main_explanation = self.explanation_templates["liability_prediction"]["template"].format(
            amount=predicted_amount, breakdown=breakdown_str
        )

        result = {
            "summary": main_explanation,
            "predicted_liability": predicted_amount,
            "computation_breakdown": breakdown,
            "regime_used": regime
        }

        if alternative_amount is not None:
            savings = abs(alternative_amount - predicted_amount)
            comparison = self.explanation_templates["liability_prediction"]["comparison"].format(
                regime=regime, savings=savings
            )
            result["comparison"] = comparison
            result["alternative_liability"] = alternative_amount
            result["potential_savings"] = savings

        return result

    def explain_audit_risk(
        self, probability: float, risk_factors: List[str]
    ) -> Dict:
        """Generate explanation for audit risk assessment."""
        if probability < 30:
            level = "low"
        elif probability < 60:
            level = "medium"
        else:
            level = "high"

        reason = "; ".join(risk_factors) if risk_factors else "No specific risk factors identified"

        return {
            "summary": self.explanation_templates["audit_risk"][level].format(
                probability=probability, reason=reason
            ),
            "risk_level": level,
            "probability": round(probability, 2),
            "risk_factors": risk_factors,
            "disclaimer": "This is an AI-based estimate. Actual audit selection depends on multiple factors and is at the discretion of the Income Tax Department."
        }

    def explain_deduction_recommendation(
        self, recommendations: List[Dict]
    ) -> Dict:
        """Generate explanation for deduction recommendations."""
        explained = []
        total_savings = 0

        for rec in recommendations:
            explanation = self.explanation_templates["deduction_recommendation"]["template"].format(
                section=rec.get('section', 'N/A'),
                savings=rec.get('potential_savings', 0),
                reason=rec.get('reason', 'This deduction is applicable based on your profile.')
            )
            explained.append({
                "explanation": explanation,
                **rec
            })
            total_savings += rec.get('potential_savings', 0)

        return {
            "recommendations": explained,
            "total_potential_savings": total_savings,
            "note": "These recommendations are based on your current financial profile. Consult a tax professional for personalized advice."
        }


# Singleton instance
explainer = AIExplainer()
