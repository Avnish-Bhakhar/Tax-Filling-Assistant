/**
 * TaxBot AI — Document Processing Controller
 * Handles document upload, classification, and data extraction
 */

document.addEventListener('DOMContentLoaded', () => {
    initDocumentProcessing();
});

function initDocumentProcessing() {
    // Upload zone drag & drop
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFileUpload(files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFileUpload(e.target.files[0]);
    });

    // Buttons
    document.getElementById('btn-classify-doc').addEventListener('click', classifyDocument);
    document.getElementById('btn-extract-doc').addEventListener('click', extractDocumentData);
    document.getElementById('btn-load-sample').addEventListener('click', loadSampleForm16);
}

async function handleFileUpload(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const text = e.target.result;
        document.getElementById('doc-text-input').value = text;
        classifyAndExtract(text);
    };
    reader.readAsText(file);
}

async function classifyDocument() {
    const text = document.getElementById('doc-text-input').value.trim();
    if (!text) {
        alert('Please enter or paste document text first.');
        return;
    }

    const btn = document.getElementById('btn-classify-doc');
    btn.innerHTML = '<span class="loading"></span> Classifying...';

    try {
        const result = await API.classifyDocument(text);

        if (result.status === 'success') {
            displayDocResults(result.data, null);
        }
    } catch (e) {
        showDocError('Failed to classify document. Please ensure the backend is running.');
    } finally {
        btn.innerHTML = 'Classify Document';
    }
}

async function extractDocumentData() {
    const text = document.getElementById('doc-text-input').value.trim();
    if (!text) {
        alert('Please enter or paste document text first.');
        return;
    }

    const btn = document.getElementById('btn-extract-doc');
    btn.innerHTML = '<span class="loading"></span> Extracting...';

    try {
        const classResult = await API.classifyDocument(text);
        const extractResult = await API.extractDocumentData(text, classResult?.data?.document_type || 'auto');

        if (extractResult.status === 'success') {
            displayDocResults(classResult?.data, extractResult.data);
        }
    } catch (e) {
        showDocError('Failed to extract data. Please ensure the backend is running.');
    } finally {
        btn.innerHTML = 'Extract Data';
    }
}

async function classifyAndExtract(text) {
    try {
        const [classResult, extractResult] = await Promise.all([
            API.classifyDocument(text),
            API.extractDocumentData(text)
        ]);

        displayDocResults(classResult?.data, extractResult?.data);
    } catch (e) {
        showDocError('Processing failed.');
    }
}

async function loadSampleForm16() {
    const btn = document.getElementById('btn-load-sample');
    btn.innerHTML = '<span class="loading"></span> Loading...';

    try {
        const result = await API.getSampleForm16();
        if (result.status === 'success') {
            document.getElementById('doc-text-input').value = result.data.text;
        }
    } catch(e) {
        // Fallback sample
        document.getElementById('doc-text-input').value = `FORM NO. 16
Certificate under section 203 of the Income-tax Act, 1961
for tax deducted at source on salary

Name: Avnish Kumar
PAN of Employee: ABCPK1234M
TAN of Deductor: DELM12345A
Assessment Year: 2025-26
Employer: TechCorp India Pvt. Ltd.

Gross Salary: 12,00,000
Basic Salary: 6,00,000
House Rent Allowance: 3,00,000
Standard Deduction: 50,000
Section 80C Investments: 1,50,000
Section 80D Medical Insurance: 25,000
Professional Tax: 2,400
Net Taxable Income: 9,72,600
Total Tax: 1,07,640
TDS Deducted: 1,07,640`;
    } finally {
        btn.innerHTML = 'Load Sample Form 16';
    }
}

function displayDocResults(classification, extraction) {
    const container = document.getElementById('doc-results');
    const content = document.getElementById('doc-results-content');
    container.classList.remove('hidden');

    let html = '';

    if (classification) {
        html += `
            <div class="result-card">
                <h3>Deep Learning Classification</h3>
                <div class="result-grid">
                    <div class="result-item">
                        <div class="label">Document Type</div>
                        <div class="value highlight">${classification.document_label || 'Unknown'}</div>
                    </div>
                    <div class="result-item">
                        <div class="label">Confidence</div>
                        <div class="value">${classification.confidence || 0}%</div>
                    </div>
                    <div class="result-item">
                        <div class="label">Model</div>
                        <div class="value" style="font-size:0.8rem">${classification.model_type || 'Neural Network'}</div>
                    </div>
                </div>
                ${classification.class_probabilities ? `
                    <h4 style="margin-top:1rem;margin-bottom:0.5rem;font-size:0.9rem;">Class Probabilities</h4>
                    <div class="result-grid">
                        ${Object.entries(classification.class_probabilities).map(([cls, prob]) => `
                            <div class="result-item">
                                <div class="label">${cls}</div>
                                <div class="value" style="font-size:1rem">${prob}%</div>
                                <div style="background:rgba(99,102,241,0.1);border-radius:3px;height:6px;margin-top:0.25rem;overflow:hidden;">
                                    <div style="background:var(--gradient-accent);width:${prob}%;height:100%;border-radius:3px"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    if (extraction) {
        const data = extraction.extracted_data || {};
        const conf = extraction.confidence_scores || {};

        html += `
            <div class="result-card">
                <h3>NLP Data Extraction</h3>
                <div class="result-grid">
                    <div class="result-item">
                        <div class="label">Fields Found</div>
                        <div class="value highlight">${extraction.fields_found || 0}</div>
                    </div>
                    <div class="result-item">
                        <div class="label">Method</div>
                        <div class="value" style="font-size:0.85rem">${extraction.processing_method || 'NLP'}</div>
                    </div>
                </div>
                <h4 style="margin-top:1.5rem;margin-bottom:0.5rem;font-size:0.9rem;">Extracted Fields</h4>
                <div class="result-grid">
                    ${Object.entries(data).map(([field, value]) => `
                        <div class="result-item">
                            <div class="label">${field.replace(/_/g, ' ').toUpperCase()}</div>
                            <div class="value" style="font-size:0.95rem">${typeof value === 'number' ? '₹' + value.toLocaleString('en-IN') : value}</div>
                            ${conf[field] ? `<div style="font-size:0.7rem;color:var(--text-muted);margin-top:0.2rem;">Confidence: ${(conf[field] * 100).toFixed(0)}%</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    content.innerHTML = html;
    container.scrollIntoView({ behavior: 'smooth' });
}

function showDocError(msg) {
    const container = document.getElementById('doc-results');
    const content = document.getElementById('doc-results-content');
    container.classList.remove('hidden');
    content.innerHTML = `
        <div class="result-card" style="border-color:rgba(244,63,94,0.3);">
            <h3>Error</h3>
            <p style="color:var(--text-secondary);">${msg}</p>
        </div>`;
}
