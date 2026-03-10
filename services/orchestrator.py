import traceback
from services.drive_service import download_resume
from services.extraction import extract_text_from_pdf, extract_text_from_docx
from services.anonymization import anonymize_text
from services.nlp_extraction import extract_entities
from services.taxonomy_mapper import map_to_taxonomy
from services.graph_service import add_candidate_to_graph
from services.scoring_service import generate_explanation
from services.email_service import send_feedback_email

def process_candidate_pipeline(name: str, email: str, drive_url: str, job_requirements: list[str]):
    """
    The master orchestrator for the background task.
    Downloads the resume, runs it through Modules 1-5, and dispatches an email.
    """
    try:
        print(f"Starting background pipeline for {name} ({email})")
        
        # 1. Download Resume from Google Drive
        file_bytes = download_resume(drive_url)
        
        # We try to extract as PDF first; if it fails, try DOCX.
        extracted_text = ""
        try:
            extracted_text = extract_text_from_pdf(file_bytes)
        except Exception:
            try:
                extracted_text = extract_text_from_docx(file_bytes)
            except Exception as e:
                print(f"Error extracting text for {name}: {e}")
                return
                
        # 2. Anonymize Text (Module 1)
        anonymized_text, _ = anonymize_text(extracted_text)
        
        # 3. Extract Entities & Map to Taxonomy (Module 2)
        extracted_entities = extract_entities(anonymized_text)
        standardized_skills, _ = map_to_taxonomy(extracted_entities.get("skills", []))
        
        # 4. Add to Graph (Module 3)
        candidate_id = email  # using email as the unique identifier for the graph
        add_candidate_to_graph(candidate_id, standardized_skills)
        
        # 5. Match & Evaluate Context (Modules 4 & 5)
        result = generate_explanation(candidate_id, job_requirements)
        
        if "error" in result:
             print(f"Error generating explanation for {name}: {result['error']}")
             return
             
        # 6. Dispatch Email Feedback
        score = result.get("score", 0)
        total_reqs = result.get("total_requirements", len(job_requirements))
        explanation = result.get("explanation", "")
        
        send_feedback_email(email, name, score, total_reqs, explanation)
        
        print(f"Finished pipeline for {name} ({email}). Score: {score}/{total_reqs}")
        
    except Exception as e:
        print(f"Pipeline error for {name} ({email}): {traceback.format_exc()}")
