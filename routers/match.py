from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from services.scoring_service import generate_explanation

router = APIRouter()

class ExplainRequest(BaseModel):
    """
    Request model for the /api/v1/match/explain endpoint.
    Expects a candidate ID and the job requirements they are being matched against.
    """
    candidate_id: str = Field(..., description="Unique ID for the candidate.")
    job_requirements: List[str] = Field(..., description="List of standardization categories required by the job.")

@router.post("/explain", status_code=status.HTTP_200_OK)
async def explain_candidate_match(request: ExplainRequest):
    """
    Takes a candidate and job requirements, fetches their graph structure,
    and returns an AI-generated natural language explanation of their fit.
    """
    if not request.candidate_id or not request.job_requirements:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Valid candidate_id and job_requirements list are required."
        )
    
    try:
        result = generate_explanation(request.candidate_id, request.job_requirements)
        
        if "error" in result:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=result["error"]
            )
            
        return {"status": "Success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to explain match: {str(e)}"
        )
