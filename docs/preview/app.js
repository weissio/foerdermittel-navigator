const statusEl = document.getElementById("statusFilter");
const projektartEl = document.getElementById("projektartFilter");
const foerderartEl = document.getElementById("foerderartFilter");
const zielgruppeEl = document.getElementById("zielgruppeFilter");
const themaEl = document.getElementById("themaFilter");
const searchEl = document.getElementById("searchFilter");
const resetBtn = document.getElementById("resetBtn");

const cardsEl = document.getElementById("cards");
const countEl = document.getElementById("count");
const countOffenEl = document.getElementById("countOffen");
const countLaufendEl = document.getElementById("countLaufend");
const standEl = document.getElementById("stand");

let data = [];

function buildOptions(selectEl, values, label = "Alle") {
  const sorted = Array.from(values).filter(Boolean).sort((a, b) => a.localeCompare(b));
  selectEl.innerHTML = "";
  const all = document.createElement("option");
  all.value = "";
  all.textContent = label;
  selectEl.appendChild(all);
  for (const v of sorted) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    selectEl.appendChild(opt);
  }
}

function parseCSV(text) {
  const lines = text.split(/\r?\n/).filter(Boolean);
  if (!lines.length) return [];
  const headers = lines[0].split(",").map(h => h.trim());
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const row = [];
    let current = "";
    let inQuotes = false;
    for (let j = 0; j < lines[i].length; j++) {
      const char = lines[i][j];
      if (char === '"' ) {
        inQuotes = !inQuotes;
      } else if (char === "," && !inQuotes) {
        row.push(current);
        current = "";
      } else {
        current += char;
      }
    }
    row.push(current);
    const obj = {};
    headers.forEach((h, idx) => {
      obj[h] = (row[idx] || "").replace(/^"|"$/g, "");
    });
    rows.push(obj);
  }
  return rows;
}

function matchesFilter(item) {
  const status = statusEl.value.trim();
  const projektart = projektartEl.value.trim().toLowerCase();
  const foerderart = foerderartEl.value.trim().toLowerCase();
  const zielgruppe = zielgruppeEl.value.trim().toLowerCase();
  const thema = themaEl.value.trim().toLowerCase();
  const q = searchEl.value.trim().toLowerCase();

  if (status && item.status !== status) return false;
  if (projektart && !item.projektart.toLowerCase().includes(projektart)) return false;
  if (foerderart && !item.foerderart.toLowerCase().includes(foerderart)) return false;
  if (zielgruppe && !item.zielgruppe.toLowerCase().includes(zielgruppe)) return false;
  if (thema && !item.themen_schwerpunkt.toLowerCase().includes(thema)) return false;
  if (q) {
    const hay = [
      item.programm_name,
      item.traeger,
      item.thema,
      item.themen_schwerpunkt,
      item.foerdergegenstand,
      item.match_reason
    ].join(" ").toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

function render() {
  const filtered = data.filter(matchesFilter);
  const offen = filtered.filter(d => d.status === "offen").length;
  const laufend = filtered.filter(d => d.status === "laufend").length;

  countEl.textContent = filtered.length;
  countOffenEl.textContent = offen;
  countLaufendEl.textContent = laufend;

  cardsEl.innerHTML = "";
  for (const item of filtered) {
    const card = document.createElement("div");
    card.className = "card";
    const letzte = item.letzte_pruefung || "-";
    const stand = item.richtlinie_stand || "-";
    card.innerHTML = `
      <h3>${item.programm_name || "Programm"}</h3>
      <div class="row">
        <span class="pill">${item.status || "n/a"}</span>
        <span class="pill">${item.kategorie || "n/a"}</span>
      </div>
      <div class="card__meta">
        <span class="pill pill--date">Letzte Pruefung: ${letzte}</span>
        <span class="pill pill--date">Richtlinie-Stand: ${stand}</span>
      </div>
      <div class="row"><strong>Traeger:</strong> ${item.traeger || "-"}</div>
      <div class="row"><strong>Foerderart:</strong> ${item.foerderart || "-"}</div>
      <div class="row"><strong>Thema:</strong> ${item.thema || "-"}</div>
      <div class="row"><strong>Projektart:</strong> ${item.projektart || "-"}</div>
      <div class="row"><strong>Frist:</strong> ${item.frist || item.call_deadline || "-"}</div>
      <div class="row"><strong>Warum passt es?</strong> ${item.match_reason || "-"}</div>
      <div class="row"><strong>Was wird gefoerdert?</strong> ${item.foerdergegenstand || "-"}</div>
      <div class="links">
        ${item.richtlinie_url ? `<a href="${item.richtlinie_url}" target="_blank">Richtlinie</a>` : ""}
        ${item.quelle_url ? ` | <a href="${item.quelle_url}" target="_blank">Quelle</a>` : ""}
      </div>
    `;
    cardsEl.appendChild(card);
  }
}

function resetFilters() {
  statusEl.value = "";
  projektartEl.value = "";
  foerderartEl.value = "";
  zielgruppeEl.value = "";
  themaEl.value = "";
  searchEl.value = "";
  render();
}

[statusEl, projektartEl, foerderartEl, zielgruppeEl, themaEl, searchEl].forEach(el => {
  el.addEventListener("input", render);
});
resetBtn.addEventListener("click", resetFilters);

const base = window.location.origin;
const candidates = [
  `${base}/data/foerderprogramme.csv`,
  `${base}/docs/preview/../../data/foerderprogramme.csv`,
  `../../data/foerderprogramme.csv`,
  `/data/foerderprogramme.csv`
];

async function loadCSV() {
  for (const url of candidates) {
    try {
      const r = await fetch(url, { cache: "no-store" });
      if (!r.ok) continue;
      const text = await r.text();
      if (text && text.trim().length > 0) {
        return text;
      }
    } catch (_) {
      // try next candidate
    }
  }
  throw new Error("CSV not found or empty");
}

loadCSV()
  .then(text => {
    data = parseCSV(text);
    buildOptions(statusEl, new Set(data.map(d => d.status)), "Alle Status");
    buildOptions(projektartEl, new Set(data.map(d => d.projektart)), "Alle Projektarten");
    buildOptions(foerderartEl, new Set(data.map(d => d.foerderart)), "Alle Foerderarten");
    buildOptions(zielgruppeEl, new Set(data.map(d => d.zielgruppe)), "Alle Zielgruppen");
    buildOptions(themaEl, new Set(data.map(d => d.themen_schwerpunkt)), "Alle Themen");
    standEl.textContent = new Date().toISOString().slice(0, 10);
    render();
  })
  .catch(err => {
    cardsEl.innerHTML = `<div class="card">Fehler beim Laden der Daten: ${err.message}</div>`;
  });
