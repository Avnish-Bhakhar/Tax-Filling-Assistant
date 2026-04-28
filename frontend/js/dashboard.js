/**
 * TaxBot AI — Dashboard & Visualization Controller
 * Renders Plotly charts and A* filing path visualization
 */

let dashboardInitialized = false;

async function initDashboard() {
    if (dashboardInitialized) return;

    const data = getFormData();
    await Promise.all([
        renderIncomeDeductionsChart(data),
        renderTaxBreakdownChart(data),
        renderRegimeComparisonChart(data),
        renderFilingPath(data)
    ]);

    dashboardInitialized = true;

    // Refresh button
    document.getElementById('btn-refresh-dashboard').addEventListener('click', async () => {
        dashboardInitialized = false;
        await initDashboard();
    });
}

const plotlyLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Inter, sans-serif', color: '#94a3b8', size: 12 },
    margin: { t: 40, r: 20, b: 60, l: 60 },
    showlegend: true,
    legend: { font: { color: '#94a3b8' } }
};

const plotlyConfig = { responsive: true, displayModeBar: false };

async function renderIncomeDeductionsChart(formData) {
    try {
        const result = await API.getIncomeVsDeductions(formData);
        if (result.status !== 'success') return;

        const d = result.data;
        const trace = {
            x: d.categories,
            y: d.values,
            type: 'bar',
            marker: {
                color: d.colors,
                line: { color: 'rgba(255,255,255,0.1)', width: 1 }
            },
            text: d.values.map(v => '₹' + v.toLocaleString('en-IN')),
            textposition: 'outside',
            textfont: { size: 10, color: '#94a3b8' }
        };

        const layout = {
            ...plotlyLayout,
            title: { text: 'Income vs Deductions', font: { size: 14, color: '#f1f5f9' } },
            xaxis: { tickangle: -30, gridcolor: 'rgba(255,255,255,0.05)' },
            yaxis: { gridcolor: 'rgba(255,255,255,0.05)', title: 'Amount (₹)' }
        };

        Plotly.newPlot('chart-income-deductions', [trace], layout, plotlyConfig);
    } catch (e) {
        console.error('Income chart error:', e);
        document.getElementById('chart-income-deductions').innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:2rem;">Start the backend server to see charts</p>';
    }
}

async function renderTaxBreakdownChart(formData) {
    try {
        const result = await API.getTaxBreakdown(formData);
        if (result.status !== 'success') return;

        const d = result.data;
        const oldTax = d.old_regime?.total_tax || 0;
        const newTax = d.new_regime?.total_tax || 0;

        const trace = {
            values: [oldTax, newTax],
            labels: ['Old Regime', 'New Regime'],
            type: 'pie',
            hole: 0.55,
            marker: {
                colors: ['#f59e0b', '#6366f1'],
                line: { color: 'rgba(10,14,26,1)', width: 2 }
            },
            textinfo: 'label+value',
            textfont: { size: 12, color: '#f1f5f9' },
            hovertemplate: '%{label}: ₹%{value:,.0f}<extra></extra>'
        };

        const layout = {
            ...plotlyLayout,
            title: { text: 'Tax by Regime', font: { size: 14, color: '#f1f5f9' } },
            annotations: [{
                text: `₹${Math.min(oldTax, newTax).toLocaleString('en-IN')}`,
                showarrow: false,
                font: { size: 16, color: '#10b981', family: 'JetBrains Mono' }
            }]
        };

        Plotly.newPlot('chart-tax-breakdown', [trace], layout, plotlyConfig);
    } catch (e) {
        console.error('Tax breakdown error:', e);
        document.getElementById('chart-tax-breakdown').innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:2rem;">Start the backend server to see charts</p>';
    }
}

async function renderRegimeComparisonChart(formData) {
    try {
        const result = await API.compareRegimes(formData);
        if (result.status !== 'success') return;

        const comp = result.data.comparison;
        const oldR = comp.old_regime;
        const newR = comp.new_regime;

        const categories = ['Gross Income', 'Std Deduction', 'Deductions', 'Taxable Income', 'Tax', 'Cess', 'Total Tax'];
        const oldValues = [oldR.gross_income, oldR.standard_deduction, oldR.total_deductions, oldR.taxable_income, oldR.tax_before_rebate, oldR.cess, oldR.total_tax];
        const newValues = [newR.gross_income, newR.standard_deduction, newR.total_deductions, newR.taxable_income, newR.tax_before_rebate, newR.cess, newR.total_tax];

        const trace1 = {
            x: categories, y: oldValues, name: 'Old Regime',
            type: 'bar', marker: { color: 'rgba(245, 158, 11, 0.7)' }
        };
        const trace2 = {
            x: categories, y: newValues, name: 'New Regime',
            type: 'bar', marker: { color: 'rgba(99, 102, 241, 0.7)' }
        };

        const layout = {
            ...plotlyLayout,
            title: { text: 'Regime Comparison', font: { size: 14, color: '#f1f5f9' } },
            barmode: 'group',
            xaxis: { tickangle: -20, gridcolor: 'rgba(255,255,255,0.05)' },
            yaxis: { gridcolor: 'rgba(255,255,255,0.05)', title: 'Amount (₹)' }
        };

        Plotly.newPlot('chart-regime-comparison', [trace1, trace2], layout, plotlyConfig);
    } catch (e) {
        console.error('Regime chart error:', e);
        document.getElementById('chart-regime-comparison').innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:2rem;">Start the backend server to see charts</p>';
    }
}

async function renderFilingPath(formData) {
    const container = document.getElementById('chart-filing-path');
    try {
        const result = await API.getFilingPath(formData);
        if (result.status !== 'success') return;

        const data = result.data;
        const path = data.optimal_path || [];

        let html = `
            <div class="search-info">
                <span>Algorithm: <strong>${data.algorithm || 'A*'}</strong></span>
                <span>Steps: <strong>${data.total_steps || 0}</strong></span>
                <span>Cost: <strong>${data.total_cost || 0}</strong></span>
                <span>Nodes Explored: <strong>${data.nodes_explored || 0}</strong></span>
            </div>
        `;

        path.forEach((step, i) => {
            html += `
                <div class="path-step">
                    <div class="path-step-number">${i + 1}</div>
                    <div class="path-step-info">
                        <div class="path-step-name">${step.step_name}</div>
                        <div class="path-step-desc">${step.description}</div>
                    </div>
                    <div class="path-step-cost">f=${step.f_cost} | g=${step.g_cost} | h=${step.h_cost}</div>
                </div>
            `;
        });

        container.innerHTML = html;
    } catch (e) {
        console.error('Filing path error:', e);
        container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:2rem;">Start the backend server to see the A* filing path</p>';
    }
}
