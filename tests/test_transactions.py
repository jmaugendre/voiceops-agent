from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.services import workflow

HAPPY_PATH_PAYLOAD = {
    "intervention_id": "WO-18342",
    "summary": "Leak under sink; supply isolated; cabinet damaged.",
    "water_isolated": True,
    "electrical_risk": "none",
    "photos_taken": True,
    "affected_area": "kitchen cabinet",
    "damage_description": "Cabinet base swollen from water exposure.",
    "next_action": "replace trap and schedule carpenter",
}


def _prepare(client, payload=None):
    response = client.post("/interventions/prepare", json=payload or HAPPY_PATH_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "prepared"
    return body["confirmation_token"]


def test_commit_without_confirmation_is_blocked(client):
    token = _prepare(client)
    response = client.post(
        "/interventions/commit",
        json={"token": token, "explicit_confirmation": False},
    )
    assert response.status_code == 409


def test_valid_commit_succeeds_and_updates_erp(client):
    token = _prepare(client)
    response = client.post(
        "/interventions/commit",
        json={"token": token, "explicit_confirmation": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "committed"
    assert body["erp_status"] == "completed"

    erp_state = client.get("/interventions/WO-18342").json()
    assert erp_state["status"] == "completed"
    assert erp_state["known_data"]["next_action"] == "replace trap and schedule carpenter"


def test_token_can_only_be_used_once(client):
    token = _prepare(client)
    first = client.post("/interventions/commit", json={"token": token, "explicit_confirmation": True})
    assert first.status_code == 200

    second = client.post("/interventions/commit", json={"token": token, "explicit_confirmation": True})
    assert second.status_code == 404


def test_expired_token_is_rejected(client):
    token = _prepare(client)
    # Force expiry deterministically instead of sleeping.
    workflow.PENDING[token].expires_at = (
        datetime.now(timezone.utc) - timedelta(seconds=1)
    ).isoformat()

    response = client.post("/interventions/commit", json={"token": token, "explicit_confirmation": True})
    assert response.status_code == 410
    # An expired token is also removed -- it cannot be retried later.
    assert token not in workflow.PENDING


def test_correction_after_prepare_invalidates_previous_pending_transaction(client):
    old_token = _prepare(client)

    corrected_payload = dict(HAPPY_PATH_PAYLOAD)
    corrected_payload["affected_area"] = "kitchen floor"
    corrected_payload["damage_description"] = "Floor damaged instead of the cabinet."
    new_token = _prepare(client, corrected_payload)

    assert new_token != old_token

    stale_commit = client.post(
        "/interventions/commit",
        json={"token": old_token, "explicit_confirmation": True},
    )
    assert stale_commit.status_code == 404

    fresh_commit = client.post(
        "/interventions/commit",
        json={"token": new_token, "explicit_confirmation": True},
    )
    assert fresh_commit.status_code == 200
    assert fresh_commit.json()["saved_payload"]["affected_area"] == "kitchen floor"


def test_simulated_backend_error_on_commit_never_reports_success(client):
    payload = dict(HAPPY_PATH_PAYLOAD)
    payload["intervention_id"] = "WO-18346"
    token = _prepare(client, payload)

    response = client.post("/interventions/commit", json={"token": token, "explicit_confirmation": True})
    assert response.status_code == 503

    erp_state = client.get("/interventions/WO-18346").json()
    assert erp_state["status"] != "completed"


def test_commit_and_escalation_events_are_audited(client):
    token = _prepare(client)
    client.post("/interventions/commit", json={"token": token, "explicit_confirmation": True})

    events = client.get("/audit").json()
    event_names = {e["event"] for e in events}
    assert {"update_prepared", "update_committed"}.issubset(event_names)
