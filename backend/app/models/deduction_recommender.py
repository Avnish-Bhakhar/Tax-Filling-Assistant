"""
Deduction Recommender — Heuristic Optimization System
=====================================================
Recommends optimal tax deductions using:
1. Rule-based heuristics (domain knowledge)
2. Greedy optimization (maximize savings within limits)
3. Personalized recommendations based on user profile

Analyzes the user's financial profile and identifies unused
deduction opportunities with estimated tax savings.
"""

from typing import Dict, List, Tuple
import json
from pathlib import Path


class DeductionRecommender:
    """
    AI-powered deduction recommendation engine.

    Uses heuristic search and optimization to find the best
    deduction strategy for maximizing tax savings.
    """

    def __init__(self, deductions_path: str = None):
        self.deductions_catalog = None
        if deductions_path:
            self.load_catalog(deductions_path)

    def load_catalog(self, path: str):
        """Load deductions catalog from JSON."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self.deductions_catalog = data.get('deductions', [])
        except Exception as e:
            print(f"Error loading catalog: {e}")
            self.deductions_catalog = []

    def recommend(self, user_data: Dict) -> Dict:
        """
        Generate personalized deduction recommendations.

        Uses a greedy optimization approach to maximize tax savings
        within legal limits, prioritized by potential impact.
        """
        income = user_data.get('annual_income', 0)
        age = user_data.get('age', 30)
        regime = user_data.get('regime_choice', 'old')

        if regime == 'new':
            return {
                'recommendations': [{
                    'section': 'Standard Deduction',
                    'current_claim': 75000,
                    'max_limit': 75000,
                    'potential_savings': 0,
                    'priority': 'info',
                    'reason': 'Under new regime, only standard deduction of ₹75,000 and employer NPS are allowed.'
                }],
                'total_potential_savings': 0,
                'note': 'New regime has limited deduction options. Consider switching to old regime if your deductions exceed ₹3.75 lakhs.'
            }

        recommendations = []

        # 1. Section 80C Analysis
        current_80c = user_data.get('investments_80c', 0)
        max_80c = 150000
        if current_80c < max_80c:
            gap = max_80c - current_80c
            tax_rate = self._get_marginal_rate(income)
            savings = gap * tax_rate

            instruments = self._recommend_80c_instruments(user_data, gap)
            recommendations.append({
                'section': '80C',
                'title': 'Investments & Expenses',
                'current_claim': current_80c,
                'max_limit': max_80c,
                'gap': gap,
                'potential_savings': round(savings),
                'priority': 'high' if gap > 50000 else 'medium',
                'reason': f'You can invest ₹{gap:,.0f} more to maximize 80C deduction.',
                'suggested_instruments': instruments
            })

        # 2. Section 80D Analysis
        current_80d = user_data.get('medical_insurance_80d', 0)
        max_80d_self = 50000 if age >= 60 else 25000
        max_80d_parents = 50000  # Assume parents are senior
        max_80d = max_80d_self + max_80d_parents

        if current_80d < max_80d:
            gap = max_80d - current_80d
            savings = gap * self._get_marginal_rate(income)
            recommendations.append({
                'section': '80D',
                'title': 'Medical Insurance Premium',
                'current_claim': current_80d,
                'max_limit': max_80d,
                'gap': gap,
                'potential_savings': round(savings),
                'priority': 'high' if gap > 25000 else 'medium',
                'reason': f'Health insurance saves tax and provides medical coverage. Gap: ₹{gap:,.0f}.',
                'tip': 'Include preventive health check-up (₹5,000 within limit) for family.'
            })

        # 3. Section 80CCD(1B) — NPS
        current_nps = user_data.get('nps_contribution', 0)
        if current_nps < 50000:
            gap = 50000 - current_nps
            savings = gap * self._get_marginal_rate(income)
            recommendations.append({
                'section': '80CCD(1B)',
                'title': 'Additional NPS Contribution',
                'current_claim': current_nps,
                'max_limit': 50000,
                'gap': gap,
                'potential_savings': round(savings),
                'priority': 'high' if income > 1000000 else 'medium',
                'reason': 'Extra ₹50K deduction over 80C limit! Great for retirement + tax saving.',
                'tip': 'NPS Tier-1 qualifies. This is OVER AND ABOVE the ₹1.5L 80C limit.'
            })

        # 4. Home Loan Interest — Section 24(b)
        current_hl = user_data.get('home_loan_interest', 0)
        if current_hl > 0 and current_hl < 200000:
            gap = 200000 - current_hl
            savings = gap * self._get_marginal_rate(income)
            recommendations.append({
                'section': '24(b)',
                'title': 'Home Loan Interest',
                'current_claim': current_hl,
                'max_limit': 200000,
                'gap': gap,
                'potential_savings': round(savings),
                'priority': 'medium',
                'reason': f'Home loan interest deduction not fully utilized. ₹{gap:,.0f} remaining.'
            })

        # 5. Education Loan — Section 80E
        edu_loan = user_data.get('education_loan_interest', 0)
        if edu_loan == 0 and age < 35:
            recommendations.append({
                'section': '80E',
                'title': 'Education Loan Interest',
                'current_claim': 0,
                'max_limit': -1,
                'gap': 0,
                'potential_savings': 0,
                'priority': 'info',
                'reason': 'If you have an education loan, the ENTIRE interest is deductible with NO upper limit.'
            })

        # 6. HRA Optimization
        hra_received = user_data.get('hra_received', 0)
        rent_paid = user_data.get('rent_paid', 0)
        if hra_received > 0 and rent_paid == 0:
            recommendations.append({
                'section': 'HRA',
                'title': 'House Rent Allowance',
                'current_claim': 0,
                'max_limit': hra_received,
                'gap': hra_received,
                'potential_savings': round(hra_received * 0.4 * self._get_marginal_rate(income)),
                'priority': 'high',
                'reason': 'You receive HRA but haven\'t claimed rent deduction! Provide rent receipts to save tax.'
            })

        # 7. Donations — Section 80G
        donations = user_data.get('donations_80g', 0)
        if donations == 0 and income > 1000000:
            recommendations.append({
                'section': '80G',
                'title': 'Donations to Charitable Institutions',
                'current_claim': 0,
                'max_limit': -1,
                'gap': 0,
                'potential_savings': 0,
                'priority': 'low',
                'reason': 'Donations to approved institutions get 50-100% deduction. PM Relief Fund donations get 100% deduction.'
            })

        # Sort by potential savings (greedy: highest savings first)
        recommendations.sort(key=lambda x: x.get('potential_savings', 0), reverse=True)

        total_savings = sum(r.get('potential_savings', 0) for r in recommendations)

        return {
            'recommendations': recommendations,
            'total_potential_savings': round(total_savings),
            'optimization_strategy': 'Greedy heuristic — prioritized by potential tax savings',
            'marginal_tax_rate': f"{self._get_marginal_rate(income) * 100:.0f}%",
            'note': 'Savings calculated at your marginal tax rate including cess.'
        }

    def _recommend_80c_instruments(self, user_data: Dict, gap: float) -> List[Dict]:
        """Recommend specific 80C instruments based on profile."""
        age = user_data.get('age', 30)
        instruments = []

        if age < 35:
            instruments.append({
                'name': 'ELSS Mutual Funds',
                'suggested_amount': min(gap, 100000),
                'reason': 'Shortest lock-in (3 years), potential for high returns',
                'risk': 'Moderate-High'
            })
        if gap > 50000:
            instruments.append({
                'name': 'Public Provident Fund (PPF)',
                'suggested_amount': min(gap, 150000),
                'reason': 'Safe, guaranteed returns (~7.1%), tax-free maturity',
                'risk': 'Low'
            })
        instruments.append({
            'name': 'Tax-Saving Fixed Deposit',
            'suggested_amount': min(gap, 150000),
            'reason': '5-year lock-in, guaranteed returns, safe option',
            'risk': 'Low'
        })

        return instruments

    def _get_marginal_rate(self, income: float) -> float:
        """Get marginal tax rate based on income (old regime)."""
        if income > 1000000:
            return 0.312  # 30% + 4% cess
        elif income > 500000:
            return 0.208  # 20% + 4% cess
        elif income > 250000:
            return 0.052  # 5% + 4% cess
        else:
            return 0


# Module-level instance
deduction_recommender = DeductionRecommender()
