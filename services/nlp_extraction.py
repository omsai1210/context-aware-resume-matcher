import spacy
from spacy.pipeline import EntityRuler
from typing import List
import json
import os

# Lazily initialized spaCy model
_nlp = None

def _get_nlp() -> spacy.language.Language:
    """
    Initializes and returns the spaCy NLP pipeline with a custom EntityRuler
    based on the mock ESCO taxonomy.
    """
    global _nlp
    if _nlp is not None:
        return _nlp

    # Load the base model. We use the one installed in Module 1.
    try:
        _nlp = spacy.load("en_core_web_lg")
    except OSError:
        raise RuntimeError(
            "spaCy model 'en_core_web_lg' not found. "
            "Please run: python -m spacy download en_core_web_lg"
        )

    # Let's dynamically create EntityRuler patterns from our taxonomy JSON
    # so we can explicitly extract these skills even if the base NER model misses them.
    taxonomy_path = os.path.join("data", "esco_mock_taxonomy.json")
    
    patterns = []
    if os.path.exists(taxonomy_path):
        try:
            with open(taxonomy_path, "r", encoding="utf-8") as f:
                taxonomy_data = json.load(f)
                
            # Create patterns for every synonym in every category
            for standard_term, synonyms in taxonomy_data.items():
                for synonym in synonyms:
                    # We match both the exact string and lowercase version
                    # "LOWER" matching helps catch "reactjs" when the taxonomy says "ReactJS"
                    patterns.append(
                        {"label": "SKILL", "pattern": [{"LOWER": word.lower()} for word in synonym.split()]}
                    )
        except Exception as e:
            print(f"Warning: Could not load taxonomy for EntityRuler: {e}")

    # Add the EntityRuler to the pipeline before the default NER (Named Entity Recognition)
    # This ensures our custom skills take precedence.
    if _nlp.has_pipe("ner"):
        ruler = _nlp.add_pipe("entity_ruler", before="ner")
    else:
        ruler = _nlp.add_pipe("entity_ruler")
        
    ruler.add_patterns(patterns)
    
    return _nlp

def extract_entities(text: str) -> List[str]:
    """
    Extracts professional entities (skills, roles, etc.) from the given text
    using a custom spaCy NLP pipeline.
    
    Args:
        text (str): The cleaned text (potentially outputs from Module 1).
        
    Returns:
        List[str]: A list of raw extracted entity strings.
    """
    if not text or not text.strip():
        return []

    nlp = _get_nlp()
    doc = nlp(text)
    
    extracted_skills = []
    
    for ent in doc.ents:
        # We specifically want our "SKILL" label defined in the ruler
        # We can also grab default entities if needed, but we focus on SKILLs here.
        if ent.label_ == "SKILL":
            extracted_skills.append(ent.text)
            
    # Remove duplicates while preserving order
    unique_skills = []
    for skill in extracted_skills:
        if skill not in unique_skills:
            unique_skills.append(skill)
            
    return unique_skills
