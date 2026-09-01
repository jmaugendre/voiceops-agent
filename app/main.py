from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="VoiceOps Agent API", version="0.1.0")


class Intervention(BaseModel):
    id: str
    customer_name: str
    address: str
    status: str
    incident_type: str
    contract_tier: str
    technician_id: str
    required_fields: list[str]
    existing_data: dict[str, str | bool | None]


class PrepareUpdateRequest(BaseModel):
    intervention_id: str
    summary: str
    water_isolated: bool | None = None
    electrical_risk: Literal["none", "possible", "confirmed", "unknown"] = "unknown"
    photos_taken: bool | None = None
    damage_area: str | None = None
    next_action: str | None = None


class PendingUpdate(BaseModel):
    token: str
    intervention_id: str
    payload: dict[str, object]
    created_at: str
    requires_confirmation: bool = True


class CommitRequest(BaseModel):
    token: str
    explicit_confirmation: bool = Field(
        description="Must be true only after the technician explicitly confirms the summarized update."
    )


ERP: dict[str, Intervention] = {
    "WO-18342": Intervention(
        id="WO-18342",
        customer_name="Camille Martin",
        address="12 rue des Forges, Nantes",
        status="in_progress",
        incident_type="water_damage",
        contract_tier="premium",
        technician_id="TECH-071",
        required_fields=[
            "summary",
            "water_isolated",
            "electrical_risk",
            "photos_taken",
            "damage_area",
            "next_action",
        ],
        existing_data={
            "water_isolated": None,
            "electrical_risk": None,
            "photos_taken": None,
            "damage_area": None,
            "next_action": None,
        },
    )
}

PENDING: dict[str, PendingUpdate] = {}
AUDIT: list[dict[str, object]] = []


def audit(event: str, **details: object) -> None:
    AUDIT.append(
        {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **details,
        }
    )


def missing_required_fields(intervention: Intervention, request: PrepareUpdateRequest) -> list[str]:
    values = request.model_dump()
    missing: list[str] = []
    for field in intervention.required_fields:
        if values.get(field) in (None, ""):
            missing.append(field)
    return missing


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/interventions/{intervention_id}")
def get_intervention(intervention_id: str) -> dict[str, object]:
    intervention = ERP.get(intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    audit("intervention_read", intervention_id=intervention_id)
    return intervention.model_dump()


@app.post("/interventions/prepare")
def prepare_update(request: PrepareUpdateRequest) -> dict[str, object]:
    intervention = ERP.get(request.intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    if request.electrical_risk in {"possible", "confirmed"}:
        audit(
            "safety_escalation",
            intervention_id=request.intervention_id,
            electrical_risk=request.electrical_risk,
        )
        return {
            "status": "escalate",
            "reason": "Potential electrical risk requires human safety review before ERP completion.",
            "allowed_action": "Contact support / safety supervisor",
        }

    missing = missing_required_fields(intervention, request)
    if missing:
        audit("prepare_blocked_missing_fields", intervention_id=request.intervention_id, missing=missing)
        return {
            "status": "needs_information",
            "missing_fields": missing,
            "instruction": "Ask only for the missing fields before preparing an ERP update.",
        }

    token = str(uuid4())
    payload = request.model_dump(exclude={"intervention_id"})
    pending = PendingUpdate(
        token=token,
        intervention_id=request.intervention_id,
        payload=payload,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    PENDING[token] = pending
    audit("update_prepared", intervention_id=request.intervention_id, token=token)

    return {
        "status": "prepared",
        "confirmation_token": token,
        "requires_explicit_confirmation": True,
        "summary_for_confirmation": payload,
    }


@app.post("/interventions/commit")
def commit_update(request: CommitRequest) -> dict[str, object]:
    pending = PENDING.get(request.token)
    if not pending:
        raise HTTPException(status_code=404, detail="Pending update not found or expired")

    if request.explicit_confirmation is not True:
        audit("commit_blocked_no_confirmation", token=request.token)
        raise HTTPException(status_code=409, detail="Explicit technician confirmation is required")

    intervention = ERP[pending.intervention_id]
    intervention.existing_data.update(pending.payload)
    intervention.status = "completed"
    del PENDING[request.token]
    audit("update_committed", intervention_id=intervention.id, token=request.token)

    return {
        "status": "committed",
        "intervention_id": intervention.id,
        "erp_status": intervention.status,
        "saved_payload": pending.payload,
    }


@app.get("/audit")
def get_audit() -> list[dict[str, object]]:
    return AUDIT
