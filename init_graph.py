import json
import os
import logging
from services.graph_db import Neo4jGraphManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_graph():
    """
    One-time initialization script to setup constraints and ingest the taxonomy.
    """
    manager = None
    try:
        manager = Neo4jGraphManager()
        
        logger.info("Setting up database constraints...")
        manager.setup_constraints()
        
        taxonomy_path = os.path.join("data", "esco_mock_taxonomy.json")
        if os.path.exists(taxonomy_path):
            logger.info(f"Loading taxonomy from {taxonomy_path}...")
            with open(taxonomy_path, "r", encoding="utf-8") as f:
                taxonomy_data = json.load(f)
            
            manager.ingest_taxonomy(taxonomy_data)
            logger.info("Taxonomy ingestion complete.")
        else:
            logger.error(f"Taxonomy file not found at {taxonomy_path}")

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
    finally:
        if manager:
            manager.close()

if __name__ == "__main__":
    initialize_graph()
