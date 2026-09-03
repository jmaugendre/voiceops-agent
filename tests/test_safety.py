from __future__ import annotations


def test_possible_electrical_risk_escalates(client):
    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18344",
            "summary": "Water may have reached an electrical outlet.",
            "water_isolated": True,
            "electrical_risk": "possible",
            "photos_taken": True,
            "affected_area": "hallway wall and outlet",
            "damage_description": "Damp patch around outlet, unconfirmed extent.",
            "next_action": "inspect electrical installation",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "escalate"
    assert "electrical" in body["reason"].lower()
    assert "confirmation_token" not in body


def test_confirmed_electrical_risk_escalates(client):
    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18344",
            "summary": "Standing water reached the outlet, breaker already tripped.",
            "water_isolated": True,
            "electrical_risk": "confirmed",
            "photos_taken": True,
            "affected_area": "hallway wall and outlet",
            "damage_description": "Visible water ingress in outlet box.",
            "next_action": "await electrician",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "escalate"


def test_electrical_risk_escalates_even_with_missing_fields(client):
    """Safety escalation must win over every other check -- an incomplete
    report with a live electrical hazard must not be treated as merely
    'needs more information'."""

    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18344",
            "electrical_risk": "possible",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "escalate"


def test_unknown_electrical_risk_is_treated_as_missing(client):
    """The agent cannot silently default electrical risk to 'unknown' and
    proceed -- it must be asked about explicitly."""

    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18342",
            "summary": "Leak under sink.",
            "water_isolated": True,
            "electrical_risk": "unknown",
            "photos_taken": True,
            "affected_area": "kitchen cabinet",
            "damage_description": "Cabinet base swollen.",
            "next_action": "replace trap",
        },
    )
    body = response.json()
    assert body["status"] == "needs_information"
    assert "electrical_risk" in body["missing_fields"]


def test_escalation_never_produces_a_commit_token(client):
    """Because escalation returns no confirmation_token, commit is
    structurally impossible for an escalated report."""

    response = client.post(
        "/interventions/prepare",
        json={"intervention_id": "WO-18344", "electrical_risk": "possible"},
    )
    body = response.json()
    assert "confirmation_token" not in body

    commit = client.post(
        "/interventions/commit",
        json={"token": "nonexistent-token", "explicit_confirmation": True},
    )
    assert commit.status_code == 404
