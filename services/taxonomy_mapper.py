import json
import os
from typing import List, Tuple

def map_to_taxonomy(extracted_entities: List[str]) -> Tuple[List[str], List[str]]:
    """
    Takes a list of raw extracted entities and standardizes them by mapping them
    to the ESCO mock taxonomy.
    
    Args:
        extracted_entities (List[str]): Raw entity strings.
        
    Returns:
        Tuple[List[str], List[str]]:
            - list of standard skill names found in the taxonomy
            - list of unmapped terms that couldn't be resolved
    """
    if not extracted_entities:
        return [], []
        
    taxonomy_path = os.path.join("data", "esco_mock_taxonomy.json")
    
    if not os.path.exists(taxonomy_path):
        # If taxonomy doesn't exist, we can't map anything
        return [], extracted_entities

    try:
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            taxonomy_data = json.load(f)
    except json.JSONDecodeError:
        print("Warning: Taxonomy JSON is malformed.")
        return [], extracted_entities

    # Reverse the mapping for O(1) lookups
    # Form: {synonym: standard_skill_name}
    synonym_to_standard = {}
    for standard_skill, synonyms in taxonomy_data.items():
        for synonym in synonyms:
            synonym_to_standard[synonym.lower()] = standard_skill
            
    standardized_skills = set()
    unmapped_terms = []
    
    for entity in extracted_entities:
        lowered_entity = entity.lower()
        if lowered_entity in synonym_to_standard:
            standardized_skills.add(synonym_to_standard[lowered_entity])
        else:
            unmapped_terms.append(entity)
            
    if unmapped_terms:
        unmapped_path = os.path.join("data", "unmapped_skills.txt")
        with open(unmapped_path, "a", encoding="utf-8") as f:
            for term in unmapped_terms:
                f.write(f"{term}\n")
                
    return list(standardized_skills), unmapped_terms
