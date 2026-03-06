from fastapi import APIRouter, HTTPException, Depends
from services.graph_db import Neo4jGraphManager
from services.matching_service import MatchingService
from services.llm_feedback import FeedbackGenerator
from services.email_service import EmailDispatcher
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependencies
def get_graph_manager():
    manager = Neo4jGraphManager()
    try:
        yield manager
    finally:
        manager.close()

def get_matching_service(graph_manager: Neo4jGraphManager = Depends(get_graph_manager)):
    return MatchingService(graph_manager)

def get_feedback_generator():
    return FeedbackGenerator()

def get_email_dispatcher():
    return EmailDispatcher()

@router.post("/process-decision/{job_id}/{candidate_id}", tags=["recruitment-pipeline"])
async def process_recruitment_decision(
    job_id: str,
    candidate_id: str,
    matching_service: MatchingService = Depends(get_matching_service),
    feedback_gen: FeedbackGenerator = Depends(get_feedback_generator),
    email_dispatcher: EmailDispatcher = Depends(get_email_dispatcher)
):
    """
    Full pipeline orchestration:
    1. Evaluate candidate skill match using GraphRAG.
    2. Generate "Glass Box" feedback via LLM.
    3. Dispatch decision email to the candidate.
    """
    try:
        # 1. Evaluate Match
        match_result = matching_service.evaluate_candidate_match(candidate_id, job_id)
        
        # 2. Mock fetching candidate info (In a real app, this comes from DB)
        candidate_name = "Candidate Name" # Placeholder
        candidate_email = "candidate@example.com" # Placeholder
        job_title = f"Role for {job_id}" # Placeholder
        
        # 3. Generate Feedback
        llm_feedback = feedback_gen.generate_feedback(
            candidate_name=candidate_name,
            job_title=job_title,
            match_data=match_result.model_dump()
        )
        
        # 4. Dispatch Email
        email_dispatcher.send_decision_email(
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            job_title=job_title,
            score=match_result.match_score,
            llm_feedback=llm_feedback
        )
        
        return {
            "status": "Decision processed and email sent",
            "match_score": match_result.match_score,
            "llm_feedback": llm_feedback,
            "candidate_id": candidate_id,
            "job_id": job_id
        }

    except Exception as e:
        logger.error(f"Pipeline processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process recruitment decision: {str(e)}")
