#!/usr/bin/env bash
set -Eeuo pipefail

trap 'printf "%s\n" "Claude workflow setup failed; files already copied remain in place." >&2' ERR

KIT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$KIT")"
HOME_KIT="${HOME:?HOME must be set}/.workflow-kit"
CLAUDE="$HOME/.claude"
SKILLS=(workflow-manager requirements-authoring requirements-diagrams test-first-coding gate-verification git-workflow grilling)
DO_CLI=0

fail() {
  printf 'Claude workflow setup: %s\n' "$1" >&2
  exit 1
}

for arg in "$@"; do
  case "$arg" in
    --install-claude-cli) DO_CLI=1 ;;
    -h|--help) echo "Usage: install-claude.sh [--install-claude-cli]"; exit 0 ;;
    *) fail "Unknown option: $arg" ;;
  esac
done

copy_tree() {
  local source_root="$1"
  local destination_root="$2"
  local source relative target

  [[ -d "$source_root" ]] || fail "Missing source directory: $source_root"
  mkdir -p -- "$destination_root"
  while IFS= read -r -d '' source; do
    relative=${source#"$source_root"/}
    target="$destination_root/$relative"
    if [[ -L "$source" ]]; then
      fail "Symbolic links are not supported: $source"
    elif [[ -d "$source" ]]; then
      if [[ -L "$target" ]] || { [[ -e "$target" ]] && [[ ! -d "$target" ]]; }; then
        fail "Destination conflicts with an existing item: $target"
      fi
      mkdir -p -- "$target"
    elif [[ -e "$target" || -L "$target" ]]; then
      printf 'skip (exists): %s\n' "$target"
    else
      cp -- "$source" "$target"
      printf 'created: %s\n' "$target"
    fi
  done < <(find "$source_root" -mindepth 1 -print0)
}

echo "Shared helpers -> $HOME_KIT"
copy_tree "$KIT/templates" "$HOME_KIT/templates"
copy_tree "$KIT/hooks" "$HOME_KIT/hooks"
if [[ -e "$HOME_KIT/scaffold-project.sh" || -L "$HOME_KIT/scaffold-project.sh" ]]; then
  printf 'skip (exists): %s\n' "$HOME_KIT/scaffold-project.sh"
else
  cp -- "$KIT/scaffold-project.sh" "$HOME_KIT/scaffold-project.sh"
  printf 'created: %s\n' "$HOME_KIT/scaffold-project.sh"
fi

echo "Claude Code layer -> $CLAUDE"
copy_tree "$KIT/claude/agents" "$CLAUDE/agents"
copy_tree "$KIT/claude/commands" "$CLAUDE/commands"
for skill in "${SKILLS[@]}"; do
  copy_tree "$ROOT/skills/$skill" "$CLAUDE/skills/$skill"
done

touch "$CLAUDE/CLAUDE.md"
tmp="$(mktemp)"
awk '/<!-- workflow-kit:start -->/{skip=1} !skip{print} /<!-- workflow-kit:end -->/{skip=0}' "$CLAUDE/CLAUDE.md" > "$tmp"
{ cat "$tmp"; [[ ! -s "$tmp" ]] || echo; cat "$KIT/claude/CLAUDE.block.md"; } > "$CLAUDE/CLAUDE.md"
rm -f -- "$tmp"

if [[ ! -e "$CLAUDE/settings.json" && ! -L "$CLAUDE/settings.json" ]]; then
  cp -- "$KIT/claude/settings.hook.json" "$CLAUDE/settings.json"
  echo "Created $CLAUDE/settings.json with the SessionStart hook."
elif grep -q 'session-start.sh' "$CLAUDE/settings.json"; then
  echo "SessionStart hook already present in $CLAUDE/settings.json."
else
  echo "NOTE: $CLAUDE/settings.json already exists. Merge the hook from $KIT/claude/settings.hook.json by hand."
fi

if [[ "$DO_CLI" -eq 1 ]]; then
  if command -v claude >/dev/null 2>&1; then
    echo "claude CLI already installed."
  elif command -v npm >/dev/null 2>&1; then
    npm install -g @anthropic-ai/claude-code
  else
    fail "npm not found. Install Node.js first, then re-run with --install-claude-cli."
  fi
fi

echo "Done. In a project repo run: bash ~/.workflow-kit/scaffold-project.sh --claude"
