#!/usr/bin/env python3
"""Validate the Clearing workbook and build upload-ready data and HTML backup files.

This script intentionally uses only the Python standard library so it can run on a
managed Mac without installing packages. It reads the Office Open XML workbook
directly, validates the editorial data, stages all output, and only replaces the
current package when every blocking check passes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.9+ includes zoneinfo.
    ZoneInfo = None


SHEET_NAME = "Courses"
COURSE_TYPES = {"Undergraduate", "Foundation year"}
AVAILABILITIES = {"Vacancies", "Limited vacancies", "Waiting list", "Full"}
YES_NO = {"Yes", "No"}
PUBLIC_FIELDS = (
    "recordId",
    "academicYear",
    "title",
    "type",
    "status",
    "ucas",
    "requirements",
    "summary",
    "info",
    "entryRequirementsUrl",
    "url",
    "lastReviewed",
)
REQUIRED_COLUMNS = (
    "Record ID",
    "Academic Year",
    "Course Title",
    "Course Type",
    "Availability",
    "Typical Offer",
    "Entry Requirement Summary",
    "Course URL",
    "Display",
    "Last Reviewed",
    "Content Owner",
    "Change Note",
)
EDITOR_COLUMNS = {
    "Record ID",
    "Academic Year",
    "Course Title",
    "Course Type",
    "Availability",
    "UCAS Code",
    "Award",
    "Typical Offer",
    "Subject-specific Requirements",
    "Entry Requirement Summary",
    "Entry Requirements URL",
    "Course URL",
    "Display",
    "Last Reviewed",
    "Content Owner",
    "Change Note",
}
BACKUP_ASSETS = ("index.html", "styles.css", "app.js", "fuse.min.js", "robots.txt")
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CELL_REF_RE = re.compile(r"^([A-Z]+)(\d+)$")
UCAS_RE = re.compile(r"^[A-Z][A-Z0-9]{3}$")
RECORD_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,79}$")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class BuildError(Exception):
    """Raised for workbook or filesystem failures rather than data errors."""


@dataclass
class Issue:
    severity: str
    message: str
    row: int | None = None
    column: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "row": self.row,
            "column": self.column,
            "message": self.message,
        }


@dataclass
class WorkbookRow:
    number: int
    values: dict[str, Any]
    formula_columns: set[str] = field(default_factory=set)


@dataclass
class ValidationResult:
    records: list[dict[str, Any]]
    issues: list[Issue]
    source_rows: int
    suppressed_rows: int

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]


def now_london() -> datetime:
    if ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo("Europe/London"))
        except Exception:
            pass
    return datetime.now().astimezone()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def column_number(cell_ref: str) -> int:
    match = CELL_REF_RE.match(cell_ref)
    if not match:
        raise BuildError(f"Invalid cell reference in workbook: {cell_ref!r}")
    number = 0
    for character in match.group(1):
        number = number * 26 + ord(character) - 64
    return number


def normalise_member(target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return str(PurePosixPath("xl") / target)


def xml_text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return "".join(text.text or "" for text in node.iter() if text.tag.endswith("}t"))


def parse_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [xml_text(item) for item in root.findall("x:si", NS)]


def parse_cell(cell: ET.Element, shared_strings: list[str]) -> Any:
    cell_type = cell.get("t")
    if cell_type == "inlineStr":
        return xml_text(cell.find("x:is", NS))

    value_node = cell.find("x:v", NS)
    if value_node is None or value_node.text is None:
        return ""
    value = value_node.text

    if cell_type == "s":
        try:
            return shared_strings[int(value)]
        except (IndexError, ValueError) as exc:
            raise BuildError("Workbook contains an invalid shared-string reference") from exc
    if cell_type in {"str", "e"}:
        return value
    if cell_type == "b":
        return value == "1"
    if cell_type == "d":
        return value
    if cell_type in {None, "n"}:
        try:
            numeric = float(value)
            return int(numeric) if numeric.is_integer() else numeric
        except ValueError:
            return value
    return value


def read_courses_sheet(source: Path) -> tuple[list[str], list[WorkbookRow]]:
    try:
        archive = zipfile.ZipFile(source)
    except (OSError, zipfile.BadZipFile) as exc:
        raise BuildError(f"Cannot open {source.name} as an Excel .xlsx workbook") from exc

    with archive:
        try:
            workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
            relationship_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        except (KeyError, ET.ParseError) as exc:
            raise BuildError("The workbook is missing required Office XML parts") from exc

        relationships = {
            item.get("Id"): normalise_member(item.get("Target", ""))
            for item in relationship_root.findall("r:Relationship", REL_NS)
        }
        sheet_member = None
        for sheet in workbook_root.findall("x:sheets/x:sheet", NS):
            if sheet.get("name") == SHEET_NAME:
                relationship_id = sheet.get(f"{{{OFFICE_REL_NS}}}id")
                sheet_member = relationships.get(relationship_id)
                break
        if not sheet_member or sheet_member not in archive.namelist():
            raise BuildError(f"Workbook must contain a sheet named {SHEET_NAME!r}")

        shared_strings = parse_shared_strings(archive)
        try:
            sheet_root = ET.fromstring(archive.read(sheet_member))
        except ET.ParseError as exc:
            raise BuildError(f"The {SHEET_NAME!r} sheet XML is invalid") from exc

        raw_rows: list[tuple[int, dict[int, Any], set[int]]] = []
        for row in sheet_root.findall("x:sheetData/x:row", NS):
            row_number = int(row.get("r", "0"))
            cells: dict[int, Any] = {}
            formula_columns: set[int] = set()
            for cell in row.findall("x:c", NS):
                reference = cell.get("r", "")
                column = column_number(reference)
                cells[column] = parse_cell(cell, shared_strings)
                if cell.find("x:f", NS) is not None:
                    formula_columns.add(column)
            raw_rows.append((row_number, cells, formula_columns))

    header_index = None
    headers: list[str] = []
    for index, (_, cells, _) in enumerate(raw_rows[:30]):
        candidate = [str(cells.get(column, "")).strip() for column in range(1, max(cells, default=0) + 1)]
        if "Record ID" in candidate and "Course Title" in candidate:
            header_index = index
            headers = candidate
            break
    if header_index is None:
        raise BuildError("Could not find the Courses table header row")

    rows: list[WorkbookRow] = []
    for row_number, cells, formula_columns in raw_rows[header_index + 1 :]:
        values = {header: cells.get(index, "") for index, header in enumerate(headers, start=1) if header}
        if not any(str(values.get(column, "")).strip() for column in EDITOR_COLUMNS):
            continue
        formula_headers = {
            headers[column - 1]
            for column in formula_columns
            if 0 < column <= len(headers) and headers[column - 1]
        }
        rows.append(WorkbookRow(row_number, values, formula_headers))
    return headers, rows


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def excel_date(value: Any) -> date | None:
    if isinstance(value, (int, float)):
        try:
            return date(1899, 12, 30) + timedelta(days=int(value))
        except (OverflowError, ValueError):
            return None
    text = clean_text(value)
    if not text:
        return None
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def public_url(value: str, *, foundation_year: bool) -> str | None:
    if not value or CONTROL_RE.search(value) or any(character.isspace() for character in value):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    try:
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or parsed.hostname != "www.keele.ac.uk"
        or parsed.username
        or parsed.password
        or port not in {None, 443}
    ):
        return None
    if foundation_year and parsed.fragment.casefold() != "foundationyear":
        return None
    return value


def add_issue(issues: list[Issue], severity: str, row: int | None, column: str | None, message: str) -> None:
    issues.append(Issue(severity, message, row, column))


def validate(headers: list[str], rows: list[WorkbookRow], today: date) -> ValidationResult:
    issues: list[Issue] = []
    records: list[dict[str, Any]] = []
    suppressed = 0

    for column in REQUIRED_COLUMNS:
        if column not in headers:
            add_issue(issues, "error", None, column, "Required column is missing")
    if any(issue.severity == "error" for issue in issues):
        return ValidationResult([], issues, len(rows), 0)

    seen_ids: dict[str, int] = {}
    seen_routes: dict[tuple[str, str], int] = {}
    seen_urls: dict[str, int] = {}
    seen_ucas: dict[str, int] = {}

    for item in rows:
        row = item.values
        row_number = item.number
        row_errors_before = sum(issue.severity == "error" for issue in issues)

        for column in sorted(item.formula_columns & EDITOR_COLUMNS):
            add_issue(issues, "error", row_number, column, "Formulas are not allowed in editor-maintained cells")

        record_id = clean_text(row.get("Record ID"))
        title = clean_text(row.get("Course Title"))
        course_type = clean_text(row.get("Course Type"))
        availability = clean_text(row.get("Availability"))
        ucas = clean_text(row.get("UCAS Code")).upper()
        award = clean_text(row.get("Award"))
        typical_offer = clean_text(row.get("Typical Offer"))
        subject_specific = clean_text(row.get("Subject-specific Requirements"))
        info = clean_text(row.get("Entry Requirement Summary"))
        entry_url = clean_text(row.get("Entry Requirements URL"))
        course_url = clean_text(row.get("Course URL"))
        display = clean_text(row.get("Display"))
        owner = clean_text(row.get("Content Owner"))
        change_note = clean_text(row.get("Change Note"))
        reviewed = excel_date(row.get("Last Reviewed"))

        year_value = row.get("Academic Year")
        try:
            academic_year = int(year_value)
        except (TypeError, ValueError):
            academic_year = 0

        required_values = {
            "Record ID": record_id,
            "Course Title": title,
            "Course Type": course_type,
            "Availability": availability,
            "Typical Offer": typical_offer,
            "Entry Requirement Summary": info,
            "Course URL": course_url,
            "Display": display,
            "Content Owner": owner,
            "Change Note": change_note,
        }
        for column, value in required_values.items():
            if not value:
                add_issue(issues, "error", row_number, column, "Required value is blank")

        for column, value in {
            "Record ID": record_id,
            "Course Title": title,
            "Award": award,
            "Typical Offer": typical_offer,
            "Entry Requirement Summary": info,
            "Content Owner": owner,
            "Change Note": change_note,
        }.items():
            if CONTROL_RE.search(value):
                add_issue(issues, "error", row_number, column, "Contains a control character")
            if "<" in value or ">" in value:
                add_issue(issues, "error", row_number, column, "HTML markup is not allowed")

        if record_id and not RECORD_ID_RE.fullmatch(record_id):
            add_issue(issues, "error", row_number, "Record ID", "Use 3-80 letters, numbers, dots, underscores or hyphens")
        if record_id.casefold() in seen_ids:
            add_issue(issues, "error", row_number, "Record ID", f"Duplicate of row {seen_ids[record_id.casefold()]}")
        elif record_id:
            seen_ids[record_id.casefold()] = row_number

        route_key = (title.casefold(), course_type.casefold())
        if title and course_type and route_key in seen_routes:
            add_issue(issues, "error", row_number, "Course Title", f"Duplicate course route from row {seen_routes[route_key]}")
        elif title and course_type:
            seen_routes[route_key] = row_number

        if not 2026 <= academic_year <= 2030:
            add_issue(issues, "error", row_number, "Academic Year", "Must be a whole year from 2026 to 2030")
        if course_type not in COURSE_TYPES:
            add_issue(issues, "error", row_number, "Course Type", f"Must be one of: {', '.join(sorted(COURSE_TYPES))}")
        if availability not in AVAILABILITIES:
            add_issue(issues, "error", row_number, "Availability", f"Must be one of: {', '.join(sorted(AVAILABILITIES))}")
        if display not in YES_NO:
            add_issue(issues, "error", row_number, "Display", "Must be Yes or No")
        if subject_specific and subject_specific not in YES_NO:
            add_issue(issues, "error", row_number, "Subject-specific Requirements", "Must be Yes, No or blank")
        if ucas and not UCAS_RE.fullmatch(ucas):
            add_issue(issues, "error", row_number, "UCAS Code", "Must be four uppercase letters/numbers beginning with a letter")
        if ucas:
            if ucas in seen_ucas:
                add_issue(issues, "warning", row_number, "UCAS Code", f"Also used on row {seen_ucas[ucas]}; confirm this is intentional")
            else:
                seen_ucas[ucas] = row_number

        is_foundation = course_type == "Foundation year"
        if course_url and public_url(course_url, foundation_year=is_foundation) is None:
            suffix = " and include #foundationyear" if is_foundation else ""
            add_issue(issues, "error", row_number, "Course URL", f"Must be a clean https://www.keele.ac.uk/ URL{suffix}")
        if entry_url and public_url(entry_url, foundation_year=False) is None:
            add_issue(issues, "error", row_number, "Entry Requirements URL", "Must be a clean https://www.keele.ac.uk/ URL")
        if typical_offer.casefold() in {"course-specific", "see entry requirements"} and not entry_url:
            add_issue(issues, "error", row_number, "Entry Requirements URL", "Required when the typical offer is course-specific")
        if course_url:
            if course_url in seen_urls:
                add_issue(issues, "warning", row_number, "Course URL", f"Also used on row {seen_urls[course_url]}; confirm this is intentional")
            else:
                seen_urls[course_url] = row_number

        if reviewed is None:
            add_issue(issues, "error", row_number, "Last Reviewed", "Must contain a valid date")
        elif reviewed > today + timedelta(days=1):
            add_issue(issues, "error", row_number, "Last Reviewed", "Cannot be in the future")
        elif reviewed < today - timedelta(days=14):
            add_issue(issues, "warning", row_number, "Last Reviewed", "Was reviewed more than 14 days ago")

        if len(title) > 160:
            add_issue(issues, "error", row_number, "Course Title", "Must be 160 characters or fewer")
        if len(typical_offer) > 160:
            add_issue(issues, "error", row_number, "Typical Offer", "Must be 160 characters or fewer")
        if len(info) > 1000:
            add_issue(issues, "error", row_number, "Entry Requirement Summary", "Must be 1,000 characters or fewer")

        row_errors_after = sum(issue.severity == "error" for issue in issues)
        if display == "No":
            suppressed += 1
        if row_errors_after != row_errors_before or display != "Yes":
            continue

        requirements = typical_offer
        if typical_offer.casefold() in {"course-specific", "see entry requirements"}:
            requirements = "See entry requirements"
        summary = award or ("Foundation Year route" if is_foundation else "Undergraduate course")
        records.append(
            {
                "recordId": record_id,
                "academicYear": academic_year,
                "title": title,
                "type": course_type,
                "status": availability,
                "ucas": ucas,
                "requirements": requirements,
                "summary": summary,
                "info": info,
                "entryRequirementsUrl": entry_url,
                "url": course_url,
                "lastReviewed": reviewed.isoformat() if reviewed else "",
            }
        )

    records.sort(key=lambda record: (record["title"].casefold(), record["type"] != "Undergraduate"))
    if not rows:
        add_issue(issues, "error", None, None, "The Courses sheet contains no records")
    if rows and not records and not any(issue.severity == "error" for issue in issues):
        add_issue(issues, "error", None, "Display", "No records are marked for display")
    return ValidationResult(records, issues, len(rows), suppressed)


def report_payload(source: Path, result: ValidationResult, generated_at: datetime) -> dict[str, Any]:
    status_counts = Counter(record["status"] for record in result.records)
    type_counts = Counter(record["type"] for record in result.records)
    return {
        "valid": not result.errors,
        "generatedAt": generated_at.isoformat(timespec="seconds"),
        "source": source.name,
        "sourceRows": result.source_rows,
        "publishedRecords": len(result.records),
        "suppressedRecords": result.suppressed_rows,
        "errorCount": len(result.errors),
        "warningCount": len(result.warnings),
        "counts": {
            "availability": dict(sorted(status_counts.items())),
            "courseType": dict(sorted(type_counts.items())),
        },
        "issues": [issue.as_dict() for issue in result.issues],
    }


def text_report(payload: dict[str, Any]) -> str:
    state = "PASS" if payload["valid"] else "FAIL"
    lines = [
        f"Clearing data validation: {state}",
        f"Generated: {payload['generatedAt']}",
        f"Source: {payload['source']}",
        f"Source rows: {payload['sourceRows']}",
        f"Published records: {payload['publishedRecords']}",
        f"Suppressed records: {payload['suppressedRecords']}",
        f"Errors: {payload['errorCount']}",
        f"Warnings: {payload['warningCount']}",
        "",
    ]
    if payload["issues"]:
        lines.append("Issues")
        lines.append("------")
        for issue in payload["issues"]:
            location = ""
            if issue["row"]:
                location += f"row {issue['row']}"
            if issue["column"]:
                location += (", " if location else "") + issue["column"]
            lines.append(f"{issue['severity'].upper()}: {location or 'workbook'}: {issue['message']}")
    else:
        lines.append("No validation issues found.")
    return "\n".join(lines) + "\n"


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_backup_html(source: str, generated_at: datetime, record_count: int) -> str:
    machine_date = generated_at.date().isoformat()
    human_date = f"{generated_at.day} {generated_at.strftime('%B %Y')}"
    replacement = f'Page last modified: <time datetime="{machine_date}">{human_date}</time>'
    updated, count = re.subn(
        r'Page last modified:\s*<time datetime="[^"]+">[^<]+</time>',
        replacement,
        source,
        count=1,
    )
    if count != 1:
        raise BuildError("Could not update the page-last-modified text in index.html")
    updated, script_count = re.subn(
        r'<script src="build/clearing-data/current/courses\.js"></script>',
        '<script src="courses.js"></script>',
        updated,
        count=1,
    )
    if script_count != 1:
        raise BuildError("Could not rewrite the generated course-data path for the static backup")
    marker = f"<!-- Generated backup: {html.escape(generated_at.isoformat(timespec='seconds'))}; {record_count} records -->"
    return updated.replace("<!doctype html>", f"<!doctype html>\n{marker}", 1)


def unique_archive_path(archive_root: Path, timestamp: str) -> Path:
    candidate = archive_root / timestamp
    counter = 2
    while candidate.exists():
        candidate = archive_root / f"{timestamp}-{counter}"
        counter += 1
    return candidate


def build_package(
    source: Path,
    result: ValidationResult,
    payload: dict[str, Any],
    output_root: Path,
    assets_dir: Path,
    generated_at: datetime,
) -> tuple[Path, Path | None]:
    for asset in BACKUP_ASSETS:
        if not (assets_dir / asset).is_file():
            raise BuildError(f"Required backup asset is missing: {assets_dir / asset}")

    output_root.mkdir(parents=True, exist_ok=True)
    archive_root = output_root / "archive"
    current = output_root / "current"
    staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=output_root))
    archived: Path | None = None

    try:
        write_json(staging / "courses.json", result.records)
        (staging / "courses.js").write_text(
            "// Generated from the validated Clearing course workbook. Do not edit directly.\n"
            f"window.CLEARING_COURSES = Object.freeze({json.dumps(result.records, ensure_ascii=False, indent=2)});\n",
            encoding="utf-8",
        )

        with (staging / "courses.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=PUBLIC_FIELDS)
            writer.writeheader()
            writer.writerows(result.records)

        write_json(staging / "validation-report.json", payload)
        (staging / "validation-report.txt").write_text(text_report(payload), encoding="utf-8")

        backup = staging / "static-backup"
        backup.mkdir()
        for asset in BACKUP_ASSETS:
            shutil.copy2(assets_dir / asset, backup / asset)
        shutil.copy2(staging / "courses.js", backup / "courses.js")
        shutil.copy2(staging / "courses.json", backup / "courses.json")
        index_source = (assets_dir / "index.html").read_text(encoding="utf-8")
        (backup / "index.html").write_text(
            update_backup_html(index_source, generated_at, len(result.records)),
            encoding="utf-8",
        )

        notes = (
            "CLEARING DATA BUILD\n\n"
            "TerminalFour/server data: courses.json (or courses.js for the current prototype).\n"
            "Emergency static site: upload the complete contents of static-backup/.\n"
            "Review validation-report.txt and manifest.json before uploading anything.\n"
            "Do not edit generated files directly; update the controlled workbook and rebuild.\n"
        )
        (staging / "DEPLOYMENT-NOTES.txt").write_text(notes, encoding="utf-8")

        checksums = {
            str(path.relative_to(staging)): sha256(path)
            for path in sorted(staging.rglob("*"))
            if path.is_file()
        }
        manifest = {
            "schemaVersion": 1,
            "generatedAt": generated_at.isoformat(timespec="seconds"),
            "sourceFile": source.name,
            "sourceSha256": sha256(source),
            "publishedRecords": len(result.records),
            "suppressedRecords": result.suppressed_rows,
            "counts": payload["counts"],
            "files": checksums,
        }
        write_json(staging / "manifest.json", manifest)

        if current.exists():
            archive_root.mkdir(parents=True, exist_ok=True)
            archived = unique_archive_path(archive_root, generated_at.strftime("%Y%m%d-%H%M%S"))
            os.replace(current, archived)
        try:
            os.replace(staging, current)
        except Exception:
            if archived is not None and not current.exists():
                os.replace(archived, current)
                archived = None
            raise
        return current, archived
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise


def write_failed_report(output_root: Path, payload: dict[str, Any], generated_at: datetime) -> tuple[Path, Path]:
    reports = output_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    stem = f"validation-{generated_at.strftime('%Y%m%d-%H%M%S')}"
    json_path = reports / f"{stem}.json"
    text_path = reports / f"{stem}.txt"
    write_json(json_path, payload)
    text_path.write_text(text_report(payload), encoding="utf-8")
    return json_path, text_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Clearing course workbook and create upload-ready data and static HTML backup files."
    )
    parser.add_argument(
        "workbook",
        type=Path,
        nargs="?",
        default=Path("inputs/Clearing-2026-Course-Data-Master.xlsx"),
        help="Exported .xlsx workbook (default: inputs/Clearing-2026-Course-Data-Master.xlsx)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("build/clearing-data"),
        help="Build root containing current/, archive/ and reports/ (default: build/clearing-data)",
    )
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory containing index.html, app.js, styles.css and other backup assets",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate only; do not create or archive a package")
    parser.add_argument(
        "--expected-count",
        type=int,
        help="Fail unless the number of displayed, valid records exactly matches this count",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generated_at = now_london()
    source = args.workbook.expanduser()
    output_root = args.output_dir.expanduser()
    assets_dir = args.assets_dir.expanduser()

    if not source.is_file():
        print(f"BUILD ERROR: workbook not found: {source}", file=sys.stderr)
        return 2
    if source.suffix.casefold() != ".xlsx":
        print("BUILD ERROR: workbook must be an .xlsx file", file=sys.stderr)
        return 2

    try:
        headers, rows = read_courses_sheet(source)
        result = validate(headers, rows, generated_at.date())
        if args.expected_count is not None and len(result.records) != args.expected_count:
            add_issue(
                result.issues,
                "error",
                None,
                None,
                f"Expected {args.expected_count} displayed records but found {len(result.records)}",
            )
        payload = report_payload(source, result, generated_at)
    except BuildError as exc:
        print(f"BUILD ERROR: {exc}", file=sys.stderr)
        return 2

    print(text_report(payload), end="")
    if result.errors:
        json_report, text_path = write_failed_report(output_root, payload, generated_at)
        print(f"Live package unchanged. Reports: {text_path} and {json_report}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("Dry run complete; no package was written.")
        return 0

    try:
        current, archived = build_package(source, result, payload, output_root, assets_dir, generated_at)
    except (BuildError, OSError, ValueError) as exc:
        print(f"BUILD ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Built upload-ready package: {current}")
    if archived is not None:
        print(f"Archived previous package: {archived}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
