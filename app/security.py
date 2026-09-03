"""Webhook authentication.

VoiceOps is called by ElevenLabs as a server-side webhook tool, not by an
end-user browser, so a single shared secret header is an appropriate and
proportionate control (see brief: "do not over-engineer identity"). When
`VOICEOPS_WEBHOOK_SECRET` is unset, auth is skipped for local development.
"""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException

from app.config import settings


def require_webhook_secret(x_voiceops_secret: str | None = Header(default=None)) -> None:
    if not settings.webhook_secret:
        return  # auth disabled -- local/dev mode
    if not x_voiceops_secret or not secrets.compare_digest(x_voiceops_secret, settings.webhook_secret):
        raise HTTPException(status_code=401, detail="Missing or invalid X-VoiceOps-Secret header")
