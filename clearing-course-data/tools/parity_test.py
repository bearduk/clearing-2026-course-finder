#!/usr/bin/env python3
"""Parity test: prove process.html agrees with build-clearing-data.py.

Why this exists
---------------
process.html is a browser-only re-implementation of the validation rules,
record shaping and CMS HTML output in build-clearing-data.py. Two copies of the
same rules will eventually drift. This test is the gate that catches drift:

  1. Builds a set of small fixture workbooks exercising each error branch.
  2. Runs them through the REAL Python validator (build-clearing-data.py).
  3. Runs the same fixtures through the REAL JavaScript (extracted live from
     process.html, via Node) and asserts identical issue lists + record counts.
  4. If build/clearing-data/current/clearing-course-source-cms.html exists, also
     asserts the JS produces a byte-identical article body for the real workbook.

Run it whenever you change a rule in either file:

    python3 tools/parity_test.py

Requirements: Python 3 (stdlib only) and Node.js with @xmldom/xmldom installed
in tools/ (one-off: `cd tools && npm install`). The browser tool itself has no
dependencies — @xmldom is only a stand-in for the browser's built-in DOMParser
so the same code can run under Node for testing.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
REF_DATE = date(2026, 6, 23)  # fixed "today" so the test is deterministic
SERIAL = (REF_DATE - date(1899, 12, 30)).days

COLS = [
    "Record ID", "Course Title", "Course Type", "Availability", "UCAS Code",
    "Award", "Typical Offer", "Entry Requirement Summary",
    "Entry Requirements URL", "Course URL", "Display", "Last Reviewed",
]


def load_build_module():
    spec = importlib.util.spec_from_file_location("bcd", ROOT / "build-clearing-data.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bcd"] = mod
    spec.loader.exec_module(mod)
    return mod


def col_letter(n: int) -> str:
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def xesc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cell_xml(ref, val, formula=False) -> str:
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return f'<c r="{ref}"><v>{val}</v></c>'
    if formula:
        return f'<c r="{ref}" t="str"><f>A1</f><v>{xesc(str(val))}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{xesc(str(val))}</t></is></c>'


def sheet_xml(headers, rows) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    out.append('<row r="1">' + "".join(
        cell_xml(f"{col_letter(i + 1)}1", h) for i, h in enumerate(headers)) + "</row>")
    for ridx, row in enumerate(rows, start=2):
        cells = []
        for i, h in enumerate(headers):
            v = row.get(h, "")
            if v == "":
                continue
            cells.append(cell_xml(f"{col_letter(i + 1)}{ridx}", v, formula=row.get("__formula__") == h))
        out.append(f'<row r="{ridx}">' + "".join(cells) + "</row>")
    out.append("</sheetData></worksheet>")
    return "".join(out)


def make_xlsx(path: Path, headers, rows) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                   '<sheets><sheet name="Courses" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml(headers, rows))


def base_ug(**kw):
    r = {"Record ID": "UG-001", "Course Title": "Accounting", "Course Type": "Undergraduate",
         "Availability": "Vacancies", "UCAS Code": "A100", "Award": "BSc", "Typical Offer": "BBB",
         "Entry Requirement Summary": "Strong maths preferred.", "Entry Requirements URL": "",
         "Course URL": "https://www.keele.ac.uk/courses/accounting", "Display": "Yes", "Last Reviewed": SERIAL}
    r.update(kw)
    return r


def base_fy(**kw):
    r = {"Record ID": "FY-001", "Course Title": "Accounting", "Course Type": "Foundation year",
         "Availability": "Vacancies", "UCAS Code": "A101", "Award": "", "Typical Offer": "CCC",
         "Entry Requirement Summary": "Foundation entry.", "Entry Requirements URL": "",
         "Course URL": "https://www.keele.ac.uk/courses/accounting-fy#foundationyear", "Display": "Yes",
         "Last Reviewed": SERIAL}
    r.update(kw)
    return r


def fixtures():
    return {
        "valid_small": (COLS, [base_ug(), base_fy()]),
        "bad_url": (COLS, [base_ug(**{"Course URL": "http://www.keele.ac.uk/courses/accounting"})]),
        "formula_cell": (COLS, [base_ug(**{"__formula__": "Course Title"})]),
        "dup_id": (COLS, [base_ug(), base_ug(**{"Course Title": "Biology",
                                                "Course URL": "https://www.keele.ac.uk/courses/biology"})]),
        "missing_column": ([c for c in COLS if c != "Course URL"],
                           [{k: v for k, v in base_ug().items() if k != "Course URL"}]),
        "future_date": (COLS, [base_ug(**{"Last Reviewed": SERIAL + 400})]),
        "overlong_title": (COLS, [base_ug(**{"Course Title": "A" * 161})]),
        "no_display_yes": (COLS, [base_ug(**{"Display": "No"})]),
        "fy_no_fragment": (COLS, [base_fy(**{"Course URL": "https://www.keele.ac.uk/courses/accounting-fy"})]),
        "course_specific_no_entry": (COLS, [base_ug(**{"Typical Offer": "course-specific"})]),
        "html_markup": (COLS, [base_ug(**{"Course Title": "History <b>"})]),
        "bad_ucas": (COLS, [base_ug(**{"UCAS Code": "1ABC"})]),
    }


def main() -> int:
    bcd = load_build_module()
    tmp = Path(tempfile.mkdtemp(prefix="clearing-parity-"))

    oracle = {}
    for name, (headers, rows) in fixtures().items():
        p = tmp / f"{name}.xlsx"
        make_xlsx(p, headers, rows)
        h, r = bcd.read_courses_sheet(p)
        res = bcd.validate(h, r, REF_DATE)
        oracle[name] = {
            "records": len(res.records),
            "issues": [[i.severity, i.row, i.column, i.message] for i in res.issues],
        }
    (tmp / "oracle.json").write_text(json.dumps(oracle))

    real = ROOT / "inputs" / "Clearing-2026-Course-Data-Master.xlsx"
    if not real.exists():
        real = ROOT / "Clearing-2026-Course-Data-Master.xlsx"
    real_arg = str(real) if real.exists() else "-"

    try:
        proc = subprocess.run(
            ["node", str(TOOLS / "run_core.cjs"), str(tmp), real_arg, REF_DATE.isoformat()],
            cwd=str(TOOLS), capture_output=True, text=True,
        )
    except FileNotFoundError:
        print("FAIL: Node.js is not installed or not on PATH.")
        return 2
    if proc.returncode == 2 and "MISSING_DEP" in proc.stderr:
        print("FAIL: @xmldom/xmldom not installed. Run:  cd tools && npm install")
        return 2
    if proc.returncode != 0:
        print("FAIL: Node runner errored:\n" + proc.stderr)
        return 2

    js = json.loads(proc.stdout)

    passed = failed = 0
    for name in oracle:
        exp, got = oracle[name], js["fixtures"].get(name, {})
        ok = got.get("issues") == exp["issues"] and got.get("records") == exp["records"]
        print(("PASS  " if ok else "FAIL  ") + name)
        if ok:
            passed += 1
        else:
            failed += 1
            print("   expected:", json.dumps(exp["issues"]))
            print("   got     :", json.dumps(got.get("issues")),
                  "records js/py:", got.get("records"), "/", exp["records"],
                  ("ERROR " + got["error"]) if got.get("error") else "")

    # Real-workbook byte-identical article check (strongest test, hundreds of rows)
    cms = ROOT / "build" / "clearing-data" / "current" / "clearing-course-source-cms.html"
    if js.get("real") and cms.exists():
        py_body = cms.read_text(encoding="utf-8")
        py_body = py_body[py_body.index("-->\n\n") + 5:]
        if js["real"]["articleBody"] == py_body:
            print(f"PASS  real workbook — article body byte-identical ({js['real']['records']} records)")
            passed += 1
        else:
            print("FAIL  real workbook — article body differs from current/ build")
            failed += 1
    else:
        print("SKIP  real workbook byte check (no current/ build to compare against)")

    print(f"\n{passed}/{passed + failed} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
