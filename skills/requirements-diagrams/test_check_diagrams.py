#!/usr/bin/env python3
"""Self-test for check_diagrams.py. Run: python3 -I test_check_diagrams.py"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_diagrams import check  # noqa: E402

PRD = """# Product Requirements

## DIA-001 Card handling
- **Layer:** PRD
- **Type:** flowchart
- **Status:** draft

```mermaid
flowchart LR
  LIB["PRD-02-05-001 Card library"]
  SHOP("PRD-02-05-002 Card shop")
  LIB -->|PRD-02-05-003 playable cards| SHOP
```

## PRD-02-05-001 Card library
- **Diagram:** DIA-001

## PRD-02-05-002 Card shop
- **Diagram:** DIA-001

## PRD-02-05-003 Playable cards
- **Diagram:** DIA-001, DIA-002

## PRD-02-05-004 Unrelated
"""

MULTI = """# Turn flow

## DIA-002 Turn
- **Layer:** PRD, TR
- **Type:** sequenceDiagram
- **Status:** draft

```mermaid
sequenceDiagram
  participant C as TR-02-01-001 Client
  participant S as TR-03-01-001 Server
  C->>S: PRD-02-05-003 playable cards
  Note over C,S: notes need no ID
```
"""

TR = """# Technical Requirements

## TR-02-01-001 Client
- **Diagram:** DIA-002

## TR-03-01-001 Server
- **Diagram:** DIA-002
"""


def run(prd=PRD, multi=MULTI, tr=TR):
    with tempfile.TemporaryDirectory() as d:
        req = Path(d) / "docs" / "requirements"
        (req / "prd" / "02-game").mkdir(parents=True)
        (req / "tr").mkdir()
        (req / "templates").mkdir()
        (Path(d) / "docs" / "diagrams").mkdir()
        (req / "prd" / "02-game" / "05-collection.md").write_text(prd)
        (req / "tr" / "02-client.md").write_text(tr)
        (req / "templates" / "prd-module.md").write_text("## DIA-001 template copy must be ignored\n")
        if multi:
            (Path(d) / "docs" / "diagrams" / "DIA-002-turn.md").write_text(multi)
        errors, count, _ = check(d)
        return errors, count


class CheckDiagrams(unittest.TestCase):
    def test_valid_set_passes(self):
        errors, count = run()
        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

    def test_node_without_id_fails(self):
        errors, _ = run(prd=PRD.replace('"PRD-02-05-002 Card shop"', '"Card shop"'))
        self.assertTrue(any("label must start" in e for e in errors), errors)

    def test_connection_without_label_fails(self):
        errors, _ = run(prd=PRD.replace("-->|PRD-02-05-003 playable cards|", "-->"))
        self.assertTrue(any("unsupported flowchart line" in e for e in errors), errors)

    def test_two_ids_in_one_label_fail(self):
        errors, _ = run(prd=PRD.replace("PRD-02-05-001 Card library", "PRD-02-05-001 PRD-02-05-004 Card library"))
        self.assertTrue(any("exactly one" in e for e in errors), errors)

    def test_missing_back_link_fails(self):
        errors, _ = run(prd=PRD.replace("## PRD-02-05-002 Card shop\n- **Diagram:** DIA-001\n", "## PRD-02-05-002 Card shop\n"))
        self.assertTrue(any("does not list DIA-001" in e for e in errors), errors)

    def test_listed_but_absent_fails(self):
        errors, _ = run(prd=PRD.replace("## PRD-02-05-004 Unrelated\n", "## PRD-02-05-004 Unrelated\n- **Diagram:** DIA-001\n"))
        self.assertTrue(any("does not contain PRD-02-05-004" in e for e in errors), errors)

    def test_unknown_requirement_fails(self):
        errors, _ = run(prd=PRD.replace('"PRD-02-05-002 Card shop"', '"PRD-02-05-099 Card shop"'))
        self.assertTrue(any("PRD-02-05-099 does not exist" in e for e in errors), errors)

    def test_missing_diagram_fails(self):
        errors, _ = run(multi=None)
        self.assertTrue(any("DIA-002, which does not exist" in e for e in errors), errors)

    def test_undefined_node_fails(self):
        errors, _ = run(prd=PRD.replace("|PRD-02-05-003 playable cards| SHOP", "|PRD-02-05-003 playable cards| VAULT"))
        self.assertTrue(any("'VAULT'" in e for e in errors), errors)

    def test_state_diagram_passes(self):
        state = PRD.replace(
            "flowchart LR\n  LIB[\"PRD-02-05-001 Card library\"]\n  SHOP(\"PRD-02-05-002 Card shop\")\n  LIB -->|PRD-02-05-003 playable cards| SHOP",
            "stateDiagram-v2\n  state \"PRD-02-05-001 Card library\" as LIB\n  state \"PRD-02-05-002 Card shop\" as SHOP\n  [*] --> LIB\n  LIB --> SHOP : PRD-02-05-003 playable cards",
        )
        errors, _ = run(prd=state)
        self.assertEqual(errors, [])

    def test_unsupported_type_fails(self):
        errors, _ = run(prd=PRD.replace("flowchart LR", "pie"))
        self.assertTrue(any("unsupported diagram type" in e for e in errors), errors)

    def test_template_placeholders_are_skipped(self):
        tpl = PRD.replace("PRD-02-05-002 Card shop", "PRD-02-05-002 <component name>") + "\n## PRD-02-05-005 Other\n- **Diagram:** <DIA-009 if needed>\n"
        errors, count = run(prd=tpl)
        self.assertEqual(errors, [])
        self.assertEqual(count, 1)

    def test_bidirectional_arrow_is_not_a_placeholder(self):
        errors, _ = run(prd=PRD.replace("LIB -->|", "LIB <-->|"))
        self.assertEqual(errors, [])

    def test_duplicate_diagram_id_fails(self):
        errors, _ = run(multi=MULTI.replace("DIA-002", "DIA-001"), tr=TR.replace("DIA-002", "DIA-001"))
        self.assertTrue(any("defined twice" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=1)
