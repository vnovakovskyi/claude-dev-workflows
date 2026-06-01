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

## Requirements

- The installer (and uninstaller) needs `python3`.
- The phase-gate hook needs `jq`. **`jq` is a hard requirement for enforcement:**
  if `jq` is missing, the hook fails open silently (it allows every tool call and
  does *not* enforce the gate). The installer warns you once if `jq` is absent.

On macOS:

```bash
brew install jq
```

## Install

From this repository:

```bash
chmod +x install.sh uninstall.sh hooks/gate.sh
./install.sh
```

The installer symlinks skills into:

```text
~/.claude/skills/
```

And symlinks the hook into:

```text
~/.claude/hooks/gate.sh
```

It also adds a `PreToolUse` hook (matcher `Write|Edit|MultiEdit|NotebookEdit|Bash`) to:

```text
~/.claude/settings.json
```

Existing settings are preserved: the installer backs up `settings.json` to
`settings.json.bak`, then appends the hook only if it is not already registered,
so it is safe to run multiple times.

> **Note:** the skills and hook are installed as *symlinks back into this repository*.
> If you move, rename, or delete `claude-dev-workflows`, the skills and the gate will
> silently stop working. Keep the repo in a stable location (and re-run `./install.sh`
> if you move it).

## Installed skills

```text
/research
/plan
/implement
/architecture
/data-model
```

## Recommended usage in a new project

Enable strict phase gating:

```bash
touch .claude-phase-gate
```

Then run Claude Code inside the project:

```bash
claude
```

Use the main workflow:

```text
/research <idea, feature, migration, or problem>
/plan <what should be planned>
```

Optionally run:

```text
/architecture <what architecture should be analyzed or designed>
/data-model <what data model should be analyzed or designed>
```

When you personally approve implementation, run this manually in your terminal:

```bash
touch .claude-phase-approved
```

Then:

```text
/implement <next slice from the plan>
```

## Why manual approval?

The approval file is intentionally manual.

If Claude can create the approval file by itself, the phase gate becomes weaker. The intended flow is:

1. Claude researches.
2. Claude plans.
3. You review the plan.
4. You approve implementation by creating `.claude-phase-approved`.
5. Claude can code.

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

> The numbers (`00`–`03`) indicate **document type**, not execution order. You can run
> `architecture` or `data-model` after research and before planning even though their
> files are numbered after `01-plan.md`.

## Phase gate behavior

If `.claude-phase-gate` exists and `.claude-phase-approved` does not exist, the hook allows planning/documentation edits but blocks source-code edits.

Allowed before approval:

```text
docs/**
CLAUDE.md
.claude/**
README.md
```

Blocked before approval:

```text
source files
configuration files
build files
migration files
file-mutating shell commands
```

The Bash check is intentionally a **soft backstop**, not a full shell parser. It blocks:

- File-mutating commands: `rm rmdir mv cp touch mkdir chmod chown ln dd tee truncate`,
  `sed -i`, `perl -pi`.
- Output redirection into a file (`> file`, `>> file`, `2> file`, `&> file`).

It deliberately does **not** block:

- Read-only redirections such as `2>&1`, `2>/dev/null`, `> /dev/null` — so commands
  like `npm test 2>&1` are not blocked.
- Interpreters and build tools (`python`, `node`, `npm`, `make`, …) — these are useful
  during research/inspection, and the skills' own rules already forbid writing code in
  the research/plan phases.

Because it is heuristic, it can be bypassed (e.g. a script that writes files from inside
an interpreter) and it can occasionally over-block. If it blocks something harmless,
either approve implementation or temporarily remove `.claude-phase-gate`.

## Uninstall

Run the uninstaller from this repository:

```bash
./uninstall.sh
```

It removes the skill and hook symlinks (only if they point back into this repo),
removes the `gate.sh` `PreToolUse` entry from `~/.claude/settings.json` (backing the
file up to `settings.json.bak` first), and leaves all your other settings intact.
Per-project marker files (`.claude-phase-gate` / `.claude-phase-approved`) are left
untouched.

If you prefer to do it by hand:

```bash
rm -f ~/.claude/hooks/gate.sh
rm -f ~/.claude/skills/research \
      ~/.claude/skills/plan \
      ~/.claude/skills/implement \
      ~/.claude/skills/architecture \
      ~/.claude/skills/data-model
```

Then remove the `gate.sh` hook entry from `~/.claude/settings.json`.

## Note about `/plan`

`plan` is a short and convenient name, but it is also generic.

If it conflicts with an existing Claude Code command or your own setup, rename the skill folder and frontmatter name to something more specific, for example:

```text
mvp-plan
product-plan
phase-plan
```
