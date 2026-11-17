---
name: requirements-authoring
description: Interview-first authoring of business, product and technical requirements and the KPI definition document, with IDs, acceptance criteria and parent links. Use for /flow draft br, prd or tr.
---

# Requirements authoring

Files live in docs/requirements/ (business-requirements.md, product-requirements.md, technical-requirements.md, kpi-definition.md). Keep the structure of the templates.

## Procedure

1. Read workflow/state.md, docs/glossary.md and the parent layer file only (PRD parent is BR, TR parent is PRD, BR has none).
2. Use the grilling skill to interview the user before drafting. Stop when the user says it is enough, read your summary back and get a yes before drafting.
3. Draft or edit the layer file. Edit only the requirements that are affected.
4. Check every requirement against the rules below and fix failures before showing the result.
5. Update workflow/state.md. Propose the gate as the next action; do not run it.

## Rules

- IDs: BR-001, PRD-001, TR-001, KPI-001. Never renumber or reuse an ID; retire it with Status: deprecated.
- One requirement is one statement using "shall". Atomic, unambiguous, and solution-neutral in BR and PRD.
- Every requirement has Statement, Parent (not for BR), Acceptance criteria, Verification level and Status. List children in the parent.
- Acceptance criteria are measurable: a number, a threshold or an observable behaviour. "Fast", "easy" and "robust" are not criteria.
- Verification level: BR is the KPI definition, PRD is a functional test, TR is an integration test (unit tests for module detail).
- No orphans: every PRD links to a BR and every TR links to a PRD.
- Remove every template placeholder written in angle brackets before you finish.
- If the repo or user folder already has a requirement-writing skill (for example req-creator), apply its quality rules as well.

## KPI definition (kpi-definition.md)

For each BR with a measurable outcome record: KPI name, definition or formula, unit, data source (write "not yet available" if unknown), baseline, target, pass threshold, measurement window and the linked BR. The pass thresholds are the gate for the BR pull request. A dashboard is a separate feature; create one only when the user asks for it.
