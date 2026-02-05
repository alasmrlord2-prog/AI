"""Chat API tests."""
import pytest
from fastapi import status


def test_chat_endpoint(client):
    """Test chat endpoint."""
    response = client.post(
        "/api/chat",
        json={
            "message": "Hello, test message",
            "session_id": "test_session"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "reply" in response.json()
    assert "session_id" in response.json()


def test_chat_without_session_id(client):
    """Test chat endpoint without session_id."""
    response = client.post(
        "/api/chat",
        json={
            "message": "Test message"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["session_id"] is not None

