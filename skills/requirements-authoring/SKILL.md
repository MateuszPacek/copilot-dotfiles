---
name: requirements-authoring
description: Interview-first authoring of business, product and technical requirements and the KPI definition document, with IDs, acceptance criteria, parent links and normative diagrams (sub-skill requirements-diagrams). Use for /flow draft br, prd or tr.
---

# Requirements authoring

Files live in docs/requirements/ as folder trees: br/ and kpi/ (one file per BR chapter, KPI tree mirrors the BR tree), prd/ and tr/ (one file per module). Chapter templates are in docs/requirements/templates/. Keep their structure.

## Procedure

1. Read workflow/state.md, docs/glossary.md, the layer's tree README (br/README.md, prd/README.md or tr/README.md) and only the parent requirements you need (PRD parent is BR, TR parent is PRD, BR has none).
2. Use the grilling skill to interview the user before drafting. Stop when the user says it is enough, read your summary back and get a yes before drafting.
3. Draft or edit the chapter files. Create a chapter file from the template only when work on that module starts. Edit only the requirements that are affected.
4. Check every requirement against the rules below, run both checks (`python3 ~/.copilot/skills/requirements-authoring/check_requirements.py` and `python3 ~/.copilot/skills/requirements-diagrams/check_diagrams.py`) and fix failures before showing the result.
5. Update workflow/state.md. Propose the gate as the next action; do not run it.

## Rules

- IDs: BR, KPI, PRD and TR IDs follow the folder tree (see below). Never renumber or reuse an ID; retire it with Status: deprecated, or record it in the tree README when a reorganisation retires it.
- One requirement is one statement using "shall". Atomic, unambiguous, and solution-neutral in BR and PRD.
- Every requirement has Statement, Parent (not for BR), Acceptance criteria, Verification level and Status. List children in the parent.
- Acceptance criteria are measurable: a number, a threshold or an observable behaviour. "Fast", "easy" and "robust" are not criteria.
- Verification level: BR is the KPI definition, PRD is a functional test, TR is an integration test (unit tests for module detail).
- No orphans: every PRD links to a BR and every TR links to a PRD.
- Remove every template placeholder written in angle brackets before you finish.
- Diagrams: when a layer needs a component, flow, state or sequence diagram, follow skill requirements-diagrams. A diagram is a requirement; every node and connection is a requirement ID, and those requirements carry the content. Run its check before you finish.
- If the repo or user folder already has a requirement-writing skill (for example req-creator), apply its quality rules as well.

## BR tree

- `br/01-general.md` holds the context and planning assumptions; it has no requirements and uses `###` headings only.
- Top folders are scopes. Use `02-common/` for requirements that apply to the whole business; if the business has alternative paths (for example publisher deal or own release), give each path its own folder (`03-<path>/`, `04-<path>/`). A business with one path keeps only `02-common/`. Each scope folder has an `_index.md` (scope, no requirements).
- Chapter files inside each scope folder: `01-product.md`, `02-finance.md`, `03-organization.md`, `04-market.md`. Create a file only when it has requirements; the numbers are reserved for these chapters.
- A requirement belongs to one scope only. If it has criteria for several scopes, split it: shared criteria in `02-common/`, scope criteria in the scope folders, each with its own new ID.
- Every BR has a `KPI` field that lists its KPIs. BRs have no Parent and no `Applies to` field; the folder decides.

## Folder tree and IDs (all layers)

- One folder per product or group, one file per module, nested as deep as needed. Names are `NN-lowercase-name` (folders) and `NN-lowercase-name.md` (files), with a two-digit number unique in its folder.
- At the layer root, `01-general.md` holds rules for all products and interfaces between products. No `_index.md` at the root.
- A folder's `_index.md` holds its chapter introduction, its diagram and the interfaces between its modules. It takes the folder's number, not a number of its own.
- IDs are the layer prefix, the numbers of the path and a three-digit sequence: `PRD-02-04-02-003` is requirement 003 in `prd/02-app/04-modes/02-basic.md`; `PRD-02-04-001` is in `prd/02-app/04-modes/_index.md`; `PRD-01-001` is in `prd/01-general.md`.
- Numbers are fixed once assigned. A new module takes the next free number; a removed number is retired, recorded in the tree README and never reused. Record every assigned number in the tree README.
- An interface requirement names the modules it connects in `- **Connects:** 02-05-01, 02-05-02` and lives in the lowest chapter that contains all of them: the shared folder's `_index.md`, or `01-general.md` when the modules are in different products.
- Abstraction: PRD describes what a player or administrator can observe; TR describes components, interfaces, data and limits. If changing the technology changes the statement, it is TR. If only a developer or a tool can observe it, it is TR. PRD uses glossary terms; TR names components and interfaces.
- `check_requirements.py` checks names, numbers, ID-to-location match, duplicates, interface placement and Parent links. Self-test: `python3 -I ~/.copilot/skills/requirements-authoring/test_check_requirements.py`.

## KPI definition (kpi/ tree)

The kpi/ tree mirrors br/: KPIs for `br/02-common/02-finance.md` live in `kpi/02-common/02-finance.md` with IDs `KPI-02-02-NNN`. `check_requirements.py` checks that every KPI names an existing BR in the mirrored file and that the BR lists it. For each BR with a measurable outcome record: KPI name, definition or formula, unit, data source (write "not yet available" if unknown), baseline, target, pass threshold, measurement window and the linked BR. The pass thresholds are the gate for the BR pull request. A dashboard is a separate feature; create one only when the user asks for it.
