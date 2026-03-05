# GraphRAG-ATS: Context-Aware Resume Matching System

![Project Status](https://img.shields.io/badge/Status-In%20Development-blue)
![Version](https://img.shields.io/badge/Version-1.0.0-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

## 📌 Project Overview
The recruitment landscape is shifting from simple digitization to **"Agentic Intelligence,"** where AI systems reason like human experts. Traditional Applicant Tracking Systems (ATS) rely heavily on "Generation 2.0" tools—keyword matching and static vector similarity—which introduce significant fragility and bias into the hiring process.

This project introduces a **Graph Retrieval-Augmented Generation (GraphRAG)** framework. It is a "Generation 3.0" approach that grounds generative AI in a structured Knowledge Graph, mapping candidate profiles to standardized ontologies like ESCO (European Skills, Competences, Qualifications and Occupations). This moves the system beyond probabilistic guessing to structured, verifiable reasoning.

## ⚠️ The Problem: The "Semantic Gap"
Current ATS platforms fail to bridge the gap between the aspirational language of job descriptions and the factual language of resumes. This manifests in three critical failures:
1. **Polysemy and Context Blindness:** Traditional systems reject qualified candidates for using synonyms (e.g., "ReactJS" vs. "Frontend Development") or conflate terms that appear in similar contexts but have different meanings (e.g., "Java" vs. "JavaScript").
2. **The Hallucination Crisis:** Standard LLMs often fabricate skills or experiences to satisfy prompt requirements, eroding recruiter trust.
3. **Algorithmic Bias:** Standard models perpetuate "Self-Preference Bias." Without structural constraints, "Black Box" models unknowingly penalize candidates based on implicit markers of gender, race, or educational background.

## 💡 Proposed Solution: The GraphRAG Architecture
GraphRAG-ATS is a **Neuro-Symbolic system** combining the linguistic fluency of Large Language Models (LLMs) with the factual precision of Graph Theory. 
* **Multi-Hop Reasoning:** Instead of isolated text chunks, the system retrieves connected subgraphs of knowledge. If a job requires "TensorFlow" and a candidate has "Keras," the graph confirms a strong link.
* **Fairness-First Ranking:** A "Blind Ranking" pre-processor strips personally identifiable information (PII) before graph traversal begins, ensuring scores are based strictly on semantic distance.
* **Glass Box Explainability:** Replaces opaque algorithms with transparent, defensible methodology for high-stakes hiring decisions.

## 👥 Team Details
* **Group No.:** SY CS J17
* **Academic Year:** 2025-26 | **Semester:** 4
* **Internal Guide:** Prof. Dr. Ganesh Bhutkar
* **Project Area:** Artificial Intelligence & Natural Language Processing (NLP)
* **Team Members:**
  * Aniket Rathod
  * Omsai Rathod
  * Vedant Sanap
  * Harsh Mahajan