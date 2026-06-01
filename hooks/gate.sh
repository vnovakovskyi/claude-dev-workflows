#!/usr/bin/env bash

# Claude Code phase gate.
#
# This hook is intentionally opt-in per project.
# It enforces the workflow only if the current project contains:
#
#   .claude-phase-gate
#
# While the gate is active and implementation is not approved, Claude may edit docs,
# but source-code edits are blocked.
#
# To approve implementation manually from your terminal, run:
#
#   touch .claude-phase-approved
#
# Do not ask Claude to create the approval file for you if you want a real gate.

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  # jq is required to parse the hook payload. Without it we cannot enforce the
  # gate, so fail open *silently* rather than printing a warning on every tool
  # call. Install jq to enable enforcement (the installer warns about this once).
  exit 0
fi

INPUT="$(cat)"

# Use the cwd supplied by Claude Code if present.
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // "."')"
cd "$CWD" 2>/dev/null || true

# No marker file = no phase gate in this project.
if [[ ! -f ".claude-phase-gate" ]]; then
  exit 0
fi

TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // ""')"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // .tool_input.notebook_path // ""')"
COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // ""')"

approved() {
  [[ -f "docs/00-research.md" && -f "docs/01-plan.md" && -f ".claude-phase-approved" ]]
}

is_allowed_planning_path() {
  local path="$1"

  # Empty path means this tool call is not file-specific.
  [[ -z "$path" ]] && return 1

  # Normalize leading ./
  path="${path#./}"

  case "$path" in
    docs/*) return 0 ;;
    CLAUDE.md) return 0 ;;
    .claude/*) return 0 ;;
    .claude-phase-gate) return 0 ;;
    README.md) return 0 ;;
    README.*) return 0 ;;
    *) return 1 ;;
  esac
}

# Returns 0 if the command appears to redirect output into a real file.
# Harmless redirections are ignored so read-only commands are not blocked:
#   - file-descriptor duplication, e.g. 2>&1, 1>&2, 2>&-
#   - redirection to the null/standard devices, e.g. >/dev/null, 2>/dev/null
# After scrubbing those, any remaining > / >> at a token boundary is treated
# as a write to a file.
redirects_to_file() {
  local cmd="$1"
  local scrubbed
  scrubbed="$(printf '%s' "$cmd" \
    | sed -E 's#[0-9]*>&[0-9-]+##g' \
    | sed -E 's#([0-9]*|&)>>?[[:space:]]*/dev/(null|stderr|stdout)##g')"
  printf '%s' "$scrubbed" | grep -Eq '(^|[[:space:]])[0-9]*&?>>?'
}

looks_like_writing_bash() {
  local cmd="$1"

  # Intentionally conservative: a soft backstop, not a full shell parser.
  # It blocks obvious file-mutating commands and stdout redirection to a file.
  # It deliberately does NOT block interpreters or build tools (python, node,
  # npm, make, ...) or read-only redirections, so research stays unobstructed.
  local mutators='(^|[[:space:];|&])(rm|rmdir|mv|cp|touch|mkdir|chmod|chown|ln|dd|tee|truncate)([[:space:]]|$)'
  local sed_inplace='(^|[[:space:]])sed([[:space:]][^|]*)?[[:space:]]-i([[:space:]=]|$)'
  local perl_inplace='(^|[[:space:]])perl([[:space:]][^|]*)?[[:space:]]-[A-Za-z]*i'

  [[ "$cmd" =~ $mutators ]] && return 0
  [[ "$cmd" =~ $sed_inplace ]] && return 0
  [[ "$cmd" =~ $perl_inplace ]] && return 0
  redirects_to_file "$cmd" && return 0

  return 1
}

if approved; then
  exit 0
fi

case "$TOOL_NAME" in
  Write|Edit|MultiEdit|NotebookEdit)
    if is_allowed_planning_path "$FILE_PATH"; then
      exit 0
    fi

    echo "Phase gate blocked a source-code edit before implementation approval." >&2
    echo "Current phase allows docs/planning changes only." >&2
    echo "Required before coding:" >&2
    echo "  1. docs/00-research.md must exist" >&2
    echo "  2. docs/01-plan.md must exist" >&2
    echo "  3. User must manually run: touch .claude-phase-approved" >&2
    echo "Blocked path: ${FILE_PATH:-unknown}" >&2
    exit 2
    ;;

  Bash)
    if looks_like_writing_bash "$COMMAND"; then
      echo "Phase gate blocked a shell command that may modify files before implementation approval." >&2
      echo "Before coding or file-changing shell commands are allowed, complete research + plan and manually run:" >&2
      echo "  touch .claude-phase-approved" >&2
      echo "Blocked command: $COMMAND" >&2
      exit 2
    fi
    exit 0
    ;;

  *)
    exit 0
    ;;
esac
