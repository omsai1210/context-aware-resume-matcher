import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/extract"

def test_extract_endpoint():
    """
    Sends a sample anonymized text to the extract API to verify
    NLP extraction and ontology mapping.
    """
    print(f"--- Testing /extract endpoint ---")
    
    # Mock output from Module 1
    sample_text = """
    [PERSON_NAME]
    Software Engineer
    Email: [EMAIL]
    
    Skills:
    - I am experienced in ReactJS and Python 3.
    - I have worked with Django, Flask, and Vue.
    - I have some background in Machine Learning and Terraform.
    - I also know a bit about CustomObscureSkill and Leadership.
    
    Roles:
    - Previously worked as a Full Stack Engineer at [LOCATION].
    """
    
    payload = {
        "anonymized_text": sample_text
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        print(f"Status Code: {response.status_code}")
        try:
            json_resp = response.json()
            print("Response JSON:")
            print(json.dumps(json_resp, indent=2))
        except ValueError:
            print("Raw Response:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Is the server running?")

if __name__ == "__main__":
    test_extract_endpoint()
