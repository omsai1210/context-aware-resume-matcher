from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
import json
import os
from services.graph_db import Neo4jGraphManager
from services.email_service import EmailDispatcher

router = APIRouter()

RESULTS_FILE = "data/batch_results.json"

class GraphUpdateRequest(BaseModel):
    new_skill: str
    parent_skill: str

# Dependency
def get_graph_manager():
    manager = Neo4jGraphManager()
    try:
        yield manager
    finally:
        manager.close()

def get_email_dispatcher():
    return EmailDispatcher()

@router.get("/admin/unmapped-skills", tags=["admin"])
async def get_unmapped_skills():
    """
    Returns unique unmapped skills discovered during extraction.
    """
    path = "data/unmapped_skills.txt"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        skills = list(set(line.strip() for line in f if line.strip()))
    return skills

@router.get("/admin/batch-results", tags=["admin"])
async def get_batch_results():
    """
    Returns the aggregated results of processed batches.
    """
    if not os.path.exists(RESULTS_FILE) or os.path.getsize(RESULTS_FILE) == 0:
        return []
    try:
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

@router.post("/admin/dispatch-bulk", tags=["admin"])
async def dispatch_bulk_emails(
    email_dispatcher: EmailDispatcher = Depends(get_email_dispatcher)
):
    """
    Sends emails to all processed candidates who haven't received one yet.
    """
    if not os.path.exists(RESULTS_FILE):
        raise HTTPException(status_code=404, detail="No batch results found.")
        
    with open(RESULTS_FILE, "r") as f:
        results = json.load(f)
        
    sent_count = 0
    for res in results:
        if not res.get("email_sent_status") and "error" not in res:
            try:
                # Mock sending
                email_dispatcher.send_decision_email(
                    candidate_email=res["email"],
                    candidate_name=res["candidate_name"],
                    job_title="Processed Role",
                    score=res["match_score"],
                    llm_feedback=res["llm_feedback"]
                )
                res["email_sent_status"] = True
                sent_count += 1
            except Exception as e:
                print(f"Failed to send email to {res['email']}: {e}")
                
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)
        
    return {"status": "success", "emails_sent": sent_count}

@router.post("/admin/update-graph", tags=["admin"])
async def update_graph_ontology(
    request: GraphUpdateRequest,
    graph_manager: Neo4jGraphManager = Depends(get_graph_manager)
):
    """
    Adds a new skill mapping to the knowledge graph.
    """
    cypher = """
    MERGE (s:Skill {name: $new_skill})
    MERGE (p:Skill {name: $parent_skill})
    MERGE (s)-[:IS_CHILD_OF]->(p)
    RETURN s, p
    """
    try:
        with graph_manager._driver.session() as session:
            session.run(cypher, new_skill=request.new_skill, parent_skill=request.parent_skill)
        return {"status": "success", "message": f"Mapped {request.new_skill} to {request.parent_skill}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph update failed: {str(e)}")
