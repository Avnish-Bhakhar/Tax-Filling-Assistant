# Prompt Design Documentation

## Overview

The AI Tax Filing Assistant uses three key prompt engineering techniques
to generate high-quality, contextual responses:

1. **Role-Based Prompting** — Persona definition
2. **Few-Shot Prompting** — Example-driven responses
3. **Chain-of-Thought (CoT)** — Step-by-step reasoning

---

## 1. Role-Based Prompting

### Available Roles

#### Tax Expert (Default)
```
You are an experienced Indian Tax Consultant with 15+ years of expertise
in income tax filing, tax planning, and compliance. You are patient,
thorough, and always explain concepts in simple language. You follow
the latest Income Tax Act provisions for FY 2024-25 (AY 2025-26).
```

#### Filing Assistant
```
You are a friendly tax filing assistant helping users complete their
Income Tax Return step by step. You ask clear questions, validate
inputs, and guide them through each section of the ITR form.
```

#### Tax Optimizer
```
You are a tax optimization AI that analyzes financial profiles to
minimize legal tax liability. You identify missed deductions, compare
regimes, and suggest investment strategies.
```

### How It Works
The system prompt sets the persona's expertise, communication style,
and ethical boundaries. The chatbot responds consistently within
this persona throughout the conversation.

---

## 2. Few-Shot Prompting

### Regime Comparison Example

**Input**: "I earn 12 lakhs and have 2 lakh deductions. Which regime?"

**Output**:
```
Old Regime: Taxable = ₹12L - ₹50K (std) - ₹2L = ₹9.5L → Tax = ₹1,06,600
New Regime: Taxable = ₹12L - ₹75K = ₹11.25L → Tax = ₹71,500
✅ NEW REGIME saves you ₹35,100!
```

### Deduction Advice Example

**Input**: "I earn 10L and only have 80K in 80C. How to save more?"

**Output**:
```
You have ₹70,000 gap in 80C alone! Action plan:
1. ELSS: ₹40K (3yr lock-in, ~12% returns)
2. PPF: ₹30K (safe, 7.1% guaranteed)
3. NPS 80CCD(1B): ₹50K EXTRA deduction
4. 80D Health Insurance: ₹25K
Total additional savings: ₹30,160 at 20% rate
```

---

## 3. Chain-of-Thought (CoT) Reasoning

### Tax Calculation CoT

```
Step 1: Identify total income → ₹12,00,000
Step 2: Apply standard deduction → ₹12,00,000 - ₹50,000 = ₹11,50,000
Step 3: Calculate deductions → 80C: ₹1.5L + 80D: ₹25K = ₹1,75,000
Step 4: Taxable income → ₹11,50,000 - ₹1,75,000 = ₹9,75,000
Step 5: Apply tax slabs → ₹0 + ₹12,500 + ₹95,000 = ₹1,07,500
Step 6: Check 87A rebate → Not eligible (>₹5L)
Step 7: Add cess 4% → ₹1,07,500 + ₹4,300 = ₹1,11,800
Final: Total tax = ₹1,11,800 | Effective rate = 9.32%
```

### Regime Decision CoT

```
Question: Which regime is better?
Given: Income = ₹15L, Deductions = ₹5L

Chain 1 — Old Regime:
  Taxable = ₹15L - ₹50K - ₹5L = ₹9.5L → Tax = ₹1,06,600

Chain 2 — New Regime:
  Taxable = ₹15L - ₹75K = ₹14.25L → Tax = ₹1,78,100

Chain 3 — Comparison:
  Old: ₹1,06,600 vs New: ₹1,78,100 → Difference = ₹71,500

Conclusion: OLD regime saves ₹71,500
```

---

## Implementation Details

All prompt templates are defined in `backend/app/services/prompt_templates.py`:

- `PromptTemplateEngine.SYSTEM_ROLES` — Role definitions
- `PromptTemplateEngine.FEW_SHOT_EXAMPLES` — Example Q&A pairs
- `PromptTemplateEngine.CHAIN_OF_THOUGHT` — Reasoning templates

The templates are used by:
- `generative_engine.py` — For generating summaries and explanations
- `chatbot_engine.py` — For context-aware response generation
- `simulator_routes.py` — For regime comparison narratives

---

## Template Variables

Templates use Python f-string formatting:
- `{income}` — User's annual income
- `{deductions}` — Total deductions amount
- `{regime}` — Recommended regime
- `{tax_amount}` — Computed tax
- `{savings}` — Potential savings
