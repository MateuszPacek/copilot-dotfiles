#!/usr/bin/env python3
"""Check normative Mermaid diagrams against the requirements.

Reads docs/requirements/ (folder trees, without templates/ and README.md files)
and docs/diagrams/*.md under ROOT (default: current
folder). Prints one line per error and exits 1 on any error, 0 otherwise.
Rules: skills/requirements-diagrams/SKILL.md.
"""
import re
import sys
from pathlib import Path

REQ_ID = r"(?:(?:BR|PRD|TR)(?:-\d{2})+-\d{3})"
REQ_HEAD = re.compile(rf"^## ({REQ_ID})\b", re.M)
DIA_HEAD = re.compile(r"^## (DIA-\d{3})\b", re.M)
DIA_FIELD = re.compile(r"^- \*\*Diagram:\*\*(.*)$", re.M)
MERMAID = re.compile(r"^```mermaid\s*\n(.*?)^```", re.M | re.S)
LABEL_ID = re.compile(rf"^\s*\"?\s*({REQ_ID})\b")
ANY_ID = re.compile(REQ_ID)
PLACEHOLDER = re.compile(r"<[A-Za-z][^<>]*>")  # unfilled template text; the gate placeholder check reports it

KEY = r"[A-Za-z0-9_]+"
FLOW_NODE = re.compile(rf"^({KEY})\s*(\[\[|\[\(|\(\(|\[/|\[\\|\[|\(\[|\(|\{{\{{|\{{|>)(.*?)(\]\]|\)\]|\)\)|/\]|\\\]|\]|\]\)|\)|\}}\}}|\}}|\])$")
FLOW_EDGE = re.compile(rf"^({KEY})\s*(<?[-=.ox]*[-=.][-=.>ox]*)\s*\|([^|]*)\|\s*({KEY})$")
FLOW_SKIP = re.compile(r"^(subgraph\b|end$|direction\b|classDef\b|class\b|style\b|linkStyle\b|%%)")
STATE_DEF = re.compile(rf"^state\s+\"([^\"]*)\"\s+as\s+({KEY})$")
STATE_EDGE = re.compile(rf"^(\[\*\]|{KEY})\s*-->\s*(\[\*\]|{KEY})\s*(?::\s*(.*))?$")
STATE_SKIP = re.compile(r"^(direction\b|note\b|end note$|%%|\}$|classDef\b|class\b)")
SEQ_PART = re.compile(rf"^(participant|actor)\s+({KEY})\s+as\s+(.+)$")
SEQ_MSG = re.compile(rf"^({KEY})\s*(-{{1,2}}(?:>>|>|x|\)))\s*[+-]?({KEY})\s*:\s*(.*)$")
SEQ_SKIP = re.compile(r"^(autonumber$|loop\b|alt\b|else\b|opt\b|par\b|and\b|critical\b|break\b|rect\b|end$|Note\b|note\b|activate\b|deactivate\b|%%)")


def sections(text, head):
    """Yield (id, body) for each '## ID' section."""
    marks = [(m.start(), m.group(1)) for m in head.finditer(text)]
    starts = [m.start() for m in re.finditer(r"^## ", text, re.M)] + [len(text)]
    for pos, ident in marks:
        end = min(s for s in starts if s > pos)
        yield ident, text[pos:end]


def label_id(label, where, errors):
    """Return the single requirement ID at the start of a label, or record an error."""
    ids = ANY_ID.findall(label or "")
    first = LABEL_ID.match(label or "")
    if not first or len(ids) != 1:
        errors.append(f"{where}: label must start with exactly one requirement ID: {label!r}")
        return None
    return first.group(1)


def parse_diagram(dia, block, errors):
    """Return the set of requirement IDs used by one Mermaid block."""
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    if not lines:
        errors.append(f"{dia}: empty mermaid block")
        return set()
    kind, body, used = lines[0].split()[0], lines[1:], set()
    defined, referenced = set(), set()

    def take(label, where):
        ident = label_id(label, where, errors)
        if ident:
            used.add(ident)

    for n, line in enumerate(body, 2):
        where = f"{dia} line {n}"
        if kind in ("flowchart", "graph"):
            if FLOW_SKIP.match(line):
                continue
            if m := FLOW_EDGE.match(line):
                take(m.group(3), where)
                referenced.update([m.group(1), m.group(4)])
            elif m := FLOW_NODE.match(line):
                take(m.group(3), where)
                defined.add(m.group(1))
            else:
                errors.append(f"{where}: unsupported flowchart line, use one node or one labelled connection per line: {line!r}")
        elif kind == "stateDiagram-v2":
            if STATE_SKIP.match(line):
                continue
            if m := STATE_DEF.match(line):
                take(m.group(1), where)
                defined.add(m.group(2))
            elif m := STATE_EDGE.match(line):
                a, b, label = m.group(1), m.group(2), m.group(3)
                if label is None and "[*]" in (a, b):
                    pass
                else:
                    take(label, where)
                referenced.update(k for k in (a, b) if k != "[*]")
            else:
                errors.append(f"{where}: unsupported state line: {line!r}")
        elif kind == "sequenceDiagram":
            if SEQ_SKIP.match(line):
                continue
            if m := SEQ_PART.match(line):
                take(m.group(3), where)
                defined.add(m.group(2))
            elif m := SEQ_MSG.match(line):
                take(m.group(4), where)
                referenced.update([m.group(1), m.group(3)])
            else:
                errors.append(f"{where}: unsupported sequence line: {line!r}")
        else:
            errors.append(f"{dia}: unsupported diagram type {kind!r}; use flowchart, stateDiagram-v2 or sequenceDiagram")
            return used
    for key in sorted(referenced - defined):
        errors.append(f"{dia}: element {key!r} is used in a connection but has no labelled definition")
    return used


def check(root):
    root = Path(root)
    req = root / "docs" / "requirements"
    files = sorted(p for p in req.rglob("*.md") if "templates" not in p.relative_to(req).parts and p.name != "README.md")
    files += sorted(p for p in (root / "docs" / "diagrams").glob("*.md") if p.name != "README.md")
    errors, reqs, diagrams, dia_files, skipped = [], {}, {}, {}, []
    for f in files:
        text = f.read_text(encoding="utf-8")
        for rid, body in sections(text, REQ_HEAD):
            field = DIA_FIELD.search(body)
            if field and PLACEHOLDER.search(field.group(1)):
                field = None
            reqs[rid] = set(re.findall(r"DIA-\d{3}", field.group(1))) if field else set()
        for did, body in sections(text, DIA_HEAD):
            if PLACEHOLDER.search(body):
                skipped.append(did)
                continue
            if did in diagrams:
                errors.append(f"{did}: defined twice ({dia_files[did]} and {f.relative_to(root)})")
                continue
            blocks = MERMAID.findall(body)
            if len(blocks) != 1:
                errors.append(f"{did}: needs exactly one mermaid block, found {len(blocks)}")
                diagrams[did] = set()
            else:
                diagrams[did] = parse_diagram(did, blocks[0], errors)
            dia_files[did] = str(f.relative_to(root))
    for did, used in diagrams.items():
        for rid in sorted(used):
            if rid not in reqs:
                errors.append(f"{did}: {rid} does not exist")
            elif did not in reqs[rid]:
                errors.append(f"{did}: {rid} is in the diagram but its Diagram field does not list {did}")
    for rid, dias in reqs.items():
        for did in sorted(dias):
            if did in skipped:
                continue
            if did not in diagrams:
                errors.append(f"{rid}: Diagram field names {did}, which does not exist")
            elif rid not in diagrams[did]:
                errors.append(f"{rid}: Diagram field names {did}, but {did} does not contain {rid}")
    return errors, len(diagrams), skipped


def main():
    errors, count, skipped = check(sys.argv[1] if len(sys.argv) > 1 else ".")
    if skipped:
        print(f"SKIP template diagram(s) with placeholders: {', '.join(skipped)}")
    for e in errors:
        print(f"FAIL {e}")
    print(f"{'FAIL' if errors else 'PASS'}: {count} diagram(s), {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
