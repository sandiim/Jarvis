import api.routers.analysis as analysis_router

from tests.factories import *


def test_analyze_single_email(
    client,
    monkeypatch,
):
    email = make_email(email_id="email-123")
    analyzed_email = make_analyzed_email(
        email_id="email-123"
    )

    def fake_get_email_by_id(service, message_id):
        assert message_id == "email-123"
        return email

    def fake_analyze_email(received_email):
        assert received_email.id == "email-123"
        return analyzed_email

    monkeypatch.setattr(
        analysis_router,
        "get_email_by_id",
        fake_get_email_by_id,
    )
    monkeypatch.setattr(
        analysis_router,
        "analyze_email",
        fake_analyze_email,
    )

    response = client.post(
        "/api/v1/analysis/emails/email-123"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"]["id"] == "email-123"
    assert data["analysis"]["category"] == "recruitment"
    assert data["analysis"]["priority"] == "high"
    assert data["analysis"]["action_required"] is True


def test_analyze_single_email_returns_502_on_failure(
    client,
    monkeypatch,
):
    def fake_get_email_by_id(service, message_id):
        raise RuntimeError("Gmail unavailable")

    monkeypatch.setattr(
        analysis_router,
        "get_email_by_id",
        fake_get_email_by_id,
    )

    response = client.post(
        "/api/v1/analysis/emails/email-123"
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": (
            "Unable to analyze Gmail message "
            "email-123."
        )
    }

def test_analyze_single_email_returns_502_when_llm_fails(
    client,
    monkeypatch,
):
    email = make_email(email_id="email-123")

    monkeypatch.setattr(
        analysis_router,
        "get_email_by_id",
        lambda service, message_id: email,
    )

    def fake_analyze_email(email):
        raise RuntimeError("Groq unavailable")

    monkeypatch.setattr(
        analysis_router,
        "analyze_email",
        fake_analyze_email,
    )

    response = client.post(
        "/api/v1/analysis/emails/email-123"
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Unable to analyze Gmail message email-123."
    )


def test_analyze_inbox(
    client,
    monkeypatch,
):
    summary = make_inbox_summary()

    def fake_analyze_latest_inbox(
        gmail_service,
        max_results,
        query,
    ):
        assert max_results == 5
        assert query == "is:unread"
        return summary

    monkeypatch.setattr(
        analysis_router,
        "analyze_latest_inbox",
        fake_analyze_latest_inbox,
    )

    response = client.post(
        "/api/v1/analysis/inbox",
        json={
            "max_results": 5,
            "query": "is:unread",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_emails"] == 1
    assert data["high_priority"] == 1
    assert data["action_required"] == 1
    assert data["categories"] == {
        "recruitment": 1,
    }


def test_analyze_inbox_rejects_zero_results(client):
    response = client.post(
        "/api/v1/analysis/inbox",
        json={"max_results": 0},
    )

    assert response.status_code == 422


def test_analyze_inbox_rejects_more_than_50_results(
    client,
):
    response = client.post(
        "/api/v1/analysis/inbox",
        json={"max_results": 51},
    )

    assert response.status_code == 422


def test_analyze_inbox_rejects_invalid_json(client):
    response = client.post(
        "/api/v1/analysis/inbox",
        json={"max_results": "not-an-integer"},
    )

    assert response.status_code == 422


def test_analyze_inbox_uses_defaults(
    client,
    monkeypatch,
):
    received_arguments = {}

    def fake_analyze_latest_inbox(
        gmail_service,
        max_results,
        query,
    ):
        received_arguments["max_results"] = max_results
        received_arguments["query"] = query
        return make_inbox_summary()

    monkeypatch.setattr(
        analysis_router,
        "analyze_latest_inbox",
        fake_analyze_latest_inbox,
    )

    response = client.post(
        "/api/v1/analysis/inbox",
        json={},
    )

    assert response.status_code == 200
    assert received_arguments == {
        "max_results": 5,
        "query": None,
    }

def test_analyze_inbox_returns_502_on_failure(
    client,
    monkeypatch,
):
    def fake_analyze_latest_inbox(
        gmail_service,
        max_results,
        query,
    ):
        raise RuntimeError("Groq unavailable")

    monkeypatch.setattr(
        analysis_router,
        "analyze_latest_inbox",
        fake_analyze_latest_inbox,
    )

    response = client.post(
        "/api/v1/analysis/inbox",
        json={"max_results": 5},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Unable to analyze the inbox."
    }