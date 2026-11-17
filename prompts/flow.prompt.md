---
description: Workflow manager. Run one step - init, status, start, draft, gate, pr, issue or fix.
agent: Default
---

Run this workflow action: ${input:action:for example status, start my-feature, draft prd, gate tr, pr code}

If the action is empty, run status. Follow the workflow-manager skill.
