import api.routers.emails as emails_router

from tests.factories import make_email


def test_list_emails_returns_parsed_emails(
    client,
    monkeypatch,
):
    emails = [
        make_email("email-1", "First email"),
        make_email("email-2", "Second email"),
    ]

    def fake_get_latest_message_ids(
        service,
        max_results,
    ):
        assert max_results == 2
        return ["email-1", "email-2"]

    def fake_get_email_by_id(service, message_id):
        return next(
            email
            for email in emails
            if email.id == message_id
        )

    monkeypatch.setattr(
        emails_router,
        "get_latest_message_ids",
        fake_get_latest_message_ids,
    )
    monkeypatch.setattr(
        emails_router,
        "get_email_by_id",
        fake_get_email_by_id,
    )

    response = client.get(
        "/api/v1/emails",
        params={"max_results": 2},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["id"] == "email-1"
    assert data[0]["subject"] == "First email"
    assert data[1]["id"] == "email-2"


def test_list_emails_uses_default_limit(
    client,
    monkeypatch,
):
    received_limit = None

    def fake_get_latest_message_ids(
        service,
        max_results,
    ):
        nonlocal received_limit
        received_limit = max_results
        return []

    monkeypatch.setattr(
        emails_router,
        "get_latest_message_ids",
        fake_get_latest_message_ids,
    )

    response = client.get("/api/v1/emails")

    assert response.status_code == 200
    assert response.json() == []
    assert received_limit == 5


def test_list_emails_rejects_zero_limit(client):
    response = client.get(
        "/api/v1/emails",
        params={"max_results": 0},
    )

    assert response.status_code == 422


def test_list_emails_rejects_excessive_limit(client):
    response = client.get(
        "/api/v1/emails",
        params={"max_results": 51},
    )

    assert response.status_code == 422


def test_get_email_returns_requested_email(
    client,
    monkeypatch,
):
    email = make_email(
        email_id="email-456",
        subject="AWS course",
    )

    def fake_get_email_by_id(service, message_id):
        assert message_id == "email-456"
        return email

    monkeypatch.setattr(
        emails_router,
        "get_email_by_id",
        fake_get_email_by_id,
    )

    response = client.get(
        "/api/v1/emails/email-456"
    )

    assert response.status_code == 200
    assert response.json()["id"] == "email-456"
    assert response.json()["subject"] == "AWS course"


def test_get_email_returns_502_when_gmail_fails(
    client,
    monkeypatch,
):
    def fake_get_email_by_id(service, message_id):
        raise RuntimeError("Gmail unavailable")

    monkeypatch.setattr(
        emails_router,
        "get_email_by_id",
        fake_get_email_by_id,
    )

    response = client.get(
        "/api/v1/emails/email-456"
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": (
            "Unable to retrieve Gmail message "
            "email-456."
        )
    }


def test_list_emails_returns_502_when_gmail_fails(
    client,
    monkeypatch,
):
    def fake_get_latest_message_ids(
        service,
        max_results,
    ):
        raise RuntimeError("Gmail unavailable")

    monkeypatch.setattr(
        emails_router,
        "get_latest_message_ids",
        fake_get_latest_message_ids,
    )

    response = client.get("/api/v1/emails")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Unable to retrieve emails from Gmail."
    }