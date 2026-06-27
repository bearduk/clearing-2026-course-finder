# Spec: client-side Excel → CMS HTML web tool

**Status:** proposal / not yet built
**Author:** drafted for Chris, 23 June 2026
**Goal:** a single page on `webstage.keele.ac.uk` where an editor uploads the controlled Clearing workbook, clicks one button, sees the validation result, and copies the CMS-ready HTML — with no server-side processing.

This replaces the local `python3 build-clearing-data.py` step for the *paste-into-T4* use case. It does **not** replace the Python build for the GitHub demo / static backup outputs.

---

## 1. Why client-side

`webstage` can run server code, but the request was to avoid that complication, and the data is not sensitive. Everything the CLI needs is reproducible in the browser:

- A `.xlsx` is a ZIP of XML — readable in JS with no upload.
- The validation ruleset is plain string/regex/date logic.
- The CMS output is a deterministic string template.

So the whole tool is one static HTML file. Nothing is uploaded anywhere; the workbook never leaves the editor's machine.

## 2. The one real risk: logic drift

The single biggest danger is that the browser tool and `build-clearing-data.py` disagree — the web tool passes a row the CLI would reject (or vice versa), and something bad reaches the CMS. The whole spec is built around preventing that.

Mitigations, in order of importance:

1. **One canonical rule list.** Treat the validation rules in section 5 as the contract. Any change to `build-clearing-data.py` must be mirrored here and in the page, and vice versa. Put a short note at the top of both files pointing at the other.
2. **Shared test fixtures.** A small set of workbooks with known-good and known-bad rows, with the expected pass/fail outcome recorded. Both the Python and the JS must produce the same verdict on every fixture. This is the verification gate (section 9).
3. **Identical parsing approach** (see section 3) so cell values are read the same way in both.
4. **Version stamp.** The page shows a `RULESET` version string; the CLI output already carries a generated-by comment. If they diverge, it's visible.

## 3. XLSX parsing — recommendation: vanilla, no dependency

You asked for whichever is easier and less prone to issues. Recommendation: **parse the OOXML directly in JS, mirroring `build-clearing-data.py`** rather than pulling in SheetJS.

Reasoning:

- **Less drift.** The Python already reads `xl/workbook.xml`, resolves the `Courses` sheet via rels, reads `sharedStrings.xml`, and converts cells — including the Excel serial-date offset (`date(1899,12,30) + days`). If the JS does the same steps, the two implementations read every cell identically. SheetJS coerces dates, numbers and strings with its own rules, which you'd then have to reconcile against the Python — exactly the drift we're trying to avoid.
- **No CDN / CSP problem.** A `webstage` page may sit behind a content-security policy that blocks external scripts. A self-contained file with no `<script src>` sidesteps that and matches the repo's existing dependency-free ethos (the README calls this out explicitly).
- **Smaller surface.** SheetJS is large and does far more than needed (formulas, styles, multiple formats). We only need: unzip, read three XML parts, pull one sheet.

Cost: we hand-write a small ZIP reader. In the browser this is straightforward using `DecompressionStream('deflate-raw')` (supported in current Chrome/Edge/Firefox/Safari) on each ZIP entry, or a tiny inflate routine if older browser support is needed. The XML parsing uses the built-in `DOMParser`. No third-party code.

If, in build, the hand-rolled ZIP reader proves fiddly for the editor's browser baseline, the fallback is SheetJS *for the unzip + sheet-to-rows step only*, while keeping our own validation and date handling on top of the raw cell values — but start vanilla.

## 4. Page flow (UX)

A single screen, three states:

1. **Idle** — title, one-line instructions, a file picker / drop zone that accepts `.xlsx`. No "process" button needed; selecting the file runs it, or keep an explicit **Process** button if you prefer a deliberate action (recommended, mirrors the mental model).
2. **Result — pass** — green banner "Validation passed: N records". A summary line (source rows, published, suppressed, warnings count). A collapsible warnings list. Below: a read-only textarea with the CMS HTML and a **Copy** button. A reminder line: "Paste inside `<div id=\"clearing-course-source\" hidden>` and record the release in the workbook Change Log."
3. **Result — fail** — red banner "Validation failed: N errors". The full issue list (errors then warnings), each as `ERROR row 42, Course URL: must be a clean https://www.keele.ac.uk/ URL`. **No HTML output is shown** — fail-closed, mirroring the CLI which never replaces `current/` on error.

Re-running on a new file resets cleanly. Everything in-memory; no storage.

Accessibility: keyboard-operable controls, proper labels, banner uses text + colour (not colour alone), since this lives in the Keele estate.

## 5. Validation rules to port (the contract)

Ported verbatim from `build-clearing-data.py`. Today's date is the browser's local date (the CLI uses Europe/London — the page should also compute London date to match around midnight).

**Structure**
- Sheet named `Courses` must exist; find the header row within the first 30 rows by locating both `Record ID` and `Course Title`.
- These columns must be present, else hard fail: Record ID, Course Title, Course Type, Availability, Typical Offer, Entry Requirement Summary, Course URL, Display, Last Reviewed.
- A row is ignored entirely if every editor column is blank.

**Per-row errors**
- No formulas in any editor-maintained cell.
- Required-and-blank check on: Record ID, Course Title, Course Type, Availability, Typical Offer, Entry Requirement Summary, Course URL, Display.
- Control characters forbidden in: Record ID, Course Title, Award, Typical Offer, Entry Requirement Summary.
- `<` or `>` forbidden in those same five fields (no HTML markup).
- Record ID matches `^[A-Za-z0-9][A-Za-z0-9._-]{2,79}$`; must be unique (case-insensitive).
- (Course Title + Course Type) route must be unique (case-insensitive).
- Course Type ∈ {Undergraduate, Foundation year}.
- Availability ∈ {Vacancies, Limited vacancies, Waiting list, Full}.
- Display ∈ {Yes, No}.
- UCAS Code, if present, matches `^[A-Z][A-Z0-9]{3}$` (uppercase it first).
- Course URL must be a clean `https://www.keele.ac.uk/` URL — https scheme, exact host, no user/pass, no non-443 port, no whitespace, no control chars. For Foundation year rows the fragment must be `#foundationyear`.
- Entry Requirements URL, if present, must be a clean `https://www.keele.ac.uk/` URL (no fragment rule).
- Entry Requirements URL is required when Typical Offer is `course-specific` or `see entry requirements`.
- Last Reviewed must parse to a valid date and not be in the future (allow +1 day tolerance).
- Length caps: Course Title ≤ 160, Typical Offer ≤ 160, Entry Requirement Summary ≤ 1000.

**Per-row warnings**
- Duplicate UCAS Code across rows.
- Duplicate Course URL across rows.
- Last Reviewed more than 14 days old.

**Workbook-level**
- No rows at all → error.
- Rows exist but none marked Display = Yes (and no other errors) → error.

**Record selection / shaping (only rows with Display = Yes and no errors)**
- `requirements` = Typical Offer, except `course-specific` / `see entry requirements` → `See entry requirements`.
- `summary` = Award, else `Foundation Year route` (Foundation) or `Undergraduate course`.
- Fields emitted: recordId, academicYear (hardcoded **2026**), title, type, status (availability), ucas, requirements, summary, info (the Entry Requirement Summary), entryRequirementsUrl, url, lastReviewed (ISO date).
- Sort: by title (case-insensitive), Undergraduate before Foundation within the same title.

**Date parsing** (match `excel_date`)
- Numeric serial → `1899-12-30` + n days.
- Text, try in order: `%Y-%m-%d`, `%d/%m/%Y`, `%d-%m-%Y`, `%d %B %Y`, `%d %b %Y`, then ISO 8601.

## 6. Output format

Byte-for-byte the same as `render_cms_source_html`:

- Leading comment block: generated-by, source filename, generated timestamp, record count, paste-location reminder.
- One `<article class="clearing-course-source-item" …>` per record, with all the `data-*` attributes HTML-escaped (`html.escape` with `quote=True` for attribute values; default escaping for the `.course-info` text), and a `<div class="course-info">` body.

The CMS finder JS in `k-website` reads these attributes, so the attribute names and escaping must match exactly. This is part of the fixture verification — diff the JS output against the Python output for the same workbook and require zero difference.

## 7. What this tool deliberately does NOT do

- Does not generate `courses.json` / `courses.js` / `courses.csv` / the static backup. Those stay with the Python build for the GitHub demo path.
- Does not write to the workbook's Change Log — that governance step remains manual.
- Does not enforce who runs it. The page is unauthenticated. Because the only output is HTML the editor still has to consciously paste into T4, this is acceptable, but note it: the tool produces *candidate* HTML, T4 publishing remains the controlled gate.

## 8. Deployment

A single `process.html` (optionally `clearing-process.html`) placed on `webstage.keele.ac.uk`. No build step, no dependencies, no server config. Add it to this repo so it is version-controlled alongside the Python whose rules it mirrors. Apply the same `noindex` / robots posture as the rest of the prototype.

## 9. Verification plan (the gate before trusting it)

1. **Fixture set.** Build 6–10 small workbooks: an all-valid one, plus one per error class (bad URL, formula in cell, duplicate ID, missing column, future date, over-length field, no Display=Yes, etc.) and a warnings-only one.
2. **Oracle.** Run each through `build-clearing-data.py` and record the expected verdict + (for passing ones) the exact `clearing-course-source-cms.html`.
3. **Parity test.** Run each through the page; assert same pass/fail, same issue list, and identical HTML output (string diff). Any mismatch is a blocker.
4. **Manual spot-check** in the real Keele template that pasted output renders in the finder.
5. Re-run the parity test whenever either implementation's rules change.

## 10. Suggested build phases

1. ZIP + OOXML reader → rows of cells (verify against one real workbook).
2. Port validation + record shaping; wire the fixture parity test.
3. Port the CMS HTML template; assert byte-identical output on fixtures.
4. UX shell (drop zone, banners, copy button, accessibility pass).
5. Deploy to webstage, noindex, link from internal docs; add the cross-reference note to `build-clearing-data.py`.

---

**Open question for you:** browser baseline. `DecompressionStream('deflate-raw')` is the clean no-dependency route but needs reasonably current browsers. Do editors use a managed, current Chrome/Edge, or do we need to support something older? That decides whether the vanilla path holds or we bring in a tiny inflate helper.
