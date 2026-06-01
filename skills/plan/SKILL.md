---
name: plan
description: Main workflow phase 2. Turn research into a concrete product/technical plan and MVP delivery sequence. Produces docs/01-plan.md. No implementation.
argument-hint: <what should be planned>
disable-model-invocation: true
---

# Phase: Plan

You are running the **Plan** phase for the user's request.

User request / topic:

`$ARGUMENTS`

## Purpose

Convert research into a clear, scoped, executable plan before coding starts.

This is the main line after `research`.

Optional supporting phases may exist:

- `architecture` — if architecture decisions are needed.
- `data-model` — if domain model, persistence, schema, or data flow decisions are important.

If `docs/02-architecture.md` or `docs/03-data-model.md` exists, read and incorporate them. Do not require them unless the research shows they are necessary.

## Hard rules

- Do **not** write implementation code.
- Do **not** create database migrations.
- Do **not** modify production files.
- Do **not** expand the scope beyond what research supports.
- You may create or update files under `docs/`.
- Main output must be `docs/01-plan.md`.

## Required inputs

Before planning, check whether these files exist:

- `docs/00-research.md` — required for serious planning.
- `docs/02-architecture.md` — optional.
- `docs/03-data-model.md` — optional.

If `docs/00-research.md` is missing, do one of these:

1. Ask the user to run `/research` first, or
2. Create a lightweight research section inside the plan only if the user explicitly wants a fast/rough plan.

## Planning principles

The plan must be:

- Small enough to implement.
- Clear enough to test.
- Explicit about what is **in scope** and **out of scope**.
- Split into milestones or implementation slices.
- Honest about risks and unknowns.
- Useful for a real developer, not just a high-level product note.

## Output file

Create or update:

`docs/01-plan.md`

Use this structure:

````md
# Plan

## 1. Goal

What we are trying to achieve.

## 2. Background

Short summary based on research.

## 3. Scope

### In Scope

What will be included.

### Out of Scope

What will not be included now.

## 4. Success Criteria

How we know the work is successful.

Include product, technical, operational, and quality criteria where relevant.

## 5. User Stories / Use Cases

Describe the main flows or engineering scenarios.

## 6. Functional Requirements

Numbered list.

## 7. Non-Functional Requirements

Performance, security, reliability, observability, maintainability, cost, scalability, compliance, etc.

## 8. Dependencies

Internal and external dependencies.

## 9. Risks and Mitigations

Risk → impact → mitigation.

## 10. Implementation Slices

Break work into small slices.

Each slice should include:
- Purpose
- Files/modules likely affected
- Expected result
- Tests/checks

## 11. Testing Strategy

Unit, integration, e2e, contract, manual checks, observability checks.

## 12. Rollout / Migration Strategy

Only if relevant.

## 13. Documentation Updates

What documentation must be created or updated.

## 14. Open Questions

Questions that remain unresolved.

## 15. Implementation Approval

Implementation is not approved yet.

To enable coding when the phase gate is active, the user must manually run:

```bash
touch .claude-phase-approved
```

Do not create this file yourself.
````

## Completion criteria

Planning is complete only when:

- `docs/01-plan.md` exists.
- Scope is explicit.
- Implementation slices are listed.
- Tests/checks are listed.
- The next implementation step is obvious.

At the end of your response, summarize:

1. What plan you created/updated.
2. Whether architecture or data-model analysis is recommended before implementation.
3. What the user must approve before coding starts.
