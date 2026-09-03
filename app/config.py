"""Environment-driven configuration.

Kept deliberately small: no extra dependency, just os.environ reads with
sane defaults so the API runs locally with zero configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Shared secret VoiceOps expects on the `X-VoiceOps-Secret` header for
    # every /interventions and /audit request. Empty = auth disabled (local
    # dev only). Configure the same value as a custom header on each
    # ElevenLabs webhook tool in production.
    webhook_secret: str = ""

    # How long a prepared update stays valid before the technician must
    # give explicit confirmation (seconds).
    token_ttl_seconds: int = 300


def load_settings() -> Settings:
    return Settings(
        webhook_secret=os.environ.get("VOICEOPS_WEBHOOK_SECRET", ""),
        token_ttl_seconds=int(os.environ.get("VOICEOPS_TOKEN_TTL_SECONDS", "300")),
    )


settings = load_settings()
