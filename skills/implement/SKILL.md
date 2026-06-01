---
name: implement
description: Main workflow phase 3. Implement only the next approved slice from docs/01-plan.md. Requires research, plan, and explicit user approval. Updates docs and runs checks.
argument-hint: <next slice from the plan>
disable-model-invocation: true
---

# Phase: Implement

You are running the **Implementation** phase for the user's request.

User request / target task:

`$ARGUMENTS`

## Purpose

Implement the next approved slice from `docs/01-plan.md` without drifting into uncontrolled scope expansion.

## Hard rules

- Do **not** start implementation if `docs/01-plan.md` is missing.
- Do **not** start implementation if the project uses `.claude-phase-gate` and `.claude-phase-approved` is missing.
- Implement only the next relevant slice from the plan.
- Do not silently redesign the architecture.
- Do not add extra features because they seem useful.
- Update documentation if implementation differs from the plan.
- Run appropriate tests/checks, or explain why they cannot be run.

## Required pre-flight check

Before editing production files, inspect:

- `docs/00-research.md`
- `docs/01-plan.md`
- `docs/02-architecture.md`, if present
- `docs/03-data-model.md`, if present
- `.claude-phase-gate`, if present
- `.claude-phase-approved`, if present

If `.claude-phase-gate` exists but `.claude-phase-approved` is missing, stop and tell the user:

```bash
touch .claude-phase-approved
```

Do not create `.claude-phase-approved` yourself.

## Implementation process

1. Read the plan.
2. Identify the next implementation slice.
3. State the slice you are about to implement.
4. List files likely to change.
5. Make the smallest useful change.
6. Add or update tests.
7. Run checks.
8. Update docs if needed.
9. Summarize exactly what changed.

## Scope control

If you discover that the plan is wrong or incomplete:

- Stop broad implementation.
- Explain the issue.
- Update `docs/01-plan.md` or recommend running `/architecture` or `/data-model`.
- Ask for confirmation before continuing if the change is significant.

## Output expectations

At the end, report:

```md
## Implementation Summary

### Implemented Slice

### Files Changed

### Tests / Checks Run

### Result

### Deviations From Plan

### Next Recommended Slice
```

## Definition of done

Implementation is done only when:

- The selected slice works.
- Tests/checks were run or limitations were explained.
- Documentation is not stale.
- No extra unplanned scope was added.
