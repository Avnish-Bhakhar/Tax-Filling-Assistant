/**
 * TaxBot AI — What-If Tax Simulator Controller
 * Real-time tax simulation with interactive sliders
 */

let simulatorInitialized = false;

function initSimulator() {
    if (simulatorInitialized) return;

    // Setup slider event listeners
    const sliders = {
        'sim-income': { display: 'sim-income-val', format: v => `₹${Number(v).toLocaleString('en-IN')}` },
        'sim-80c': { display: 'sim-80c-val', format: v => `₹${Number(v).toLocaleString('en-IN')}` },
        'sim-80d': { display: 'sim-80d-val', format: v => `₹${Number(v).toLocaleString('en-IN')}` },
        'sim-nps': { display: 'sim-nps-val', format: v => `₹${Number(v).toLocaleString('en-IN')}` },
        'sim-hl': { display: 'sim-hl-val', format: v => `₹${Number(v).toLocaleString('en-IN')}` },
        'sim-hra': { display: 'sim-hra-val', format: v => `₹${Number(v).toLocaleString('en-IN')}` },
    };

    Object.entries(sliders).forEach(([id, config]) => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', () => {
                document.getElementById(config.display).textContent = config.format(slider.value);
            });
        }
    });

    // Simulate button
    document.getElementById('btn-simulate').addEventListener('click', runSimulation);

    // Run initial simulation
    runSimulation();

    simulatorInitialized = true;
}

function getSimulatorData() {
    return {
        annual_income: parseFloat(document.getElementById('sim-income').value) || 1200000,
        investments_80c: parseFloat(document.getElementById('sim-80c').value) || 0,
        medical_insurance_80d: parseFloat(document.getElementById('sim-80d').value) || 0,
        nps_contribution: parseFloat(document.getElementById('sim-nps').value) || 0,
        home_loan_interest: parseFloat(document.getElementById('sim-hl').value) || 0,
        hra_received: parseFloat(document.getElementById('sim-hra').value) || 0,
        basic_salary: (parseFloat(document.getElementById('sim-income').value) || 1200000) * 0.5,
        rent_paid: 240000,
        metro_city: true,
        age: 30,
        employment_type: 'salaried',
        city_tier: 1,
        savings_interest: 10000,
        professional_tax: 2400,
        leave_travel_allowance: 0,
        other_income: 0,
        donations_80g: 0,
        education_loan_interest: 0
    };
}

async function runSimulation() {
    const btn = document.getElementById('btn-simulate');
    btn.innerHTML = '<span class="loading"></span> Simulating...';
    btn.disabled = true;

    try {
        const data = getSimulatorData();
        const result = await API.compareRegimes(data);

        if (result.status === 'success') {
            const comp = result.data.comparison;
            const oldTax = comp.old_regime.total_tax;
            const newTax = comp.new_regime.total_tax;
            const savings = comp.potential_savings;
            const recommended = comp.recommended_regime;

            // Update cards
            document.getElementById('sim-old-tax').textContent = `₹${oldTax.toLocaleString('en-IN')}`;
            document.getElementById('sim-new-tax').textContent = `₹${newTax.toLocaleString('en-IN')}`;
            document.getElementById('sim-savings').textContent = `₹${savings.toLocaleString('en-IN')}`;
            document.getElementById('sim-old-rate').textContent = `${comp.old_regime.effective_rate}% effective`;
            document.getElementById('sim-new-rate').textContent = `${comp.new_regime.effective_rate}% effective`;
            document.getElementById('sim-best-regime').textContent = `with ${recommended.toUpperCase()} regime`;

            // Render chart
            renderSimulatorChart(comp);
        }
    } catch (e) {
        console.error('Simulation error:', e);
        document.getElementById('sim-old-tax').textContent = '—';
        document.getElementById('sim-new-tax').textContent = '—';
        document.getElementById('sim-savings').textContent = '—';
        document.getElementById('chart-simulator').innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:2rem;">Start the backend server to use the simulator</p>';
    } finally {
        btn.innerHTML = 'Run Simulation';
        btn.disabled = false;
    }
}

function renderSimulatorChart(comparison) {
    const oldR = comparison.old_regime;
    const newR = comparison.new_regime;
    const income = oldR.gross_income;

    const c = typeof getPlotlyColors === 'function' ? getPlotlyColors() : {
        textColor: '#8b95a8', titleColor: '#e8ecf4', gridColor: 'rgba(255,255,255,0.05)', bgColor: 'rgba(0,0,0,0)'
    };

    // Waterfall-style bar chart showing tax components
    const categories = ['Gross Income', 'Std Deduction', 'Deductions', 'Taxable Income', 'Base Tax', 'Rebate', 'Cess', 'Total Tax'];

    const oldValues = [
        income, -oldR.standard_deduction, -oldR.total_deductions,
        oldR.taxable_income, oldR.tax_before_rebate, -oldR.rebate_87a,
        oldR.cess, oldR.total_tax
    ];
    const newValues = [
        income, -newR.standard_deduction, -newR.total_deductions,
        newR.taxable_income, newR.tax_before_rebate, -newR.rebate_87a,
        newR.cess, newR.total_tax
    ];

    const trace1 = {
        x: categories,
        y: oldValues.map(v => Math.abs(v)),
        name: 'Old Regime',
        type: 'bar',
        marker: {
            color: oldValues.map(v => v < 0 ? 'rgba(229, 166, 62, 0.3)' : 'rgba(229, 166, 62, 0.7)'),
            line: { width: 1, color: c.gridColor }
        }
    };

    const trace2 = {
        x: categories,
        y: newValues.map(v => Math.abs(v)),
        name: 'New Regime',
        type: 'bar',
        marker: {
            color: newValues.map(v => v < 0 ? 'rgba(79, 109, 245, 0.3)' : 'rgba(79, 109, 245, 0.7)'),
            line: { width: 1, color: c.gridColor }
        }
    };

    const layout = {
        paper_bgcolor: c.bgColor,
        plot_bgcolor: c.bgColor,
        font: { family: 'Inter, sans-serif', color: c.textColor, size: 12 },
        margin: { t: 20, r: 20, b: 80, l: 70 },
        barmode: 'group',
        xaxis: {
            tickangle: -25,
            gridcolor: c.gridColor
        },
        yaxis: {
            gridcolor: c.gridColor,
            title: 'Amount (₹)',
            tickformat: ',.0f'
        },
        legend: {
            font: { color: c.textColor },
            orientation: 'h',
            y: -0.3
        }
    };

    Plotly.newPlot('chart-simulator', [trace1, trace2], layout, { responsive: true, displayModeBar: false });
}
