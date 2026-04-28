/**
 * TaxBot AI — API Client Wrapper
 * Centralized API communication layer
 */

const API = {
    // Replace with your actual Render backend URL after deployment
    BASE_URL: 'https://taxfilling-assistant-backend.onrender.com',

    async request(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, options);
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API call failed: ${endpoint}`, error);
            throw error;
        }
    },

    // Tax endpoints
    async calculateTax(data) {
        return this.request('/api/tax/calculate', 'POST', data);
    },

    async recommendRegime(data) {
        return this.request('/api/tax/recommend-regime', 'POST', data);
    },

    async predictLiability(data) {
        return this.request('/api/tax/predict-liability', 'POST', data);
    },

    async recommendDeductions(data) {
        return this.request('/api/tax/recommend-deductions', 'POST', data);
    },

    async assessAuditRisk(data) {
        return this.request('/api/tax/audit-risk', 'POST', data);
    },

    async generateSummary(data) {
        return this.request('/api/tax/generate-summary', 'POST', data);
    },

    // Chat endpoints
    async sendMessage(message, sessionId = 'default') {
        return this.request('/api/chat/message', 'POST', { message, session_id: sessionId });
    },

    async resetChat(sessionId = 'default') {
        return this.request('/api/chat/reset', 'POST', { session_id: sessionId });
    },

    // Analysis endpoints
    async getIncomeVsDeductions(data) {
        return this.request('/api/analysis/income-vs-deductions', 'POST', data);
    },

    async getTaxBreakdown(data) {
        return this.request('/api/analysis/tax-breakdown', 'POST', data);
    },

    async getFilingPath(data) {
        return this.request('/api/analysis/filing-path', 'POST', data);
    },

    async getSampleData() {
        return this.request('/api/analysis/sample-data');
    },

    // Document endpoints
    async classifyDocument(text) {
        return this.request('/api/documents/classify', 'POST', { text, document_type: 'auto' });
    },

    async extractDocumentData(text, docType = 'auto') {
        return this.request('/api/documents/extract', 'POST', { text, document_type: docType });
    },

    async getSampleForm16() {
        return this.request('/api/documents/sample-form16');
    },

    // Simulator endpoints
    async runWhatIf(baseData, scenarios = []) {
        return this.request('/api/simulator/what-if', 'POST', {
            base_data: baseData, scenarios
        });
    },

    async compareRegimes(data) {
        return this.request('/api/simulator/compare-regimes', 'POST', data);
    },

    // System endpoints
    async getHealth() {
        return this.request('/api/health');
    },

    async getModelStatus() {
        return this.request('/api/model-status');
    },

    async getGlossary() {
        return this.request('/api/glossary');
    }
};
