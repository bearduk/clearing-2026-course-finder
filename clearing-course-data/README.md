# Clearing course data

Self-contained module for turning the controlled Clearing course workbook into
the markup the Clearing course finder reads. It lives in the k-website repo so
the data **producer** (this module) and the **consumer** (the
`k-clearing-course-finder` content type) sit in one place and can be changed and
tested together.

> **No website-build coupling.** Nothing here hooks into k-website's npm/CI
> build. Everything runs as a standalone script or a static file. Do not add any
> of it to the site build pipeline.

## What's here

| Path | What it is | How it runs |
|------|-----------|-------------|
| `build-clearing-data.py` | The generator. Reads the `.xlsx`, validates it, and emits the CMS source HTML plus JSON/CSV/static backup. Python standard library only. | Manual/seasonal: `python3 build-clearing-data.py <workbook>` |
| `process.html` | Browser version of the same thing: an editor uploads the workbook, validates, and copies the CMS HTML. No server, no dependencies, no upload. | Static file; deployed on its own to `webstage.keele.ac.uk` |
| `tools/` | Parity test: proves `process.html` and `build-clearing-data.py` agree. | Dev-only: `python3 tools/parity_test.py` |
| `docs/web-tool-spec.md` | Design spec for the browser tool. | Reference |
| `reference/` | Proof-of-concept of the consumer (`cms-course-reader.js`) and the TerminalFour content-type notes — i.e. the `data-*` contract. | Reference; reconcile with the real finder (see below) |
| `demo/` | Standalone demo / emergency static backup of the finder (Fuse.js search). | Optional static site |
| `inputs/` | Where an approved working copy of the workbook is placed at build time (git-ignored). | — |

## The data-* contract (the reason this is co-located)

`build-clearing-data.py` and `process.html` emit one `<article>` per published
course with these 11 attributes, plus a `course-info` div:

```
data-record-id  data-academic-year  data-title  data-type  data-status
data-ucas  data-requirements  data-summary  data-entry-requirements-url
data-url  data-last-reviewed
<div class="course-info">…entry requirement summary…</div>
```

The finder reads exactly these. (`letter` and the current `view` are derived by
the finder itself and are **not** part of the source contract.) If you rename or
add an attribute, change it in the generator **and** the finder **and** the
parity/contract test in the same PR. See `INTEGRATION.md` for wiring the
cross-seam test against the real `k-clearing-course-finder`.

## Keeping the two implementations in lock-step

The validation rules, record shaping and HTML output exist twice: Python
(`build-clearing-data.py`) and JavaScript (`process.html`). The parity test is
the gate that catches drift:

```bash
cd tools && npm install      # one-off; installs a Node stand-in for DOMParser
python3 tools/parity_test.py # run after any rule change in either file
```

`@xmldom/xmldom` is a **test-only** substitute for the browser's built-in
`DOMParser`; the shipped `process.html` has no dependencies.

## Deploy paths (kept separate on purpose)

- **CMS finder data:** run the generator, paste `clearing-course-source-cms.html`
  into `#clearing-course-source` on the Clearing page in TerminalFour, record the
  release in the workbook Change Log.
- **Browser tool:** publish `process.html` as a standalone page on webstage.
- These are independent. Folding the code into k-website does not make either
  deploy with the site build.

## Deliberately not included from the prototype repo

The legacy Word importer (`scripts/import_courses.py`, `archive/legacy-word-import/`)
and a one-off audit `.docx` were left out as not needed going forward. Pull them
across separately if you want them for traceability.
