# Next-Action Guidance

> Synthetic internal guidance for the VoiceOps demo.

Every completed water-damage intervention records a `next_action`: what
needs to happen after this visit. This is free text describing the
follow-up, but it should be concrete enough to be useful to whoever reads
the ERP record next.

## Typical next actions

- **No follow-up needed** — the repair was fully completed during the
  visit and no further work is required.
- **Repair or replace a component** — e.g. "replace the trap", "replace the
  supply line", when a specific part needs work beyond this visit.
- **Schedule a specialist** — e.g. "schedule a carpenter", "schedule an
  electrician", when the damage requires a trade the technician doesn't
  perform themselves.
- **Monitor** — e.g. "monitor for mold over the next few days", when the
  area needs to be checked again but no active repair is pending.
- **Await escalation outcome** — used only for escalated (electrical-risk)
  interventions; the next action is determined by the safety supervisor,
  not the technician, and should not be filled in as if this were a normal
  close-out.

## How to ask about it

A natural prompt is "What follow-up is needed?" or "Is there anything else
that needs to happen after this visit?". If the technician's initial report
already states the next step (e.g. "we probably need a carpenter"), use
that instead of asking again.

## What this is not

`next_action` describes what should happen next, not a confirmation that it
has already happened. The agent should never imply a follow-up action (like
a carpenter visit) has been scheduled unless a tool actually confirmed it —
this document only helps recognize what kind of follow-up the technician is
describing.
