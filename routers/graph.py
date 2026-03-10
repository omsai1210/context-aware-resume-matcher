from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from services.graph_service import init_db, load_taxonomy_to_graph, add_candidate_to_graph

router = APIRouter()

class CandidateGraphRequest(BaseModel):
    """
    Request model for the /api/v1/graph/candidate endpoint.
    Expects data from Module 2 containing candidate ID and structured skills.
    """
    candidate_id: str = Field(..., description="Unique ID for the candidate (e.g., filename or email).")
    standardized_skills: List[str] = Field(..., description="List of standardized skills representing Category nodes.")

@router.post("/init", status_code=status.HTTP_200_OK)
async def initialize_graph():
    """
    Initializes the database schema and loads the base taxonomy 
    from the data/esco_mock_taxonomy.json into Neo4j.
    """
    try:
        init_db()
        load_taxonomy_to_graph()
        return {"status": "Success", "message": "Graph initialized and taxonomy loaded."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to initialize graph: {str(e)}"
        )

@router.post("/candidate", status_code=status.HTTP_201_CREATED)
async def map_candidate_to_graph(request: CandidateGraphRequest):
    """
    Takes a candidate's ID and standardized skills, creating nodes and
    relationships in Neo4j.
    """
    if not request.candidate_id or not request.standardized_skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Valid candidate_id and standardized_skills list are required."
        )

    try:
        # Create candidate node and connect to SKillCategory nodes
        add_candidate_to_graph(request.candidate_id, request.standardized_skills)
        return {"status": "Success", "message": f"Candidate {request.candidate_id} added successfully to the graph."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to add candidate to graph: {str(e)}"
        )
