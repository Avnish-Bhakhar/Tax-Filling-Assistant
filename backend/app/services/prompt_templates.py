"""
Prompt Engineering Templates
=============================
Implements three key prompt engineering techniques:
1. Few-Shot Prompting — Examples to guide response format
2. Role-Based Prompting — System persona definition
3. Chain-of-Thought (CoT) — Step-by-step reasoning templates
"""

from typing import Dict, List


class PromptTemplateEngine:
    """
    Prompt engineering engine implementing industry-standard techniques
    for generating high-quality AI responses in the tax domain.
    """

    # ═══════════════════════════════════════
    # ROLE-BASED PROMPTING TEMPLATES
    # ═══════════════════════════════════════

    SYSTEM_ROLES = {
        "tax_expert": {
            "role": "Senior Tax Consultant",
            "prompt": """You are an experienced Indian Tax Consultant with 15+ years of expertise 
in income tax filing, tax planning, and compliance. You are patient, thorough, 
and always explain concepts in simple language. You follow the latest Income Tax 
Act provisions for FY 2024-25 (AY 2025-26). You prioritize accuracy and always 
recommend consulting a CA for complex cases. You never give illegal tax advice.""",
            "personality": "Professional, empathetic, detail-oriented"
        },
        "filing_assistant": {
            "role": "Tax Filing Guide",
            "prompt": """You are a friendly tax filing assistant helping users complete their 
Income Tax Return step by step. You ask clear questions, validate inputs, 
and guide them through each section of the ITR form. You simplify complex 
tax jargon and use examples from everyday life.""",
            "personality": "Friendly, patient, encouraging"
        },
        "tax_optimizer": {
            "role": "Tax Optimization Specialist",
            "prompt": """You are a tax optimization AI that analyzes financial profiles to 
minimize legal tax liability. You identify missed deductions, compare regimes, 
and suggest investment strategies. You always emphasize that recommendations 
are based on current tax laws and should be verified with a professional.""",
            "personality": "Analytical, proactive, data-driven"
        }
    }

    # ═══════════════════════════════════════
    # FEW-SHOT PROMPTING TEMPLATES
    # ═══════════════════════════════════════

    FEW_SHOT_EXAMPLES = {
        "regime_comparison": {
            "description": "Compare old vs new tax regime",
            "examples": [
                {
                    "input": "I earn 12 lakhs and have 2 lakh deductions. Which regime?",
                    "output": """Let me analyze both regimes for you:

**Old Regime (₹12L income, ₹2L deductions):**
- Taxable Income: ₹12L - ₹50K (std) - ₹2L = ₹9.5L
- Tax: ₹0 + ₹12,500 (5%) + ₹90,000 (20%) = ₹1,02,500
- Cess: ₹4,100
- Total: ₹1,06,600

**New Regime (₹12L income, no deductions except std):**
- Taxable Income: ₹12L - ₹75K = ₹11.25L
- Tax: ₹0 + ₹20,000 (5%) + ₹30,000 (10%) + ₹18,750 (15%) = ₹68,750
- Cess: ₹2,750
- Total: ₹71,500

✅ **Recommendation: NEW REGIME** saves you ₹35,100!"""
                },
                {
                    "input": "Income 15 lakhs, deductions 5 lakhs including HRA",
                    "output": """With ₹5L in deductions, the old regime becomes attractive:

**Old Regime:** Taxable = ₹15L - ₹50K - ₹5L = ₹9.5L → Tax ≈ ₹1,06,600
**New Regime:** Taxable = ₹15L - ₹75K = ₹14.25L → Tax ≈ ₹1,78,100

✅ **Recommendation: OLD REGIME** saves you ₹71,500!
Your deductions are substantial enough to make old regime clearly better."""
                }
            ]
        },
        "deduction_advice": {
            "description": "Recommend deductions",
            "examples": [
                {
                    "input": "I earn 10L and only have 80K in 80C. How to save more tax?",
                    "output": """You have ₹70,000 gap in 80C alone! Here's your action plan:

1. **80C Gap (₹70K):**
   - ELSS Mutual Funds: ₹40K (3yr lock-in, ~12% returns)
   - PPF: ₹30K (safe, 7.1% guaranteed)

2. **80CCD(1B) — NPS: ₹50,000** (EXTRA deduction!)
   - This is OVER AND ABOVE ₹1.5L of 80C

3. **80D — Health Insurance: ₹25,000**
   - Self + family coverage + tax benefit

Total additional deductions: ₹1,45,000
At 20% tax rate, you save: ₹30,160 (including cess)"""
                }
            ]
        },
        "tax_explanation": {
            "description": "Explain tax concepts",
            "examples": [
                {
                    "input": "What is HRA exemption?",
                    "output": """**HRA (House Rent Allowance) Exemption** is a tax benefit for salaried individuals who receive HRA and pay rent.

**How it works:**
The exempt amount is the MINIMUM of:
1. Actual HRA received from employer
2. 50% of basic salary (metro cities) or 40% (non-metro)
3. Rent paid minus 10% of basic salary

**Example:**
- Basic: ₹6L, HRA: ₹3L, Rent: ₹2L, Metro: Yes
- Min(₹3L, ₹3L, ₹1.4L) = ₹1.4L exempt
- Taxable HRA = ₹3L - ₹1.4L = ₹1.6L

💡 Available only under OLD regime. Keep rent receipts!"""
                }
            ]
        }
    }

    # ═══════════════════════════════════════
    # CHAIN-OF-THOUGHT TEMPLATES
    # ═══════════════════════════════════════

    CHAIN_OF_THOUGHT = {
        "tax_calculation": {
            "description": "Step-by-step tax calculation reasoning",
            "template": """Let me think through this step by step:

**Step 1: Identify total income**
{step1}

**Step 2: Apply standard deduction**
{step2}

**Step 3: Calculate eligible deductions**
{step3}

**Step 4: Compute taxable income**
{step4}

**Step 5: Apply tax slabs**
{step5}

**Step 6: Check for rebate (Section 87A)**
{step6}

**Step 7: Add surcharge and cess**
{step7}

**Final Answer:**
{conclusion}"""
        },
        "regime_decision": {
            "description": "Reasoning for regime selection",
            "template": """Let me reason through the regime selection:

**Question:** Which tax regime is better for this profile?

**Given Information:**
{given_info}

**Reasoning:**

**Chain 1: Old Regime Analysis**
{old_analysis}

**Chain 2: New Regime Analysis**
{new_analysis}

**Chain 3: Comparison**
{comparison}

**Conclusion:**
{conclusion}"""
        },
        "deduction_optimization": {
            "description": "Optimal deduction strategy reasoning",
            "template": """Let me optimize the deduction strategy:

**Current Profile:**
{profile}

**Step 1: Identify used deductions**
{used_deductions}

**Step 2: Identify opportunities**
{opportunities}

**Step 3: Rank by impact (marginal tax rate × gap)**
{ranking}

**Step 4: Recommend action plan**
{action_plan}

**Total Potential Savings:** {total_savings}"""
        }
    }

    def __init__(self):
        self.active_role = "tax_expert"

    def get_system_prompt(self, role: str = None) -> str:
        """Get the system prompt for a specific role."""
        role = role or self.active_role
        role_config = self.SYSTEM_ROLES.get(role, self.SYSTEM_ROLES["tax_expert"])
        return role_config["prompt"]

    def get_few_shot_examples(self, task: str) -> List[Dict]:
        """Get few-shot examples for a specific task."""
        return self.FEW_SHOT_EXAMPLES.get(task, {}).get("examples", [])

    def build_cot_prompt(self, template_name: str, **kwargs) -> str:
        """Build a chain-of-thought prompt with filled values."""
        template = self.CHAIN_OF_THOUGHT.get(template_name, {}).get("template", "")
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Template error: missing key {e}"

    def generate_regime_cot(self, user_data: Dict, old_tax: float, new_tax: float) -> str:
        """Generate chain-of-thought reasoning for regime recommendation."""
        income = user_data.get('annual_income', 0)
        deductions = (
            user_data.get('investments_80c', 0) +
            user_data.get('medical_insurance_80d', 0) +
            user_data.get('home_loan_interest', 0) +
            user_data.get('nps_contribution', 0)
        )

        return self.build_cot_prompt(
            "regime_decision",
            given_info=f"Income: ₹{income:,.0f}, Total Deductions: ₹{deductions:,.0f}",
            old_analysis=f"Under old regime with ₹{50000:,} std deduction + ₹{deductions:,.0f} deductions, taxable = ₹{max(0, income-50000-deductions):,.0f} → Tax = ₹{old_tax:,.0f}",
            new_analysis=f"Under new regime with ₹{75000:,} std deduction only, taxable = ₹{max(0, income-75000):,.0f} → Tax = ₹{new_tax:,.0f}",
            comparison=f"Old: ₹{old_tax:,.0f} vs New: ₹{new_tax:,.0f}. Difference = ₹{abs(old_tax-new_tax):,.0f}",
            conclusion=f"{'OLD' if old_tax <= new_tax else 'NEW'} regime is better, saving ₹{abs(old_tax-new_tax):,.0f}"
        )

    def get_all_templates_info(self) -> Dict:
        """Get summary of all available prompt templates."""
        return {
            'roles': {k: v['role'] for k, v in self.SYSTEM_ROLES.items()},
            'few_shot_tasks': list(self.FEW_SHOT_EXAMPLES.keys()),
            'cot_templates': list(self.CHAIN_OF_THOUGHT.keys()),
            'active_role': self.active_role
        }


# Module-level instance
prompt_engine = PromptTemplateEngine()
