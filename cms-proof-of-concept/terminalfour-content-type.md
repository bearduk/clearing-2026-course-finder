# TerminalFour content type sketch

## Content Type: Clearing Course

Create one content item for each row/course route.

Suggested fields:

| Field name | Type | Required | Notes |
| --- | --- | --- | --- |
| Record ID | Plain text | Yes | Stable unique key, e.g. `2026-NN34-UG` |
| Academic Year | Number/text | Yes | `2026` |
| Course Title | Plain text | Yes | e.g. `Children's Nursing (Dual Registration)` |
| Course Type | Select list | Yes | `Undergraduate` or `Foundation year` |
| Availability | Select list | Yes | `Vacancies`, `Limited vacancies`, `Waiting list`, `Full` |
| UCAS Code | Plain text | No | Four-character UCAS code where available |
| Typical Offer | Plain text | Yes | e.g. `64 UCAS tariff points` or `See entry requirements` |
| Award | Plain text | No | Used as card summary, e.g. `BSc (Hons)` |
| Entry Requirement Summary | Plain text / textarea | Yes | Longer copy; output as text, not raw editor HTML |
| Entry Requirements URL | Link/text | No | Required when offer is course-specific |
| Course URL | Link/text | Yes | Public Keele course URL |
| Display | Select list | Yes | `Yes` or `No`; content layout should only output `Yes` items |
| Last Reviewed | Date | Yes | Used by validation |
| Content Owner | Plain text | Yes | Internal governance |
| Change Note | Plain text | Yes | Internal governance |

## Content layout idea

The content layout should output inert source HTML. The JavaScript reads this source, validates it, and renders the public course finder elsewhere on the page.

Use TerminalFour's safe escaping modifier for every editor-maintained value. The exact modifier syntax may vary by local T4 version, but the pattern is:

```html
<article
  class="clearing-course-source-item"
  data-record-id="<t4 type=&quot;content&quot; name=&quot;Record ID&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-academic-year="<t4 type=&quot;content&quot; name=&quot;Academic Year&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-title="<t4 type=&quot;content&quot; name=&quot;Course Title&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-type="<t4 type=&quot;content&quot; name=&quot;Course Type&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-status="<t4 type=&quot;content&quot; name=&quot;Availability&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-ucas="<t4 type=&quot;content&quot; name=&quot;UCAS Code&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-requirements="<t4 type=&quot;content&quot; name=&quot;Typical Offer&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-summary="<t4 type=&quot;content&quot; name=&quot;Award&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-entry-requirements-url="<t4 type=&quot;content&quot; name=&quot;Entry Requirements URL&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-url="<t4 type=&quot;content&quot; name=&quot;Course URL&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
  data-last-reviewed="<t4 type=&quot;content&quot; name=&quot;Last Reviewed&quot; output=&quot;normal&quot; modifiers=&quot;htmlentities&quot; />"
>
  <div class="course-info">
    <t4 type="content" name="Entry Requirement Summary" output="normal" modifiers="htmlentities" />
  </div>
</article>
```

## Page layout idea

The page or section layout should contain:

```html
<div id="clearing-cms-validation" aria-live="polite"></div>

<div id="clearing-course-source" hidden>
  <!-- TerminalFour repeats Clearing Course content items here. -->
</div>

<div id="clearing-course-app">
  <!-- Finder controls and results live here. -->
</div>
```

For CMS preview, leave the validation panel visible. For production, the panel can be hidden unless the page has blocking errors.

