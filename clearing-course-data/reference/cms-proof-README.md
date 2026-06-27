# TerminalFour CMS proof of concept

This folder explores a CMS-native version of the Clearing course finder.

The main prototype in the repository treats the controlled Excel workbook as the editorial source. This proof of concept assumes TerminalFour may need to hold one content item per course instead. The page then renders those content items as inert HTML, reads them with JavaScript, validates them in browser preview, and builds the same searchable course finder interface.

## Files

- `index.html` - standalone sample page with three hidden CMS-style course items
- `cms-course-reader.js` - reads repeated `article` elements, validates records and renders the finder
- `cms-proof.css` - small styles for the CMS validation panel
- `terminalfour-content-type.md` - suggested content type fields and content layout examples

## How the source markup works

TerminalFour would output one `article` for each course content item:

```html
<article
  class="clearing-course-source-item"
  data-record-id="2026-NN34-UG"
  data-academic-year="2026"
  data-title="Accounting and Finance"
  data-type="Undergraduate"
  data-status="Vacancies"
  data-ucas="NN34"
  data-requirements="64 UCAS tariff points"
  data-summary="BSc (Hons)"
  data-entry-requirements-url="https://www.keele.ac.uk/clearing/entry-requirements/"
  data-url="https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/accountingandfinance/"
  data-last-reviewed="2026-06-22"
>
  <div class="course-info">Entry requirement copy goes here.</div>
</article>
```

Short controlled values live in `data-*` attributes. Longer prose lives inside child elements and is read with `textContent`, so the app does not depend on raw HTML.

## Testing

Open `index.html` directly in a browser. The sample includes:

- `Accounting and Finance`
- `Children's Nursing (Dual Registration)`
- `Business & Management with Foundation Year`

These deliberately exercise apostrophes, brackets and ampersands.

