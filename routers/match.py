from fastapi import APIRouter, HTTPException, Depends
from services.graph_db import Neo4jGraphManager
from services.matching_service import MatchingService, MatchResult

router = APIRouter()

# Dependency for Graph Manager
def get_graph_manager():
    manager = Neo4jGraphManager()
    try:
        yield manager
    finally:
        manager.close()

# Dependency for Matching Service
def get_matching_service(graph_manager: Neo4jGraphManager = Depends(get_graph_manager)):
    return MatchingService(graph_manager)

@router.get("/match/{job_id}/{candidate_id}", response_model=MatchResult, tags=["matching-engine"])
async def match_candidate_to_job(
    job_id: str, 
    candidate_id: str, 
    matching_service: MatchingService = Depends(get_matching_service)
):
    """
    Evaluates a specific candidate against a specific job using GraphRAG (Multi-hop reasoning).
    Returns exact matches, multi-hop matches, and missing skills with a weighted score.
    """
    try:
        result = matching_service.evaluate_candidate_match(candidate_id, job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching evaluation failed: {str(e)}")
