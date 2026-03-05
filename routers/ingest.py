from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Dict
from services.extraction import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from services.anonymization import anonymize_text
import re

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

class IngestResponse(BaseModel):
    """
    Response model for the /api/v1/ingest endpoint.
    """
    filename: str
    status: str
    original_text_length: int
    anonymized_text: str
    redacted_entities: Dict[str, int]

@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def ingest_document(file: UploadFile = File(...)):
    """
    Accepts a single file upload (PDF, DOCX, TXT), extracts readable text,
    and strips out Personally Identifiable Information (PII) for blind ranking.
    """
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded.")
    
    # 1. Validate File Size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail=f"File {file.filename} exceeds the 5MB limit."
        )

    # 2. Extract Text based on File Type
    filename = file.filename
    # Secure filename extraction if needed, but for simplicity we rely on suffix
    extracted_text = ""
    
    if filename.endswith(".pdf"):
        try:
            extracted_text = extract_text_from_pdf(content)
        except ValueError as e:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    elif filename.endswith(".docx"):
        try:
            extracted_text = extract_text_from_docx(content)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    elif filename.endswith(".txt"):
         try:
            extracted_text = extract_text_from_txt(content)
         except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail="Unsupported file format. Please upload a .pdf, .docx, or .txt file."
        )
        
    original_len = len(extracted_text)
    
    # 3. Anonymize the extracted text
    try:
         anonymized_text, redacted_summary = anonymize_text(extracted_text)
    except Exception as e:
        # Catch unexpected errors during the NLP step
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error during PII redaction: {str(e)}"
        )
        
    # 4. Return the processed result
    return IngestResponse(
        filename=filename,
        status="Success",
        original_text_length=original_len,
        anonymized_text=anonymized_text,
        redacted_entities=redacted_summary
    )
