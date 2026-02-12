const statusEl = document.getElementById("statusFilter");
const projektartEl = document.getElementById("projektartFilter");
const foerderartEl = document.getElementById("foerderartFilter");
const zielgruppeEl = document.getElementById("zielgruppeFilter");
const themaEl = document.getElementById("themaFilter");
const searchEl = document.getElementById("searchFilter");
const resetBtn = document.getElementById("resetBtn");

const cardsEl = document.getElementById("cards");
const countEl = document.getElementById("count");
const statusCountsEl = document.getElementById("statusCounts");
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

function collectThemeValues(rows) {
  const set = new Set();
  const splitBy = /[|/,;]/;
  for (const row of rows) {
    const raw = (row.themen_schwerpunkt || row.thema || "").trim();
    if (!raw) continue;
    raw
      .split(splitBy)
      .map(s => s.trim())
      .filter(Boolean)
      .forEach(v => set.add(v));
  }
  return set;
}

function parseCSV(text) {
  if (!text || !text.trim()) return [];
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const next = text[i + 1];

    if (ch === '"') {
      if (inQuotes && next === '"') {
        field += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (ch === "," && !inQuotes) {
      row.push(field);
      field = "";
      continue;
    }

    if ((ch === "\n" || ch === "\r") && !inQuotes) {
      if (ch === "\r" && next === "\n") i += 1;
      row.push(field);
      field = "";
      if (row.some(cell => cell !== "")) rows.push(row);
      row = [];
      continue;
    }

    field += ch;
  }

  if (field.length || row.length) {
    row.push(field);
    if (row.some(cell => cell !== "")) rows.push(row);
  }

  if (!rows.length) return [];
  const headers = rows[0].map(h => (h || "").trim());
  return rows.slice(1).map(cols => {
    const obj = {};
    headers.forEach((h, idx) => {
      obj[h] = (cols[idx] || "").trim();
    });
    return obj;
  });
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
  const themaField = (item.themen_schwerpunkt || item.thema || "")
    .toLowerCase()
    .replace(/[|/,;]/g, " ");
  if (thema && !themaField.includes(thema)) return false;
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

function deadlineCandidates(item) {
  return [item.call_deadline, item.call_close_date, item.frist]
    .filter(Boolean)
    .flatMap(v => String(v).split("|"))
    .map(v => v.trim())
    .filter(v => /^\d{4}-\d{2}-\d{2}$/.test(v))
    .sort();
}

function firstDeadline(item) {
  const candidates = deadlineCandidates(item);
  return candidates[0] || "";
}

function nextDeadline(item) {
  const candidates = deadlineCandidates(item);
  if (!candidates.length) return "";
  const today = new Date().toISOString().slice(0, 10);
  return candidates.find(d => d >= today) || candidates[candidates.length - 1];
}

function isRollingDeadline(item) {
  const frist = String(item.frist || "").toLowerCase();
  if (firstDeadline(item)) return false;
  return ["rollierend", "losverfahren", "programmabhaengig", "laufend"].some(k => frist.includes(k));
}

function compareItems(a, b) {
  const rank = { offen: 0, laufend: 1, geplant: 2 };
  const aStatus = (a.status || "").toLowerCase();
  const bStatus = (b.status || "").toLowerCase();
  const aRank = rank[aStatus] ?? 9;
  const bRank = rank[bStatus] ?? 9;
  if (aRank !== bRank) return aRank - bRank;

  const aDeadline = nextDeadline(a);
  const bDeadline = nextDeadline(b);
  if (aStatus === "offen") {
    if (aDeadline && bDeadline && aDeadline !== bDeadline) return aDeadline.localeCompare(bDeadline);
    if (aDeadline && !bDeadline) return -1;
    if (!aDeadline && bDeadline) return 1;
  }

  return (a.programm_name || "").localeCompare(b.programm_name || "");
}

function render() {
  const filtered = data.filter(matchesFilter).sort(compareItems);
  const byStatus = { offen: 0, laufend: 0, geplant: 0 };
  for (const d of filtered) {
    const key = (d.status || "").toLowerCase();
    if (Object.prototype.hasOwnProperty.call(byStatus, key)) byStatus[key] += 1;
  }

  countEl.textContent = filtered.length;
  statusCountsEl.textContent = `offen: ${byStatus.offen} | laufend: ${byStatus.laufend} | geplant: ${byStatus.geplant}`;

  cardsEl.innerHTML = "";
  for (const item of filtered) {
    const card = document.createElement("div");
    card.className = "card";
    const letzte = item.letzte_pruefung || "-";
    const stand = item.richtlinie_stand || "-";
    const deadline = nextDeadline(item) || item.frist || "-";
    const deadlineType = isRollingDeadline(item) ? " (rollierend)" : "";
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
      <div class="row"><strong>Frist:</strong> ${deadline}${deadlineType}</div>
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
    buildOptions(themaEl, collectThemeValues(data), "Alle Themen");
    const letztePruefungen = data
      .map(d => d.letzte_pruefung)
      .filter(v => /^\d{4}-\d{2}-\d{2}$/.test(v))
      .sort();
    standEl.textContent = letztePruefungen.length ? letztePruefungen[letztePruefungen.length - 1] : "-";
    render();
  })
  .catch(err => {
    cardsEl.innerHTML = `<div class="card">Fehler beim Laden der Daten: ${err.message}</div>`;
  });
