import requests
import json

API_URL_INIT = "http://127.0.0.1:8000/api/v1/graph/init"
API_URL_CANDIDATE = "http://127.0.0.1:8000/api/v1/graph/candidate"

def test_graph_endpoints():
    print("--- Testing /graph/init endpoint ---")
    try:
        response_init = requests.post(API_URL_INIT)
        print(f"Init Status Code: {response_init.status_code}")
        print("Init Response JSON:")
        try:
             print(json.dumps(response_init.json(), indent=2))
        except ValueError:
             print(response_init.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Is the server running?")
        return

    print("\n--- Testing /graph/candidate endpoint ---")
    
    # Mock data output from Module 2 mapping
    payload = {
        "candidate_id": "test_candidate_123",
        "standardized_skills": [
            "Machine Learning",
            "Python Programming",
            "Cloud Computing"
        ]
    }
    
    try:
        response_cand = requests.post(API_URL_CANDIDATE, json=payload)
        print(f"Candidate Status Code: {response_cand.status_code}")
        print("Candidate Response JSON:")
        try:
             print(json.dumps(response_cand.json(), indent=2))
        except ValueError:
             print(response_cand.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Is the server running?")

if __name__ == "__main__":
    test_graph_endpoints()
