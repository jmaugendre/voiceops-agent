# Evaluation

## Backend (automated, measured)

Real, current results from `pytest` (see `tests/`):

```
22 passed in 0.50s
```

Coverage: health, intervention retrieval (known/unknown/pre-populated
context), audit trail, missing-fields detection, successful prepare,
conflict detection, both electrical-risk escalation levels, escalation
overriding an incomplete report, commit blocked without confirmation, valid
commit, one-time token enforcement, expired-token rejection, correction
invalidating a stale pending transaction, simulated backend failure on
commit, and audit-event generation.

Re-run locally with:

```bash
pip install -e ".[dev]"
pytest -v
```

## ElevenLabs agent (conversational, not yet measured)

**Status: pending.** The scenarios below are configured as ElevenLabs Agent
Tests per `docs/elevenlabs-setup.md`, but this table is intentionally left
unfilled until they have actually been run against the live agent --
inventing numbers here would defeat the point of the evaluation section.

| Scenario | Pass rate | Notes |
| --- | --- | --- |
| A. Happy path | -- | |
| B. Missing information | -- | |
| C. Electrical escalation | -- | |
| D. Ambiguous confirmation | -- | |
| E. User correction | -- | |
| F. Backend failure | -- | |
| G. Hallucination resistance | -- | |

Target: **unconfirmed ERP writes = 0** across all runs.

This section will be updated with real measured results once the agent is
configured and Agent Testing has been run (see roadmap in the README).
