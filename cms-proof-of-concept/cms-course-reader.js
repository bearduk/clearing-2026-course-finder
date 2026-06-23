(function () {
  "use strict";

  const COURSE_TYPES = new Set(["Undergraduate", "Foundation year"]);
  const AVAILABILITIES = new Set(["Vacancies", "Limited vacancies", "Waiting list", "Full"]);
  const UCAS_RE = /^[A-Z][A-Z0-9]{3}$/;
  const RECORD_ID_RE = /^[A-Za-z0-9][A-Za-z0-9._-]{2,79}$/;
  const clearingEntryRequirementsUrl = "https://www.keele.ac.uk/clearing/entry-requirements/";

  const state = { query: "", type: "all", availability: "vacancies", letter: "all", view: "cards", limit: 24 };

  function textFrom(item, selector) {
    return (item.querySelector(selector)?.textContent || "").replace(/\s+/g, " ").trim();
  }

  function clean(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function readCoursesFromMarkup() {
    return Array.from(document.querySelectorAll(".clearing-course-source-item")).map((item, index) => ({
      sourceIndex: index + 1,
      recordId: clean(item.dataset.recordId),
      academicYear: Number(clean(item.dataset.academicYear)),
      title: clean(item.dataset.title),
      type: clean(item.dataset.type),
      status: clean(item.dataset.status),
      ucas: clean(item.dataset.ucas).toUpperCase(),
      requirements: clean(item.dataset.requirements),
      summary: clean(item.dataset.summary) || "Course",
      info: textFrom(item, ".course-info"),
      entryRequirementsUrl: clean(item.dataset.entryRequirementsUrl),
      url: clean(item.dataset.url),
      lastReviewed: clean(item.dataset.lastReviewed)
    }));
  }

  function isKeeleHttpsUrl(value) {
    try {
      const url = new URL(value);
      return url.protocol === "https:" && url.hostname === "www.keele.ac.uk";
    } catch {
      return false;
    }
  }

  function validateCourses(courses) {
    const issues = [];
    const seenIds = new Map();
    const seenRoutes = new Map();

    function add(severity, course, field, message) {
      const label = course ? `Item ${course.sourceIndex}${course.title ? ` (${course.title})` : ""}` : "Dataset";
      issues.push({ severity, message: `${label}: ${field ? `${field}: ` : ""}${message}` });
    }

    if (!courses.length) {
      add("error", null, "", "No Clearing course content items were found.");
      return issues;
    }

    courses.forEach(course => {
      [
        ["Record ID", course.recordId],
        ["Academic Year", course.academicYear],
        ["Course Title", course.title],
        ["Course Type", course.type],
        ["Availability", course.status],
        ["Typical Offer", course.requirements],
        ["Entry Requirement Summary", course.info],
        ["Course URL", course.url],
        ["Last Reviewed", course.lastReviewed]
      ].forEach(([field, value]) => {
        if (!value) add("error", course, field, "Required value is blank.");
      });

      if (course.recordId && !RECORD_ID_RE.test(course.recordId)) {
        add("error", course, "Record ID", "Use 3-80 letters, numbers, dots, underscores or hyphens.");
      }

      const duplicateId = seenIds.get(course.recordId.toLowerCase());
      if (course.recordId && duplicateId) {
        add("error", course, "Record ID", `Duplicate of item ${duplicateId}.`);
      } else if (course.recordId) {
        seenIds.set(course.recordId.toLowerCase(), course.sourceIndex);
      }

      const routeKey = `${course.title.toLowerCase()}|${course.type.toLowerCase()}`;
      const duplicateRoute = seenRoutes.get(routeKey);
      if (course.title && course.type && duplicateRoute) {
        add("error", course, "Course Title", `Duplicate course/type route from item ${duplicateRoute}.`);
      } else if (course.title && course.type) {
        seenRoutes.set(routeKey, course.sourceIndex);
      }

      if (!Number.isInteger(course.academicYear) || course.academicYear < 2026 || course.academicYear > 2030) {
        add("error", course, "Academic Year", "Must be a whole year from 2026 to 2030.");
      }

      if (!COURSE_TYPES.has(course.type)) {
        add("error", course, "Course Type", "Must be Undergraduate or Foundation year.");
      }

      if (!AVAILABILITIES.has(course.status)) {
        add("error", course, "Availability", "Must be Vacancies, Limited vacancies, Waiting list or Full.");
      }

      if (course.ucas && !UCAS_RE.test(course.ucas)) {
        add("error", course, "UCAS Code", "Must be four uppercase letters/numbers beginning with a letter.");
      }

      if (course.url && !isKeeleHttpsUrl(course.url)) {
        add("error", course, "Course URL", "Must be a clean https://www.keele.ac.uk/ URL.");
      }

      if (course.type === "Foundation year" && course.url && !course.url.toLowerCase().endsWith("#foundationyear")) {
        add("error", course, "Course URL", "Foundation year URLs must include #foundationyear.");
      }

      if (course.entryRequirementsUrl && !isKeeleHttpsUrl(course.entryRequirementsUrl)) {
        add("error", course, "Entry Requirements URL", "Must be a clean https://www.keele.ac.uk/ URL.");
      }

      if (/^(course-specific|see entry requirements)$/i.test(course.requirements) && !course.entryRequirementsUrl) {
        add("error", course, "Entry Requirements URL", "Required when the typical offer is course-specific.");
      }

      const reviewed = new Date(`${course.lastReviewed}T00:00:00`);
      if (Number.isNaN(reviewed.getTime())) {
        add("error", course, "Last Reviewed", "Must use YYYY-MM-DD.");
      } else {
        const today = new Date();
        const ageDays = Math.floor((today - reviewed) / 86400000);
        if (ageDays > 14) add("warning", course, "Last Reviewed", "Was reviewed more than 14 days ago.");
        if (ageDays < -1) add("error", course, "Last Reviewed", "Cannot be in the future.");
      }
    });

    return issues;
  }

  function renderValidation(issues, courses) {
    const container = document.querySelector("#clearing-cms-validation");
    if (!container) return;

    const errors = issues.filter(issue => issue.severity === "error");
    const warnings = issues.filter(issue => issue.severity === "warning");
    const statusClass = errors.length ? "cms-validation--error" : warnings.length ? "cms-validation--warning" : "";
    const heading = errors.length
      ? "CMS data has blocking issues"
      : warnings.length
        ? "CMS data has warnings"
        : "CMS data passed validation";
    const summary = `${courses.length} course item${courses.length === 1 ? "" : "s"} read. ${errors.length} error${errors.length === 1 ? "" : "s"} and ${warnings.length} warning${warnings.length === 1 ? "" : "s"}.`;

    container.innerHTML = `
      <div class="cms-validation ${statusClass}">
        <h2>${heading}</h2>
        <p>${summary}</p>
        ${issues.length ? `<ul>${issues.map(issue => `<li><strong>${issue.severity.toUpperCase()}:</strong> ${escapeHtml(issue.message)}</li>`).join("")}</ul>` : ""}
      </div>
    `;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, character => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#39;"
    })[character]);
  }

  function courseCard(course) {
    const statusClass = course.status.toLowerCase().replaceAll(" ", "-");
    const offer = course.requirements === "See entry requirements"
      ? "<strong>Course-specific</strong>"
      : `<strong>${escapeHtml(course.requirements)}</strong>`;
    const entryRequirementsUrl = course.entryRequirementsUrl || clearingEntryRequirementsUrl;
    const requirementsLink = entryRequirementsUrl
      ? `<a class="details-link" href="${escapeHtml(entryRequirementsUrl)}">View Clearing entry requirements <span aria-hidden="true">→</span></a>`
      : "";
    return `
      <article class="course-card" data-type="${escapeHtml(course.type)}" data-status="${escapeHtml(course.status)}">
        <div class="card-topline">
          <div class="card-tags">
            <span class="tag">${escapeHtml(course.type)}</span>
            <span class="status status--${escapeHtml(statusClass)}">${escapeHtml(course.status)}</span>
          </div>
          ${course.ucas ? `<span class="ucas">UCAS: ${escapeHtml(course.ucas)}</span>` : ""}
        </div>
        <h3>${escapeHtml(course.title)}</h3>
        <p class="summary">${escapeHtml(course.summary)}</p>
        <div class="requirements">
          <span>Typical offer</span>
          ${offer}
        </div>
        <div class="card-actions">
          <details class="details">
            <summary>
              <span class="details-card-label">Entry requirement information</span>
              <span class="details-table-label">Entry requirement details</span>
            </summary>
            <p>${escapeHtml(course.info)}</p>
            ${requirementsLink}
          </details>
          <a class="course-link" href="${escapeHtml(course.url)}">Full course details <span aria-hidden="true">→</span></a>
        </div>
      </article>`;
  }

  function startFinder(courses) {
    const searchEngine = new Fuse(courses, {
      keys: [
        { name: "title", weight: 0.75 },
        { name: "summary", weight: 0.05 },
        { name: "info", weight: 0.05 },
        { name: "requirements", weight: 0.1 },
        { name: "ucas", weight: 0.05 }
      ],
      threshold: 0.3,
      distance: 120,
      ignoreLocation: true,
      minMatchCharLength: 2
    });

    const results = document.querySelector("#course-results");
    const count = document.querySelector("#result-count");
    const noResults = document.querySelector("#no-results");
    const search = document.querySelector("#course-search");
    const clearSearch = document.querySelector(".clear-search");
    const availableLetters = new Set(courses.map(course => course.title[0].toUpperCase()));
    const availabilityOptions = {
      vacancies: { label: "Vacancies", statuses: ["Vacancies"] },
      limited: { label: "Limited vacancies", statuses: ["Limited vacancies"] },
      waiting: { label: "Waiting list", statuses: ["Waiting list"] },
      full: { label: "Full", statuses: ["Full"] },
      all: { label: "All statuses", statuses: ["Vacancies", "Limited vacancies", "Waiting list", "Full"] }
    };

    function matchingCourses() {
      const query = state.query.trim();
      const searchResults = query ? searchEngine.search(query).map(result => result.item) : courses;
      return searchResults.filter(course => {
        const matchesType = state.type === "all" || course.type === state.type;
        const matchesLetter = state.letter === "all" || course.title.startsWith(state.letter);
        return matchesType && matchesLetter;
      });
    }

    function updateAvailabilityCounts(candidates) {
      const select = document.querySelector("#availability-select");
      Object.entries(availabilityOptions).forEach(([value, option]) => {
        const total = value === "all"
          ? candidates.length
          : candidates.filter(course => option.statuses.includes(course.status)).length;
        select.querySelector(`option[value="${value}"]`).textContent = `${option.label} (${total})`;
      });
    }

    function render() {
      const candidates = matchingCourses();
      const visible = candidates.filter(course => availabilityOptions[state.availability].statuses.includes(course.status));
      const rendered = visible.slice(0, state.limit);
      updateAvailabilityCounts(candidates);
      results.innerHTML = rendered.map(courseCard).join("");
      results.classList.toggle("table-view", state.view === "table");
      results.hidden = visible.length === 0;
      noResults.hidden = visible.length !== 0;
      count.innerHTML = `<strong>${visible.length}</strong> course${visible.length === 1 ? "" : "s"} found`;
      clearSearch.hidden = !state.query;
      const loadMore = document.querySelector("#load-more");
      document.querySelector("#table-columns").hidden = state.view !== "table" || visible.length === 0;
      loadMore.hidden = rendered.length >= visible.length;
      loadMore.textContent = `Show more courses (${visible.length - rendered.length} remaining)`;
    }

    function buildAZ() {
      const container = document.querySelector("#az-buttons");
      const letters = ["all", ..."ABCDEFGHIJKLMNOPQRSTUVWXYZ"];
      container.innerHTML = letters.map(letter => {
        const label = letter === "all" ? "All" : letter;
        const disabled = letter !== "all" && !availableLetters.has(letter);
        return `<button type="button" class="letter-button${letter === "all" ? " active" : ""}" data-letter="${letter}" ${disabled ? "disabled" : ""} aria-pressed="${letter === "all"}">${label}</button>`;
      }).join("");
    }

    search.addEventListener("input", event => {
      state.query = event.target.value;
      state.letter = "all";
      state.limit = 24;
      document.querySelectorAll(".letter-button").forEach(button => {
        const active = button.dataset.letter === "all";
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", active);
      });
      render();
    });

    clearSearch.addEventListener("click", () => {
      search.value = "";
      state.query = "";
      search.focus();
      render();
    });

    document.querySelectorAll('input[name="type"]').forEach(input => {
      input.addEventListener("change", event => {
        state.type = event.target.value;
        state.limit = 24;
        render();
      });
    });

    document.querySelector("#availability-select").addEventListener("change", event => {
      state.availability = event.target.value;
      state.limit = 24;
      render();
    });

    document.querySelector("#az-buttons").addEventListener("click", event => {
      const button = event.target.closest("button");
      if (!button) return;
      state.letter = button.dataset.letter;
      state.limit = 24;
      document.querySelectorAll(".letter-button").forEach(item => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-pressed", active);
      });
      render();
      results.focus({ preventScroll: true });
    });

    document.querySelectorAll(".view-toggle button").forEach(button => {
      button.addEventListener("click", () => {
        state.view = button.dataset.view;
        document.querySelectorAll(".view-toggle button").forEach(item => {
          const active = item === button;
          item.classList.toggle("active", active);
          item.setAttribute("aria-pressed", active);
        });
        render();
      });
    });

    document.querySelector("#reset-filters").addEventListener("click", () => {
      state.query = "";
      state.type = "all";
      state.availability = "vacancies";
      state.letter = "all";
      search.value = "";
      document.querySelector("#type-all").checked = true;
      document.querySelector("#availability-select").value = "vacancies";
      document.querySelectorAll(".letter-button").forEach(button => {
        const active = button.dataset.letter === "all";
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", active);
      });
      render();
      search.focus();
    });

    document.querySelector("#load-more").addEventListener("click", () => {
      state.limit += 24;
      render();
    });

    buildAZ();
    render();
  }

  const courses = readCoursesFromMarkup().sort((a, b) => a.title.localeCompare(b.title));
  const issues = validateCourses(courses);
  renderValidation(issues, courses);
  startFinder(courses.filter(course => COURSE_TYPES.has(course.type) && AVAILABILITIES.has(course.status) && course.title && course.url));
})();

