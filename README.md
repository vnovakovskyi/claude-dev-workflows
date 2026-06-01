# Claude Dev Workflows

Reusable personal workflow skills for Claude Code.

Main line:

```text
research → plan → implement
```

Optional manual skills:

```text
architecture
data-model
```

Use `architecture` or `data-model` whenever needed:

- After research, before planning.
- Inside an existing service to document/review current architecture.
- Inside an existing service to review or redesign the data model.
- Before a migration/refactoring task.

## How the workflow keeps Claude from coding too early

This repo uses a **soft, conversational gate** — no hook, no marker files in the
normal flow. The discipline lives in the skills themselves:

- `plan` produces a **phased plan** in `docs/01-plan.md`. Each phase has its own
  **Automated** and **Manual** success-criteria checkboxes, plus an explicit
  "Out of Scope". `plan` never writes code — it ends by asking you to review and
  then run `/implement`.
- `implement` does **one phase at a time**. It implements the phase, runs that
  phase's automated checks, ticks the `- [x]` boxes in the plan, and then
  **pauses and waits for you** to confirm manual verification before the next
  phase.

So approval is a normal conversational act (you choose to run `/implement`, and
you confirm between phases) — there is no approval file to create, forget, or
delete. Progress is tracked by the checkboxes inside `docs/01-plan.md`, so work
is resumable: re-running `/implement` picks up at the first unchecked phase.

> If you also want **hard** enforcement — where Claude is *physically* blocked
> from editing code until you approve — there is an optional hook. See
> [Optional: hard enforcement gate](#optional-hard-enforcement-gate).

## Requirements

The default install has no special requirements (just `bash`).

The optional hard gate (`--with-gate`) additionally needs:

- `python3` — to safely edit `~/.claude/settings.json`.
- `jq` — the hook uses it to parse its input. If `jq` is missing the hook fails
  open (allows everything, no enforcement). On macOS: `brew install jq`.

## Install

From this repository:

```bash
chmod +x install.sh uninstall.sh hooks/gate.sh
./install.sh
```

This symlinks the skills into `~/.claude/skills/`. It does **not** touch
`~/.claude/settings.json` and installs no hook.

> **Note:** the skills are installed as *symlinks back into this repository*. If
> you move, rename, or delete `claude-dev-workflows`, the skills will stop
> working. Keep the repo in a stable location (and re-run `./install.sh` if you
> move it).

## Installed skills

```text
/research
/plan
/implement
/architecture
/data-model
```

## Usage

Run Claude Code inside your project and use the main workflow:

```text
/research <idea, feature, migration, or problem>
/plan <what should be planned>
```

Optionally run, when useful (e.g. after research, before planning):

```text
/architecture <what architecture should be analyzed or designed>
/data-model <what data model should be analyzed or designed>
```

Review the plan in `docs/01-plan.md`, then implement phase by phase:

```text
/implement <optional: a specific phase>
```

`/implement` will implement one phase, run its checks, tick its boxes, and pause
for your manual verification. Tell it to continue when you're ready for the next
phase.

## Generated docs

The skills write these files:

```text
docs/00-research.md
docs/01-plan.md
docs/02-architecture.md
docs/03-data-model.md
```

`architecture` and `data-model` are optional. The main line only requires:

```text
docs/00-research.md
docs/01-plan.md
```

> The numbers (`00`–`03`) indicate **document type**, not execution order. You can
> run `architecture` or `data-model` after research and before planning even
> though their files are numbered after `01-plan.md`.

## Optional: hard enforcement gate

If you want Claude to be *physically* unable to edit code before you approve
(rather than relying on the skills' instructions), install the optional hook:

```bash
./install.sh --with-gate
```

This symlinks `hooks/gate.sh` into `~/.claude/hooks/` and adds a `PreToolUse`
hook (matcher `Write|Edit|MultiEdit|NotebookEdit|Bash`) to
`~/.claude/settings.json`. Existing settings are preserved: the installer backs
up `settings.json` to `settings.json.bak`, then appends the hook only if it
isn't already registered, so it is safe to run multiple times.

The gate is **opt-in per project** via a marker file. In a project's root:

```bash
touch .claude-phase-gate          # enable the gate for this project
```

While the gate is active and implementation is **not** approved, Claude may edit
docs/planning files but source-code edits are blocked. To approve:

```bash
touch .claude-phase-approved      # approve implementation (run this yourself)
```

Approval requires `docs/00-research.md` and `docs/01-plan.md` to exist plus the
`.claude-phase-approved` file. Do **not** let Claude create `.claude-phase-approved`
itself — that would defeat the gate (the gate blocks Claude from creating it).

### Gate behavior

Allowed before approval: `docs/**`, `CLAUDE.md`, `.claude/**`, `README.*`.

Blocked before approval: source/config/build/migration file edits, and
file-mutating shell commands. The Bash check is a **soft backstop** (not a full
shell parser):

- Blocks: `rm rmdir mv cp touch mkdir chmod chown ln dd tee truncate`, `sed -i`,
  `perl -pi`, and output redirection into a file (`> file`, `>> file`, etc.).
- Allows: read-only redirections (`2>&1`, `2>/dev/null`) and interpreters/build
  tools (`python`, `node`, `npm`, `make`, …), so research isn't obstructed.

If it ever blocks something harmless, approve implementation or temporarily
`rm .claude-phase-gate`.

### Caveat: approval is a persistent flag

`.claude-phase-approved` stays until you remove it, so if you re-run `/plan`
after approving, the *old* approval is still in effect. With the gate, remove the
file (`rm .claude-phase-approved`) when you re-plan. The soft (default) workflow
avoids this entirely because it has no approval file.

### Version control of the gate's marker files

The marker files live in each working project, so committing them is a
per-project decision (made in that project's `.gitignore`):

- **`.claude-phase-approved` — recommended to gitignore.** It is transient, local,
  per-developer state. If committed, every clone is permanently "approved".
- **`.claude-phase-gate` — your choice:** commit it to share the gate with the
  team, or gitignore it to keep the gate personal. For anyone without the hook
  installed, the marker is an inert empty file and changes nothing.

Suggested per-project `.gitignore`:

```gitignore
# Local implementation approval — never commit (would disable the gate on clone)
.claude-phase-approved

# Phase-gate opt-in: uncomment to keep it personal/local instead of shared.
# .claude-phase-gate
```

## Uninstall

Run the uninstaller from this repository:

```bash
./uninstall.sh
```

It removes the skill symlinks (only if they point back into this repo) and, if
the optional gate was installed, removes the `gate.sh` symlink and its
`PreToolUse` entry from `~/.claude/settings.json` (backing the file up to
`settings.json.bak` first), leaving all your other settings intact. Per-project
marker files are left untouched.

## Note about `/plan`

`plan` is a short and convenient name, but it is also generic.

If it conflicts with an existing Claude Code command or your own setup, rename
the skill folder and frontmatter `name` to something more specific, for example:

```text
mvp-plan
product-plan
phase-plan
```
