"""
Tax Routes — Tax Calculation, Regime Recommendation, Liability Prediction API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

router = APIRouter(prefix="/api/tax", tags=["Tax"])


class TaxInput(BaseModel):
    annual_income: float = Field(..., description="Gross annual income")
    age: int = Field(default=30, description="Age of taxpayer")
    city_tier: int = Field(default=1, description="City tier (1=metro, 2=tier2, 3=tier3)")
    employment_type: str = Field(default="salaried", description="salaried or self_employed")
    basic_salary: float = Field(default=0)
    hra_received: float = Field(default=0)
    rent_paid: float = Field(default=0)
    metro_city: bool = Field(default=False)
    investments_80c: float = Field(default=0)
    medical_insurance_80d: float = Field(default=0)
    home_loan_interest: float = Field(default=0)
    education_loan_interest: float = Field(default=0)
    donations_80g: float = Field(default=0)
    nps_contribution: float = Field(default=0)
    savings_interest: float = Field(default=0)
    professional_tax: float = Field(default=0)
    leave_travel_allowance: float = Field(default=0)
    other_income: float = Field(default=0)
    regime: str = Field(default="auto", description="old, new, or auto")
    name: str = Field(default="Taxpayer")


class WhatIfScenario(BaseModel):
    name: str = "Scenario"
    changes: Dict[str, float] = {}


class WhatIfInput(BaseModel):
    base_data: TaxInput
    scenarios: List[WhatIfScenario]


@router.post("/calculate")
async def calculate_tax(data: TaxInput):
    """Calculate tax liability with full breakdown."""
    try:
        from app.services.tax_calculator import tax_calculator
        from app.config import Config

        if not tax_calculator.tax_slabs:
            tax_calculator.load_slabs(str(Config.TAX_SLABS_JSON))

        user_data = data.dict()
        result = tax_calculator.calculate_tax(user_data, data.regime)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-regime")
async def recommend_regime(data: TaxInput):
    """AI-powered regime recommendation."""
    try:
        from app.models.tax_regime_classifier import regime_classifier
        from app.models.bayesian_network import bayesian_network
        from app.utils.explainability import explainer

        user_data = data.dict()

        # ML prediction
        ml_result = regime_classifier.predict(user_data)

        # Bayesian analysis
        bayesian_result = bayesian_network.calculate_regime_probability(user_data)

        # Combine results
        explanation = explainer.explain_regime_recommendation(
            ml_result['recommended_regime'],
            ml_result['confidence'],
            ml_result['feature_importance'],
            user_data
        )

        return {
            "status": "success",
            "data": {
                "ml_recommendation": ml_result,
                "bayesian_analysis": bayesian_result,
                "explanation": explanation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-liability")
async def predict_liability(data: TaxInput):
    """Predict tax liability using ML model."""
    try:
        from app.models.liability_predictor import liability_predictor

        user_data = data.dict()
        result = liability_predictor.predict(user_data)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-deductions")
async def recommend_deductions(data: TaxInput):
    """AI deduction recommendation engine."""
    try:
        from app.models.deduction_recommender import deduction_recommender
        from app.config import Config

        if not deduction_recommender.deductions_catalog:
            deduction_recommender.load_catalog(str(Config.DEDUCTIONS_JSON))

        user_data = data.dict()
        result = deduction_recommender.recommend(user_data)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audit-risk")
async def assess_audit_risk(data: TaxInput):
    """Bayesian audit risk assessment."""
    try:
        from app.models.bayesian_network import bayesian_network
        from app.utils.explainability import explainer

        user_data = data.dict()
        result = bayesian_network.calculate_audit_risk(user_data)

        explanation = explainer.explain_audit_risk(
            result['audit_probability'],
            result['risk_factors']
        )

        return {
            "status": "success",
            "data": {**result, "explanation": explanation}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deductions-catalog")
async def get_deductions_catalog():
    """Get all available deduction sections."""
    try:
        import json
        from app.config import Config
        with open(Config.DEDUCTIONS_JSON, 'r') as f:
            catalog = json.load(f)
        return {"status": "success", "data": catalog}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-summary")
async def generate_summary(data: TaxInput):
    """Generate AI tax summary."""
    try:
        from app.services.tax_calculator import tax_calculator
        from app.services.generative_engine import generative_engine
        from app.config import Config

        if not tax_calculator.tax_slabs:
            tax_calculator.load_slabs(str(Config.TAX_SLABS_JSON))

        user_data = data.dict()
        tax_result = tax_calculator.calculate_tax(user_data, 'auto')
        summary = generative_engine.generate_tax_summary(user_data, tax_result)
        explanation = generative_engine.explain_calculation(tax_result)
        advice = generative_engine.generate_personalized_advice(user_data, tax_result)

        return {
            "status": "success",
            "data": {
                "summary": summary,
                "explanation": explanation,
                "advice": advice,
                "tax_result": tax_result
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
