# Keele Clearing course finder proof of concept

A dependency-free prototype for showing undergraduate and foundation year Clearing courses in one searchable A–Z. Course data is maintained in a controlled Excel workbook, validated locally, and published as generated files.

This is a public proof of concept, not a production service. Search indexing is discouraged through page-level `noindex` directives and a site-wide `robots.txt` disallow rule.

## What the prototype demonstrates

- Fuzzy search across course title, description and requirements (Fuse.js)
- Undergraduate / Foundation year filters and availability filtering
- A–Z filtering, card and table views
- Expandable entry-requirement information
- Links to full Keele course pages
- Responsive layout and keyboard-accessible controls
- A validated dataset generated from the controlled Excel workbook

## Data architecture

1. Teams/SharePoint holds the controlled Excel master and its version history.
2. An approved copy is downloaded to `inputs/Clearing-2026-Course-Data-Master.xlsx` (or use the repo root copy).
3. `build-clearing-data.py` validates every row and generates the publish package.
4. **TerminalFour (recommended):** paste `clearing-course-source-cms.html` into `#clearing-course-source` on the Clearing page; the k-website finder JS reads the markup.
5. **GitHub demo / emergency backup:** loads `build/clearing-data/current/courses.js` via `index.html`.

The Excel workbook is the only editorial source. Generated files must never be edited directly.

## Excel workbook columns

Editor-maintained columns on the **Courses** sheet:

| Column | Required |
|--------|----------|
| Record ID | Yes |
| Course Title | Yes |
| Course Type | Yes |
| Availability | Yes |
| UCAS Code | No |
| Award | No |
| Typical Offer | Yes |
| Entry Requirement Summary | Yes |
| Entry Requirements URL | No |
| Course URL | Yes |
| Display | Yes |
| Last Reviewed | Yes |
| Row Check | Formula (do not edit) |

Academic year is hardcoded to **2026** in the build (`CLEARING_ACADEMIC_YEAR`). Governance uses the **Change Log** sheet, not per-row owner/note columns.

See **START HERE** in the workbook for editing workflow and entry-requirements guidance.

## Building approved course data

```bash
python3 build-clearing-data.py --dry-run Clearing-2026-Course-Data-Master.xlsx
```

When the report passes (review warnings), create the package:

```bash
python3 build-clearing-data.py Clearing-2026-Course-Data-Master.xlsx
```

A successful run creates under `build/clearing-data/current/`:

| Output | Use |
|--------|-----|
| `clearing-course-source-cms.html` | **Paste into TerminalFour** `#clearing-course-source` (articles only) |
| `courses.json` / `courses.js` | GitHub demo, integrations |
| `courses.csv` | Audit |
| `static-backup/` | Emergency static site |
| `validation-report.txt` | Pre-publish check |

The build is fail-closed: errors do not replace `current/`. Previous packages archive to `build/clearing-data/archive/`.

Use `--expected-count 372` when a separately approved total is available.

## CMS publish workflow (k-website)

1. Run build (0 errors).
2. Copy contents of `clearing-course-source-cms.html`.
3. In T4, replace articles inside `<div id="clearing-course-source" hidden>` on the Clearing page.
4. Ensure the page also has `#clearing-cms-validation` and the `k-clearing-course-finder` module (one-time setup).
5. Preview with k-website `npm run watch` + t4proxy.
6. Record release in workbook **Change Log**.

Full CMS handoff: `k-website` repo → `t4/content-types/k-clearing-course-finder/k-clearing-course-finder-notes.md`.

## Original Word import

```bash
python3 scripts/import_courses.py "/path/to/Clearing vacancies and ER page for 2026.docx"
```

Retained for traceability only. The Excel master is the ongoing workflow.

## Production notes

- Restrict edit access to the Teams master; retain version history.
- Second-person review before paste/publish (QA Dashboard in workbook).
- Confirm approved record total; do not copy the previous build count blindly.
- TerminalFour presents generated data; do not maintain a second manual source.
- Run accessibility review with the component in the full Keele template.
