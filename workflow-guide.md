# Workflow guide

The workflow is business requirements (BR) -> product requirements (PRD) ->
technical requirements (TR) -> code. Gates run in reverse: KPI definition,
functional tests, integration tests, then unit tests. Use `/flow <action>` for
one action at a time.

## Copilot

Use `Default` as the coordinator. It hands requirements work to
`requirements-author`, implementation to `coder`, and independent gates to
`verifier`. The verifier must use a fresh chat for an independent gate. The
`prompts/flow.prompt.md` file provides `/flow`; if it is not listed, configure
`chat.promptFilesLocations` for `~/.copilot/prompts`.

## Claude Code

In a Codespace, run `bash ~/.copilot/workflow-kit/install-claude.sh`. It
installs the Claude-specific files and copies project helpers to
`~/.workflow-kit`. Claude requirements and coding run in the main conversation;
the verifier runs as a subagent. Claude authentication must use the user's
subscription route. The session-start hook warns about API credentials but
does not block them. Never store credentials in the repository.

## Project workflow

Run `/flow init` or `bash ~/.workflow-kit/scaffold-project.sh` from the project
root. The scaffold creates `workflow/state.md`, `workflow/config.md`,
`workflow/gates/`, `docs/glossary.md`, the requirements tree READMEs
(`docs/requirements/br/`, `kpi/`, `prd/`, `tr/`) and the chapter templates in
`docs/requirements/templates/`, without overwriting existing files.

Create stacked branches in order:

| Layer | Branch | Parent branch | Gate |
|---|---|---|---|
| BR | `feat/<slug>/br` | default branch | Each BR links to a KPI with a measurable target, pass threshold and data source |
| PRD | `feat/<slug>/prd` | `feat/<slug>/br` | Functional tests pass and cover PRD IDs |
| TR | `feat/<slug>/tr` | `feat/<slug>/prd` | Integration tests pass and cover TR IDs |
| Code | `feat/<slug>/code` | `feat/<slug>/tr` | Unit tests pass and cover TR IDs |

Passing layers use staged pull requests into their parent branch. The user
merges pull requests bottom-up; agents never merge. A failed gate produces a
report. Ask before filing an issue. A gate result is valid only for its
recorded commit.

The stack and test commands are project-specific. Fill in
`workflow/config.md`; blank values must be asked, not guessed. A dashboard is
separate work and is built only when requested. Instructions guide the model;
they are not an enforcement boundary. Hard gates require repository branch
protection and required checks.
