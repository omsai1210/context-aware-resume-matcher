from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

@patch("routers.webhook.BackgroundTasks.add_task")
def test_apply_webhook_success(mock_add_task):
    request_payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "resume_drive_url": "https://drive.google.com/file/d/1abcdefg234567890/view",
        "job_requirements": ["Python Programming", "Machine Learning"]
    }
    
    response = client.post("/api/v1/webhook/apply", json=request_payload)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "Success"
    assert "Processing in background" in json_data["message"]
    
    # Verify that the background task was actually queued to trigger the orchestrator
    mock_add_task.assert_called_once()

def test_apply_webhook_missing_fields():
    # Only sending name, omitting email, drive url, etc.
    request_payload = {
        "name": "Jane Doe"
    }
    
    response = client.post("/api/v1/webhook/apply", json=request_payload)
    
    assert response.status_code == 422 # FastAPI validation failure
