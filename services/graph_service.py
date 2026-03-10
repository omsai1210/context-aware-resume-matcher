from neo4j import GraphDatabase, Driver
import os
import json
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Singleton driver instance
_driver: Driver = None

def get_db_driver() -> Driver:
    """
    Returns the Neo4j Driver instance, initializing it if necessary.
    Requires NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD in .env.
    """
    global _driver
    if _driver is None:
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not uri or not user or not password:
            raise ValueError("Neo4j credentials not found in environment variables.")
            
        _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver

def init_db():
    """
    Initializes the database schema by setting up necessary constraints.
    Ensures that Skill and SkillCategory names are unique.
    """
    driver = get_db_driver()
    with driver.session() as session:
        # We use IF NOT EXISTS to avoid errors if run multiple times
        session.run("CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE")
        session.run("CREATE CONSTRAINT category_name IF NOT EXISTS FOR (sc:SkillCategory) REQUIRE sc.name IS UNIQUE")
        session.run("CREATE CONSTRAINT candidate_id IF NOT EXISTS FOR (c:Candidate) REQUIRE c.id IS UNIQUE")
        print("Database constraints verified.")

def load_taxonomy_to_graph():
    """
    Reads the esco_mock_taxonomy.json and populates the Neo4j database.
    Creates SkillCategory nodes and Skill nodes, connected by :INCLUDES relationships.
    """
    taxonomy_path = os.path.join("data", "esco_mock_taxonomy.json")
    if not os.path.exists(taxonomy_path):
        raise FileNotFoundError(f"Taxonomy file not found at {taxonomy_path}")
        
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        taxonomy_data = json.load(f)
        
    driver = get_db_driver()
    
    # Cypher query to merge (create if not exists) the Category, Skill, and Relationship
    query = """
    MERGE (cat:SkillCategory {name: $category_name})
    WITH cat
    UNWIND $skills AS skill_name
    MERGE (s:Skill {name: skill_name})
    MERGE (cat)-[:INCLUDES]->(s)
    """
    
    with driver.session() as session:
        for category_name, skills in taxonomy_data.items():
            # For the taxonomy logic, we consider the category name itself as the 'Standardized Skill Bucket'
            # and the items in the list as synonyms. 
            # In our graph, we will represent the 'Category' as the main node, and the 'synonyms' as specific skills.
            session.run(query, category_name=category_name, skills=skills)
            
    print("Taxonomy loaded into Neo4j successfully.")

def add_candidate_to_graph(candidate_id: str, skills: List[str]):
    """
    Creates a Candidate node and connects it to the standardized Skill 
    (or SkillCategory) nodes they possess.
    
    Args:
        candidate_id (str): Unique identifier for the candidate (e.g., filename or email).
        skills (List[str]): List of standardized skill names the candidate possesses.
    """
    driver = get_db_driver()
    
    query = """
    MERGE (c:Candidate {id: $candidate_id})
    WITH c
    UNWIND $skills AS skill_name
    
    // We try to match either a specific Skill or a SkillCategory based on what Module 2 returned
    // Because Module 2 returns the keys of our taxonomy (which we made SkillCategory nodes),
    // we match on SkillCategory here. If your mapping logic returns something else, adjust accordingly.
    MATCH (sc:SkillCategory {name: skill_name})
    
    MERGE (c)-[:HAS_SKILL]->(sc)
    """
    
    with driver.session() as session:
        session.run(query, candidate_id=candidate_id, skills=skills)
