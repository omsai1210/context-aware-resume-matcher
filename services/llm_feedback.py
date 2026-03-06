import google.generativeai as genai
from config import settings
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FeedbackGenerator:
    """
    Generates explainable, human-readable feedback for candidates 
    based on their graph-based match results.
    """

    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI Feedback Generator initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.model = None

    def generate_feedback(self, candidate_name: str, job_title: str, match_data: Dict[str, Any]) -> str:
        """
        Constructs a prompt and queries the LLM for a technical recruiter's summary.
        """
        if not self.model:
            return "Thank you for your application. Our team is currently reviewing your profile against the job requirements."

        score = match_data.get("match_score", 0)
        exact = match_data.get("exact_matches", [])
        multi_hop = match_data.get("multi_hop_matches", [])
        missing = match_data.get("missing_skills", [])

        prompt = f"""
        Act as an empathetic, professional technical recruiter. 
        Write a concise 3-to-4 sentence summary for a candidate named '{candidate_name}' 
        who applied for the role of '{job_title}'.
        
        The candidate received a match score of {score}/100 based on our knowledge graph evaluation.
        
        Data points to use:
        - Exact Skill Matches: {', '.join(exact) if exact else 'None'}
        - Related/Semantic Matches: {', '.join(multi_hop) if multi_hop else 'None'}
        - Missing Requirements: {', '.join(missing) if missing else 'None'}
        
        Instructions:
        1. Explain why they received this score based ONLY on the data provided.
        2. Highlight their strengths (exact/related matches).
        3. Politely mention why they fell short if the score is low (missing skills).
        4. Do NOT hallucinate skills or experiences not listed above.
        5. Maintain a professional yet encouraging tone.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating LLM feedback: {e}")
            return f"We've evaluated your profile for the {job_title} position. You have strong experience in {', '.join(exact[:2]) if exact else 'related areas'}, though we noticed some gaps in required technical domains."
