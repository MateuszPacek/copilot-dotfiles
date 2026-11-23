---
name: test-first-coding
description: Test-first implementation of technical requirements, with unit, integration and functional tests tagged by requirement ID. Use for /flow draft code.
---

# Solution coding

1. Read workflow/state.md, workflow/config.md (stack and test commands; ask if blank) and the TR chapter files in docs/requirements/tr/ that you implement. Read PRD chapter files in docs/requirements/prd/ only for the PRD IDs that your TRs link to.
2. Confirm with the user which TR IDs are in scope. Work on one TR at a time, smallest vertical slice first.
3. Before writing code, list the tests the acceptance criteria imply and get the user's yes.
4. Test first: write a failing test, write the minimal code that passes it, run it, repeat. Refactor only when green.
5. Tag every test with the requirement ID it verifies, in its name or a comment, for example `TR-02-01-003`. Unit and integration tests carry TR IDs. Functional tests carry PRD IDs. The gate finds coverage through these tags.
6. Write tests at all three levels for the scope. Only the unit tests must pass before the code PR.
7. Do not edit requirement files on the code branch. If a requirement is wrong or untestable, stop and tell the user: the fix belongs on that requirement's own branch.
8. Run the unit test command and show the result. Update workflow/state.md. Propose the gate; do not run it.
