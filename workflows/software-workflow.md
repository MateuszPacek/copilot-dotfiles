# Software workflow

Read for software work. Shared approval, privacy, glossary, and reporting controls remain in the personal instructions; do not copy them into each role.

## Select roles

Identify and briefly explain only the requested roles. A request can select more than one; do not add unrequested work.

| Role | Agent | Necessary output |
|---|---|---|
| Functional requirements | `product-requirements` | Testable product requirements and implementation-independent behavior models where possible. Explain when a suitable model cannot be produced. |
| Technical requirements | `technical-requirements` | Software design and technical specification linked to applicable product requirements and models. |
| Coding | `solution-coding` | Authorized implementation using the same approved inputs and relevant validation. |
| Testing | `staged-testing` | Code tests, technical requirements, then functional compliance; stop if a stage fails or cannot be verified. |

Use `Default` coordination guidance when supported. Selecting a coordinator or role does not itself require an agent launch or change runtime mode or permissions.

## Execute or delegate

Respect runtime delegation rules. Handle small work directly when permitted; delegate only substantial independent work to the matching agent.
Retain execution helpers required by the runtime; the small-task rule does not bypass them.
Before applying a role directly, read its corresponding file in `~/.copilot/agents` unless its current instructions are already available.
Preserve the `req-creator` skill dependency for product and technical requirements even when applying those roles directly.
If delegation is unavailable or disallowed, state this when relevant and apply the role instructions directly when permitted. If those instructions cannot be read, report the limitation.
Do not claim the selected agent in the UI changed.

## Handoff

Provide a bounded objective and stop condition, with only relevant:
- Original request, approved baseline version and text, scope, decisions, and open questions.
- Product requirements, models, software design, technical specification, and requirement identifiers applicable to the selected role.
- Source paths or bounded excerpts, evidence locations, and verification results.
- Personal and project controls, constraints, and granted permissions.

Do not assume agents inherit instructions. If inheritance is uncertain, supply applicable controls explicitly or require the agent to read the exact source before acting.
A file path alone is insufficient when the recipient cannot read it.
Do not send full conversation histories or execution logs by default.
Ask for missing inputs or permissions; do not invent requirements or treat assumptions as approved.

Return concise findings, changed-file references, evidence, and unresolved issues. Reuse the authoritative task record rather than making another copy.
Routine coding validation does not establish completion of the separate staged-testing role.
