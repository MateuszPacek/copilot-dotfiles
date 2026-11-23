# <Module name>

Template for one PRD chapter file in `docs/requirements/prd/`. Copy it to the module's place in the tree (see `prd/README.md`), as `NN-module-name.md` for a module or `_index.md` for a folder chapter, and delete these instructions.
Layer 2. Parent: business requirements. Describes what the product does for its users, without prescribing the implementation.
One requirement per `##` section. IDs follow the file's location: `PRD-<folder numbers>-<file number>-NNN` in a module file, `PRD-<folder numbers>-NNN` in an `_index.md`. IDs are never reused or renumbered. Status is draft, approved or deprecated.
An interface between modules goes into the lowest chapter that contains all of them (the folder's `_index.md`, or `01-general.md` between products) and names them in `Connects`. Delete the `Connects` line in other requirements.
Diagrams are requirements: see skill requirements-diagrams. Delete the example diagram if the chapter needs none.

## DIA-001 <diagram title>
- **Layer:** PRD
- **Type:** <flowchart, stateDiagram-v2 or sequenceDiagram>
- **Status:** draft

```mermaid
flowchart LR
  A["PRD-02-05-01-001 <component name>"]
  B["PRD-02-05-02-001 <component name>"]
  A -->|PRD-02-05-001 <what the connection carries>| B
```

## PRD-02-05-01-001 <short title>
- **Statement:** The product shall ...
- **Parent:** BR-02-01-001
- **Connects:** <module numbers, for example 02-05-01, 02-05-02, for an interface; otherwise delete this line>
- **Diagram:** <DIA-001 if this requirement is a node or connection in a diagram; otherwise delete this line>
- **Acceptance criteria:**
  - AC1: Given <context>, when <action>, then <observable result>
- **Children:** TR-02-01-001
- **Verification level:** Functional test (tag tests with the PRD ID)
- **Status:** draft
