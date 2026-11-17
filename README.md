# Workflow kit: requirements chain with test gates

Runs the chain business requirements (BR) -> product requirements (PRD) -> technical requirements (TR) -> code,
with gates unit -> integration -> functional -> KPI, stacked branches and staged PRs.
You are the orchestrator: every step is triggered by you with `/flow <action>`.

## Default agent: `orchestrator`

Start every workflow session with it. It runs one step at a time and hands off to `requirements-author`, `coder` and `verifier`.
- Copilot: pick `orchestrator` in the Agent dropdown. VS Code has no file-based setting that preselects a default agent, so `/flow` is the reliable shortcut: it always runs the orchestrator.
- Claude Code: the same agent exists in `~/.claude/agents`. To make it the main-thread default for a project, run `bash ~/.workflow-kit/scaffold-project.sh --claude` (creates `.claude/settings.json` with `"agent": "orchestrator"` if absent), or start with `claude --agent orchestrator`. This comes from user reports in Anthropic's issue tracker, so verify it.
- You already have a `Default` agent in this repo. Two coordinators overlap, so decide which one stays the single default: either keep `Default` and add the handoffs from `orchestrator` to it, or retire one of them.

## Layout (repo root = the `~/.copilot` folder)

| Path | Purpose |
|---|---|
| `agents/` | `orchestrator` (default), `requirements-author`, `coder`, `verifier` (`*.agent.md`) |
| `skills/` | The logic, shared by both tools: `workflow-manager`, `requirements-authoring`, `test-first-coding`, `gate-verification`, `git-workflow` |
| `prompts/flow.prompt.md` | The `/flow` command for Copilot |
| `instructions/workflow.instructions.md` | Tiny rules file, loaded only for `workflow/` and `docs/requirements/` files |
| `workflow-kit/` | Everything that is not Copilot-native: templates, scaffold and install scripts, hook, Claude Code layer, devcontainer snippet |

This matches the documented user-level Copilot locations: `~/.copilot/agents/*.agent.md`, `~/.copilot/skills/<name>/SKILL.md` and `~/.copilot/instructions/*.instructions.md`. Nothing to install for Copilot when the repo sits in `~/.copilot`.

Prompt files are the exception: the documented default for user-level prompts is your VS Code profile, not `~/.copilot/prompts`. If `/flow` does not appear, add this to your VS Code user settings:
`"chat.promptFilesLocations": { "~/.copilot/prompts": true }`
Skills also appear as slash commands, so `/workflow-manager` works regardless.

## Install

1. Unzip into the repo root (it merges; all names are new). Also replace the root `install.sh` with the patched one delivered next to this zip. It differs from yours in three places: it adds `prompts` and `workflow-kit` to the folders your installer copies into `~/.copilot` (your original copies only `agents`, `instructions`, `skills` and `workflows`). Everything else, including its refusal to overwrite existing files, is unchanged.
2. Stage the installer with `git add --chmod=+x install.sh`, review, commit and push, as in your codespaces guide. New Codespaces get the change; existing ones do not.
3. Claude route only: add one line to your Codespace setup, or run it by hand: `bash ~/.copilot/workflow-kit/install-claude.sh` (add `--install-claude-cli` if the CLI is not already installed).
4. Merge `workflow-kit/devcontainer.snippet.jsonc` into your `.devcontainer/devcontainer.json` (keep your existing keys).
5. In each project: `bash ~/.copilot/workflow-kit/scaffold-project.sh` (add `--claude` for the Claude default agent), or run `/flow init`. It never overwrites.

The Claude installer edits `~/.claude/CLAUDE.md` only between its own marker lines and never overwrites an existing `~/.claude/settings.json`.

## Daily use

`/flow status` -> `/flow start <feature>` -> `/flow draft br` -> `/flow gate br` -> `/flow pr br` -> `/flow draft prd` -> ... -> `/flow draft code` -> `/flow gate code`.
Failed gate: `/flow issue`. Optional automatic fix on a new branch: `/flow fix <issue number>` (max 2 attempts).

| Layer | Branch (stacked) | PR base | Gate |
|---|---|---|---|
| BR | `feat/<slug>/br` | default branch | KPI definition has measurable pass criteria |
| PRD | `feat/<slug>/prd` | `.../br` | functional tests pass |
| TR | `feat/<slug>/tr` | `.../prd` | integration tests pass |
| Code | `feat/<slug>/code` | `.../tr` | unit tests pass |

You merge PRs bottom-up (code, tr, prd, br). Agents never merge.

## Differences between the two tools

- Copilot: 4 agents with handoff buttons. Run the gate in a **new chat** with `verifier`, because a handoff keeps the earlier conversation and the check would not be independent.
- Claude Code: requirements and coding run in the main conversation (the interview needs you). Only the gate runs as a subagent, which gives it a fresh context.
- The session-start hook exists for Claude only. It loads `workflow/state.md` and warns if an API key is set.

## Claude Pro only (no API billing) in Codespaces

- Never set `ANTHROPIC_API_KEY` as a Codespaces secret or variable. The hook warns if one is present; it cannot block it.
- Login: either log in by hand in each Codespace, or run `claude setup-token` once on your PC and store the result as a private Codespaces **user secret** named `CLAUDE_CODE_OAUTH_TOKEN` (never in the repo). Both points come from user reports, not official documentation: test them in a fresh Codespace and check your Claude usage page afterwards.
- Pro has usage limits. Cost-saving here means fewer tokens, not lower dollars.

## Cost-saving built in

- Always-on text is tiny: a very short instructions file that loads only for `workflow/` and `docs/requirements/` files, and a very short CLAUDE.md block. The logic is in skills, which load only when needed.
- Agents read only `workflow/state.md`, the glossary, the current layer and its parent.
- State lives in files, so new chats start cheap. One layer per chat.
- Model per agent: Copilot agents have a commented `# model:` line to fill in; the Claude verifier uses `sonnet`. Test a cheaper model on the verifier before trusting it.
- Do not use Copilot code review as a gate (it uses extra billing). Gates here are tests plus the verifier.

## Fit with your current agents

Your `Default`, `product-requirements`, `technical-requirements`, `coding` and `testing` agents overlap with `orchestrator`, `requirements-author` (both requirement layers), `coder` and `verifier`. No names collide, so both sets work side by side. Your agents carry things this kit does not (model-based design, the `req-creator` SMART/INCOSE guidance); this kit adds what yours lack (business requirements and KPI definition, stacked branches, PRs, failure issues, a state file). Retire an old agent only after folding its unique rules into the new one. `requirements-authoring` applies `req-creator` when present.

## Decisions left to you (agents ask if blank)

- `pr_mode` in `workflow/config.md`: draft or ready PRs.
- Test commands per project (language and stack are decided per project).
- Whether to restrict the verifier's tools in Copilot (a read-only verifier is safer; tool names depend on your VS Code version, so `tools` is left unset).

## Limits and what to verify

- Instructions guide the AI; they do not enforce anything. For a hard block, add GitHub branch protection plus required checks on the stacked branches.
- Built and checked as files and scripts only. I could not run VS Code, Copilot or Claude Code. Verify in a real session: agents appear in the dropdown, handoffs and `${input:...}` work, `/flow` is listed, skills load.
- Not included: Copilot hooks, GitHub Actions gates, the KPI dashboard feature.
