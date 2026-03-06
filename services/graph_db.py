import os
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver, Session, Transaction
from neo4j.exceptions import ServiceUnavailable, AuthError
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jGraphManager:
    """
    Manages the connection and core operations for the Neo4j Knowledge Graph.
    Uses the official Neo4j Python driver with session management.
    """

    def __init__(self):
        self._uri = settings.NEO4J_URI
        self._user = settings.NEO4J_USERNAME
        self._password = settings.NEO4J_PASSWORD
        self._driver: Optional[Driver] = None
        
        try:
            self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j instance.")
        except AuthError as e:
            logger.error(f"Neo4j Authentication failed: {e}")
            raise
        except ServiceUnavailable as e:
            logger.error(f"Neo4j Service unavailable: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4j: {e}")
            raise

    def close(self) -> None:
        """
        Cleanly closes the Neo4j driver connection.
        """
        if self._driver:
            self._driver.close()
            logger.info("Neo4j driver connection closed.")

    def setup_constraints(self) -> None:
        """
        Initializes uniqueness constraints on Candidate, Job, and Skill nodes.
        Constraints ensure data integrity and improve lookup performance.
        """
        queries = [
            "CREATE CONSTRAINT candidate_id_unique IF NOT EXISTS FOR (c:Candidate) REQUIRE c.candidate_id IS UNIQUE",
            "CREATE CONSTRAINT job_id_unique IF NOT EXISTS FOR (j:Job) REQUIRE j.job_id IS UNIQUE",
            "CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE"
        ]
        
        with self._driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                    logger.info(f"Executed constraint query: {query}")
                except Exception as e:
                    logger.error(f"Failed to setup constraint: {e}")

    def ingest_taxonomy(self, taxonomy_data: Dict[str, List[str]]) -> None:
        """
        Ingests the ESCO mock taxonomy into the graph.
        Creates skill nodes and establishes synonym/hierarchical relationships.
        
        Cypher Logic:
        - MERGE Skill nodes for the standard term.
        - UNWIND synonyms and MERGE Skill nodes for each.
        - Create IS_SYNONYM_OF relationship between synonym and standard term.
        """
        query = """
        UNWIND $data AS entry
        MERGE (standard:Skill {name: entry.standard_term})
        WITH standard, entry.synonyms AS synonyms
        UNWIND synonyms AS synonym
        MERGE (s:Skill {name: synonym})
        MERGE (s)-[:IS_SYNONYM_OF]->(standard)
        """
        
        # Transform dict into list of objects for UNWIND
        formatted_data = [
            {"standard_term": key, "synonyms": values} 
            for key, values in taxonomy_data.items()
        ]

        with self._driver.session() as session:
            try:
                session.run(query, data=formatted_data)
                logger.info(f"Successfully ingested {len(formatted_data)} taxonomy entries.")
            except Exception as e:
                logger.error(f"Failed to ingest taxonomy: {e}")

    def add_candidate_skills(self, candidate_id: str, skills: List[str]) -> None:
        """
        Links a candidate to a list of extracted skills.
        
        Cypher Logic:
        - MERGE Candidate node by candidate_id.
        - UNWIND skills list.
        - MERGE Skill node for each.
        - MERGE HAS_SKILL relationship.
        """
        query = """
        MERGE (c:Candidate {candidate_id: $c_id})
        WITH c
        UNWIND $skills_list AS skill_name
        MERGE (s:Skill {name: skill_name})
        MERGE (c)-[:HAS_SKILL]->(s)
        """

        with self._driver.session() as session:
            try:
                session.run(query, c_id=candidate_id, skills_list=skills)
                logger.info(f"Linked candidate {candidate_id} to {len(skills)} skills.")
            except Exception as e:
                logger.error(f"Failed to add candidate skills for {candidate_id}: {e}")

    def add_job_requirements(self, job_id: str, skills: List[str]) -> None:
        """
        Links a job to its required skills.
        """
        query = """
        MERGE (j:Job {job_id: $j_id})
        WITH j
        UNWIND $skills_list AS skill_name
        MERGE (s:Skill {name: skill_name})
        MERGE (j)-[:REQUIRES_SKILL]->(s)
        """

        with self._driver.session() as session:
            try:
                session.run(query, j_id=job_id, skills_list=skills)
                logger.info(f"Linked job {job_id} to {len(skills)} requirements.")
            except Exception as e:
                logger.error(f"Failed to add job requirements for {job_id}: {e}")
