from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("routers.match.generate_explanation")
def test_explain_match_success(mock_explain):
    # Mock the return value of generate_explanation
    mock_data = {
        "candidate_id": "candidate_123",
        "score": 2,
        "total_requirements": 2,
        "explanation": "This is a mock AI explanation of the candidate's skills.",
        "subgraph_context_used": [
            {"category": "Python Programming", "related_skills": ["Python"]},
            {"category": "Machine Learning", "related_skills": ["TensorFlow"]}
        ]
    }
    mock_explain.return_value = mock_data

    request_payload = {
        "candidate_id": "candidate_123",
        "job_requirements": ["Python Programming", "Machine Learning"]
    }
    
    response = client.post("/api/v1/match/explain", json=request_payload)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "Success"
    assert json_data["data"]["candidate_id"] == "candidate_123"
    assert json_data["data"]["explanation"] == "This is a mock AI explanation of the candidate's skills."
    mock_explain.assert_called_once_with("candidate_123", ["Python Programming", "Machine Learning"])

@patch("routers.match.generate_explanation")
def test_explain_match_not_found(mock_explain):
    # Mock explanation returning an error (e.g., candidate not found)
    mock_explain.return_value = {"error": "Candidate unknown_candidate not found in the graph."}
    
    request_payload = {
        "candidate_id": "unknown_candidate",
        "job_requirements": ["Python Programming"]
    }
    
    response = client.post("/api/v1/match/explain", json=request_payload)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()
    mock_explain.assert_called_once_with("unknown_candidate", ["Python Programming"])

def test_explain_missing_payload():
    request_payload = {
        "candidate_id": "candidate_123"
        # missing job_requirements
    }
    response = client.post("/api/v1/match/explain", json=request_payload)
    assert response.status_code == 422 # FastAPI validation error for missing field
