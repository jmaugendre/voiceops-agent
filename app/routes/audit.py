"""Optional audit-trail endpoint. Not called by the agent -- useful for the
demo UI and for verifying, from outside the conversation, exactly what the
backend did and why.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.security import require_webhook_secret
from app.services import audit

router = APIRouter(prefix="/audit", tags=["audit"], dependencies=[Depends(require_webhook_secret)])


@router.get("")
def list_audit_events(intervention_id: str | None = None) -> list[dict[str, object]]:
    return audit.all_events(intervention_id)
