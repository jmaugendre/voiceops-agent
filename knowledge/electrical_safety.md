# Electrical Safety Rules

> Synthetic internal guidance for the VoiceOps demo. Not real electrical
> safety advice — do not use for an actual incident.

Electrical risk assessment always takes priority over every other step of a
water-damage intervention. A technician should never be pushed toward
closing out an intervention while an electrical hazard is unresolved.

## Risk levels

VoiceOps classifies electrical risk into one of four levels. These map
directly to the `electrical_risk` field the backend expects:

- **none** — no water contact with electrical fixtures, wiring, or outlets
  was observed or suspected.
- **possible** — there is some indication water may have reached an
  electrical fixture, outlet, wiring, or panel, but it has not been
  confirmed (e.g. "the wall near the outlet felt damp", "I'm not sure if
  the wiring was affected").
- **confirmed** — water contact with an electrical fixture, outlet, wiring,
  or panel has been directly observed (e.g. visible water in an outlet box,
  a tripped breaker traced to water ingress).
- **unknown** — the technician has not yet assessed this. This is never an
  acceptable final answer: the technician should be asked directly rather
  than leaving it unset.

## What counts as a signal to ask about electrical risk

Listen for statements like: dampness or wetness near an outlet, switch, or
panel; a burning smell; a tripped breaker; visible water intrusion in a
wall or ceiling cavity near wiring; or simple uncertainty about whether
wiring was affected. Any of these should prompt a direct follow-up question
about electrical risk if it has not already been answered.

## Escalation behavior

When a technician reports `possible` or `confirmed` electrical risk, the
backend will refuse to prepare a normal ERP update and will return an
escalation instruction instead. The agent must:

1. Stop the normal completion flow — do not continue collecting the
   remaining checklist fields as if this were a routine close-out.
2. Clearly tell the technician that this intervention needs to be escalated
   to a safety supervisor and cannot be completed as a standard update.
3. Never call the commit tool for an escalated intervention.

This is a deterministic backend rule, not a suggestion — the agent should
treat the backend's `escalate` response as final and not attempt to argue
the technician out of it or find a way around it.
