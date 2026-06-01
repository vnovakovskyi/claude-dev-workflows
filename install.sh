#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
GATE_HOOK="$HOOKS_DIR/gate.sh"

mkdir -p "$SKILLS_DIR" "$HOOKS_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required for install.sh" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "WARNING: jq is not installed. The phase gate hook needs jq to enforce rules." >&2
  echo "On macOS, install it with: brew install jq" >&2
fi


install_symlink() {
  local source="$1"
  local target="$2"

  if [[ -e "$target" && ! -L "$target" ]]; then
    echo "ERROR: $target already exists and is not a symlink."
    echo "Move it manually or run with FORCE=1 to replace it."
    if [[ "${FORCE:-0}" == "1" ]]; then
      rm -rf "$target"
    else
      exit 1
    fi
  fi

  ln -sfn "$source" "$target"
}

for skill_path in "$ROOT"/skills/*; do
  [[ -d "$skill_path" ]] || continue
  skill_name="$(basename "$skill_path")"
  install_symlink "$skill_path" "$SKILLS_DIR/$skill_name"
  echo "Installed skill: /$skill_name"
done

install_symlink "$ROOT/hooks/gate.sh" "$GATE_HOOK"
chmod +x "$ROOT/hooks/gate.sh"
echo "Installed hook: $GATE_HOOK"

# Register the hook in ~/.claude/settings.json without overwriting other settings.
python3 - <<'INSTALLER_PY'
import json
from pathlib import Path

settings_file = Path.home() / ".claude" / "settings.json"
settings_file.parent.mkdir(parents=True, exist_ok=True)

if settings_file.exists() and settings_file.read_text().strip():
    original_text = settings_file.read_text()
    try:
        settings = json.loads(original_text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: {settings_file} contains invalid JSON: {exc}")
    # Back up the existing settings before we rewrite the file.
    backup_file = settings_file.with_name(settings_file.name + ".bak")
    backup_file.write_text(original_text)
    print(f"Backed up existing settings to: {backup_file}")
else:
    settings = {}

hooks = settings.setdefault("hooks", {})
pre_tool = hooks.setdefault("PreToolUse", [])

# Use the tilde form so it matches settings-snippet.json exactly and the
# duplicate check below never registers two copies of the same hook.
command = "~/.claude/hooks/gate.sh"
entry = {
    "matcher": "Write|Edit|MultiEdit|NotebookEdit|Bash",
    "hooks": [
        {
            "type": "command",
            "command": command,
        }
    ],
}

already_exists = any(
    hook.get("command") == command
    for item in pre_tool
    for hook in item.get("hooks", [])
)

if not already_exists:
    pre_tool.append(entry)

settings_file.write_text(json.dumps(settings, indent=2) + "\n")
print(f"Updated settings: {settings_file}")
INSTALLER_PY

echo
echo "Done."
echo
echo "Available skills:"
echo "  /research"
echo "  /plan"
echo "  /implement"
echo "  /architecture"
echo "  /data-model"
echo
echo "To enable strict phase gating in a project:"
echo "  touch .claude-phase-gate"
echo
echo "After research + plan are complete and you approve implementation:"
echo "  touch .claude-phase-approved"
