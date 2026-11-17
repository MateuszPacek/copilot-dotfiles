# Software workflow

Read for software work. Shared approval, privacy, glossary, and reporting
controls remain in the personal instructions; do not copy them into each role.

## Roles

| Work | Agent | Output |
|---|---|---|
| Coordination | `Default` | One `/flow` action at a time; status, branches and handoffs |
| Requirements | `requirements-author` | Business, product and technical requirements, models where suitable, and KPI definitions |
| Coding | `coder` | Test-first implementation of approved technical requirements |
| Gates | `verifier` | Independent verification and gate report for the selected layer |

Use the specialist handoffs for requirements, coding and gates. A gate must be
independent of the authoring work; run the Copilot verifier in a fresh chat.
Claude Code runs requirements and coding in the main conversation and the
verifier as a subagent. Do not claim that a visible agent selection changed.

## Requirements and gates

The workflow is business requirements (BR) -> product requirements (PRD) ->
technical requirements (TR) -> code. Requirements work is interview-first and
uses `requirements-authoring` and the existing `req-creator` guidance. Product
models describe behavior independently of implementation choices where a
suitable model can be produced. Technical work includes software design and a
technical specification linked to product requirements and models.

Use stable IDs (`BR-001`, `PRD-001`, `TR-001`, `KPI-001`) and never reuse a
retired ID. Requirements link to their parents and children. Acceptance
criteria must be measurable. Tests identify the requirement they verify;
uncovered requirements fail the gate.

| Layer | Gate |
|---|---|
| BR | Each business requirement links to a KPI with a target, measurable pass threshold and data source |
| PRD | Functional tests pass and cover PRD IDs |
| TR | Integration tests pass and cover TR IDs |
| Code | Unit tests pass and cover TR IDs; zero collected tests is a failure |

The verifier checks only the selected layer, records the commit SHA, per-ID
results and evidence in `workflow/gates/`, and updates `workflow/state.md`.
A PASS is valid only for that commit. On failure, return the report and ask
the user before filing an issue. Missing requirements or test commands are
not invented.

## Branches and staged pull requests

Use stacked branches: `feat/<slug>/br` from the default branch,
`feat/<slug>/prd` from BR, `feat/<slug>/tr` from PRD, and
`feat/<slug>/code` from TR. Passing layers use pull requests into their parent
branch. The user merges them bottom-up; agents never merge. PR creation
requires a passing gate for the current HEAD and follows `pr_mode` in
`workflow/config.md`.

The fix action is optional and user-triggered. It creates a new issue branch,
does not edit requirements, and stops after at most two attempts.

## Project context and cost

Project requirements, conventions, glossary, workflow state and evidence stay
in the relevant project. Read the state, config, current layer, its parent and
glossary as required by the selected skill. Ask for blank stack, test-command,
PR-mode or issue-label values rather than guessing.

Keep always-on instructions brief and put procedures in on-demand skills.
Instructions guide the model; they are not a security boundary. Tool
restrictions, agent selection, delegation and runtime behavior must be checked
in the intended VS Code or Codespaces environment. Hard gates require branch
protection and required checks.

The optional Claude Code layer installs its project helpers from
`workflow-kit/`. Its hook warns if Anthropic API credentials are present but
cannot block them. Use only the user's approved subscription authentication
route; never place credentials in the repository. The devcontainer snippet is
provided for review and must be merged with existing project settings, not
copied over them.

## Hook diagnostics

The personal `baseline-probe` hook records `sessionStart` and
`userPromptSubmitted` events. Its script stays in the protected personal hooks
folder. It writes one UTF-8 JSONL file per invocation under
`[IO.Path]::GetTempPath()\copilot-hook-diagnostics`, not beside the script.
The runtime's temporary folder must permit writes in the session sandbox.
Do not grant write access to hook code to enable diagnostic records.

Each record contains the event name, UTC recording time, input property names,
and flags for the presence of session and agent identifiers. It does not record
prompt text or identifier values. Unique file names prevent concurrent hook
invocations from appending to the same file. Files remain until temporary-file
cleanup removes them.

A successful invocation writes `{}` to standard output. Invalid input or a
failed file write produces an explicit error and exit code 1. Direct script
tests alone do not verify runtime dispatch.
