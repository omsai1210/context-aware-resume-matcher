# Technology Stack & Architecture

## 🖥️ Frontend (User Interface)
* **Streamlit / Next.js:** Chosen for rapid development of data-centric dashboards. It allows recruiters to easily upload documents and view parsed results.
* **PyVis / Cytoscape.js:** Used to render interactive graph visualizations of the multi-hop reasoning pathways, providing the "Glass Box" explainability.

## ⚙️ Backend (API & Core Logic)
* **FastAPI:** A high-performance, asynchronous web framework for building APIs with Python. Chosen for its speed and automatic Swagger UI documentation generation.
* **PyMuPDF (`fitz`) & `python-docx`:** Robust libraries for extracting raw text from uploaded PDF and Word documents without losing formatting context.

## 🧠 AI, NLP & Neuro-Symbolic Engine
* **LlamaIndex / LangChain:** The orchestration framework used to connect the LLM with the Knowledge Graph. LlamaIndex is particularly preferred for its native GraphRAG abstractions.
* **spaCy:** Used for Named Entity Recognition (NER) to extract hard skills, soft skills, and experiences from raw resume text.
* **Microsoft Presidio:** An open-source library used to implement the "Blind Ranking" feature. It detects and redacts Personally Identifiable Information (PII) such as names, emails, and demographic markers.
* **HuggingFace (`all-MiniLM-L6-v2`):** A lightweight, open-source embedding model used for initial vector similarity searches before graph traversal.

## 🗄️ Database
* **Neo4j AuraDB:** A native graph database designed to store, manage, and query highly connected data. It holds the ESCO taxonomy and candidate skill mappings using nodes and edges.

## 🔌 External APIs & Taxonomies
* **ESCO Taxonomy API:** The European Commission's standardized dictionary of skills and occupations, serving as the foundational truth for the Knowledge Graph.
* **Groq API / Google Gemini API:** Provides the LLM inference engine required to generate natural language explanations of the graph traversals.