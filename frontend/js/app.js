/**
 * TaxBot AI — Main Application Controller
 * Handles tab navigation, form submission, and result display
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initTaxForm();
    checkModelStatus();
});

// ═══════════════════ TAB NAVIGATION ═══════════════════
function initNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            switchTab(targetTab);
        });
    });
}

function switchTab(tabName) {
    // Update nav
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Trigger tab-specific loading
    if (tabName === 'dashboard') initDashboard();
    if (tabName === 'simulator') initSimulator();
}

// ═══════════════════ MODEL STATUS ═══════════════════
async function checkModelStatus() {
    try {
        const result = await API.getModelStatus();
        if (result.models) {
            const trained = Object.values(result.models).filter(m => m.trained || m.active).length;
            document.getElementById('stat-models').textContent = trained;
            document.getElementById('model-status-text').textContent = `${trained} AI Models Active`;
        }
    } catch (e) {
        document.getElementById('model-status-text').textContent = 'Connecting...';
        document.querySelector('.status-dot').style.background = '#e5a63e';
    }
}

// ═══════════════════ TAX FORM ═══════════════════
function initTaxForm() {
    const form = document.getElementById('tax-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await calculateAndDisplay();
    });

    document.getElementById('btn-regime').addEventListener('click', getRegimeRecommendation);
    document.getElementById('btn-deductions').addEventListener('click', getDeductionTips);
}

function getFormData() {
    return {
        name: document.getElementById('input-name').value || 'Taxpayer',
        age: parseInt(document.getElementById('input-age').value) || 30,
        annual_income: parseFloat(document.getElementById('input-income').value) || 0,
        employment_type: document.getElementById('input-employment').value,
        basic_salary: parseFloat(document.getElementById('input-basic').value) || 0,
        hra_received: parseFloat(document.getElementById('input-hra').value) || 0,
        rent_paid: parseFloat(document.getElementById('input-rent').value) || 0,
        metro_city: document.getElementById('input-metro').value === 'true',
        investments_80c: parseFloat(document.getElementById('input-80c').value) || 0,
        medical_insurance_80d: parseFloat(document.getElementById('input-80d').value) || 0,
        home_loan_interest: parseFloat(document.getElementById('input-homeloan').value) || 0,
        education_loan_interest: parseFloat(document.getElementById('input-eduloan').value) || 0,
        nps_contribution: parseFloat(document.getElementById('input-nps').value) || 0,
        donations_80g: parseFloat(document.getElementById('input-donations').value) || 0,
        savings_interest: parseFloat(document.getElementById('input-savings-interest').value) || 0,
        other_income: parseFloat(document.getElementById('input-other-income').value) || 0,
        professional_tax: 2400,
        leave_travel_allowance: 0,
        city_tier: 1,
        regime: 'auto'
    };
}

async function calculateAndDisplay() {
    const btn = document.getElementById('btn-calculate');
    btn.innerHTML = '<span class="loading"></span> Computing...';
    btn.disabled = true;

    try {
        const data = getFormData();
        const result = await API.calculateTax(data);

        if (result.status === 'success') {
            displayTaxResults(result.data, data);
        }
    } catch (error) {
        showError('Unable to connect to the server. Please ensure the backend is running.');
    } finally {
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> Calculate Tax & Get AI Recommendations`;
        btn.disabled = false;
    }
}

function displayTaxResults(data, formData) {
    const section = document.getElementById('results-section');
    const content = document.getElementById('results-content');
    section.classList.remove('hidden');

    const recommended = data.recommended_regime || 'new';
    const oldTax = data.old_regime?.total_tax || 0;
    const newTax = data.new_regime?.total_tax || 0;
    const savings = data.potential_savings || 0;
    const bestResult = data[`${recommended}_regime`] || data.old_regime || {};

    content.innerHTML = `
        <div class="result-card">
            <h3>AI Tax Computation Result</h3>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">Recommended Regime</div>
                    <div class="value highlight">${recommended.toUpperCase()}</div>
                    <span class="regime-badge ${recommended}">${recommended === 'old' ? 'Old Regime' : 'New Regime'}</span>
                </div>
                <div class="result-item">
                    <div class="label">Total Tax Liability</div>
                    <div class="value">₹${bestResult.total_tax?.toLocaleString('en-IN') || '0'}</div>
                </div>
                <div class="result-item">
                    <div class="label">You Save</div>
                    <div class="value highlight">₹${savings.toLocaleString('en-IN')}</div>
                </div>
                <div class="result-item">
                    <div class="label">Effective Tax Rate</div>
                    <div class="value">${bestResult.effective_rate || 0}%</div>
                </div>
                <div class="result-item">
                    <div class="label">Old Regime Tax</div>
                    <div class="value">₹${oldTax.toLocaleString('en-IN')}</div>
                </div>
                <div class="result-item">
                    <div class="label">New Regime Tax</div>
                    <div class="value">₹${newTax.toLocaleString('en-IN')}</div>
                </div>
                <div class="result-item">
                    <div class="label">Taxable Income</div>
                    <div class="value">₹${bestResult.taxable_income?.toLocaleString('en-IN') || '0'}</div>
                </div>
                <div class="result-item">
                    <div class="label">Total Deductions</div>
                    <div class="value">₹${bestResult.total_deductions?.toLocaleString('en-IN') || '0'}</div>
                </div>
            </div>
        </div>

        <div class="result-card">
            <h3>Step-by-Step Computation</h3>
            <div class="result-steps">${(bestResult.computation_steps || []).join('\n')}</div>
        </div>
    `;

    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function getRegimeRecommendation() {
    const btn = document.getElementById('btn-regime');
    btn.innerHTML = '<span class="loading"></span> Analyzing...';

    try {
        const data = getFormData();
        const result = await API.recommendRegime(data);
        const auditResult = await API.assessAuditRisk(data);

        if (result.status === 'success') {
            const section = document.getElementById('results-section');
            const content = document.getElementById('results-content');
            section.classList.remove('hidden');

            const ml = result.data.ml_recommendation;
            const bayesian = result.data.bayesian_analysis;
            const explanation = result.data.explanation;
            const audit = auditResult.data || {};

            content.innerHTML = `
                <div class="result-card">
                    <h3>AI Regime Recommendation</h3>
                    <div class="result-grid">
                        <div class="result-item">
                            <div class="label">ML Recommended</div>
                            <div class="value highlight">${ml.recommended_regime?.toUpperCase()}</div>
                        </div>
                        <div class="result-item">
                            <div class="label">ML Confidence</div>
                            <div class="value">${ml.confidence}%</div>
                        </div>
                        <div class="result-item">
                            <div class="label">Bayesian Recommended</div>
                            <div class="value">${bayesian.recommended_regime?.toUpperCase()}</div>
                        </div>
                        <div class="result-item">
                            <div class="label">Bayesian Confidence</div>
                            <div class="value">${bayesian.confidence}%</div>
                        </div>
                        <div class="result-item">
                            <div class="label">Model Type</div>
                            <div class="value" style="font-size:0.8rem">${ml.model_type}</div>
                        </div>
                        <div class="result-item">
                            <div class="label">Methodology</div>
                            <div class="value" style="font-size:0.8rem">${bayesian.methodology || 'Bayesian Network'}</div>
                        </div>
                    </div>
                    <div class="result-steps">${explanation?.summary || ''}\n\n${explanation?.factors || ''}</div>
                </div>

                <div class="result-card">
                    <h3>Audit Risk Assessment (Bayesian Network)</h3>
                    <div class="result-grid">
                        <div class="result-item">
                            <div class="label">Risk Level</div>
                            <div class="value" style="color:${audit.risk_level === 'low' ? 'var(--accent-teal)' : audit.risk_level === 'medium' ? 'var(--accent-amber)' : 'var(--accent-rose)'}">${(audit.risk_level || 'N/A').toUpperCase()}</div>
                        </div>
                        <div class="result-item">
                            <div class="label">Probability</div>
                            <div class="value">${audit.audit_probability || 0}%</div>
                        </div>
                    </div>
                    ${audit.risk_factors?.length ? `<ul class="advice-list">${audit.risk_factors.map(f => `<li>${f}</li>`).join('')}</ul>` : ''}
                    ${audit.recommendations?.length ? `<ul class="advice-list">${audit.recommendations.map(r => `<li>${r}</li>`).join('')}</ul>` : ''}
                </div>
            `;

            section.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        showError('Failed to get AI recommendation. Ensure the backend is running.');
    } finally {
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> AI Regime Recommendation';
    }
}

async function getDeductionTips() {
    const btn = document.getElementById('btn-deductions');
    btn.innerHTML = '<span class="loading"></span> Analyzing...';

    try {
        const data = getFormData();
        const result = await API.recommendDeductions(data);

        if (result.status === 'success') {
            const section = document.getElementById('results-section');
            const content = document.getElementById('results-content');
            section.classList.remove('hidden');

            const recs = result.data.recommendations || [];

            content.innerHTML = `
                <div class="result-card">
                    <h3>AI Deduction Recommendations</h3>
                    <div class="result-grid">
                        <div class="result-item">
                            <div class="label">Total Potential Savings</div>
                            <div class="value highlight">₹${(result.data.total_potential_savings || 0).toLocaleString('en-IN')}</div>
                        </div>
                        <div class="result-item">
                            <div class="label">Your Marginal Rate</div>
                            <div class="value">${result.data.marginal_tax_rate || 'N/A'}</div>
                        </div>
                        <div class="result-item">
                            <div class="label">Strategy</div>
                            <div class="value" style="font-size:0.8rem">${result.data.optimization_strategy || 'Greedy Heuristic'}</div>
                        </div>
                    </div>
                    <ul class="advice-list">
                        ${recs.map(r => `
                            <li>
                                <strong>${r.section} — ${r.title || ''}</strong><br>
                                ${r.reason}<br>
                                ${r.potential_savings > 0 ? `Potential savings: <strong>₹${r.potential_savings.toLocaleString('en-IN')}</strong>` : ''}
                                ${r.gap > 0 ? ` | Gap: ₹${r.gap.toLocaleString('en-IN')}` : ''}
                                ${r.tip ? `<br>${r.tip}` : ''}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
            section.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        showError('Failed to get deduction tips. Ensure the backend is running.');
    } finally {
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> Smart Deduction Tips';
    }
}

function showError(msg) {
    const section = document.getElementById('results-section');
    const content = document.getElementById('results-content');
    section.classList.remove('hidden');
    content.innerHTML = `
        <div class="result-card" style="border-color:rgba(224,84,113,0.3);">
            <h3>Connection Error</h3>
            <p style="color:var(--text-secondary);">${msg}</p>
            <p style="color:var(--text-muted);font-size:0.85rem;margin-top:0.75rem;">
                Run these commands to start the server:<br>
                <code style="color:var(--accent-cyan);font-family:var(--font-mono);">cd backend && pip install -r requirements.txt && python training/train_all_models.py && python -m app.main</code>
            </p>
        </div>
    `;
}

function formatINR(num) {
    return '₹' + Number(num).toLocaleString('en-IN');
}
