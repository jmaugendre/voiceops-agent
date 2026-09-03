"""Synthetic ERP store.

Five scenarios cover the workflow behaviours the demo needs to prove:

- WO-18342  happy path (nothing recorded yet)
- WO-18343  several mandatory fields missing
- WO-18344  potential electrical risk
- WO-18345  pre-existing data that a new report can conflict with
- WO-18346  simulated downstream ERP/backend failure on commit

All names, addresses and notes are fictional.
"""

from __future__ import annotations

from app.models import Intervention

REQUIRED_FIELDS = [
    "summary",
    "water_isolated",
    "electrical_risk",
    "photos_taken",
    "affected_area",
    "damage_description",
    "next_action",
]

# Work orders where the commit step should simulate a downstream ERP failure,
# e.g. an outage in the real system this backend fronts. Used by the
# "backend failure" test scenario -- the agent must never claim success.
SIMULATED_COMMIT_FAILURES: set[str] = {"WO-18346"}


def _empty_known_data() -> dict[str, object | None]:
    return {field: None for field in REQUIRED_FIELDS}


def _build_erp() -> dict[str, Intervention]:
    return {
        "WO-18342": Intervention(
            id="WO-18342",
            customer_name="Camille Martin",
            service_address="12 Rue des Forges, Nantes",
            incident_type="water_damage",
            contract_tier="premium",
            technician_id="TECH-071",
            initial_notes="Customer reported a leak under the kitchen sink overnight.",
            urgency="standard",
            status="in_progress",
            required_fields=list(REQUIRED_FIELDS),
            known_data=_empty_known_data(),
        ),
        "WO-18343": Intervention(
            id="WO-18343",
            customer_name="Sofiane Belkacem",
            service_address="4 Allee du Lavoir, Rennes",
            incident_type="water_damage",
            contract_tier="standard",
            technician_id="TECH-088",
            initial_notes="Tenant reported a slow leak near the bathroom.",
            urgency="standard",
            status="in_progress",
            required_fields=list(REQUIRED_FIELDS),
            known_data=_empty_known_data(),
        ),
        "WO-18344": Intervention(
            id="WO-18344",
            customer_name="Elena Duarte",
            service_address="27 Rue du Marche, Lyon",
            incident_type="water_damage",
            contract_tier="standard",
            technician_id="TECH-045",
            initial_notes="Customer mentioned the hallway wall felt damp near a power outlet.",
            urgency="standard",
            status="in_progress",
            required_fields=list(REQUIRED_FIELDS),
            known_data=_empty_known_data(),
        ),
        "WO-18345": Intervention(
            id="WO-18345",
            customer_name="Youssef Amrani",
            service_address="9 Impasse des Tilleuls, Toulouse",
            incident_type="water_damage",
            contract_tier="premium",
            technician_id="TECH-071",
            initial_notes=(
                "A first technician visit already recorded partial details. "
                "Confirm before overwriting."
            ),
            urgency="standard",
            status="in_progress",
            required_fields=list(REQUIRED_FIELDS),
            known_data={
                **_empty_known_data(),
                "photos_taken": True,
                "affected_area": "hallway ceiling",
            },
        ),
        "WO-18346": Intervention(
            id="WO-18346",
            customer_name="Nadia Fontaine",
            service_address="58 Boulevard de la Gare, Lille",
            incident_type="water_damage",
            contract_tier="standard",
            technician_id="TECH-052",
            initial_notes="Leak reported under the utility room sink.",
            urgency="standard",
            status="in_progress",
            required_fields=list(REQUIRED_FIELDS),
            known_data=_empty_known_data(),
        ),
    }


ERP: dict[str, Intervention] = _build_erp()


def reset() -> None:
    """Restore the ERP store to its initial synthetic state (used by tests).

    Mutates the existing dict in place (rather than rebinding the module
    global) so any module that imported `ERP` by reference still sees the
    reset data.
    """

    ERP.clear()
    ERP.update(_build_erp())


def get(intervention_id: str) -> Intervention | None:
    return ERP.get(intervention_id)


def simulates_commit_failure(intervention_id: str) -> bool:
    return intervention_id in SIMULATED_COMMIT_FAILURES
