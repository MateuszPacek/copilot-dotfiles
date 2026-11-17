#!/usr/bin/env bash
set -Eeuo pipefail
exec "$(dirname -- "$0")/workflow-kit/install-claude.sh" "$@"
