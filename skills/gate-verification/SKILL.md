---
name: gate-verification
description: Independent verification of one layer against its acceptance criteria, producing a pass or fail report that cites requirement IDs, and filing a GitHub issue on failure. Use for /flow gate and when the verifier agent runs.
---

# Gate verification

You verify; you never fix. Do not edit code or requirements, and never weaken a criterion to make a gate pass. Ignore earlier reasoning in the conversation and rely only on files and command output.

## Procedure

1. Read workflow/config.md and workflow/state.md (ask the user if a needed command is blank), the layer's requirements file and its parent file.
2. Run the check for the layer:
   - code: the unit test command. Zero tests collected is a FAIL.
   - tr: the integration test command.
   - prd: the functional test command.
   - br: no test command. Check kpi-definition.md: every BR links to a KPI with a measurable pass threshold, a target and a data source (or "not yet available"), and every KPI links to a BR.
3. Placeholders: any template placeholder in angle brackets left in the layer's files is a FAIL.
4. Coverage (tr and prd): search the repo outside docs/ for tests tagged with each requirement ID of the layer. A requirement with no tagged test at the right level is a FAIL (uncovered), even when all tests pass.
5. Write workflow/gates/LAYER-YYYYMMDD-HHMM.md: verdict, git commit SHA, a per-requirement table (ID, result, evidence), failing test names and file paths, and links to the requirement documents.
6. Update the Gates table in workflow/state.md. A PASS is valid only for the commit SHA it names; any new commit needs a new gate.
7. On FAIL, summarise and ask the user to confirm filing a GitHub issue, then follow the issue steps in skill git-workflow. If you cannot ask the user (you run as a subagent), return the report and let the caller ask.
8. Reply with the verdict, one line per failing requirement and the report path.
