from google import genai
from google.genai import types
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from services.rag_service import get_candidate_subgraph, match_candidates

load_dotenv()

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    return genai.Client(api_key=api_key)

def generate_explanation(candidate_id: str, job_requirements: List[str]) -> Dict[str, Any]:
    """
    Retrieves the candidate's subgraph and uses Gemini to explain why they are a match.
    """
    subgraph = get_candidate_subgraph(candidate_id)
    if not subgraph:
        return {"error": f"Candidate {candidate_id} not found in the graph."}
        
    # Re-run match to get the score for this specific candidate
    # (In a real system, you'd likely pass the score directly or fetch it optimized)
    all_matches = match_candidates(job_requirements)
    candidate_match = next((m for m in all_matches if m["candidate_id"] == candidate_id), None)
    
    score = candidate_match["match_count"] if candidate_match else 0
    
    # Construct Prompts
    prompt = f"""
    You are an AI Recruitment Assistant for GraphRAG-ATS.
    Your task is to concisely explain why the following candidate is a good match (or not) for the job requirements.
    
    Job Requirements (Skill Categories Required):
    {', '.join(job_requirements)}
    
    Candidate's Graph Subgraph (Skills they possess and the category they fall under):
    {subgraph['skill_mapping']}
    
    The candidate matched {score} out of {len(job_requirements)} required categories.
    
    Provide a 2-3 sentence 'Glass Box' explanation that justifies their fit. Be objective and direct. Do not mention 'GraphRAG' or 'Subgraph' in your explanation, just talk about their skills.
    """
    
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        return {
            "candidate_id": candidate_id,
            "score": score,
            "total_requirements": len(job_requirements),
            "explanation": response.text.strip(),
            "subgraph_context_used": subgraph['skill_mapping']
        }
        
    except Exception as e:
         return {"error": f"Failed to generate explanation from Gemini API: {str(e)}"}
