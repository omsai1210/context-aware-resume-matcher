from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from services import rag_service

client = TestClient(app)

@patch("routers.rag.match_candidates")
def test_match_candidates_success(mock_match):
    # Mock the return value of match_candidates
    mock_data = [
        {"candidate_id": "candidate_123", "matched_skills": ["Frontend Development", "Backend Development"], "match_count": 2},
        {"candidate_id": "candidate_456", "matched_skills": ["Frontend Development"], "match_count": 1}
    ]
    mock_match.return_value = mock_data

    request_payload = {
        "required_skills": ["Frontend Development", "Backend Development"]
    }
    
    response = client.post("/api/v1/rag/match", json=request_payload)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "Success"
    assert len(json_data["matches"]) == 2
    assert json_data["matches"][0]["candidate_id"] == "candidate_123"
    assert json_data["matches"][0]["match_count"] == 2
    mock_match.assert_called_once_with(["Frontend Development", "Backend Development"])

@patch("routers.rag.get_candidate_subgraph")
def test_get_subgraph_success(mock_subgraph):
    # Mock subgraph response
    mock_data = {
        "candidate_id": "candidate_123",
        "skill_mapping": [
            {"category": "Frontend Development", "related_skills": ["ReactJS", "HTML5", "CSS3"]},
            {"category": "Backend Development", "related_skills": ["Node.js"]}
        ]
    }
    mock_subgraph.return_value = mock_data
    
    response = client.get("/api/v1/rag/candidate/candidate_123/subgraph")
    assert response.status_code == 200
    json_data = response.json()
    
    assert json_data["status"] == "Success"
    assert json_data["data"]["candidate_id"] == "candidate_123"
    assert len(json_data["data"]["skill_mapping"]) == 2
    mock_subgraph.assert_called_once_with("candidate_123")
    
@patch("routers.rag.get_candidate_subgraph")
def test_get_subgraph_not_found(mock_subgraph):
    # Mock subgraph returning None (not found)
    mock_subgraph.return_value = None
    
    response = client.get("/api/v1/rag/candidate/unknown_candidate/subgraph")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    mock_subgraph.assert_called_once_with("unknown_candidate")

def test_match_missing_skills_payload():
    request_payload = {
        "required_skills": []
    }
    response = client.post("/api/v1/rag/match", json=request_payload)
    assert response.status_code == 400
