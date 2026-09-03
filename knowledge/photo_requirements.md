# Photo / Evidence Requirements

> Synthetic internal guidance for the VoiceOps demo.

Photo evidence is one of the required fields (`photos_taken`) on every
water-damage intervention. This document explains what the field means so
the agent can ask about it naturally rather than reading a form field name
aloud.

## What counts as "photos taken"

`photos_taken` should be `true` only if the technician actually captured
photo evidence during the visit — typically of the source of the leak, the
affected area, and any visible damage. It should be `false` if no photos
were taken, for example because the damage was minor and undocumented, or
access was not possible.

## Why it matters

Photo evidence supports the customer file and, for premium-tier contracts,
is often required before an insurance-adjacent claim can be processed. The
agent does not need to enforce this — it is a required field like any
other, validated by the backend before an update can be prepared.

## How to ask about it

Prefer a direct, natural question such as "Did you take photos of the
damage?" rather than referencing the field name. If the technician has
already mentioned photos in their initial report (e.g. "photos taken"),
do not ask again.
