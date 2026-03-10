from typing import List, Dict, Any
from services.graph_service import get_db_driver

def match_candidates(required_categories: List[str]) -> List[Dict[str, Any]]:
    """
    Find candidates who possess skills falling under the requested skill categories.
    This effectively uses the taxonomy structure loaded in Module 3.
    Matches are ranked by the number of matching categories they possess.
    """
    driver = get_db_driver()
    
    # query to find matching candidates
    query = """
    UNWIND $required_categories AS req_category
    MATCH (c:Candidate)-[:HAS_SKILL]->(sc:SkillCategory {name: req_category})
    WITH c, collect(sc.name) AS matched_skills, count(sc) as match_count
    ORDER BY match_count DESC
    RETURN c.id AS candidate_id, matched_skills, match_count
    """
    
    results = []
    with driver.session() as session:
        records = session.run(query, required_categories=required_categories)
        for record in records:
            results.append({
                "candidate_id": record["candidate_id"],
                "matched_skills": record["matched_skills"],
                "match_count": record["match_count"]
            })
            
    return results

def get_candidate_subgraph(candidate_id: str) -> Dict[str, Any]:
    """
    Retrieves the subgraph for a specific candidate to understand their skills
    and how they map to the broader taxonomy categories. Useful for explainability.
    """
    driver = get_db_driver()
    
    # query to get candidate skills and their specific skills mapped
    query = """
    MATCH (c:Candidate {id: $candidate_id})-[:HAS_SKILL]->(sc:SkillCategory)
    OPTIONAL MATCH (sc)-[:INCLUDES]->(s:Skill)
    WITH c, sc, collect(s.name) AS specific_skills
    RETURN c.id AS candidate_id, collect({category: sc.name, related_skills: specific_skills}) AS skill_mapping
    """
    
    with driver.session() as session:
        result = session.run(query, candidate_id=candidate_id).single()
        if result:
            return {
                "candidate_id": result["candidate_id"],
                "skill_mapping": result["skill_mapping"]
            }
        
    return None
