const sampleCourses = [
  {
    title: "Accounting and Finance",
    type: "Foundation year",
    ucas: "N4N3",
    requirements: "40 UCAS tariff points",
    summary: "Build core business skills before progressing to the full Accounting and Finance degree.",
    info: "We welcome a wide range of qualifications. GCSE English and Maths requirements may also apply.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/accountingandfinance/#foundationyear"
  },
  {
    title: "Animation",
    type: "Foundation year",
    ucas: "W6W7",
    requirements: "40 UCAS tariff points",
    summary: "Develop creative, technical and academic skills before progressing to the Animation degree.",
    info: "A portfolio may be discussed as part of your application. GCSE requirements may also apply.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/animation/#foundationyear"
  },
  {
    title: "Biology",
    type: "Undergraduate",
    ucas: "C100",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Explore life from molecules and cells to organisms, ecosystems and global environments.",
    info: "A science subject is normally required. Equivalent BTEC and Access qualifications are considered.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/biology/"
  },
  {
    title: "Biomedical Science",
    type: "Foundation year",
    ucas: "B9B9",
    requirements: "40 UCAS tariff points",
    summary: "Prepare for degree-level study and discover how science supports the diagnosis of disease.",
    info: "This route is designed for applicants who do not currently meet direct-entry requirements.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/biomedicalscience/#foundationyear"
  },
  {
    title: "Business Management",
    type: "Undergraduate",
    ucas: "N200",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Develop practical insight into how organisations work, lead people and respond to change.",
    info: "Applicants with A levels, BTEC, Access and other recognised qualifications are considered.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/businessmanagement/"
  },
  {
    title: "Chemical Engineering",
    type: "Undergraduate",
    ucas: "H800",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Apply chemistry, physics and mathematics to processes that shape modern industry.",
    info: "A level Maths and a relevant science subject, or accepted equivalents, are normally required.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/chemicalengineering/"
  },
  {
    title: "Chemistry",
    type: "Undergraduate",
    ucas: "F100",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Study the science behind materials, medicines and technologies in modern laboratories.",
    info: "A level Chemistry or an accepted equivalent is normally required for direct entry.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/chemistry/"
  },
  {
    title: "Computer Science",
    type: "Foundation year",
    ucas: "G4G4",
    requirements: "40 UCAS tariff points",
    summary: "Gain the academic and technical foundations needed to progress to a computing degree.",
    info: "No previous programming experience is needed. GCSE Maths requirements may apply.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/computerscience/#foundationyear"
  },
  {
    title: "Criminology",
    type: "Undergraduate",
    ucas: "L611",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Examine crime, justice and social harm through contemporary debates and real-world cases.",
    info: "No specific A level subject is required. A range of Level 3 qualifications is considered.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/criminology/"
  },
  {
    title: "Education",
    type: "Foundation year",
    ucas: "X3X3",
    requirements: "40 UCAS tariff points",
    summary: "Prepare for degree-level study while exploring education, learning and social change.",
    info: "This route welcomes applicants with varied educational and professional backgrounds.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/education/#foundationyear"
  },
  {
    title: "Environmental Science",
    type: "Undergraduate",
    ucas: "F900",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Investigate environmental challenges through scientific study, fieldwork and practical skills.",
    info: "A relevant science or geography qualification may be required. Check the full course page.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/environmentalscience/"
  },
  {
    title: "Forensic Science",
    type: "Undergraduate",
    ucas: "F410",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Use scientific techniques to investigate evidence and understand the criminal justice context.",
    info: "A relevant science qualification is normally required. Equivalent Level 3 routes are considered.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/forensicscience/"
  },
  {
    title: "Geography (Human)",
    type: "Foundation year",
    ucas: "L7L8",
    requirements: "40 UCAS tariff points",
    summary: "Build academic confidence before studying people, places and global social challenges.",
    info: "No specific Level 3 subject is normally required for the foundation route.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/geographyhuman/#foundationyear"
  },
  {
    title: "Law",
    type: "Foundation year",
    ucas: "M1M1",
    requirements: "40 UCAS tariff points",
    summary: "Build confidence in academic study before progressing to Keele's qualifying Law degree.",
    info: "The foundation year supports students returning to education or changing subject area.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/law/#foundationyear"
  },
  {
    title: "Marketing",
    type: "Undergraduate",
    ucas: "N500",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Explore consumer behaviour, branding and digital strategy through practical business challenges.",
    info: "A range of A level, BTEC, Access and other recognised qualifications is considered.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/marketing/"
  },
  {
    title: "Mathematics",
    type: "Foundation year",
    ucas: "G1G2",
    requirements: "40 UCAS tariff points",
    summary: "Strengthen mathematical and study skills before progressing to a mathematics degree.",
    info: "GCSE Maths requirements apply. The route supports applicants without the usual direct-entry profile.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/mathematics/#foundationyear"
  },
  {
    title: "Nursing (Adult)",
    type: "Undergraduate",
    ucas: "B740",
    requirements: "BBB / 120 UCAS tariff points",
    summary: "Combine clinical placements with study to prepare for a rewarding career in adult nursing.",
    info: "Selection includes an interview and health and DBS checks. GCSE requirements also apply.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/adultnursing/"
  },
  {
    title: "Philosophy",
    type: "Undergraduate",
    ucas: "V500",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Question ideas about knowledge, ethics and society through rigorous debate and analysis.",
    info: "No specific A level subject is required. A broad range of qualifications is accepted.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/philosophy/"
  },
  {
    title: "Psychology",
    type: "Undergraduate",
    ucas: "C800",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Understand human thought and behaviour through scientific theory, research and application.",
    info: "No specific A level subject is required. GCSE Maths requirements may apply.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/psychology/"
  },
  {
    title: "Radiography (Diagnostic Imaging)",
    type: "Undergraduate",
    ucas: "B821",
    requirements: "BBB / 120 UCAS tariff points",
    summary: "Combine university learning and clinical placements to develop diagnostic imaging expertise.",
    info: "Selection requirements include an interview, health checks and a DBS check. GCSE criteria apply.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/radiographydiagnosticimaging/"
  },
  {
    title: "Sport and Exercise Science",
    type: "Foundation year",
    ucas: "C6C7",
    requirements: "40 UCAS tariff points",
    summary: "Develop the scientific and academic foundations for studying human performance and exercise.",
    info: "The foundation route considers a wide range of qualifications and prior learning.",
    url: "https://www.keele.ac.uk/study/undergraduate/undergraduatecourses/sportandexercisescience/#foundationyear"
  },
  {
    title: "Zoology",
    type: "Undergraduate",
    ucas: "C300",
    requirements: "BBC / 112 UCAS tariff points",
    summary: "Explore animal biology, behaviour and conservation through laboratory and field experience.",
    info: "A relevant science subject is normally required. Equivalent qualifications are considered.",
    url: "https://www.keele.ac.uk/study/undergraduate-2026/undergraduatecourses/zoology/"
  }
];

const courses = window.CLEARING_COURSES || sampleCourses;

const state = { query: "", type: "all", availability: "vacancies", letter: "all", view: "cards", limit: 24 };
const courseSearch = new Fuse(courses, {
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

function courseCard(course) {
  const statusClass = course.status.toLowerCase().replaceAll(" ", "-");
  return `
    <article class="course-card" data-type="${course.type}" data-status="${course.status}">
      <div class="card-topline">
        <div class="card-tags">
          <span class="tag">${course.type}</span>
          <span class="status status--${statusClass}">${course.status}</span>
        </div>
        ${course.ucas ? `<span class="ucas">UCAS: ${course.ucas}</span>` : ""}
      </div>
      <h3>${course.title}</h3>
      <p class="summary">${course.summary}</p>
      <div class="requirements">
        <span>Typical offer</span>
        <strong>${course.requirements}</strong>
      </div>
      <div class="card-actions">
        <details class="details">
          <summary>
            <span class="details-card-label">More about entry requirements</span>
            <span class="details-table-label">Entry requirement details</span>
          </summary>
          <p>${course.info}</p>
        </details>
        <a class="course-link" href="${course.url}">Full course details <span aria-hidden="true">→</span></a>
      </div>
    </article>`;
}

const availabilityOptions = {
  vacancies: { label: "Vacancies", statuses: ["Vacancies"] },
  limited: { label: "Limited vacancies", statuses: ["Limited vacancies"] },
  waiting: { label: "Waiting list", statuses: ["Waiting list"] },
  full: { label: "Full", statuses: ["Full"] },
  all: { label: "All statuses", statuses: ["Vacancies", "Limited vacancies", "Waiting list", "Full"] }
};

function matchingCourses() {
  const query = state.query.trim();
  const searchResults = query ? courseSearch.search(query).map(result => result.item) : courses;

  return searchResults.filter(course => {
    const matchesType = state.type === "all" || course.type === state.type;
    const matchesLetter = state.letter === "all" || course.title.startsWith(state.letter);
    return matchesType && matchesLetter;
  });
}

function updateAvailabilityCounts(candidates) {
  const select = document.querySelector("#availability-select");
  Object.entries(availabilityOptions).forEach(([value, option]) => {
    const count = value === "all"
      ? candidates.length
      : candidates.filter(course => option.statuses.includes(course.status)).length;
    select.querySelector(`option[value="${value}"]`).textContent = `${option.label} (${count})`;
  });
}

function render() {
  const candidates = matchingCourses();
  const visible = candidates.filter(course => availabilityOptions[state.availability].statuses.includes(course.status));
  updateAvailabilityCounts(candidates);
  const rendered = visible.slice(0, state.limit);
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
