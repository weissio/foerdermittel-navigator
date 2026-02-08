const statusEl = document.getElementById("statusFilter");
const kategorieEl = document.getElementById("kategorieFilter");
const projektartEl = document.getElementById("projektartFilter");
const themaEl = document.getElementById("themaFilter");
const searchEl = document.getElementById("searchFilter");
const resetBtn = document.getElementById("resetBtn");

const cardsEl = document.getElementById("cards");
const countEl = document.getElementById("count");
const countOffenEl = document.getElementById("countOffen");
const countLaufendEl = document.getElementById("countLaufend");
const standEl = document.getElementById("stand");

let data = [];

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
  const kategorie = kategorieEl.value.trim();
  const projektart = projektartEl.value.trim().toLowerCase();
  const thema = themaEl.value.trim().toLowerCase();
  const q = searchEl.value.trim().toLowerCase();

  if (status && item.status !== status) return false;
  if (kategorie && item.kategorie !== kategorie) return false;
  if (projektart && !item.projektart.toLowerCase().includes(projektart)) return false;
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
    card.innerHTML = `
      <h3>${item.programm_name || "Programm"}</h3>
      <div class="row">
        <span class="pill">${item.status || "n/a"}</span>
        <span class="pill">${item.kategorie || "n/a"}</span>
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
  kategorieEl.value = "";
  projektartEl.value = "";
  themaEl.value = "";
  searchEl.value = "";
  render();
}

[statusEl, kategorieEl, projektartEl, themaEl, searchEl].forEach(el => {
  el.addEventListener("input", render);
});
resetBtn.addEventListener("click", resetFilters);

fetch("/data/foerderprogramme.csv")
  .then(r => r.text())
  .then(text => {
    data = parseCSV(text);
    standEl.textContent = new Date().toISOString().slice(0, 10);
    render();
  })
  .catch(err => {
    cardsEl.innerHTML = `<div class="card">Fehler beim Laden der Daten: ${err}</div>`;
  });
