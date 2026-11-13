# Software workflow

The personal Copilot configuration defines four roles: functional requirements,
technical requirements, coding, and staged testing. The `Default` personal
agent coordinates the roles. Apply the same coordination workflow to every
personal request, including sessions that do not select a custom agent.
Explicit choices, the approved request, and existing approval controls remain
in force.

Functional work produces product requirements, using model-based design whenever
possible. Models describe product behavior independently of software
implementation choices. Technical work includes software design and a technical
specification linked to applicable product requirements and models. Coding and
testing use these same approved inputs. If a suitable product model cannot be
produced, the functional role explains the limitation and retains testable
product requirements in text.

The functional role is named `product-requirements`; the technical role is
named `technical-requirements`. Both load the personal `req-creator` skill,
which holds their shared SMART and INCOSE requirements engineering guidance.
Maintain that method in the skill, not as separate copies in the agents.

Select the Copilot session target and open **Chat: Open Customizations**. In
**Agents**, find `Default` and the four role agents. Start a new session after
changing agent files. Select `Default` where the session supports custom-agent
selection. The custom-agent definition does not force its selection for every
session; global personal instructions carry the coordination behavior across
sessions. Agent selection does not guarantee model selection or delegation.
If delegation is not available or allowed, `Default` reports the limitation
and applies the relevant role directly. It does not claim the visible agent
selection changed.

The testing role checks code tests first, technical requirements second, and
functional compliance third. It stops at a failed or unverified stage and reports
later stages as not checked. Supply existing approved requirements for the
checks; missing requirements are not invented. File changes and command
execution still need the applicable permissions.

The current VS Code user settings specify `chat.defaultConfiguration.mode` as
`plan`. Autopilot is not equivalent to Plan: it can run tools without approval
and answer questions automatically. The mode setting does not prevent a user
or runtime from selecting Autopilot. VS Code documentation reviewed here does
not define a setting that forces a personal custom agent to be selected in
every session.

Personal agents are stored in the Copilot user agent directory. Project
requirements, conventions, and evidence stay in the relevant project. No
project files, hooks, external integrations, or new skills are necessary by
default. Agent instructions guide the model; they are not a security boundary.
Tool restrictions and delegation depend on the session runtime and must be
verified in the intended environment.

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
cleanup removes them. The old `baseline-probe.jsonl` beside the script is
historical and is no longer updated.

A successful invocation writes `{}` to standard output. Invalid input or a
failed file write produces an explicit error and exit code 1. After changing
the hook, start a fresh chat and confirm that both event files appear without
a hook error. Direct script tests alone do not verify runtime dispatch.
