---
name: implement
description: Main workflow phase 3. Implement one phase at a time from docs/01-plan.md, run its automated checks, tick its checkboxes, then pause for human verification before the next phase.
argument-hint: <optional: a specific phase from the plan>
disable-model-invocation: true
---

# Phase: Implement

You are running the **Implementation** phase for the user's request.

User request / target task:

`$ARGUMENTS`

## Purpose

Implement the next **phase** from `docs/01-plan.md` — one phase at a time —
without drifting into uncontrolled scope expansion.

## Hard rules

- Do **not** start implementation if `docs/01-plan.md` is missing. Ask the user
  to run `/plan` first.
- Implement **only one phase per run**, unless the user explicitly asks you to
  continue through multiple phases.
- Do not silently redesign the architecture.
- Do not add extra features because they seem useful.
- Update documentation if implementation differs from the plan.
- Run the phase's automated checks, or explain why they cannot be run.
- **Pause after each phase** and wait for the user before starting the next one.

## Required pre-flight check

Before editing any files, read fully:

- `docs/01-plan.md` (required)
- `docs/00-research.md`, if present
- `docs/02-architecture.md`, if present
- `docs/03-data-model.md`, if present

Then determine **which phase to implement**:

- Read the phase checkboxes in the plan. Trust completed items (`- [x]`).
- Pick up at the first phase whose criteria are not yet checked off.
- If the user named a specific phase, use that one.

## Implementation process

1. Read the plan fully (no limit/offset — you need complete context).
2. State the phase you are about to implement and why it is next.
3. List the files likely to change.
4. Make the smallest useful change to satisfy that phase.
5. Add or update tests.
6. Run the phase's **Automated** success-criteria checks.
7. Check off the automated `- [x]` items you verified, directly in `docs/01-plan.md`.
8. Update docs if the implementation deviated from the plan.
9. **Pause for human verification** (see below) — do not start the next phase.

## Pause for human verification

After a phase passes its automated checks, stop and report in this format, then wait:

```text
Phase N complete — ready for manual verification.

Automated checks: <what you ran and the result>

Please verify manually:
- <manual success-criteria items from the plan for this phase>

Tell me when manual testing passes and I'll continue to Phase N+1.
```

Do not check off **Manual** criteria yourself — only the user confirms those.

## Scope control

If you discover that the plan is wrong or incomplete:

- Stop implementation.
- Explain the mismatch clearly:

  ```text
  Issue in Phase N:
  Expected: <what the plan says>
  Found: <actual situation>
  Why it matters: <explanation>

  How should I proceed?
  ```

- Update `docs/01-plan.md` or recommend running `/architecture` or `/data-model`.
- Wait for the user's direction before continuing if the change is significant.

## Output expectations

At the end, report:

```md
## Implementation Summary

### Implemented Phase

### Files Changed

### Automated Checks Run

### Result

### Deviations From Plan

### Awaiting Manual Verification

(List the manual items the user must confirm, then the next phase.)
```

## Definition of done

A phase is done only when:

- The phase's change works and its automated checks pass (or limits are explained).
- The automated `- [x]` items for the phase are checked off in `docs/01-plan.md`.
- Documentation is not stale.
- No extra unplanned scope was added.
- You have paused and asked the user to verify before the next phase.
