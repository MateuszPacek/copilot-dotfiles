#!/usr/bin/env python3
"""Check the BR, KPI, PRD and TR folder trees: file names, IDs, interface placement, parents and BR-KPI links.

Reads docs/requirements/br/, kpi/, prd/ and tr/ under ROOT (default: the
current folder). Prints one line per error and exits 1 on any error, 0 otherwise.
Rules: skills/requirements-authoring/SKILL.md, section "Folder tree and IDs".
"""
import re
import sys
from pathlib import Path

LAYERS = {"br": "BR", "kpi": "KPI", "prd": "PRD", "tr": "TR"}
PARENT_OF = {"PRD": "BR", "TR": "PRD"}
NAME = re.compile(r"^(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*$")
HEAD = re.compile(r"^## (.*)$", re.M)
REQ_HEAD = re.compile(r"^((?:BR|KPI|PRD|TR)(?:-\d{2})+-\d{3})\b")
DIA_HEAD = re.compile(r"^DIA-\d{3}\b")
FIELD = r"^- \*\*{}:\*\*(.*)$"
CODE = re.compile(r"^\d{2}(?:-\d{2})*$")
PLACEHOLDER = re.compile(r"<[A-Za-z][^<>]*>")
IGNORED = {"README.md"}


def sections(text):
    """Yield (heading, body) for each '## ' section."""
    starts = [m.start() for m in HEAD.finditer(text)] + [len(text)]
    for a, b in zip(starts, starts[1:]):
        body = text[a:b]
        yield body.splitlines()[0][3:].strip(), body


def field(body, name):
    m = re.search(FIELD.format(re.escape(name)), body, re.M)
    return m.group(1).strip() if m else None


def walk(layer_dir, errors):
    """Return {file: codes}, where codes is the location of the file's requirements, and the set of module codes."""
    files, modules = {}, set()

    def visit(folder, codes):
        seen = {}
        for p in sorted(folder.iterdir()):
            rel = p.relative_to(layer_dir.parent.parent.parent)
            if p.name in IGNORED:
                continue
            if p.is_file() and p.name == "_index.md":
                if not codes:
                    errors.append(f"{rel}: no _index.md at the layer root; use 01-general.md")
                else:
                    files[p] = codes
                continue
            stem = p.stem if p.is_file() else p.name
            if p.is_file() and p.suffix != ".md":
                errors.append(f"{rel}: only .md files are allowed")
                continue
            m = NAME.match(stem)
            if not m:
                errors.append(f"{rel}: name must be NN-lowercase-name (two digits, a hyphen, a lowercase name)")
                continue
            num = m.group(1)
            if num == "00":
                errors.append(f"{rel}: number 00 is not allowed")
                continue
            if num in seen:
                errors.append(f"{rel}: number {num} is already used by {seen[num]}")
                continue
            seen[num] = p.name
            if not codes and num == "01" and not (p.is_file() and stem == "01-general"):
                errors.append(f"{rel}: number 01 at the layer root is reserved for 01-general.md")
            mycodes = codes + [num]
            modules.add("-".join(mycodes))
            if p.is_dir():
                visit(p, mycodes)
            else:
                files[p] = mycodes

    if layer_dir.is_dir():
        visit(layer_dir, [])
    return files, modules


def lowest_common(codes_list):
    """Codes shared at the start of every code list."""
    parts = [c.split("-") for c in codes_list]
    common = []
    for level in zip(*parts):
        if len(set(level)) != 1:
            break
        common.append(level[0])
    return common


def check_kpi_link(prefix, rel, rid, codes, body, ids, bodies, errors):
    """A BR lists its KPIs; a KPI names its BR, sits in the KPI file that mirrors the BR file, and is listed by that BR."""
    if prefix == "BR":
        value = field(body, "KPI")
        if value is None:
            errors.append(f"{rel}: {rid} has no KPI field")
            return
        kids = re.findall(r"KPI(?:-\d{2})+-\d{3}", value)
        if not kids and not PLACEHOLDER.search(value):
            errors.append(f"{rel}: {rid} KPI field names no KPI")
        for kid in kids:
            if kid not in ids["KPI"]:
                errors.append(f"{rel}: {rid} KPI {kid} does not exist")
        return
    value = field(body, "Business requirement")
    if value is None:
        errors.append(f"{rel}: {rid} has no Business requirement field")
        return
    bids = re.findall(r"BR(?:-\d{2})+-\d{3}", value)
    if not bids:
        errors.append(f"{rel}: {rid} Business requirement must name a BR")
    for bid in bids:
        if bid not in ids["BR"]:
            errors.append(f"{rel}: {rid} Business requirement {bid} does not exist")
            continue
        bcodes, bbody = bodies[bid]
        if bcodes != codes:
            errors.append(f"{rel}: {rid} belongs in the KPI file that mirrors {bid} (IDs KPI-{'-'.join(bcodes)}-NNN)")
        if rid not in (field(bbody, "KPI") or ""):
            errors.append(f"{rel}: {rid} is not listed in the KPI field of {bid}")


def check(root):
    root = Path(root)
    req_dir = root / "docs" / "requirements"
    errors, ids = [], {}
    parsed, bodies = {}, {}
    for folder, prefix in LAYERS.items():
        files, modules = walk(req_dir / folder, errors)
        ids[prefix] = set()
        parsed[prefix] = []
        for f, codes in files.items():
            rel = f.relative_to(root)
            expected = f"{prefix}-{'-'.join(codes)}-"
            for heading, body in sections(f.read_text(encoding="utf-8")):
                if DIA_HEAD.match(heading):
                    continue
                m = REQ_HEAD.match(heading)
                if not m:
                    errors.append(f"{rel}: heading '## {heading}' is not a requirement ID ({expected}NNN) or a diagram ID (DIA-NNN)")
                    continue
                rid = m.group(1)
                if not rid.startswith(expected) or len(rid) != len(expected) + 3:
                    errors.append(f"{rel}: {rid} does not match its location; IDs in this file are {expected}NNN")
                    continue
                if rid in ids[prefix]:
                    errors.append(f"{rel}: {rid} is defined twice")
                    continue
                ids[prefix].add(rid)
                bodies[rid] = (codes, body)
                parsed[prefix].append((rel, rid, codes, body, modules))
    for prefix in ("BR", "KPI"):
        for rel, rid, codes, body, modules in parsed[prefix]:
            check_kpi_link(prefix, rel, rid, codes, body, ids, bodies, errors)
    for prefix in ("PRD", "TR"):
        for rel, rid, codes, body, modules in parsed[prefix]:
            connects = field(body, "Connects")
            if connects and not PLACEHOLDER.search(connects):
                targets = [c.strip() for c in connects.split(",") if c.strip()]
                bad = [c for c in targets if not CODE.match(c) or c not in modules]
                if bad:
                    errors.append(f"{rel}: {rid} Connects names modules that do not exist: {', '.join(bad)}")
                elif len(set(targets)) < 2:
                    errors.append(f"{rel}: {rid} Connects must name at least two different modules")
                else:
                    home = lowest_common(targets) or ["01"]
                    if home != codes:
                        place = f"{prefix}-{'-'.join(home)}-NNN"
                        errors.append(f"{rel}: {rid} is an interface between {', '.join(targets)} and belongs in the chapter with IDs {place}")
            parent = field(body, "Parent")
            want = PARENT_OF[prefix]
            if parent is None:
                errors.append(f"{rel}: {rid} has no Parent field")
            elif not PLACEHOLDER.search(parent):
                pids = re.findall(rf"{want}(?:-\d{{2}})+-\d{{3}}", parent)
                if not pids:
                    errors.append(f"{rel}: {rid} Parent must name a {want} requirement")
                for pid in pids:
                    if pid not in ids[want]:
                        errors.append(f"{rel}: {rid} Parent {pid} does not exist")
    return errors, {k: len(v) for k, v in ids.items()}


def main():
    errors, counts = check(sys.argv[1] if len(sys.argv) > 1 else ".")
    for e in errors:
        print(f"FAIL {e}")
    summary = ", ".join(f"{n} {k}" for k, n in counts.items())
    print(f"{'FAIL' if errors else 'PASS'}: {summary} requirement(s), {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
