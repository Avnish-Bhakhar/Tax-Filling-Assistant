"""
Analysis Routes — Dashboard & Visualization API (Plotly data endpoints)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import json

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


class DashboardInput(BaseModel):
    annual_income: float = 0
    investments_80c: float = 0
    medical_insurance_80d: float = 0
    home_loan_interest: float = 0
    education_loan_interest: float = 0
    donations_80g: float = 0
    nps_contribution: float = 0
    hra_received: float = 0
    savings_interest: float = 0
    other_income: float = 0


@router.post("/income-vs-deductions")
async def income_vs_deductions(data: DashboardInput):
    """Get data for income vs deductions chart."""
    try:
        total_deductions = (
            data.investments_80c + data.medical_insurance_80d +
            data.home_loan_interest + data.education_loan_interest +
            data.donations_80g + data.nps_contribution
        )

        return {
            "status": "success",
            "data": {
                "chart_type": "bar",
                "categories": [
                    "Gross Income", "Section 80C", "Section 80D",
                    "Home Loan (24b)", "Education Loan (80E)",
                    "Donations (80G)", "NPS (80CCD)", "Total Deductions"
                ],
                "values": [
                    data.annual_income,
                    data.investments_80c,
                    data.medical_insurance_80d,
                    data.home_loan_interest,
                    data.education_loan_interest,
                    data.donations_80g,
                    data.nps_contribution,
                    total_deductions
                ],
                "colors": [
                    "#4F46E5", "#10B981", "#F59E0B",
                    "#EF4444", "#8B5CF6", "#EC4899",
                    "#06B6D4", "#6366F1"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tax-breakdown")
async def tax_breakdown(data: DashboardInput):
    """Get data for tax breakdown pie chart."""
    try:
        from app.services.tax_calculator import tax_calculator
        from app.config import Config

        if not tax_calculator.tax_slabs:
            tax_calculator.load_slabs(str(Config.TAX_SLABS_JSON))

        user_data = data.dict()
        user_data['age'] = 30
        user_data['city_tier'] = 1
        user_data['employment_type'] = 'salaried'
        user_data['basic_salary'] = data.annual_income * 0.5
        user_data['metro_city'] = True
        user_data['rent_paid'] = 0
        user_data['professional_tax'] = 2400
        user_data['leave_travel_allowance'] = 0

        result = tax_calculator.calculate_tax(user_data, 'auto')
        recommended = result['recommended_regime']
        regime_result = result[f'{recommended}_regime']

        return {
            "status": "success",
            "data": {
                "chart_type": "pie",
                "regime": recommended,
                "labels": [
                    "Exempt (No Tax)", "5% Slab", "10% Slab",
                    "15% Slab", "20% Slab", "30% Slab",
                    "Cess", "Surcharge"
                ],
                "old_regime": {
                    "total_tax": result['old_regime']['total_tax'],
                    "taxable_income": result['old_regime']['taxable_income'],
                    "effective_rate": result['old_regime']['effective_rate']
                },
                "new_regime": {
                    "total_tax": result['new_regime']['total_tax'],
                    "taxable_income": result['new_regime']['taxable_income'],
                    "effective_rate": result['new_regime']['effective_rate']
                },
                "recommendation": result['comparison'],
                "computation_steps": regime_result.get('computation_steps', [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-data")
async def get_sample_data():
    """Get sample taxpayer dataset for visualization."""
    try:
        import csv
        from app.config import Config

        data = []
        with open(Config.TAXPAYERS_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({k: float(v) if v.replace('.','').replace('-','').isdigit()
                           else v for k, v in row.items()})

        # Aggregate stats
        incomes = [d.get('annual_income', 0) for d in data if isinstance(d.get('annual_income'), (int, float))]
        taxes = [d.get('actual_tax_paid', 0) for d in data if isinstance(d.get('actual_tax_paid'), (int, float))]

        return {
            "status": "success",
            "data": {
                "records": data[:50],
                "total_records": len(data),
                "stats": {
                    "avg_income": sum(incomes) / len(incomes) if incomes else 0,
                    "avg_tax": sum(taxes) / len(taxes) if taxes else 0,
                    "min_income": min(incomes) if incomes else 0,
                    "max_income": max(incomes) if incomes else 0
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filing-path")
async def get_filing_path(data: DashboardInput):
    """Get optimal tax filing path using A* search."""
    try:
        from app.models.state_space_search import tax_search

        user_data = data.dict()
        result = tax_search.a_star_search(user_data)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
