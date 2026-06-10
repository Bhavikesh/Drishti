from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
import pytest

client = TestClient(app)

@patch("routes.chat.mistral_client.query_mistral")
@patch("routes.chat.rag_pipeline.retrieve_relevant_crimes")
@patch("routes.chat.translation.translate_to_english")
def test_chat_endpoint(mock_translate, mock_rag, mock_mistral):
    # Setup mocks
    mock_translate.return_value = "What is the crime rate in Mysore?"
    mock_rag.return_value = {"documents": [["Mock crime doc 1"]], "metadatas": [[{"case_id": "123"}]]}
    mock_mistral.return_value = "The crime rate in Mysore is stable."
    
    response = client.post("/api/chat/", json={
        "message": "ಮೈಸೂರಿನಲ್ಲಿ ಅಪರಾಧ ಪ್ರಮಾಣ ಎಷ್ಟು?",
        "session_id": "test_session_123",
        "language": "kn"
    })
    
    assert response.status_code == 200
    assert "response" in response.json()
    assert "sources" in response.json()
