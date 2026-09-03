"""Webhook tools consumed by the ElevenLabs agent.

Three endpoints, matching the three allowed actions: read, prepare (never a
write), and commit (the only endpoint that ever mutates the ERP, and only
with a valid, unexpired, single-use token plus explicit confirmation).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.models import CommitRequest, PrepareUpdateRequest
from app.security import require_webhook_secret
from app.services import audit, erp, workflow

router = APIRouter(prefix="/interventions", tags=["interventions"], dependencies=[Depends(require_webhook_secret)])


@router.get("/{intervention_id}")
def get_intervention(intervention_id: str) -> dict[str, object]:
    intervention = erp.get(intervention_id)
    if intervention is None:
        raise HTTPException(status_code=404, detail="Intervention not found")
    audit.record("intervention_read", intervention_id=intervention_id)
    return intervention.model_dump()


@router.post("/prepare")
def prepare(request: PrepareUpdateRequest) -> dict[str, object]:
    result = workflow.prepare_update(request)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Intervention not found")
    return result


@router.post("/commit")
def commit(request: CommitRequest) -> dict[str, object]:
    try:
        return workflow.commit_update(request.token, request.explicit_confirmation)
    except workflow.CommitError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
