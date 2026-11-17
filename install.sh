#!/usr/bin/env bash

set -Eeuo pipefail

trap 'printf "%s\n" "Installation failed; any files already copied remain in place." >&2' ERR

source_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

destination="${HOME:?HOME must be set}/.copilot"

personal="$source_root/instructions/copilot personalization.instructions.md"

# Folders copied into ~/.copilot. prompts and workflow-kit hold the /flow prompt and the workflow kit helpers.
install_dirs=(agents instructions skills workflows prompts workflow-kit)

fail() {
  printf 'Codespaces setup: %s\n' "$1" >&2
  exit 1
}

for directory in "${install_dirs[@]}"; do
  [[ -d "$source_root/$directory" ]] || fail "Missing source directory: $directory"
done

for file in "$personal" "$source_root/glossary.md" "$source_root/workflow-guide.md" \
  "$source_root/skills/asd-ste100/SKILL.md"; do
  [[ -f "$file" ]] || fail "Missing source file: $file"
done

awk '
NR == 1 { line = $0; sub(/\r$/, "", line); if (line != "---") exit 1; next }
{ line = $0; sub(/\r$/, "", line); if (line == "---") { found = 1; exit } }
END { if (!found) exit 1 }
' "$personal" || fail "Personal instructions need a complete frontmatter header."

shopt -s dotglob globstar nullglob

directories=("$destination")
sources=()
targets=()

for directory in "${install_dirs[@]}"; do
  directories+=("$destination/$directory")
  for source in "$source_root/$directory"/**; do
    relative=${source#"$source_root/"}
    [[ "$relative" != */.git && "$relative" != */.git/* ]] || continue
    [[ "$source" != "$personal" ]] || continue
    [[ ! -L "$source" ]] || fail "Symbolic links are not supported: $source"
    if [[ -d "$source" ]]; then
      directories+=("$destination/$relative")
    elif [[ -f "$source" ]]; then
      sources+=("$source")
      targets+=("$destination/$relative")
    else
      fail "Unsupported source item: $source"
    fi
  done
done

for file in glossary.md workflow-guide.md; do
  sources+=("$source_root/$file")
  targets+=("$destination/$file")
done

targets+=("$destination/copilot-instructions.md")

for directory in "${directories[@]}"; do
  if [[ -L "$directory" ]] || { [[ -e "$directory" ]] && [[ ! -d "$directory" ]]; }; then
    fail "Destination directory conflicts with an existing item: $directory"
  fi
done

for target in "${targets[@]}"; do
  if [[ -e "$target" || -L "$target" ]]; then
    fail "Destination already exists: $target"
  fi
done

for directory in "${directories[@]}"; do
  mkdir -p -- "$directory"
done

for ((index = 0; index < ${#sources[@]}; index++)); do
  cp -- "${sources[index]}" "${targets[index]}"
done

awk '
NR == 1 { header = 1; next }
header { line = $0; sub(/\r$/, "", line); if (line == "---") header = 0; next }
{ print }
' "$personal" > "$destination/copilot-instructions.md"

printf '%s\n' "Personal Copilot files installed in $destination."
printf '%s\n' "Start a new Copilot session and verify personal and project customizations."
