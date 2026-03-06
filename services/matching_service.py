from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from services.graph_db import Neo4jGraphManager
import logging
import csv
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class MatchResult(BaseModel):
    """
    Pydantic model representing the result of a candidate-to-job match assessment.
    """
    candidate_id: str
    job_id: str
    match_score: float
    exact_matches: List[str]
    multi_hop_matches: List[str]
    missing_skills: List[str]

class MatchingService:
    """
    Core engine for comparing candidates against job descriptions using 
    knowledge-graph-based semantic reasoning.
    """

    def __init__(self, graph_manager: Neo4jGraphManager):
        self.graph_manager = graph_manager

    def evaluate_candidate_match(self, candidate_id: str, job_id: str) -> MatchResult:
        """
        Executes a multi-hop Cypher query to score a candidate's alignment with a job requirements.
        
        Reasoning Logic:
        1. Identifies all required skills for the job.
        2. Segregates candidate's skills into:
           - EXACT: Direct match (Candidate → Skill ← Job).
           - MULTI-HOP: Connected via synonym or child relationships (Candidate → Skill-A [IS_SYNONYM|IS_CHILD_OF*1..2] Skill-B ← Job).
           - MISSING: Required skill not found in candidate's profile.
        """
        
        query = """
        // 1. Get all required skills for the job
        MATCH (j:Job {job_id: $j_id})-[:REQUIRES_SKILL]->(target:Skill)
        
        // 2. For each requirement, find the "best" match from the candidate's skills
        OPTIONAL MATCH (c:Candidate {candidate_id: $c_id})-[:HAS_SKILL]->(cand_skill:Skill)
        
        WITH target, cand_skill,
             CASE
               WHEN cand_skill = target THEN 1.0 // Exact Match
               WHEN (cand_skill)-[:IS_SYNONYM_OF|IS_CHILD_OF*1..2]-(target) THEN 0.5 // Multi-hop Match
               ELSE 0.0
             END AS match_weight
        
        // Group by requirement to find the best match for each
        WITH target, MAX(match_weight) AS best_weight
        
        RETURN 
          target.name AS skill_name,
          best_weight
        """

        exact_matches = []
        multi_hop_matches = []
        missing_skills = []
        total_points = 0.0
        total_requirements = 0

        with self.graph_manager._driver.session() as session:
            try:
                results = session.run(query, j_id=job_id, c_id=candidate_id)
                for record in results:
                    total_requirements += 1
                    skill_name = record["skill_name"]
                    weight = record["best_weight"]
                    
                    if weight == 1.0:
                        exact_matches.append(skill_name)
                        total_points += 1.0
                    elif weight == 0.5:
                        multi_hop_matches.append(skill_name)
                        total_points += 0.5
                    else:
                        missing_skills.append(skill_name)
            except Exception as e:
                logger.error(f"Error executing match query: {e}")
                raise

        # Calculate final score
        match_score = (total_points / total_requirements * 100) if total_requirements > 0 else 0.0
        match_score = round(match_score, 2)

        # EdTech Analytics: Track Rejections (score < 80)
        if match_score < 80:
            self._log_rejection(job_id, match_score, missing_skills, exact_matches + multi_hop_matches)

        return MatchResult(
            candidate_id=candidate_id,
            job_id=job_id,
            match_score=match_score,
            exact_matches=exact_matches,
            multi_hop_matches=multi_hop_matches,
            missing_skills=missing_skills
        )

    def _log_rejection(self, job_role: str, score: float, missing: List[str], matched: List[str]):
        """
        Logs rejected candidate data to a local CSV for analytics.
        """
        os.makedirs("data", exist_ok=True)
        file_path = "data/rejected_analytics.csv"
        file_exists = os.path.isfile(file_path)

        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Job_Role", "Candidate_Score", "Missing_Skills", "Matched_Skills"])
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                job_role,
                score,
                ",".join(missing),
                ",".join(matched)
            ])
