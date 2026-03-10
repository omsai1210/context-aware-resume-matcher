from fastapi import APIRouter, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import List
from services.orchestrator import process_candidate_pipeline

router = APIRouter()

class ApplyWebhookPayload(BaseModel):
    """
    Request model for the /api/v1/webhook/apply endpoint.
    Expects data pushed directly from a Google Forms Apps Script.
    """
    name: str = Field(..., description="Candidate's full name")
    email: str = Field(..., description="Candidate's email address")
    resume_drive_url: str = Field(..., description="Google Drive link to the uploaded resume")
    job_requirements: List[str] = Field(..., description="List of required standard skill categories")

@router.post("/apply", status_code=status.HTTP_200_OK)
async def handle_application_webhook(payload: ApplyWebhookPayload, background_tasks: BackgroundTasks):
    """
    Webhook receiver for new candidates.
    Immediately returns 200 OK to the sender and kicks off the heavy 
    GraphRAG processing pipeline in a background thread.
    """
    background_tasks.add_task(
        process_candidate_pipeline,
        name=payload.name,
        email=payload.email,
        drive_url=payload.resume_drive_url,
        job_requirements=payload.job_requirements
    )
    
    return {
        "status": "Success",
        "message": f"Application for {payload.name} received. Processing in background..."
    }
