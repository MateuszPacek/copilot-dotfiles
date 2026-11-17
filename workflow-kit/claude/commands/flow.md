---
description: Workflow manager. Run one step - init, status, start, draft, gate, pr, issue or fix.
argument-hint: <action> [layer | feature name | issue number]
---

Use the workflow-manager skill. Run this action and then stop: $ARGUMENTS

If the action is empty, run status.
- draft br, prd or tr: follow requirements-authoring in the main conversation because the interview needs the user.
- draft code: follow test-first-coding in the main conversation.
- gate LAYER: delegate to the verifier subagent, relay its verdict, then ask before filing an issue.
- pr, issue, fix: follow git-workflow.
