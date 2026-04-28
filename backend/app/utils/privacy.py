"""
Privacy & Data Protection Module
Implements responsible AI practices including data anonymization,
consent management, and GDPR/DPDPA-inspired data handling.
"""

import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class DataPrivacyManager:
    """
    Manages data privacy, anonymization, and consent for user data.
    Follows principles inspired by India's DPDPA (Digital Personal Data Protection Act).
    """

    # Categories of personal data
    SENSITIVE_FIELDS = {
        'pan_number', 'aadhaar_number', 'phone', 'email',
        'bank_account', 'address', 'date_of_birth'
    }

    FINANCIAL_FIELDS = {
        'annual_income', 'investments', 'bank_balance',
        'loan_amount', 'salary', 'deductions'
    }

    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.consent_log: Dict[str, Dict] = {}
        self.data_processing_log: List[Dict] = []

    def anonymize_pan(self, pan: str) -> str:
        """Anonymize PAN number: ABCDE1234F → A***E****F"""
        if pan and len(pan) == 10:
            return f"{pan[0]}***{pan[4]}****{pan[9]}"
        return "[INVALID_PAN]"

    def anonymize_aadhaar(self, aadhaar: str) -> str:
        """Anonymize Aadhaar: Show only last 4 digits."""
        clean = re.sub(r'\D', '', str(aadhaar))
        if len(clean) == 12:
            return f"XXXX-XXXX-{clean[-4:]}"
        return "[INVALID_AADHAAR]"

    def anonymize_email(self, email: str) -> str:
        """Anonymize email: john.doe@gmail.com → j***e@g***l.com"""
        if '@' in email:
            local, domain = email.split('@')
            if len(local) > 2:
                local = f"{local[0]}***{local[-1]}"
            domain_parts = domain.split('.')
            if len(domain_parts[0]) > 2:
                domain_parts[0] = f"{domain_parts[0][0]}***{domain_parts[0][-1]}"
            return f"{local}@{'.'.join(domain_parts)}"
        return "[INVALID_EMAIL]"

    def anonymize_data(self, data: Dict) -> Dict:
        """
        Anonymize sensitive fields in a data dictionary.
        Returns a copy with sensitive fields masked.
        """
        result = data.copy()

        if 'pan_number' in result:
            result['pan_number'] = self.anonymize_pan(result['pan_number'])
        if 'aadhaar_number' in result:
            result['aadhaar_number'] = self.anonymize_aadhaar(result['aadhaar_number'])
        if 'email' in result:
            result['email'] = self.anonymize_email(result['email'])
        if 'phone' in result:
            result['phone'] = f"{'X' * (len(str(result['phone'])) - 4)}{str(result['phone'])[-4:]}"
        if 'bank_account' in result:
            result['bank_account'] = f"{'X' * (len(str(result['bank_account'])) - 4)}{str(result['bank_account'])[-4:]}"

        return result

    def hash_identifier(self, identifier: str) -> str:
        """Create a one-way hash of an identifier for anonymous tracking."""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    def record_consent(self, user_id: str, purpose: str, granted: bool):
        """Record user consent for data processing."""
        if user_id not in self.consent_log:
            self.consent_log[user_id] = {}

        self.consent_log[user_id][purpose] = {
            'granted': granted,
            'timestamp': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(days=self.retention_days)).isoformat()
        }

        self.data_processing_log.append({
            'action': 'consent_recorded',
            'user_hash': self.hash_identifier(user_id),
            'purpose': purpose,
            'granted': granted,
            'timestamp': datetime.now().isoformat()
        })

    def check_consent(self, user_id: str, purpose: str) -> bool:
        """Check if user has given valid consent for a specific purpose."""
        if user_id not in self.consent_log:
            return False
        if purpose not in self.consent_log[user_id]:
            return False

        consent = self.consent_log[user_id][purpose]
        if not consent['granted']:
            return False

        # Check expiry
        expiry = datetime.fromisoformat(consent['expires'])
        if datetime.now() > expiry:
            return False

        return True

    def get_data_summary(self, user_id: str) -> Dict:
        """Get summary of data held for a user (Right to Information)."""
        return {
            'user_hash': self.hash_identifier(user_id),
            'consents': self.consent_log.get(user_id, {}),
            'data_retention_days': self.retention_days,
            'processing_purposes': [
                'tax_calculation', 'regime_recommendation',
                'deduction_optimization', 'audit_risk_assessment'
            ],
            'data_categories': {
                'sensitive': list(self.SENSITIVE_FIELDS),
                'financial': list(self.FINANCIAL_FIELDS)
            },
            'your_rights': [
                'Right to access your data',
                'Right to correction',
                'Right to erasure',
                'Right to data portability',
                'Right to withdraw consent'
            ]
        }

    def generate_privacy_notice(self) -> str:
        """Generate privacy notice for the application."""
        return """
        PRIVACY NOTICE — AI Tax Filing Assistant
        ==========================================

        DATA COLLECTION:
        We collect financial information solely for the purpose of tax calculation
        and filing assistance. This includes income details, deductions, and
        investment information.

        AI PROCESSING:
        Your data is processed by AI models for:
        - Tax regime recommendation
        - Tax liability prediction
        - Deduction optimization
        - Audit risk assessment
        - Chatbot-based guidance

        DATA PROTECTION:
        - All sensitive data (PAN, Aadhaar) is anonymized in logs
        - Data is retained for {retention} days only
        - No data is shared with third parties
        - All processing happens locally on this system

        YOUR RIGHTS:
        - Access your data
        - Request correction
        - Request deletion
        - Withdraw consent at any time

        AI TRANSPARENCY:
        - All AI recommendations include explanations
        - Feature importance is provided for ML decisions
        - Confidence scores accompany all predictions
        - Disclaimer: AI recommendations should not replace professional tax advice
        """.format(retention=self.retention_days)


# Singleton instance
privacy_manager = DataPrivacyManager()
