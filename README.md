# Keele Clearing course finder proof of concept

A dependency-free prototype for showing undergraduate and foundation year Clearing courses in one searchable A-Z. Open `index.html` directly or serve the folder with any static web server.

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
- A generated dataset imported from the supplied Clearing 2026 Word document

## Proposed TerminalFour Content Type

Create one parent content item containing a repeatable `Courses` group. Suggested elements:

| Element | Type | Required | Example |
| --- | --- | --- | --- |
| Course title | Plain text | Yes | Biology |
| Course type | Select list | Yes | Undergraduate / Foundation year |
| UCAS code | Plain text | No | C100 |
| Short description | Plain text or 1-line HTML | Yes | Explore life from molecules... |
| Entry requirements summary | Plain text | Yes | BBC / 112 UCAS tariff points |
| Entry requirements info | HTML | No | A science subject is normally required... |
| Entry requirements URL | Link or plain text | No | https://www.keele.ac.uk/clearing/entry-requirements/ |
| Full course URL | Link or plain text | Yes | https://www.keele.ac.uk/.../biology/ |
| Availability | Select list | Yes | Vacancies / Limited vacancies / Waiting list / Full |
| Display order | Number | No | 10 |

The Content Layout would output each repeatable item as either JSON consumed by `app.js`, or as semantic `<article>` markup carrying values in `data-*` attributes. JSON is simpler to filter and reduces duplicated markup.

## Building approved course data

The controlled Excel workbook is the editorial source for ongoing Clearing updates. Export or download the approved `.xlsx` from Teams, then validate it without changing any live files:

```bash
python3 build-clearing-data.py "/path/to/Clearing-2026-Course-Data-Master.xlsx" --dry-run
```

When the report passes and its warnings have been reviewed, create the upload package:

```bash
python3 build-clearing-data.py "/path/to/Clearing-2026-Course-Data-Master.xlsx"
```

The script uses only Python's standard library. A successful run creates:

- `build/clearing-data/current/courses.json` for a TerminalFour or server integration
- `build/clearing-data/current/courses.js` for the current prototype
- `build/clearing-data/current/courses.csv` for audit and checking
- `build/clearing-data/current/static-backup/` as a complete emergency HTML site
- `manifest.json`, SHA-256 checksums and human/machine-readable validation reports

The build is fail-closed. Validation errors produce a report under `build/clearing-data/reports/` but do not replace `current/`. On each later successful build, the previous `current/` package moves to a timestamped folder under `archive/` before the new staged package is promoted. Upload generated files only; never edit them directly.

Use `--expected-count 372` when a separately approved total is available. This catches an accidental bulk deletion even when the remaining rows are individually valid. The number should come from the release approval, not simply from the previous build.

## Original Word import

The UI initially used a one-off import from the supplied working Word document:

```bash
python3 scripts/import_courses.py "/path/to/Clearing vacancies and ER page for 2026.docx" --output courses.js
```

The importer merges the undergraduate vacancy list and Foundation Year A-Z, preserves document hyperlinks, appends `#foundationyear` to FY links, standardises tariff wording and carries known vacancy statuses into the dataset. It is retained for traceability, but it is not the ongoing production workflow once the Excel master is in use.

## Production notes

- The sample availability, UCAS codes and requirements in `app.js` are not approved Clearing data.
- Confirm whether the source of truth will be manually maintained in TerminalFour or imported from a course system.
- Add `Last reviewed` and optional `Clearing note` fields if editors need time-sensitive messaging.
- Use Keele's production header/footer and existing design tokens when moved into the main site.
- Run an accessibility review with the component inside the full Keele template.

## Search behaviour

Fuse.js is loaded locally from `fuse.min.js`, so search also works when `index.html` is opened directly. Results are weighted toward course titles, followed by the short description, additional entry information and requirements. The threshold is deliberately forgiving enough to match common misspellings without making unrelated results too prominent.
