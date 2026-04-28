# Ethics Statement — Responsible AI in Tax Filing

## 1. Transparency & Explainability

### Decision Explanations
Every AI recommendation includes:
- **Feature importance rankings** — Shows which factors drove the decision
- **Confidence scores** — Indicates model certainty (0-100%)
- **Methodology labels** — Clearly states which algorithm was used
- **Chain-of-thought reasoning** — Step-by-step explanation of calculations

### Model Documentation
- All models are documented with architecture details
- Training metrics (accuracy, R², MAE) are tracked and displayed
- Model versions are registered in the MLOps registry

## 2. Data Privacy & Protection

### PII Handling (Inspired by India's DPDPA)
- **PAN numbers** — Automatically redacted in logs (ABCPK1234M → A***K****M)
- **Aadhaar numbers** — Masked to show only last 4 digits
- **Email addresses** — Partially anonymized in logs
- **Phone numbers** — Masked except last 4 digits

### Data Minimization
- Only financial data necessary for tax computation is processed
- No data is stored permanently — session-based processing
- Data retention policy: 30 days maximum

### Consent Management
- Purpose-specific consent tracking
- Right to access, correction, and deletion
- Transparent privacy notice available at `/api/privacy-notice`

## 3. Fairness & Bias Mitigation

### Training Data
- Synthetic dataset designed with balanced distribution across:
  - Income levels (₹3L to ₹31L+)
  - Age groups (22 to 55)
  - Employment types (salaried, self-employed)
  - Both tax regimes (old and new)
  - Metro and non-metro cities

### Model Validation
- Cross-validation ensures consistent performance across subgroups
- Feature importance analysis reveals no demographic bias
- Rule-based fallbacks ensure equitable access even without trained models

## 4. Safety & Reliability

### Disclaimers
- Clear statement: "AI recommendations are for informational purposes only"
- Professional consultation recommended for complex cases
- All outputs include confidence levels for user judgment

### Error Handling
- Graceful degradation — rule-based fallbacks when ML models fail
- Input validation on all API endpoints
- Structured logging for debugging without exposing PII

### Security
- No external API calls — all processing happens locally
- No sensitive data transmitted to third parties
- CORS protection on API endpoints

## 5. Human Oversight

### Design Philosophy
- AI assists, humans decide
- Users can override any AI recommendation
- Manual regime selection always available
- Tax calculations shown step-by-step for verification

### Audit Trail
- All AI predictions are logged (with PII redaction)
- Model performance monitored over time
- Deployment events tracked in registry

## 6. Accountability

### Limitations Acknowledged
- Tax laws change annually — model trained on FY 2024-25 rules
- Synthetic training data may not capture all edge cases
- NLP chatbot has limited vocabulary (~25 intent categories)
- Document parsing relies on text patterns — may miss complex formats

### Continuous Improvement
- MLOps pipeline enables retraining with new data
- Model monitoring detects performance drift
- User feedback loop for chatbot improvement
