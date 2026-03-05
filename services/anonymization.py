from typing import Dict, Tuple

# Optional: If the user hasn't downloaded the spaCy model yet, importing Presidio
# could cause an error at runtime. We'll handle initialization gracefully.
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
except ImportError:
    AnalyzerEngine = None
    AnonymizerEngine = None
    OperatorConfig = None

# Initialize the engines once to save resources.
# This assumes the underlying spaCy model ('en_core_web_lg' by default for English)
# is available. If not, the application might fail to start if instantiated globally here.
# To be robust, we lazily initialize or catch errors.

_analyzer: AnalyzerEngine = None
_anonymizer: AnonymizerEngine = None

def _get_engines() -> Tuple[AnalyzerEngine, AnonymizerEngine]:
    """
    Lazily initializes and returns the Presidio engines.
    
    Returns:
        Tuple[AnalyzerEngine, AnonymizerEngine]: The analyzer and anonymizer engines.
        
    Raises:
        RuntimeError: If Presidio cannot be imported or initialized (e.g., missing spaCy model).
    """
    global _analyzer, _anonymizer
    
    if AnalyzerEngine is None or AnonymizerEngine is None:
         raise RuntimeError("Presidio libraries are not installed. Please check your setup.")
         
    if _analyzer is None:
        try:
            # We construct the analyzer with the default NLP engine setup,
            # which expects 'en_core_web_lg' for English out of the box.
            # You can customize the registry to use other models.
            _analyzer = AnalyzerEngine()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AnalyzerEngine. Ensure 'en_core_web_lg' is downloaded: {str(e)}")
            
    if _anonymizer is None:
         _anonymizer = AnonymizerEngine()
         
    return _analyzer, _anonymizer


def anonymize_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Analyzes and strips Personally Identifiable Information (PII) from text.
    
    Target Entities: PERSON, EMAIL_ADDRESS, PHONE_NUMBER, LOCATION, URL
    
    Args:
        text (str): The raw text to anonymize.
        
    Returns:
        Tuple[str, Dict[str, int]]: 
            - The anonymized text.
            - A summary dictionary mapping entity types to the count of how many were redacted.
    """
    if not text:
         return "", {}

    try:
        analyzer, anonymizer = _get_engines()
    except RuntimeError as e:
        # If engines fail to load, we cannot sanitize. Better to fail securely than leak text.
        raise ValueError(f"Anonymization service unavailable: {str(e)}")

    # Define the entities we care about for "Blind Ranking"
    entities_to_find = [
        "PERSON", 
        "EMAIL_ADDRESS", 
        "PHONE_NUMBER", 
        "LOCATION", 
        "URL"
    ]
    
    # Analyze the text
    analyzer_results = analyzer.analyze(
        text=text, 
        entities=entities_to_find, 
        language='en'
    )
    
    # Configure operators to replace entities with their type name, e.g., <PERSON>
    # The default operator for AnonymizerEngine replaces with <ENTITY_TYPE>
    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "[PERSON_NAME]"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
        "URL": OperatorConfig("replace", {"new_value": "[URL]"})
    }
    
    # Anonymize
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators=operators
    )
    
    anonymized_text = anonymized_result.text
    
    # Summarize redactions
    redacted_entities: Dict[str, int] = {}
    for item in analyzer_results:
        entity_type = item.entity_type
        redacted_entities[entity_type] = redacted_entities.get(entity_type, 0) + 1
        
    return anonymized_text, redacted_entities
