"""Deterministic workflow rules.

This module is the single authority for mandatory-field validation, safety
escalation, conflict detection and transaction (prepare/commit) handling.
None of these decisions are delegated to the LLM: the ElevenLabs agent only
ever sees the outcome (`prepared` / `needs_information` / `escalate` /
`conflict` / `committed` / an error) and reports it back to the technician.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.config import settings
from app.models import PendingUpdate, PrepareUpdateRequest
from app.services import audit, erp

PENDING: dict[str, PendingUpdate] = {}


def reset() -> None:
    PENDING.clear()


def _is_missing(field: str, value: object) -> bool:
    if value is None or value == "":
        return True
    # electrical_risk must be an explicit safety determination -- "unknown"
    # is not an acceptable default for a required field.
    if field == "electrical_risk" and value == "unknown":
        return True
    return False


def missing_required_fields(required_fields: list[str], payload: dict[str, object]) -> list[str]:
    return [field for field in required_fields if _is_missing(field, payload.get(field))]


def detect_conflicts(known_data: dict[str, object], payload: dict[str, object]) -> list[dict[str, object]]:
    """Fields where the ERP already holds a value that the new report contradicts."""

    conflicts = []
    for field, reported in payload.items():
        if reported is None:
            continue
        existing = known_data.get(field)
        if existing is not None and existing != reported:
            conflicts.append({"field": field, "existing_value": existing, "reported_value": reported})
    return conflicts


def _invalidate_pending_for(intervention_id: str) -> None:
    """Drop any earlier pending update for this intervention.

    Called whenever a fresh `prepare` succeeds so a technician's correction
    can never be shadowed by a stale, previously-prepared transaction.
    """

    stale_tokens = [t for t, p in PENDING.items() if p.intervention_id == intervention_id]
    for token in stale_tokens:
        del PENDING[token]
        audit.record("prepare_invalidated_previous", intervention_id=intervention_id, token=token)


def prepare_update(request: PrepareUpdateRequest) -> dict[str, object]:
    intervention = erp.get(request.intervention_id)
    if intervention is None:
        return {"status": "not_found"}

    payload = request.model_dump(exclude={"intervention_id"})

    if request.electrical_risk in ("possible", "confirmed"):
        audit.record(
            "safety_escalation",
            intervention_id=request.intervention_id,
            electrical_risk=request.electrical_risk,
        )
        return {
            "status": "escalate",
            "reason": "Potential electrical risk requires human safety review before ERP completion.",
            "instruction": (
                "Stop the normal completion flow. Tell the technician this must be escalated to "
                "the safety supervisor and must not be closed out as a standard water-damage update."
            ),
        }

    conflicts = detect_conflicts(intervention.known_data, payload)
    if conflicts:
        audit.record(
            "prepare_blocked_conflict",
            intervention_id=request.intervention_id,
            conflicting_fields=conflicts,
        )
        return {
            "status": "conflict",
            "conflicting_fields": conflicts,
            "instruction": (
                "Read back each conflicting field and ask the technician to confirm which value is "
                "correct before preparing an update."
            ),
        }

    missing = missing_required_fields(intervention.required_fields, payload)
    if missing:
        audit.record(
            "prepare_blocked_missing_fields",
            intervention_id=request.intervention_id,
            missing=missing,
        )
        return {
            "status": "needs_information",
            "missing_fields": missing,
            "instruction": "Ask only for the missing fields before preparing an ERP update.",
        }

    _invalidate_pending_for(request.intervention_id)

    now = datetime.now(timezone.utc)
    token = str(uuid4())
    pending = PendingUpdate(
        token=token,
        intervention_id=request.intervention_id,
        payload=payload,
        created_at=now.isoformat(),
        expires_at=(now + timedelta(seconds=settings.token_ttl_seconds)).isoformat(),
    )
    PENDING[token] = pending
    audit.record("update_prepared", intervention_id=request.intervention_id, token=token)

    return {
        "status": "prepared",
        "confirmation_token": token,
        "expires_at": pending.expires_at,
        "requires_explicit_confirmation": True,
        "summary_for_confirmation": payload,
    }


class CommitError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def commit_update(token: str, explicit_confirmation: bool) -> dict[str, object]:
    pending = PENDING.get(token)
    if pending is None:
        raise CommitError(404, "Pending update not found, already used, or expired.")

    expires_at = datetime.fromisoformat(pending.expires_at)
    if datetime.now(timezone.utc) >= expires_at:
        del PENDING[token]
        audit.record("commit_blocked_expired_token", intervention_id=pending.intervention_id, token=token)
        raise CommitError(410, "Confirmation token has expired. Prepare the update again.")

    if explicit_confirmation is not True:
        audit.record("commit_blocked_no_confirmation", intervention_id=pending.intervention_id, token=token)
        raise CommitError(409, "Explicit technician confirmation is required.")

    if erp.simulates_commit_failure(pending.intervention_id):
        audit.record("backend_error_simulated", intervention_id=pending.intervention_id, token=token)
        raise CommitError(503, "Simulated ERP backend error: the update could not be written. Nothing was saved.")

    intervention = erp.get(pending.intervention_id)
    if intervention is None:
        # Defensive: the ERP record was removed after the update was prepared.
        del PENDING[token]
        raise CommitError(404, "Intervention no longer exists.")

    intervention.known_data.update(pending.payload)
    intervention.status = "completed"
    del PENDING[token]
    audit.record("update_committed", intervention_id=intervention.id, token=token)

    return {
        "status": "committed",
        "intervention_id": intervention.id,
        "erp_status": intervention.status,
        "saved_payload": pending.payload,
    }
