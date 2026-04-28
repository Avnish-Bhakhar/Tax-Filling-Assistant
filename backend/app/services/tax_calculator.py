"""
Tax Calculator Service — Core Tax Computation Engine
=====================================================
Complete Indian Income Tax computation for FY 2024-25.
Supports both Old and New regime with all components:
- Slab-wise tax computation
- HRA exemption calculation
- Surcharge and cess
- Rebate under Section 87A
- Standard deduction
- Step-by-step breakdown with explanations
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


class TaxCalculator:
    """
    Indian Income Tax Calculator for FY 2024-25.
    Implements complete tax computation under both regimes.
    """

    def __init__(self, slabs_path: str = None):
        self.tax_slabs = None
        if slabs_path:
            self.load_slabs(slabs_path)

    def load_slabs(self, path: str):
        """Load tax slab configuration."""
        try:
            with open(path, 'r') as f:
                self.tax_slabs = json.load(f)
        except Exception as e:
            print(f"Error loading slabs: {e}")
            self._use_default_slabs()

    def _use_default_slabs(self):
        """Use hardcoded default slabs if JSON loading fails."""
        self.tax_slabs = {
            "old_regime": {
                "slabs": [
                    {"min": 0, "max": 250000, "rate": 0},
                    {"min": 250001, "max": 500000, "rate": 5},
                    {"min": 500001, "max": 1000000, "rate": 20},
                    {"min": 1000001, "max": 999999999, "rate": 30}
                ],
                "standard_deduction": 50000,
                "rebate_87a_limit": 500000,
                "rebate_87a_max": 12500,
                "cess_rate": 4
            },
            "new_regime": {
                "slabs": [
                    {"min": 0, "max": 300000, "rate": 0},
                    {"min": 300001, "max": 700000, "rate": 5},
                    {"min": 700001, "max": 1000000, "rate": 10},
                    {"min": 1000001, "max": 1200000, "rate": 15},
                    {"min": 1200001, "max": 1500000, "rate": 20},
                    {"min": 1500001, "max": 999999999, "rate": 30}
                ],
                "standard_deduction": 75000,
                "rebate_87a_limit": 700000,
                "rebate_87a_max": 25000,
                "cess_rate": 4
            }
        }

    def calculate_hra_exemption(self, user_data: Dict) -> Dict:
        """Calculate HRA exemption under Section 10(13A)."""
        basic_salary = user_data.get('basic_salary', 0)
        hra_received = user_data.get('hra_received', 0)
        rent_paid = user_data.get('rent_paid', 0)
        metro_city = user_data.get('metro_city', False)

        if hra_received == 0 or rent_paid == 0:
            return {
                'exemption': 0,
                'reason': 'HRA or rent data not provided',
                'breakdown': {}
            }

        # Three components
        component_1 = hra_received  # Actual HRA received
        component_2 = (0.5 if metro_city else 0.4) * basic_salary  # 50%/40% of basic
        component_3 = max(0, rent_paid - 0.10 * basic_salary)  # Rent - 10% basic

        exemption = min(component_1, component_2, component_3)

        return {
            'exemption': round(exemption),
            'taxable_hra': round(hra_received - exemption),
            'breakdown': {
                'actual_hra_received': hra_received,
                '50_or_40_pct_basic': round(component_2),
                'rent_minus_10pct_basic': round(component_3),
                'metro_city': metro_city,
                'city_rate': '50%' if metro_city else '40%'
            },
            'calculation_steps': [
                f"1. Actual HRA received: ₹{hra_received:,.0f}",
                f"2. {'50%' if metro_city else '40%'} of Basic Salary (₹{basic_salary:,.0f}): ₹{component_2:,.0f}",
                f"3. Rent paid (₹{rent_paid:,.0f}) - 10% of Basic (₹{basic_salary*0.1:,.0f}): ₹{component_3:,.0f}",
                f"HRA Exemption = Minimum of above = ₹{exemption:,.0f}"
            ]
        }

    def calculate_total_deductions(self, user_data: Dict) -> Dict:
        """Calculate total deductions under Chapter VIA."""
        deductions = {}

        # Section 80C (max 1.5L)
        investments_80c = min(user_data.get('investments_80c', 0), 150000)
        deductions['section_80c'] = investments_80c

        # Section 80CCD(1B) - NPS additional (max 50K)
        nps = min(user_data.get('nps_contribution', 0), 50000)
        deductions['section_80ccd_1b'] = nps

        # Section 80D - Medical insurance
        medical = min(user_data.get('medical_insurance_80d', 0), 100000)
        deductions['section_80d'] = medical

        # Section 80E - Education loan (no limit)
        edu_loan = user_data.get('education_loan_interest', 0)
        deductions['section_80e'] = edu_loan

        # Section 80G - Donations (simplified: 50%)
        donations = user_data.get('donations_80g', 0) * 0.5
        deductions['section_80g'] = donations

        # Section 80TTA - Savings interest (max 10K)
        savings_interest = min(user_data.get('savings_interest', 0), 10000)
        deductions['section_80tta'] = savings_interest

        # Section 24(b) - Home loan interest (max 2L)
        home_loan = min(user_data.get('home_loan_interest', 0), 200000)
        deductions['section_24b'] = home_loan

        # Professional tax
        prof_tax = min(user_data.get('professional_tax', 0), 2500)
        deductions['professional_tax'] = prof_tax

        total = sum(deductions.values())

        return {
            'deductions': deductions,
            'total_deductions': round(total),
            'breakdown': {k: round(v) for k, v in deductions.items() if v > 0}
        }

    def calculate_tax(self, user_data: Dict, regime: str = 'auto') -> Dict:
        """
        Calculate complete tax liability.

        Args:
            user_data: User's financial data
            regime: 'old', 'new', or 'auto' (computes both)

        Returns:
            Complete tax computation with step-by-step breakdown
        """
        if not self.tax_slabs:
            self._use_default_slabs()

        if regime == 'auto':
            old_result = self._compute_regime(user_data, 'old')
            new_result = self._compute_regime(user_data, 'new')

            better_regime = 'old' if old_result['total_tax'] <= new_result['total_tax'] else 'new'
            savings = abs(old_result['total_tax'] - new_result['total_tax'])

            return {
                'recommended_regime': better_regime,
                'potential_savings': round(savings),
                'old_regime': old_result,
                'new_regime': new_result,
                'comparison': {
                    'old_regime_tax': old_result['total_tax'],
                    'new_regime_tax': new_result['total_tax'],
                    'savings_with_recommended': round(savings),
                    'recommendation': f"The {better_regime} regime saves you ₹{savings:,.0f}"
                }
            }
        else:
            return self._compute_regime(user_data, regime)

    def _compute_regime(self, user_data: Dict, regime: str) -> Dict:
        """Compute tax under a specific regime."""
        regime_config = self.tax_slabs.get(f'{regime}_regime', self.tax_slabs.get(regime, {}))
        gross_income = user_data.get('annual_income', 0)
        steps = []

        steps.append(f"Gross Total Income: ₹{gross_income:,.0f}")

        # Standard deduction
        std_deduction = regime_config.get('standard_deduction', 50000)
        if user_data.get('employment_type', 'salaried') == 'salaried':
            income_after_std = gross_income - std_deduction
            steps.append(f"Less: Standard Deduction: ₹{std_deduction:,.0f}")
        else:
            income_after_std = gross_income
            std_deduction = 0

        # Deductions (only for old regime)
        total_deductions = 0
        deduction_details = {}

        if regime == 'old':
            ded_result = self.calculate_total_deductions(user_data)
            total_deductions = ded_result['total_deductions']
            deduction_details = ded_result['breakdown']

            # HRA exemption
            hra_result = self.calculate_hra_exemption(user_data)
            hra_exemption = hra_result['exemption']
            if hra_exemption > 0:
                total_deductions += hra_exemption
                deduction_details['hra_exemption'] = hra_exemption

            steps.append(f"Less: Total Deductions (Chapter VIA + HRA): ₹{total_deductions:,.0f}")

        taxable_income = max(0, income_after_std - total_deductions)
        steps.append(f"Net Taxable Income: ₹{taxable_income:,.0f}")

        # Slab-wise computation
        slabs = regime_config.get('slabs', [])
        tax = 0
        slab_breakdown = []

        remaining = taxable_income
        for slab in slabs:
            slab_min = slab['min']
            slab_max = slab['max']
            rate = slab['rate']

            if remaining <= 0:
                break

            taxable_in_slab = min(remaining, slab_max - slab_min + 1)
            if taxable_income > slab_min:
                actual_in_slab = min(taxable_income, slab_max) - slab_min
                if slab_min == 0:
                    actual_in_slab = min(taxable_income, slab_max)

                tax_in_slab = actual_in_slab * rate / 100
                if tax_in_slab > 0 or rate == 0:
                    slab_breakdown.append({
                        'slab': slab.get('label', f"₹{slab_min:,} - ₹{slab_max:,}"),
                        'rate': f"{rate}%",
                        'taxable_amount': round(actual_in_slab),
                        'tax': round(tax_in_slab)
                    })
                tax += tax_in_slab

        # Recalculate using simpler method for accuracy
        tax = self._slab_calculation(taxable_income, slabs)

        steps.append(f"Tax on Taxable Income: ₹{tax:,.0f}")

        # Rebate under 87A
        rebate = 0
        rebate_limit = regime_config.get('rebate_87a_limit', 500000)
        rebate_max = regime_config.get('rebate_87a_max', 12500)
        if taxable_income <= rebate_limit:
            rebate = min(tax, rebate_max)
            steps.append(f"Less: Rebate u/s 87A: ₹{rebate:,.0f}")

        tax_after_rebate = max(0, tax - rebate)

        # Surcharge
        surcharge = 0
        surcharge_rate = 0
        for slab in regime_config.get('surcharge', []):
            if taxable_income > slab['min']:
                surcharge_rate = slab['rate']

        if surcharge_rate > 0:
            surcharge = tax_after_rebate * surcharge_rate / 100
            steps.append(f"Add: Surcharge ({surcharge_rate}%): ₹{surcharge:,.0f}")

        # Cess
        cess_rate = regime_config.get('cess_rate', 4)
        cess = (tax_after_rebate + surcharge) * cess_rate / 100
        steps.append(f"Add: Health & Education Cess ({cess_rate}%): ₹{cess:,.0f}")

        total_tax = round(tax_after_rebate + surcharge + cess)
        steps.append(f"Total Tax Liability: ₹{total_tax:,.0f}")

        return {
            'regime': regime,
            'gross_income': round(gross_income),
            'standard_deduction': std_deduction,
            'total_deductions': round(total_deductions),
            'deduction_details': deduction_details,
            'taxable_income': round(taxable_income),
            'tax_before_rebate': round(tax),
            'rebate_87a': round(rebate),
            'tax_after_rebate': round(tax_after_rebate),
            'surcharge': round(surcharge),
            'surcharge_rate': surcharge_rate,
            'cess': round(cess),
            'total_tax': total_tax,
            'effective_rate': round((total_tax / gross_income * 100), 2) if gross_income > 0 else 0,
            'computation_steps': steps,
            'slab_breakdown': slab_breakdown
        }

    def _slab_calculation(self, taxable_income: float, slabs: List[Dict]) -> float:
        """Calculate tax using slab rates (accurate method)."""
        tax = 0
        remaining = taxable_income

        for i, slab in enumerate(slabs):
            if remaining <= 0:
                break

            slab_min = slab['min']
            slab_max = slab['max']
            rate = slab['rate']

            if i == 0:
                slab_range = slab_max
            else:
                slab_range = slab_max - slab_min + 1

            amount_in_slab = min(remaining, slab_range)
            tax += amount_in_slab * rate / 100
            remaining -= amount_in_slab

        return tax

    def what_if_analysis(self, base_data: Dict, scenarios: List[Dict]) -> Dict:
        """
        Run what-if analysis for multiple tax scenarios.

        Args:
            base_data: Base user financial data
            scenarios: List of modified scenarios to compare

        Returns:
            Comparison of all scenarios
        """
        base_result = self.calculate_tax(base_data, 'auto')
        base_best_tax = min(
            base_result['old_regime']['total_tax'],
            base_result['new_regime']['total_tax']
        )

        scenario_results = []
        for i, scenario in enumerate(scenarios):
            modified_data = {**base_data, **scenario.get('changes', {})}
            result = self.calculate_tax(modified_data, 'auto')
            best_tax = min(
                result['old_regime']['total_tax'],
                result['new_regime']['total_tax']
            )

            scenario_results.append({
                'scenario_name': scenario.get('name', f'Scenario {i+1}'),
                'changes': scenario.get('changes', {}),
                'best_regime': result['recommended_regime'],
                'total_tax': best_tax,
                'savings_vs_base': round(base_best_tax - best_tax),
                'effective_rate': round((best_tax / modified_data.get('annual_income', 1)) * 100, 2),
                'old_regime_tax': result['old_regime']['total_tax'],
                'new_regime_tax': result['new_regime']['total_tax']
            })

        return {
            'base_case': {
                'tax': base_best_tax,
                'regime': base_result['recommended_regime']
            },
            'scenarios': scenario_results
        }


# Module-level instance
tax_calculator = TaxCalculator()
