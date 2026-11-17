#!/usr/bin/env bash
# Claude Code SessionStart hook. Its output is added to the session context.
# 1) Warns when an Anthropic API credential is set (it could bill the API instead of the Claude Pro plan).
# 2) Loads workflow/state.md when the current folder is a workflow project.
if [ -n "${ANTHROPIC_API_KEY:-}" ] || [ -n "${ANTHROPIC_AUTH_TOKEN:-}" ]; then
  echo "WARNING: an Anthropic API credential is set in this environment. Claude Code may bill the API instead of the Claude Pro subscription. Tell the user immediately and ask them to unset it before continuing."
fi
if [ -f workflow/state.md ]; then
  echo "--- workflow/state.md ---"
  cat workflow/state.md
fi
exit 0
