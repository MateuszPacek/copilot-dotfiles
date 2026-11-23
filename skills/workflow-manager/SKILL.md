---
name: workflow-manager
description: Workflow manager for the business requirements, product requirements, technical requirements and code chain with test gates, stacked branches and PRs. Use when the user runs /flow, starts a feature, asks for status, the next layer, a gate, a PR, a failure issue or an automated fix, or when the repo contains an workflow/ folder.
---

# Workflow manager

The user is the orchestrator. Do one action per request, report, and stop. Never chain actions on your own.

## Layers

| Layer | Files | Branch | PR base | Gate before it merges up |
|---|---|---|---|---|
| BR | docs/requirements/br/, docs/requirements/kpi/ | feat/SLUG/br | default branch | KPI definition: every BR has measurable pass criteria |
| PRD | docs/requirements/prd/ | feat/SLUG/prd | feat/SLUG/br | functional tests of PRD acceptance criteria pass |
| TR | docs/requirements/tr/ | feat/SLUG/tr | feat/SLUG/prd | integration tests of TR acceptance criteria pass |
| Code | source and tests | feat/SLUG/code | feat/SLUG/tr | unit tests pass |

Branches are stacked: br from the default branch, prd from br, tr from prd, code from tr. Work goes top-down. PRs merge bottom-up: code to tr, tr to prd, prd to br, br to the default branch. The user merges; you never do.

## Actions

Invoked as `/flow <action> [argument]`. No action means `status`.

- init: if workflow/config.md is missing, run `bash ~/.workflow-kit/scaffold-project.sh` (if that path does not exist, use `bash ~/.copilot/workflow-kit/scaffold-project.sh`). It never overwrites files. Then help the user fill workflow/config.md by asking, not guessing.
- status: read only workflow/state.md. Report feature, layer, gates, open issues and the next suggested action.
- start FEATURE NAME: confirm the slug with the user, require a clean git tree, create feat/SLUG/br from the default branch, fill workflow/state.md.
- draft br, prd or tr: skill requirements-authoring. Create the layer branch from its parent branch first if it does not exist.
- draft code: skill test-first-coding (branch feat/SLUG/code from feat/SLUG/tr).
- gate LAYER: skill gate-verification, run by the verifier in a fresh context.
- pr LAYER, issue, fix ISSUE_NUMBER: skill git-workflow.

## Rules

1. Think first. State assumptions. If anything is unclear, ask before acting; do not guess. A blank field in workflow/config.md is a question for the user: ask, then record the answer.
2. Keep it simple and surgical: the smallest change that meets the acceptance criteria, touching only what the current layer needs. Report unrelated problems; do not fix them.
3. Goal-driven: before work, state the checkable success criteria. After work, show evidence (command output, test results), not claims.
4. Independent check: whoever writes a layer never grades it. Gates run in the verifier.
5. Context discipline: workflow/state.md is the memory. Read it first and update it after every action. Read only the current layer, its parent and the glossary. One layer per chat. Keep replies short.
6. Language: use docs/glossary.md terms exactly. Propose new terms; add them only after the user agrees.
7. Safety: never push to the default branch, merge, force-push, rewrite history or delete branches. Ask before every push, PR or issue. Never write secrets into files.
8. If the session warns about an Anthropic API credential in the environment, tell the user first and wait for their answer.
