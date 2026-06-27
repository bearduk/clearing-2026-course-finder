# tools/ — parity test

`process.html` (the browser upload-and-copy tool) re-implements the validation
rules, record shaping and CMS HTML output from `build-clearing-data.py`. Two
copies of the same rules drift over time. This test catches drift.

## Run it

One-off setup (installs a Node stand-in for the browser's built-in XML parser):

```bash
cd tools && npm install
```

Then, from the repo root, whenever you change a rule in **either**
`build-clearing-data.py` or `process.html`:

```bash
python3 tools/parity_test.py
```

Green = the browser tool and the Python build agree. A non-zero exit means they
diverged — fix whichever file is wrong before publishing.

## What it checks

- A dozen fixture workbooks, one per error branch (bad URL, formula in a cell,
  duplicate ID, missing column, future date, over-length field, no Display=Yes,
  foundation-year fragment, course-specific offer, HTML markup, bad UCAS). Each
  must produce the **exact same issue list and record count** from the Python
  validator and from the JavaScript in `process.html`.
- If a `build/clearing-data/current/clearing-course-source-cms.html` is present,
  the real workbook's article output must be **byte-identical** between the two.

The JavaScript is extracted live from `process.html` at run time, so the test
always exercises the shipped file — there is no second copy to keep in sync.

## Notes

- The shipped `process.html` has **no dependencies**. `@xmldom/xmldom` is only a
  test-time substitute for `DOMParser`, which browsers provide natively but Node
  does not. It is never part of what you deploy.
- `node_modules/` here is dev-only and git-ignored.
