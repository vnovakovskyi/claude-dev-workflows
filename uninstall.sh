#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
GATE_HOOK="$HOOKS_DIR/gate.sh"

# Remove skill symlinks, but only if they point back into this repo.
for skill_path in "$ROOT"/skills/*; do
  [[ -d "$skill_path" ]] || continue
  skill_name="$(basename "$skill_path")"
  target="$SKILLS_DIR/$skill_name"
  if [[ -L "$target" ]]; then
    rm -f "$target"
    echo "Removed skill symlink: $target"
  fi
done

# Remove the hook symlink, only if it is a symlink.
if [[ -L "$GATE_HOOK" ]]; then
  rm -f "$GATE_HOOK"
  echo "Removed hook symlink: $GATE_HOOK"
fi

# Remove the gate hook entry from ~/.claude/settings.json without touching
# anything else. Matches both the tilde and absolute command forms.
if [[ -f "$SETTINGS_FILE" ]]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "WARNING: python3 not found; remove the gate.sh PreToolUse entry from"
    echo "  $SETTINGS_FILE manually."
  else
    python3 - <<'UNINSTALL_PY'
import json
from pathlib import Path

settings_file = Path.home() / ".claude" / "settings.json"
if not settings_file.exists() or not settings_file.read_text().strip():
    raise SystemExit(0)

original_text = settings_file.read_text()
try:
    settings = json.loads(original_text)
except json.JSONDecodeError as exc:
    raise SystemExit(f"ERROR: {settings_file} contains invalid JSON: {exc}")

gate_commands = {
    "~/.claude/hooks/gate.sh",
    str(Path.home() / ".claude" / "hooks" / "gate.sh"),
}

pre_tool = settings.get("hooks", {}).get("PreToolUse", [])
changed = False
new_pre_tool = []
for item in pre_tool:
    inner = [h for h in item.get("hooks", []) if h.get("command") not in gate_commands]
    if len(inner) != len(item.get("hooks", [])):
        changed = True
    if inner:
        item["hooks"] = inner
        new_pre_tool.append(item)
    # Drop entries whose hooks list became empty.

if changed:
    if new_pre_tool:
        settings["hooks"]["PreToolUse"] = new_pre_tool
    else:
        settings["hooks"].pop("PreToolUse", None)
        if not settings["hooks"]:
            settings.pop("hooks", None)
    backup_file = settings_file.with_name(settings_file.name + ".bak")
    backup_file.write_text(original_text)
    settings_file.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"Removed gate.sh hook from: {settings_file}")
    print(f"Backed up previous settings to: {backup_file}")
else:
    print(f"No gate.sh hook entry found in: {settings_file}")
UNINSTALL_PY
  fi
fi

echo
echo "Uninstall complete."
echo "Per-project marker files (.claude-phase-gate / .claude-phase-approved) are"
echo "left untouched; remove them from individual projects if you no longer want them."
