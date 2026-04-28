"""
Document Routes — Document Upload and Processing API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api/documents", tags=["Documents"])


class DocumentText(BaseModel):
    text: str = Field(..., description="Document text content")
    document_type: str = Field(default="auto", description="Document type or auto-detect")


@router.post("/classify")
async def classify_document(data: DocumentText):
    """Classify a document using deep learning model."""
    try:
        from app.models.document_classifier import document_classifier

        result = document_classifier.classify(data.text)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_data(data: DocumentText):
    """Extract structured data from document text."""
    try:
        from app.services.document_processor import document_processor

        if data.document_type == 'form16' or data.document_type == 'auto':
            result = document_processor.process_form16(data.text)
        elif data.document_type == 'salary_slip':
            result = document_processor.process_salary_slip(data.text)
        else:
            result = document_processor.extract_from_text(data.text, data.document_type)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        from app.models.document_classifier import document_classifier
        from app.services.document_processor import document_processor

        content = await file.read()
        text = content.decode('utf-8', errors='ignore')

        # Classify
        classification = document_classifier.classify(text)

        # Extract data
        doc_type = classification.get('document_type', 'auto')
        if doc_type == 'form16':
            extraction = document_processor.process_form16(text)
        elif doc_type == 'salary_slip':
            extraction = document_processor.process_salary_slip(text)
        else:
            extraction = document_processor.extract_from_text(text, doc_type)

        return {
            "status": "success",
            "data": {
                "filename": file.filename,
                "classification": classification,
                "extracted_data": extraction
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-form16")
async def get_sample_form16():
    """Get a sample Form 16 text for testing."""
    try:
        from app.services.document_processor import document_processor
        sample = document_processor.generate_sample_form16_text()
        return {"status": "success", "data": {"text": sample}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
