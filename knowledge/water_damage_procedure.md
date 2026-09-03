# Water Damage Intervention Procedure

> Synthetic internal procedure for the VoiceOps demo. Not a real company
> policy.

This is the standard checklist a field technician follows when closing out a
water-damage intervention. It exists so VoiceOps can hold a natural
conversation about the work — the actual record of what was done is always
retrieved from and written to the ERP through tools, never inferred from this
document alone.

## Standard checklist

1. **Isolate the water source.** Confirm the leak or supply has been shut off
   or otherwise stopped before any other step.
2. **Check for electrical risk.** See `electrical_safety.md`. This step
   always takes priority over the rest of the checklist.
3. **Document the damage.** Identify the affected area (e.g. "kitchen
   cabinet", "hallway ceiling") and describe the damage observed.
4. **Take evidence photos.** See `photo_requirements.md`.
5. **Determine the next action.** See `next_actions.md`.
6. **Report a summary.** A short, plain-language description of what
   happened and what was done, suitable for the customer file.

## What "complete" means

An intervention is only ready to close when all of the following are known:
whether the water was isolated, the electrical risk level, whether photos
were taken, the affected area, a damage description, and the next action.
If any of these is missing, the technician should be asked about it directly
— not assumed.

## Typical incidents

Common water-damage causes in this synthetic dataset: a failed sink or
appliance connection, a slow pipe leak, a roof or ceiling infiltration, or a
supply line failure. The cause is useful context but is not itself a
required field.

## Conflicting reports

If a technician's report contradicts something already recorded for the
same intervention (for example, a different affected area than what a
previous visit logged), do not silently overwrite it. Read back both values
and ask the technician to confirm which one is correct.
