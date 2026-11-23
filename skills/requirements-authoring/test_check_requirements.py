#!/usr/bin/env python3
"""Self-test for check_requirements.py. Run: python3 -I test_check_requirements.py"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_requirements import check  # noqa: E402


def brq(rid, kpis):
    return f"## {rid} Title\n- **Statement:** The studio shall work.\n- **KPI:** {kpis}\n"


def kpi(kid, br):
    return f"## {kid} Title\n- **Business requirement:** {br}\n"


def req(rid, parent="BR-02-01-001", extra=""):
    return f"## {rid} Title\n- **Statement:** The product shall work.\n- **Parent:** {parent}\n{extra}\n"


VALID = {
    "br/01-general.md": "# General\n\n### Context\n",
    "br/02-common/_index.md": "# Common\n",
    "br/02-common/01-product.md": brq("BR-02-01-001", "KPI-02-01-001") + brq("BR-02-01-002", "KPI-02-01-002, KPI-02-01-003"),
    "br/03-scope-a/02-finance.md": brq("BR-03-02-001", "KPI-03-02-001"),
    "kpi/02-common/01-product.md": kpi("KPI-02-01-001", "BR-02-01-001") + kpi("KPI-02-01-002", "BR-02-01-002 AC1") + kpi("KPI-02-01-003", "BR-02-01-002 AC2"),
    "kpi/03-scope-a/02-finance.md": kpi("KPI-03-02-001", "BR-03-02-001"),
    "prd/01-general.md": req("PRD-01-001", extra="- **Connects:** 02-03, 03-01\n"),
    "prd/02-app/_index.md": req("PRD-02-001", extra="- **Connects:** 02-01, 02-03\n"),
    "prd/02-app/01-account.md": req("PRD-02-01-001") + req("PRD-02-01-002", "BR-03-02-001"),
    "prd/02-app/03-reports.md": req("PRD-02-03-001"),
    "prd/02-app/04-modes/_index.md": req("PRD-02-04-001", extra="- **Connects:** 02-04-01, 02-04-02\n"),
    "prd/02-app/04-modes/01-advanced.md": req("PRD-02-04-01-001"),
    "prd/02-app/04-modes/02-basic.md": "# Basic\n\n## DIA-001 Flow\n\n" + req("PRD-02-04-02-001") + req("PRD-02-04-02-002") + req("PRD-02-04-02-003"),
    "prd/03-admin/01-dashboard.md": req("PRD-03-01-001"),
    "prd/README.md": "## Not checked\n",
    "tr/02-client/01-ui.md": req("TR-02-01-001", "PRD-02-04-02-003"),
}


def run(changes=None, remove=()):
    files = dict(VALID)
    files.update(changes or {})
    for r in remove:
        files.pop(r)
    with tempfile.TemporaryDirectory() as d:
        base = Path(d) / "docs" / "requirements"
        base.mkdir(parents=True)
        for rel, text in files.items():
            p = base / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        return check(d)


class CheckRequirements(unittest.TestCase):
    def has(self, errors, text):
        self.assertTrue(any(text in e for e in errors), errors)

    def test_valid_tree_passes(self):
        errors, counts = run()
        self.assertEqual(errors, [])
        self.assertEqual(counts, {"BR": 3, "KPI": 4, "PRD": 11, "TR": 1})

    def test_id_must_match_location(self):
        errors, _ = run({"prd/02-app/04-modes/01-advanced.md": req("PRD-02-04-02-009")})
        self.has(errors, "does not match its location")

    def test_index_takes_folder_number(self):
        errors, _ = run({"prd/02-app/04-modes/_index.md": req("PRD-02-04-01-001", extra="- **Connects:** 02-04-01, 02-04-02\n")})
        self.has(errors, "does not match its location")

    def test_bad_name_fails(self):
        errors, _ = run({"prd/02-app/Shop.md": req("PRD-02-05-001")})
        self.has(errors, "name must be NN-lowercase-name")

    def test_duplicate_number_fails(self):
        errors, _ = run({"prd/02-app/01-profile.md": req("PRD-02-01-009")})
        self.has(errors, "number 01 is already used")

    def test_root_01_reserved_for_general(self):
        errors, _ = run({"prd/01-other.md": req("PRD-01-001")}, remove=["prd/01-general.md"])
        self.has(errors, "reserved for 01-general.md")

    def test_root_index_fails(self):
        errors, _ = run({"prd/_index.md": req("PRD-01-002")})
        self.has(errors, "no _index.md at the layer root")

    def test_interface_in_module_file_fails(self):
        errors, _ = run({"prd/02-app/04-modes/01-advanced.md": req("PRD-02-04-01-001", extra="- **Connects:** 02-04-01, 02-04-02\n")})
        self.has(errors, "belongs in the chapter with IDs PRD-02-04-NNN")

    def test_cross_product_interface_goes_to_general(self):
        errors, _ = run({"prd/02-app/_index.md": req("PRD-02-001", extra="- **Connects:** 02-03, 03-01\n")})
        self.has(errors, "belongs in the chapter with IDs PRD-01-NNN")

    def test_unknown_module_fails(self):
        errors, _ = run({"prd/02-app/_index.md": req("PRD-02-001", extra="- **Connects:** 02-01, 02-09\n")})
        self.has(errors, "do not exist: 02-09")

    def test_duplicate_id_fails(self):
        errors, _ = run({"prd/02-app/03-reports.md": req("PRD-02-03-001") + req("PRD-02-03-001")})
        self.has(errors, "defined twice")

    def test_missing_parent_fails(self):
        errors, _ = run({"prd/02-app/03-reports.md": "## PRD-02-03-001 Title\n- **Statement:** x\n"})
        self.has(errors, "has no Parent field")

    def test_unknown_parent_fails(self):
        errors, _ = run({"tr/02-client/01-ui.md": req("TR-02-01-001", "PRD-02-04-02-099")})
        self.has(errors, "Parent PRD-02-04-02-099 does not exist")

    def test_wrong_parent_layer_fails(self):
        errors, _ = run({"tr/02-client/01-ui.md": req("TR-02-01-001", "BR-02-01-001")})
        self.has(errors, "Parent must name a PRD requirement")

    def test_unknown_br_parent_fails(self):
        errors, _ = run({"prd/02-app/03-reports.md": req("PRD-02-03-001", "BR-02-01-099")})
        self.has(errors, "Parent BR-02-01-099 does not exist")

    def test_br_id_must_match_location(self):
        errors, _ = run({"br/03-scope-a/02-finance.md": brq("BR-04-02-001", "KPI-03-02-001")})
        self.has(errors, "does not match its location")

    def test_br_without_kpi_field_fails(self):
        errors, _ = run({"br/03-scope-a/02-finance.md": "## BR-03-02-001 Title\n- **Statement:** x\n"})
        self.has(errors, "has no KPI field")

    def test_br_unknown_kpi_fails(self):
        errors, _ = run({"br/03-scope-a/02-finance.md": brq("BR-03-02-001", "KPI-03-02-001, KPI-03-02-009")})
        self.has(errors, "KPI KPI-03-02-009 does not exist")

    def test_kpi_must_mirror_br_file(self):
        errors, _ = run({"kpi/03-scope-a/02-finance.md": kpi("KPI-03-02-001", "BR-02-01-001")})
        self.has(errors, "belongs in the KPI file that mirrors BR-02-01-001")

    def test_kpi_must_be_listed_by_br(self):
        errors, _ = run({"kpi/02-common/01-product.md": kpi("KPI-02-01-001", "BR-02-01-001") + kpi("KPI-02-01-002", "BR-02-01-002") + kpi("KPI-02-01-003", "BR-02-01-002") + kpi("KPI-02-01-004", "BR-02-01-001")})
        self.has(errors, "KPI-02-01-004 is not listed in the KPI field of BR-02-01-001")

    def test_kpi_unknown_br_fails(self):
        errors, _ = run({"kpi/03-scope-a/02-finance.md": kpi("KPI-03-02-001", "BR-03-02-007")})
        self.has(errors, "Business requirement BR-03-02-007 does not exist")

    def test_other_heading_fails(self):
        errors, _ = run({"prd/02-app/03-reports.md": "## Notes\n" + req("PRD-02-03-001")})
        self.has(errors, "is not a requirement ID")


if __name__ == "__main__":
    unittest.main(verbosity=1)
