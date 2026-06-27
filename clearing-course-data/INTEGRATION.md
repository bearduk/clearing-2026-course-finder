# Integration prompt — wiring `clearing-course-data/` into k-website

Paste the section below to an agent working in the **k-website** repo (or follow
it yourself). It assumes the `clearing-course-data/` folder has already been
copied into the repo.

---

## Task: integrate the Clearing course-data module

A new self-contained folder, `clearing-course-data/`, has been added to this
repo. It is the **producer** of the Clearing course finder's source markup: a
Python generator (`build-clearing-data.py`) and a browser tool (`process.html`)
that read a controlled Excel workbook and emit `<article>` elements. The
**consumer** is this repo's existing `k-clearing-course-finder` content type,
which reads those elements' `data-*` attributes.

The reason for co-locating producer and consumer is to guard the contract
between them. Do the following.

### Hard constraints

1. **Do not add anything to the website build.** Nothing in
   `clearing-course-data/` may be wired into the npm/webpack/CI build that ships
   the site. The generator is a standalone, on-demand Python script; the browser
   tool is a static file deployed separately to webstage; the parity test is a
   dev tool. Confirm there is no bundler entry point, `package.json` script, or
   build step that pulls this folder into the site output. (A **separate**,
   non-blocking CI job that runs the parity test is fine — see step 4 — but it
   must not be part of the site build.)
2. **Keep the module's `.gitignore` rules** so workbook copies (`inputs/*`),
   generated `build/` output, and the dev-only `tools/node_modules/` are never
   committed.
3. Do not edit `build-clearing-data.py` or `process.html` validation logic as
   part of integration. If a contract mismatch is found (step 3), report it and
   propose the fix — do not silently change either side.

### Steps

1. **Place the folder** per this repo's conventions (top-level, or alongside the
   other content-type tooling — wherever a self-contained, non-shipped tool
   belongs). Update any repo index/README that lists modules.

2. **Locate the consumer.** Find the real `k-clearing-course-finder` source
   (the notes reference `t4/content-types/k-clearing-course-finder/`). Identify
   every `data-*` attribute it reads from the `#clearing-course-source`
   `<article>` elements (look for `dataset.*` and `getAttribute('data-…')`).

3. **Reconcile against the source contract.** The generator emits exactly these
   11 attributes per article, plus a `course-info` div:

   ```
   data-record-id  data-academic-year  data-title  data-type  data-status
   data-ucas  data-requirements  data-summary  data-entry-requirements-url
   data-url  data-last-reviewed
   <div class="course-info">…entry requirement summary…</div>
   ```

   The finder may additionally use a `letter` value and a `view` state — these
   are **derived by the finder itself** (letter from the title, view from UI
   state) and are NOT part of the source markup, so they are out of scope.
   Confirm the real finder reads only the 11 source attributes above (plus the
   `course-info` text). Report any attribute the finder reads that the generator
   does not emit, or vice versa.

4. **Add a cross-seam contract test.** Add a small, standalone test (its own
   script, not part of the site build) that:
   - extracts the set of `data-*` attributes emitted by the generator — parse
     them out of `process.html` / `build-clearing-data.py` (the
     `render_cms_source_article` template), and
   - extracts the set the finder reads from its source, and
   - asserts the two sets are equal (ignoring the finder-derived `letter`/`view`).

   Wire it next to the existing parity test so one command checks both seams:
   Python↔JS (already in `clearing-course-data/tools/parity_test.py`) and
   generator↔finder (new). Document how to run it.

5. **Optional CI:** add a separate workflow job (not gating the site build) that
   runs `python3 clearing-course-data/tools/parity_test.py` and the new contract
   test, so drift is caught in PRs. Requires Node + a one-off
   `cd clearing-course-data/tools && npm install` (installs `@xmldom/xmldom`, a
   test-only stand-in for the browser's `DOMParser`).

6. **Update the finder's notes** (e.g.
   `t4/content-types/k-clearing-course-finder/…-notes.md`) to point at
   `clearing-course-data/` as the source of the markup, and cross-link back so a
   future editor of either side sees the other.

### Done when

- The folder sits in a sensible location and is documented in the repo index.
- It is provably **not** part of the site build.
- The generator↔finder `data-*` contract is verified and any mismatch reported.
- A standalone contract test exists and passes, alongside the Python↔JS parity
  test.
- The finder's notes reference the module.
