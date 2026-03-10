from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from services.rag_service import match_candidates, get_candidate_subgraph

router = APIRouter()

class MatchRequest(BaseModel):
    """
    Request model for the /api/v1/rag/match endpoint.
    Expects a list of required skill categories (Job Requirements).
    """
    required_skills: List[str] = Field(..., description="List of standardization categories required by the job.")

@router.post("/match", status_code=status.HTTP_200_OK)
async def find_matching_candidates(request: MatchRequest):
    """
    Executes a Cypher query in Neo4j to find candidates possessing the 
    required skill categories, ranked by match count.
    """
    if not request.required_skills:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Valid required_skills list is required."
        )
    
    try:
        matches = match_candidates(request.required_skills)
        return {"status": "Success", "matches": matches}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to match candidates: {str(e)}"
        )

@router.get("/candidate/{candidate_id}/subgraph", status_code=status.HTTP_200_OK)
async def get_subgraph(candidate_id: str):
    """
    Retrieves the skill mapping subgraph for a specific candidate.
    Provides the explainable path of how a candidate's specific skills 
    relate to broader categories.
    """
    try:
        subgraph = get_candidate_subgraph(candidate_id)
        if not subgraph:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Candidate {candidate_id} not found in graph."
            )
        return {"status": "Success", "data": subgraph}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve subgraph: {str(e)}"
        )
