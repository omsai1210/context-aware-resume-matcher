from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict, Any
import asyncio
import json
import os
from datetime import datetime

# Import existing router logic/services (we'll call the service layers directly for efficiency)
from services.extraction import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from services.anonymization import anonymize_text
from services.nlp_extraction import extract_entities
from services.taxonomy_mapper import map_to_taxonomy
from services.matching_service import MatchingService
from services.graph_db import Neo4jGraphManager
from services.llm_feedback import FeedbackGenerator

router = APIRouter()

RESULTS_FILE = "data/batch_results.json"

# Dependency for Services
def get_graph_manager():
    manager = Neo4jGraphManager()
    try:
        yield manager
    finally:
        manager.close()

def get_matching_service(graph_manager: Neo4jGraphManager = Depends(get_graph_manager)):
    return MatchingService(graph_manager)

def get_feedback_gen():
    return FeedbackGenerator()

async def process_single_resume(
    file: UploadFile, 
    job_id: str, 
    matching_service: MatchingService,
    feedback_gen: FeedbackGenerator
) -> Dict[str, Any]:
    """
    Sub-pipeline for a single resume.
    """
    try:
        content = await file.read()
        filename = file.filename
        
        # 1. Extraction
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(content)
        elif filename.endswith(".docx"):
            text = extract_text_from_docx(content)
        else:
            text = extract_text_from_txt(content)
            
        # 2. Anonymize & Extract Identity (Roughly for demo)
        # In a real app, we'd use better regex for Email/Name
        anonymized, redacted = anonymize_text(text)
        
        # 3. NLP & Taxonomy Mapping
        raw_skills = extract_entities(anonymized)
        standardized, unmapped = map_to_taxonomy(raw_skills)
        
        # 4. Matching (We'll use a dummy candidate_id or create one in actual schema)
        # For bulk processing, we'll assume we've "ingested" it into graph or we use a temporary session
        # Here we just use the matching logic
        # NOTE: A real system would save the candidate to Neo4j first.
        # For simplicity in this bulk demo, we evaluate based on standardized skills.
        result = matching_service.evaluate_candidate_match("CANDIDATE_TEMP", job_id)
        
        # 5. LLM Feedback
        feedback = feedback_gen.generate_feedback(
            candidate_name=filename.split(".")[0],
            job_title=f"Role: {job_id}",
            match_data=result.model_dump()
        )
        
        return {
            "candidate_name": filename.split(".")[0],
            "email": "bulk_candidate@example.com", # Mock
            "match_score": result.match_score,
            "match_details": result.model_dump(), # Store full detail for Inspector
            "status": "Shortlisted" if result.match_score >= 80 else "Rejected",
            "llm_feedback": feedback,
            "email_sent_status": False,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "filename": file.filename}

@router.post("/bulk-process", tags=["bulk"])
async def bulk_process_resumes(
    job_id: str,
    files: List[UploadFile] = File(...),
    matching_service: MatchingService = Depends(get_matching_service),
    feedback_gen: FeedbackGenerator = Depends(get_feedback_gen)
):
    """
    Asynchronously processes a batch of resumes.
    """
    tasks = [process_single_resume(f, job_id, matching_service, feedback_gen) for f in files]
    results = await asyncio.gather(*tasks)
    
    # Save to data/batch_results.json
    os.makedirs("data", exist_ok=True)
    
    # Load existing or start new
    all_data = []
    if os.path.exists(RESULTS_FILE) and os.path.getsize(RESULTS_FILE) > 0:
        try:
            with open(RESULTS_FILE, "r") as f:
                all_data = json.load(f)
        except json.JSONDecodeError:
            all_data = [] # Reset if corrupt
            
    all_data.extend(results)
    
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_data, f, indent=4)
        
    return {"message": f"Processed {len(files)} resumes successfully.", "results": results}
