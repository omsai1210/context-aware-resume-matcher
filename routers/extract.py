from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from services.nlp_extraction import extract_entities
from services.taxonomy_mapper import map_to_taxonomy

router = APIRouter()

class ExtractRequest(BaseModel):
    """
    Request model for the /api/v1/extract endpoint.
    Expects the PII-stripped text from Module 1.
    """
    anonymized_text: str = Field(..., description="The cleaned, PII-stripped text from which to extract entities.")

class ExtractResponse(BaseModel):
    """
    Response model for the /api/v1/extract endpoint.
    """
    status: str
    extracted_entities: List[str]
    standardized_skills: List[str]
    unmapped_terms: List[str]

@router.post("/extract", response_model=ExtractResponse, status_code=status.HTTP_200_OK)
async def extract_professional_entities(request: ExtractRequest):
    """
    Accepts anonymized text, extracts professional skills and roles using NLP, 
    and standardizes them against the ESCO mock taxonomy.
    """
    text = request.anonymized_text
    
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The 'anonymized_text' field cannot be empty."
        )

    try:
        # 1. NLP Extraction
        raw_entities = extract_entities(text)
        
        # 2. Ontology Mapping
        standardized, unmapped = map_to_taxonomy(raw_entities)
        
        return ExtractResponse(
            status="Success",
            extracted_entities=raw_entities,
            standardized_skills=standardized,
            unmapped_terms=unmapped
        )
        
    except Exception as e:
        # Catch unforeseen errors in the NLP pipeline or mapping service
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error processing entities: {str(e)}"
        )
