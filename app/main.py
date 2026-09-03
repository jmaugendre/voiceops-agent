"""VoiceOps Agent API.

FastAPI backend that fronts a synthetic ERP for a voice-first field-service
workflow. See docs/architecture.md for the full design and README.md for
the project overview.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routes import audit, interventions


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not settings.webhook_secret:
        print(
            "[voiceops] WARNING: VOICEOPS_WEBHOOK_SECRET is not set -- webhook "
            "endpoints are unauthenticated. This is fine for local development "
            "only; set it before exposing this API publicly.",
            file=sys.stderr,
        )
    yield


app = FastAPI(
    title="VoiceOps Agent API",
    version="0.2.0",
    description="Governed voice-to-ERP webhook backend for the VoiceOps ElevenLabs agent demo.",
    lifespan=lifespan,
)

app.include_router(interventions.router)
app.include_router(audit.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
