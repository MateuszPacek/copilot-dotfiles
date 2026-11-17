#!/usr/bin/env bash
if [[ -n "${ANTHROPIC_API_KEY:-}" || -n "${ANTHROPIC_AUTH_TOKEN:-}" ]]; then
  echo "WARNING: an Anthropic API credential is set in this environment. Claude Code may bill the API instead of the Claude Pro subscription. Tell the user immediately and ask them to unset it before continuing."
fi
if [[ -f workflow/state.md ]]; then
  echo "--- workflow/state.md ---"
  cat workflow/state.md
fi
