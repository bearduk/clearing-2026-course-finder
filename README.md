# Keele Clearing course finder proof of concept

A dependency-free prototype for showing undergraduate and foundation year Clearing courses in one searchable A-Z. Course data is maintained in a controlled Excel workbook, validated locally, and published as generated files. Open `index.html` directly or serve the folder with any static web server after running the build.

This is a public proof of concept, not a production service. Search indexing is discouraged through page-level `noindex` directives and a site-wide `robots.txt` disallow rule. These measures are not authentication and do not make a published URL private.

## What the prototype demonstrates

- Fuzzy search across course title, description and requirements, powered by a locally vendored Fuse.js 7.1.0 build
- Undergraduate/Foundation Year filters
- Availability filtering for vacancies, limited vacancies, waiting lists and full courses
- A-Z filtering
- Card and compact table-style views
- Expandable entry-requirement information
- Links to full Keele course pages
- Responsive layout and keyboard-accessible controls
- An explicit warning that the prototype data is illustrative
- A page last-modified date, ready to map to TerminalFour metadata
- A validated dataset generated from the controlled Clearing Excel workbook

## Data architecture

The working model is deliberately separate from TerminalFour content items:

1. Teams/SharePoint holds the controlled Excel master and its version history.
2. An approved copy is downloaded to `inputs/Clearing-2026-Course-Data-Master.xlsx`.
3. `build-clearing-data.py` validates every row and generates the public data package.
4. The main prototype loads `build/clearing-data/current/courses.js`.
5. TerminalFour can use the generated `courses.json` or `courses.js` without creating one section or content item per course.
6. `static-backup/` is uploaded as a complete emergency site if the TerminalFour presentation is unavailable.

The Excel workbook is the only editorial source. Generated JSON, JavaScript, CSV and HTML files must never be edited directly.

## Building approved course data

The controlled Excel workbook in Teams is the editorial source for ongoing Clearing updates. Download the approved copy to `inputs/Clearing-2026-Course-Data-Master.xlsx`, replacing the previous local input, then validate it without changing any live files:

```bash
python3 build-clearing-data.py --dry-run
```

When the report passes and its warnings have been reviewed, create the upload package:

```bash
python3 build-clearing-data.py
```

Before uploading, read `build/clearing-data/current/validation-report.txt`, confirm the approved total and warning decisions, and spot-check the generated static backup. Upload the required generated data file for TerminalFour and the complete `static-backup/` directory to its agreed emergency location.

The `inputs/` directory is local working space and is excluded from Git so the editorial workbook is not published through GitHub Pages. The script uses only Python's standard library. A successful run creates:

- `build/clearing-data/current/courses.json` for a TerminalFour or server integration
- `build/clearing-data/current/courses.js` for the current prototype
- `build/clearing-data/current/courses.csv` for audit and checking
- `build/clearing-data/current/static-backup/` as a complete emergency HTML site
- `manifest.json`, SHA-256 checksums and human/machine-readable validation reports

The build is fail-closed. Validation errors produce a report under `build/clearing-data/reports/` but do not replace `current/`. On each later successful build, the previous `current/` package moves to a timestamped folder under `archive/` before the new staged package is promoted. Upload generated files only; never edit them directly.

The old `outputs/` directory contains only workbook-generation artefacts and visual previews. It is not read by the site or build process and can be deleted.

Use `--expected-count 372` when a separately approved total is available. This catches an accidental bulk deletion even when the remaining rows are individually valid. The number should come from the release approval, not simply from the previous build.

## Original Word import

The UI initially used a one-off import from the supplied working Word document:

```bash
python3 scripts/import_courses.py "/path/to/Clearing vacancies and ER page for 2026.docx"
```

The importer writes to `archive/legacy-word-import/courses.js` by default. It merges the undergraduate vacancy list and Foundation Year A-Z, preserves document hyperlinks, appends `#foundationyear` to FY links, standardises tariff wording and carries known vacancy statuses into the dataset. It is retained for traceability, but it is not the ongoing production workflow once the Excel master is in use.

## Production notes

- Keep edit access to the Teams master restricted to the named officers and retain SharePoint version history.
- Use the second-person review and release record described in the workbook before uploading generated files.
- Confirm the separately approved record total instead of copying the previous build's total automatically.
- Keep the emergency static backup in a distinct, documented server location and test it after each upload.
- TerminalFour should present the generated data; it should not become a second manually maintained source.
- Use Keele's production header/footer and existing design tokens when moved into the main site.
- Run an accessibility review with the component inside the full Keele template.

## Search behaviour

Fuse.js is loaded locally from `fuse.min.js`, so search also works when `index.html` is opened directly. Results are weighted toward course titles, followed by the short description, additional entry information and requirements. The threshold is deliberately forgiving enough to match common misspellings without making unrelated results too prominent.
