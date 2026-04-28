"""
Document Processor Service
===========================
Extracts structured data from uploaded tax documents using
NLP techniques: regex patterns, field extraction, and the
deep learning document classifier.
"""

import re
from typing import Dict, List, Optional


class DocumentProcessor:
    """
    Processes uploaded tax documents to extract structured financial data.
    Combines regex pattern matching with field-specific extraction logic.
    """

    # Field extraction patterns
    EXTRACTION_PATTERNS = {
        'pan': r'[A-Z]{5}[0-9]{4}[A-Z]',
        'name': r'(?:Name|Employee\s*Name|Mr\.|Mrs\.|Ms\.)\s*[:\-]?\s*([A-Za-z\s\.]+)',
        'employer': r'(?:Employer|Company|Organization)\s*[:\-]?\s*([A-Za-z\s\.&,]+)',
        'gross_salary': r'(?:Gross\s*(?:Total\s*)?(?:Salary|Income)|Total\s*Earnings)\s*[:\-]?\s*₹?\s*([\d,]+)',
        'basic_salary': r'(?:Basic\s*(?:Salary|Pay))\s*[:\-]?\s*₹?\s*([\d,]+)',
        'hra': r'(?:HRA|House\s*Rent\s*Allowance)\s*[:\-]?\s*₹?\s*([\d,]+)',
        'tds': r'(?:TDS|Tax\s*Deducted|Total\s*Tax\s*Deducted)\s*[:\-]?\s*₹?\s*([\d,]+)',
        'deductions_80c': r'(?:(?:Section\s*)?80C|Deduction.*80C)\s*[:\-]?\s*₹?\s*([\d,]+)',
        'deductions_80d': r'(?:(?:Section\s*)?80D|Medical\s*Insurance)\s*[:\-]?\s*₹?\s*([\d,]+)',
        'net_tax': r'(?:Net\s*Tax|Tax\s*Payable|Total\s*Tax)\s*[:\-]?\s*₹?\s*([\d,]+)',
        'assessment_year': r'(?:Assessment\s*Year|AY)\s*[:\-]?\s*(\d{4}[\-/]\d{2,4})',
        'financial_year': r'(?:Financial\s*Year|FY)\s*[:\-]?\s*(\d{4}[\-/]\d{2,4})',
        'tan': r'[A-Z]{4}\d{5}[A-Z]',
        'professional_tax': r'(?:Professional\s*Tax)\s*[:\-]?\s*₹?\s*([\d,]+)',
        'standard_deduction': r'(?:Standard\s*Deduction)\s*[:\-]?\s*₹?\s*([\d,]+)',
    }

    def __init__(self):
        pass

    def extract_from_text(self, text: str, document_type: str = 'auto') -> Dict:
        """
        Extract structured data from document text.

        Args:
            text: Raw text content from the document
            document_type: Type of document (auto-detected if not specified)

        Returns:
            Dictionary with extracted fields and confidence scores
        """
        extracted = {}
        confidence_scores = {}

        for field, pattern in self.EXTRACTION_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                value = matches[0].strip() if isinstance(matches[0], str) else matches[0]
                # Clean numeric values
                if field in ['gross_salary', 'basic_salary', 'hra', 'tds',
                           'deductions_80c', 'deductions_80d', 'net_tax',
                           'professional_tax', 'standard_deduction']:
                    try:
                        value = float(value.replace(',', ''))
                    except (ValueError, AttributeError):
                        pass

                extracted[field] = value
                # Confidence based on pattern specificity
                confidence_scores[field] = 0.9 if len(matches) == 1 else 0.7

        # Post-processing
        if 'gross_salary' in extracted and 'basic_salary' not in extracted:
            extracted['basic_salary'] = extracted['gross_salary'] * 0.5  # Estimate
            confidence_scores['basic_salary'] = 0.4

        return {
            'extracted_data': extracted,
            'confidence_scores': confidence_scores,
            'fields_found': len(extracted),
            'document_type': document_type,
            'processing_method': 'NLP Regex + Pattern Matching',
            'note': 'Fields marked with low confidence should be verified manually.'
        }

    def process_form16(self, text: str) -> Dict:
        """Process Form 16 specifically."""
        result = self.extract_from_text(text, 'form16')

        # Form 16 specific fields
        form16_patterns = {
            'employer_tan': r'TAN\s*[:\-]?\s*([A-Z]{4}\d{5}[A-Z])',
            'employee_pan': r'PAN\s*(?:of\s*Employee)?\s*[:\-]?\s*([A-Z]{5}\d{4}[A-Z])',
            'total_income': r'(?:Gross\s*Total\s*Income|Total\s*Income)\s*[:\-]?\s*₹?\s*([\d,]+)',
            'total_tax_deposited': r'(?:Total\s*Tax\s*Deposited|Tax\s*Deposited)\s*[:\-]?\s*₹?\s*([\d,]+)',
        }

        for field, pattern in form16_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                if field in ['total_income', 'total_tax_deposited']:
                    try:
                        value = float(value.replace(',', ''))
                    except (ValueError, AttributeError):
                        pass
                result['extracted_data'][field] = value
                result['confidence_scores'][field] = 0.85

        return result

    def process_salary_slip(self, text: str) -> Dict:
        """Process salary slip specifically."""
        result = self.extract_from_text(text, 'salary_slip')

        slip_patterns = {
            'month': r'(?:Month|Period|Pay\s*Period)\s*[:\-]?\s*([A-Za-z]+\s*\d{4})',
            'net_pay': r'(?:Net\s*Pay|Take\s*Home|Net\s*Salary)\s*[:\-]?\s*₹?\s*([\d,]+)',
            'epf_contribution': r'(?:EPF|PF|Provident\s*Fund)\s*[:\-]?\s*₹?\s*([\d,]+)',
        }

        for field, pattern in slip_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                if field in ['net_pay', 'epf_contribution']:
                    try:
                        value = float(value.replace(',', ''))
                    except (ValueError, AttributeError):
                        pass
                result['extracted_data'][field] = value
                result['confidence_scores'][field] = 0.8

        return result

    def generate_sample_form16_text(self) -> str:
        """Generate a sample Form 16 text for testing."""
        return """
        FORM NO. 16
        [See rule 31(1)(a)]

        Certificate under section 203 of the Income-tax Act, 1961
        for tax deducted at source on salary

        PART A

        Name: Avnish Kumar
        PAN of Employee: ABCPK1234M
        TAN of Deductor: DELM12345A
        Assessment Year: 2025-26

        Employer: TechCorp India Pvt. Ltd.

        Period: April 2024 to March 2025

        PART B
        1. Gross Salary: 12,00,000
        2. Basic Salary: 6,00,000
        3. House Rent Allowance: 3,00,000
        4. Special Allowance: 3,00,000

        Deductions:
        - Standard Deduction: 50,000
        - Section 80C Investments: 1,50,000
        - Section 80D Medical Insurance: 25,000
        - Professional Tax: 2,400

        Gross Total Income: 12,00,000
        Total Deductions: 2,27,400
        Net Taxable Income: 9,72,600
        Total Tax: 1,07,640
        TDS Deducted: 1,07,640
        Net Tax Payable: 0

        Total Tax Deposited: 1,07,640
        """


# Module-level instance
document_processor = DocumentProcessor()
