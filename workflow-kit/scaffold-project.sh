#!/usr/bin/env bash
set -Eeuo pipefail

KIT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SRC="$KIT/templates"
DO_CLAUDE=0

for arg in "$@"; do
  case "$arg" in
    --claude) DO_CLAUDE=1 ;;
    -h|--help) echo "Usage: scaffold-project.sh [--claude]"; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$arg" >&2; exit 1 ;;
  esac
done

if [[ ! -d "$SRC" ]]; then
  printf 'Templates not found at %s.\n' "$SRC" >&2
  exit 1
fi
if [[ ! -e .git ]]; then
  echo "Warning: no .git here. Run this from the repo root." >&2
fi

while IFS= read -r -d '' source; do
  relative=${source#"$SRC"/}
  if [[ -e "$relative" || -L "$relative" ]]; then
    printf 'skip (exists): %s\n' "$relative"
  else
    mkdir -p -- "$(dirname -- "$relative")"
    cp -- "$source" "$relative"
    printf 'created: %s\n' "$relative"
  fi
done < <(find "$SRC" -type f -print0)

mkdir -p workflow/gates

if [[ "$DO_CLAUDE" -eq 1 ]]; then
  if [[ -e .claude/settings.json || -L .claude/settings.json ]]; then
    echo 'skip (exists): .claude/settings.json. To select the Claude workflow agent, configure "agent": "orchestrator" after reviewing your settings.'
  else
    mkdir -p .claude
    printf '{\n  "agent": "orchestrator"\n}\n' > .claude/settings.json
    echo 'created: .claude/settings.json (agent: orchestrator)'
  fi
fi

echo "Done. Fill in workflow/config.md, then run /flow start <feature name>."
