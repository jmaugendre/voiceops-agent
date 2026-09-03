from __future__ import annotations


def test_prepare_unknown_intervention_returns_404(client):
    response = client.post(
        "/interventions/prepare",
        json={"intervention_id": "WO-99999", "summary": "n/a"},
    )
    assert response.status_code == 404


def test_prepare_with_missing_fields_asks_only_for_what_is_missing(client):
    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18343",
            "summary": "Leak fixed and water isolated.",
            "water_isolated": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_information"
    assert set(body["missing_fields"]) == {
        "electrical_risk",
        "photos_taken",
        "affected_area",
        "damage_description",
        "next_action",
    }


def test_successful_prepare_returns_token_and_summary(client):
    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18342",
            "summary": "Leak under sink; supply isolated; cabinet damaged.",
            "water_isolated": True,
            "electrical_risk": "none",
            "photos_taken": True,
            "affected_area": "kitchen cabinet",
            "damage_description": "Cabinet base swollen from water exposure.",
            "next_action": "replace trap and schedule carpenter",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "prepared"
    assert body["confirmation_token"]
    assert body["summary_for_confirmation"]["next_action"] == "replace trap and schedule carpenter"


def test_conflict_detection_flags_contradicted_fields(client):
    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18345",
            "summary": "Ceiling leak in the hallway.",
            "water_isolated": True,
            "electrical_risk": "none",
            "photos_taken": False,  # ERP already has photos_taken=True
            "affected_area": "living room",  # ERP already has "hallway ceiling"
            "damage_description": "Water staining on ceiling tiles.",
            "next_action": "monitor and repaint",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "conflict"
    conflicted_fields = {c["field"] for c in body["conflicting_fields"]}
    assert conflicted_fields == {"photos_taken", "affected_area"}


def test_prepare_blocked_events_are_audited(client):
    client.post(
        "/interventions/prepare",
        json={"intervention_id": "WO-18343", "summary": "Leak fixed."},
    )
    events = client.get("/audit").json()
    assert any(e["event"] == "prepare_blocked_missing_fields" for e in events)
