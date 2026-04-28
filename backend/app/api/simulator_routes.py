"""
Simulator Routes — What-If Tax Simulator API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List

router = APIRouter(prefix="/api/simulator", tags=["Simulator"])


class SimulatorInput(BaseModel):
    annual_income: float = 1000000
    age: int = 30
    investments_80c: float = 0
    medical_insurance_80d: float = 0
    home_loan_interest: float = 0
    education_loan_interest: float = 0
    donations_80g: float = 0
    nps_contribution: float = 0
    hra_received: float = 0
    rent_paid: float = 0
    metro_city: bool = False
    basic_salary: float = 0
    savings_interest: float = 0
    professional_tax: float = 2400
    leave_travel_allowance: float = 0
    other_income: float = 0
    employment_type: str = "salaried"
    city_tier: int = 1


class WhatIfScenario(BaseModel):
    name: str = "Scenario"
    changes: Dict[str, float] = {}


class WhatIfInput(BaseModel):
    base_data: SimulatorInput
    scenarios: List[WhatIfScenario] = []


@router.post("/what-if")
async def run_what_if(data: WhatIfInput):
    """Run what-if tax scenarios."""
    try:
        from app.services.tax_calculator import tax_calculator
        from app.services.generative_engine import generative_engine
        from app.config import Config

        if not tax_calculator.tax_slabs:
            tax_calculator.load_slabs(str(Config.TAX_SLABS_JSON))

        base_data = data.base_data.dict()
        scenarios = [s.dict() for s in data.scenarios]

        if not scenarios:
            # Generate default scenarios
            scenarios = [
                {"name": "Maximize 80C", "changes": {"investments_80c": 150000}},
                {"name": "Add NPS 50K", "changes": {"nps_contribution": 50000}},
                {"name": "Add Health Insurance", "changes": {"medical_insurance_80d": 25000}},
                {"name": "Max All Deductions", "changes": {
                    "investments_80c": 150000,
                    "nps_contribution": 50000,
                    "medical_insurance_80d": 50000
                }},
            ]

        result = tax_calculator.what_if_analysis(base_data, scenarios)
        narrative = generative_engine.generate_what_if_narrative(result)

        return {
            "status": "success",
            "data": {
                **result,
                "narrative": narrative
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-regimes")
async def compare_regimes(data: SimulatorInput):
    """Compare both tax regimes for given inputs."""
    try:
        from app.services.tax_calculator import tax_calculator
        from app.services.generative_engine import generative_engine
        from app.services.prompt_templates import prompt_engine
        from app.config import Config

        if not tax_calculator.tax_slabs:
            tax_calculator.load_slabs(str(Config.TAX_SLABS_JSON))

        user_data = data.dict()
        result = tax_calculator.calculate_tax(user_data, 'auto')

        # Generate chain-of-thought explanation
        cot = prompt_engine.generate_regime_cot(
            user_data,
            result['old_regime']['total_tax'],
            result['new_regime']['total_tax']
        )

        # Generate detailed explanation
        explanation = generative_engine.explain_calculation(result)

        return {
            "status": "success",
            "data": {
                "comparison": result,
                "chain_of_thought": cot,
                "explanation": explanation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
