# System Modules & Implementation Plan

## Module 1: Document Ingestion & Bias Mitigation ("Blind Ranking")
* **Description:** Handles the ingestion of raw files and ensures fairness by removing bias-inducing data.
* **Input:** `.pdf`, `.docx`, or `.txt` resume files.
* **Process:**
  1. Extract raw text from documents.
  2. Pass text through Microsoft Presidio to detect and mask PII (Name, Phone, Email, University, etc.).
  3. Clean and normalize the text for downstream NLP processing.
* **Output:** Anonymized, machine-readable text blocks.

## Module 2: Entity Extraction & Ontology Mapping
* **Description:** Identifies core professional attributes and maps them to a global standard.
* **Input:** Anonymized text blocks.
* **Process:**
  1. Utilize spaCy NER pipelines to extract skills, tools, and job roles.
  2. Query the ESCO taxonomy to find standardized equivalents for the extracted terms.
  3. Resolve synonyms (e.g., standardizing "ReactJS" and "React.js").
* **Output:** A structured JSON object containing standardized skills and roles.

## Module 3: Knowledge Graph Construction
* **Description:** Establishes the structural foundation of the system.
* **Input:** Standardized JSON objects and ESCO taxonomy data.
* **Process:**
  1. Define Neo4j schema: `(:Candidate)`, `(:Job)`, `(:Skill)`, `(:Role)`.
  2. Define relationships: `[:HAS_SKILL]`, `[:REQUIRES_SKILL]`, `[:IS_PARENT_OF]`.
  3. Load base ESCO hierarchies into Neo4j.
* **Output:** A populated, queryable graph database.

## Module 4: GraphRAG & Multi-Hop Reasoning Engine
* **Description:** The core engine that finds semantic matches using graph traversal.
* **Input:** Parsed Job Description requirements.
* **Process:**
  1. Translate job requirements into Cypher queries.
  2. Execute multi-hop traversal to find exact matches and "neighboring" skills (e.g., candidate has `Keras`, job requires `TensorFlow`; graph verifies they share a parent node `Deep Learning`).
* **Output:** Connected subgraphs showing the relationship between the candidate and the job.

## Module 5: Matching, Scoring & Explanation
* **Description:** Generates the final ranking and human-readable reasoning.
* **Input:** Connected subgraphs from Module 4.
* **Process:**
  1. Calculate a match score based on graph distance metrics (closer nodes = higher score).
  2. Pass the subgraph context to the LLM to generate a "Glass Box" summary explaining *why* the candidate matched.
* **Output:** A ranked list of candidates with natural language justifications.

## Module 6: User Interface (Dashboard)
* **Description:** The recruiter-facing application.
* **Input:** User interactions (uploading files, selecting jobs).
* **Process:**
  1. Provide a drag-and-drop interface for resumes and JDs.
  2. Display the ranked, anonymized list of applicants.
  3. Render the PyVis/Cytoscape graph showing the skill matching pathways.
* **Output:** Interactive web dashboard.