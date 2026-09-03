"""Pydantic models shared across routes and services."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ElectricalRisk = Literal["none", "possible", "confirmed", "unknown"]

# Fields a technician can report by voice. These populate `Intervention.known_data`.
REPORTABLE_FIELDS = (
    "summary",
    "water_isolated",
    "electrical_risk",
    "photos_taken",
    "affected_area",
    "damage_description",
    "next_action",
)


class Intervention(BaseModel):
    """A synthetic ERP work order."""

    id: str
    customer_name: str
    service_address: str
    incident_type: str
    contract_tier: str
    technician_id: str
    initial_notes: str
    urgency: str
    status: str
    required_fields: list[str]
    known_data: dict[str, object | None]


class PrepareUpdateRequest(BaseModel):
    """Structured facts extracted from the technician's voice report."""

    intervention_id: str
    summary: str | None = None
    water_isolated: bool | None = None
    electrical_risk: ElectricalRisk | None = None
    photos_taken: bool | None = None
    affected_area: str | None = None
    damage_description: str | None = None
    next_action: str | None = None


class PendingUpdate(BaseModel):
    """A prepared-but-unconfirmed ERP change."""

    token: str
    intervention_id: str
    payload: dict[str, object]
    created_at: str
    expires_at: str


class CommitRequest(BaseModel):
    token: str
    explicit_confirmation: bool = Field(
        description="Must be true only after the technician explicitly confirms the summarized update."
    )
