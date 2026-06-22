# Keele Clearing course finder proof of concept

A dependency-free prototype for showing undergraduate and foundation year courses open in Clearing. Open `index.html` directly or serve the folder with any static web server.

This is a public proof of concept, not a production service. Search indexing is discouraged through page-level `noindex` directives and a site-wide `robots.txt` disallow rule. These measures are not authentication and do not make a published URL private.

## What the prototype demonstrates

- Fuzzy search across course title, description and requirements, powered by a locally vendored Fuse.js 7.1.0 build
- Undergraduate/Foundation Year filters
- A-Z filtering
- Card and compact table-style views
- Expandable entry-requirement information
- Links to full Keele course pages
- Responsive layout and keyboard-accessible controls
- An explicit warning that the prototype data is illustrative
- A page last-modified date, ready to map to TerminalFour metadata

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
| Full course URL | Link or plain text | Yes | https://www.keele.ac.uk/.../biology/ |
| Open in Clearing | Checkbox | Yes | Checked |
| Display order | Number | No | 10 |

The Content Layout would output each repeatable item as either JSON consumed by `app.js`, or as semantic `<article>` markup carrying values in `data-*` attributes. JSON is simpler to filter and reduces duplicated markup.

## Production notes

- The sample availability, UCAS codes and requirements in `app.js` are not approved Clearing data.
- Confirm whether the source of truth will be manually maintained in TerminalFour or imported from a course system.
- Add `Last reviewed` and optional `Clearing note` fields if editors need time-sensitive messaging.
- Use Keele's production header/footer and existing design tokens when moved into the main site.
- Run an accessibility review with the component inside the full Keele template.

## Search behaviour

Fuse.js is loaded locally from `fuse.min.js`, so search also works when `index.html` is opened directly. Results are weighted toward course titles, followed by the short description, additional entry information and requirements. The threshold is deliberately forgiving enough to match common misspellings without making unrelated results too prominent.
