from __future__ import annotations


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_intervention_returns_known_context(client):
    response = client.get("/interventions/WO-18342")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "WO-18342"
    assert body["status"] == "in_progress"
    assert "required_fields" in body
    assert "known_data" in body
    # Nothing reported yet -- the agent should ask, not assume.
    assert body["known_data"]["water_isolated"] is None


def test_get_intervention_pre_populated_context_avoids_redundant_questions(client):
    response = client.get("/interventions/WO-18345")
    assert response.status_code == 200
    known = response.json()["known_data"]
    assert known["photos_taken"] is True
    assert known["affected_area"] == "hallway ceiling"


def test_get_unknown_intervention_returns_404(client):
    response = client.get("/interventions/WO-99999")
    assert response.status_code == 404


def test_intervention_read_is_audited(client):
    client.get("/interventions/WO-18342")
    events = client.get("/audit").json()
    assert any(e["event"] == "intervention_read" and e["intervention_id"] == "WO-18342" for e in events)
