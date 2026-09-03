"""In-memory audit trail.

A portfolio-scale substitute for a real audit sink. Every workflow decision
(read, blocked, escalated, prepared, committed) is recorded so the demo can
show a traceable history of what the agent did and why.
"""

from __future__ import annotations

from datetime import datetime, timezone

AUDIT: list[dict[str, object]] = []


def record(event: str, **details: object) -> dict[str, object]:
    entry = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **details,
    }
    AUDIT.append(entry)
    return entry


def all_events(intervention_id: str | None = None) -> list[dict[str, object]]:
    if intervention_id is None:
        return list(AUDIT)
    return [e for e in AUDIT if e.get("intervention_id") == intervention_id]


def reset() -> None:
    AUDIT.clear()
