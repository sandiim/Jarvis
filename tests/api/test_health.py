from fastapi.testclient import TestClient

from api.dependencies import provide_gmail_service

from app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "jarvis-email-assistant",
        "version": "0.1.0",
    }
