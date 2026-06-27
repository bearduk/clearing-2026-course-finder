/*
 * Parity-test runner (Node side).
 *
 * Extracts the live JavaScript from ../process.html, shims an XML parser
 * (browsers provide DOMParser natively; Node does not), runs the tool's
 * readCoursesSheet / validate / renderCmsSourceHtml against the supplied
 * fixtures and the real workbook, and prints the results as JSON for
 * parity_test.py to compare against the Python validator.
 *
 * Invoked by parity_test.py — not meant to be run by hand.
 * Usage: node run_core.cjs <fixturesDir> <realWorkbookPath|"-"> <today YYYY-MM-DD>
 */
"use strict";
const fs = require("fs");
const path = require("path");

let DOMParser;
try {
  ({ DOMParser } = require("@xmldom/xmldom"));
} catch (e) {
  console.error("MISSING_DEP");
  process.exit(2);
}
globalThis.__parseXml = (t) => new DOMParser().parseFromString(t, "application/xml");

// Pull the inline <script> straight out of process.html so the test always
// exercises the shipped file, never a stale copy.
const html = fs.readFileSync(path.join(__dirname, "..", "process.html"), "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("NO_SCRIPT"); process.exit(2); }
const coreModule = { exports: {} };
new Function("module", "exports", m[1])(coreModule, coreModule.exports);
const core = coreModule.exports;

const [, , fixturesDir, realPath, todayStr] = process.argv;
const [ty, tm, td] = todayStr.split("-").map(Number);
const TODAY = core.ordFromMs(Date.UTC(ty, tm - 1, td));

function bodyOf(htmlStr) { return htmlStr.slice(htmlStr.indexOf("-->\n\n") + 5); }

(async () => {
  const out = { fixtures: {}, real: null };

  const names = JSON.parse(fs.readFileSync(path.join(fixturesDir, "oracle.json"), "utf8"));
  for (const name of Object.keys(names)) {
    const buf = fs.readFileSync(path.join(fixturesDir, name + ".xlsx"));
    const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
    try {
      const { headers, rows } = await core.readCoursesSheet(ab);
      const r = core.validate(headers, rows, TODAY);
      out.fixtures[name] = {
        records: r.records.length,
        issues: r.issues.map((i) => [i.severity, i.row, i.column, i.message]),
      };
    } catch (err) {
      out.fixtures[name] = { error: String(err && err.message ? err.message : err) };
    }
  }

  if (realPath && realPath !== "-") {
    const buf = fs.readFileSync(realPath);
    const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
    const { headers, rows } = await core.readCoursesSheet(ab);
    const r = core.validate(headers, rows, TODAY);
    out.real = {
      records: r.records.length,
      errors: r.issues.filter((i) => i.severity === "error").length,
      warnings: r.issues.filter((i) => i.severity === "warning").length,
      articleBody: bodyOf(core.renderCmsSourceHtml(r.records, "x", "x")),
    };
  }

  process.stdout.write(JSON.stringify(out));
})().catch((e) => { console.error(e); process.exit(2); });
