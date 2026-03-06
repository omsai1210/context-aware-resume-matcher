import os
import json
import logging
from services.graph_db import Neo4jGraphManager
from services.matching_service import MatchingService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_matching_logic():
    """
    Simulates a candidate and a job to verify the multi-hop matching logic.
    """
    manager = None
    try:
        manager = Neo4jGraphManager()
        service = MatchingService(manager)
        
        # 1. Setup Data
        candidate_id = "test_candidate_1"
        job_id = "test_job_1"
        
        # Candidate has "ReactJS" and "Python"
        # Job requires "Frontend Development" and "Java"
        
        logger.info("Injecting test data...")
        manager.add_candidate_skills(candidate_id, ["ReactJS", "Python"])
        manager.add_job_requirements(job_id, ["Frontend Development", "Java"])
        
        # 2. Evaluate Match
        logger.info(f"Evaluating match for {candidate_id} against {job_id}...")
        result = service.evaluate_candidate_match(candidate_id, job_id)
        
        logger.info("Match Results:")
        logger.info(f"Score: {result.match_score}")
        logger.info(f"Exact Matches: {result.exact_matches}")
        logger.info(f"Multi-hop Matches: {result.multi_hop_matches}")
        logger.info(f"Missing Skills: {result.missing_skills}")
        
        # Expectations:
        # - "Frontend Development" should be a Multi-hop match for "ReactJS" (via IS_SYNONYM_OF)
        # - "Java" should be a Missing skill.
        # - Score should be (0.5 / 2) * 100 = 25.0
        
        if result.match_score == 25.0:
            logger.info("SUCCESS: Matching logic verified correctly.")
        else:
            logger.warning(f"UNEXPECTED SCORE: Expected 25.0, got {result.match_score}")

    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        if manager:
            manager.close()

if __name__ == "__main__":
    test_matching_logic()
