from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_happy_path_requires_confirmation_before_commit():
    prepare = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18342",
            "summary": "Leak under sink; supply isolated; cabinet damaged.",
            "water_isolated": True,
            "electrical_risk": "none",
            "photos_taken": True,
            "damage_area": "kitchen cabinet",
            "next_action": "replace trap and schedule carpenter",
        },
    )
    assert prepare.status_code == 200
    body = prepare.json()
    assert body["status"] == "prepared"
    token = body["confirmation_token"]

    blocked = client.post(
        "/interventions/commit",
        json={"token": token, "explicit_confirmation": False},
    )
    assert blocked.status_code == 409

    committed = client.post(
        "/interventions/commit",
        json={"token": token, "explicit_confirmation": True},
    )
    assert committed.status_code == 200
    assert committed.json()["status"] == "committed"


def test_missing_information_blocks_prepare():
    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18342",
            "summary": "Leak handled.",
            "water_isolated": True,
            "electrical_risk": "none",
            "photos_taken": None,
            "damage_area": None,
            "next_action": None,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_information"
    assert set(body["missing_fields"]) == {"photos_taken", "damage_area", "next_action"}


def test_possible_electrical_risk_escalates():
    response = client.post(
        "/interventions/prepare",
        json={
            "intervention_id": "WO-18342",
            "summary": "Water may have reached an electrical outlet.",
            "water_isolated": True,
            "electrical_risk": "possible",
            "photos_taken": True,
            "damage_area": "kitchen wall and outlet",
            "next_action": "inspect electrical installation",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "escalate"
    assert "electrical" in body["reason"].lower()
