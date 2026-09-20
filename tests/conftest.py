import pytest
from fastapi.testclient import TestClient
from api.dependencies import provide_gmail_service

from app import app


class FakeGmailService:
    """Prevents tests from creating a real Gmail service."""


@pytest.fixture
def fake_gmail_service():
    return FakeGmailService()


@pytest.fixture
def client(fake_gmail_service):
    def override_gmail_service():
        return fake_gmail_service

    app.dependency_overrides[provide_gmail_service] = (
        override_gmail_service
    )

    with TestClient(app) as test_client:
        yield test_client

    # Prevent the override from leaking into other tests.
    app.dependency_overrides.clear()