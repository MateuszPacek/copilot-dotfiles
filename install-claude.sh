#!/usr/bin/env bash
# Installs the Claude Code layer of the workflow kit into ~/.claude and the shared helpers into ~/.workflow-kit.
# The Copilot layer needs no installer: this repo already is the ~/.copilot folder. Safe to re-run.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../workflow-kit
ROOT="$(dirname "$KIT")"                               # repo root (skills live here)
HOME_KIT="$HOME/.workflow-kit"
CLAUDE="$HOME/.claude"
SKILLS=(workflow-manager requirements-authoring test-first-coding gate-verification git-workflow)
DO_CLI=0

for arg in "$@"; do
  case "$arg" in
    --install-claude-cli) DO_CLI=1 ;;
    -h|--help) echo "Usage: install-claude.sh [--install-claude-cli]"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

echo "Shared helpers -> $HOME_KIT"
mkdir -p "$HOME_KIT/hooks" "$HOME_KIT/templates"
cp -R "$KIT/templates/." "$HOME_KIT/templates/"
cp "$KIT/hooks/session-start.sh" "$HOME_KIT/hooks/session-start.sh"
cp "$KIT/scaffold-project.sh" "$HOME_KIT/scaffold-project.sh"
chmod +x "$HOME_KIT/hooks/session-start.sh" "$HOME_KIT/scaffold-project.sh"

echo "Claude Code layer -> $CLAUDE"
mkdir -p "$CLAUDE/agents" "$CLAUDE/commands" "$CLAUDE/skills"
cp -R "$KIT/claude/agents/." "$CLAUDE/agents/"
cp -R "$KIT/claude/commands/." "$CLAUDE/commands/"
for s in "${SKILLS[@]}"; do
  rm -rf "${CLAUDE:?}/skills/$s"
  cp -R "$ROOT/skills/$s" "$CLAUDE/skills/$s"
done

# Replace the kit's block in CLAUDE.md (or add it), leaving the rest of the file untouched.
touch "$CLAUDE/CLAUDE.md"
tmp="$(mktemp)"
awk '/<!-- workflow-kit:start -->/{skip=1} !skip{print} /<!-- workflow-kit:end -->/{skip=0}' "$CLAUDE/CLAUDE.md" > "$tmp"
{ cat "$tmp"; [ -s "$tmp" ] && echo; cat "$KIT/claude/CLAUDE.block.md"; } > "$CLAUDE/CLAUDE.md"
rm -f "$tmp"

if [ ! -f "$CLAUDE/settings.json" ]; then
  cp "$KIT/claude/settings.hook.json" "$CLAUDE/settings.json"
  echo "Created $CLAUDE/settings.json with the SessionStart hook."
elif grep -q 'session-start.sh' "$CLAUDE/settings.json"; then
  echo "SessionStart hook already present in $CLAUDE/settings.json."
else
  echo "NOTE: $CLAUDE/settings.json already exists. Merge the hook from $KIT/claude/settings.hook.json by hand."
fi

if [ "$DO_CLI" -eq 1 ]; then
  if command -v claude >/dev/null 2>&1; then
    echo "claude CLI already installed."
  elif command -v npm >/dev/null 2>&1; then
    npm install -g @anthropic-ai/claude-code
  else
    echo "npm not found. Install Node.js first, then re-run with --install-claude-cli." >&2
  fi
fi
echo "Done. In a project repo run: bash ~/.workflow-kit/scaffold-project.sh --claude"
