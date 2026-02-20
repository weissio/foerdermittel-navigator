const companyTypeEl = document.getElementById("companyTypeFilter");
const objectiveEl = document.getElementById("objectiveFilter");
const regionEl = document.getElementById("regionFilter");
const foerderartEl = document.getElementById("foerderartFilter");
const projektphaseEl = document.getElementById("projektphaseFilter");
const themaEl = document.getElementById("themaFilter");
const statusEl = document.getElementById("statusFilter");
const searchEl = document.getElementById("searchFilter");
const onlyAmountEl = document.getElementById("onlyAmountFilter");
const onlyRateEl = document.getElementById("onlyRateFilter");
const resetBtn = document.getElementById("resetBtn");

const cardsEl = document.getElementById("cards");
const countEl = document.getElementById("count");
const statusCountsEl = document.getElementById("statusCounts");
const standEl = document.getElementById("stand");

const reportModalEl = document.getElementById("reportModal");
const reportMetaEl = document.getElementById("reportMeta");
const reportCommentEl = document.getElementById("reportComment");
const reportSendBtn = document.getElementById("reportSendBtn");
const reportCopyBtn = document.getElementById("reportCopyBtn");
const reportCloseBtn = document.getElementById("reportCloseBtn");

let data = [];
let currentReport = null;
const REPORT_RECIPIENT = "feedback@foerdermittel-navigator.de";

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
  if (!text || !text.trim()) return [];
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
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

function splitValues(value) {
  return String(value || "")
    .split(/[|/,;]/)
    .map(x => x.trim())
    .filter(Boolean);
}

function companyType(item) {
  const z = (item.zielgruppe || "").toLowerCase();
  if (/kmu|mittelstand/.test(z)) return "KMU";
  if (/startup|start-up|gruender|gründ/.test(z)) return "Start-up/Gruendung";
  if (/freiberuf/.test(z)) return "Freiberuf";
  if (/gross|gro[eß]ere|midcap/.test(z)) return "Groesseres Unternehmen";
  if (/forschung|hochschule|wissenschaft/.test(z)) return "Forschung/Hochschule";
  return "Unternehmen allgemein";
}

function objectiveTags(item) {
  const text = [item.projektart, item.projektphase, item.thema, item.themen_schwerpunkt, item.foerdergegenstand]
    .join(" ")
    .toLowerCase();
  const tags = [];
  if (/f&e|forschung|entwicklung/.test(text)) tags.push("F&E");
  if (/einzelprojekt/.test(text)) tags.push("F&E Einzelprojekt");
  if (/kooperation|verbund/.test(text)) tags.push("F&E Kooperation");
  if (/prototyp|pilot|demonstr/.test(text)) tags.push("Prototyp/Pilot");
  if (/digital/.test(text)) tags.push("Digitalisierung");
  if (/ki|artificial intelligence/.test(text)) tags.push("KI");
  if (/energie|effizienz|klima|co2|dekarbon/.test(text)) tags.push("Energie/Klimaschutz");
  if (/gruendung|gründung|startup|start-up/.test(text)) tags.push("Gruendung");
  if (/beratung|coaching/.test(text)) tags.push("Beratung");
  if (/invest|wachstum|finanzierung/.test(text)) tags.push("Investition/Wachstum");
  if (!tags.length) tags.push("Sonstiges Vorhaben");
  return [...new Set(tags)];
}

function matchesFilter(item) {
  const selectedCompany = companyTypeEl.value;
  const selectedObjective = objectiveEl.value;
  const selectedRegion = regionEl.value;
  const selectedFoerderart = foerderartEl.value;
  const selectedProjektphase = projektphaseEl.value;
  const selectedThema = themaEl.value;
  const selectedStatus = statusEl.value;
  const q = searchEl.value.trim().toLowerCase();

  if (selectedCompany && companyType(item) !== selectedCompany) return false;
  if (selectedObjective && !objectiveTags(item).includes(selectedObjective)) return false;
  if (selectedRegion && (item.region || "") !== selectedRegion) return false;
  if (selectedFoerderart && (item.foerderart || "") !== selectedFoerderart) return false;
  if (selectedProjektphase && (item.projektphase || "") !== selectedProjektphase) return false;

  const themen = splitValues(item.themen_schwerpunkt || item.thema || "");
  if (selectedThema && !themen.includes(selectedThema)) return false;
  if (selectedStatus && (item.status || "") !== selectedStatus) return false;

  if (onlyAmountEl.checked && !(item.foerderhoehe || "").trim()) return false;
  if (onlyRateEl.checked && !(item.foerdersatz || "").trim()) return false;

  if (q) {
    const hay = [
      item.programm_name,
      item.traeger,
      item.thema,
      item.themen_schwerpunkt,
      item.foerdergegenstand,
      item.match_reason,
      item.zielgruppe
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

function nextDeadline(item) {
  const candidates = deadlineCandidates(item);
  if (!candidates.length) return "";
  const today = new Date().toISOString().slice(0, 10);
  return candidates.find(d => d >= today) || candidates[candidates.length - 1];
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
    const card = document.createElement("article");
    card.className = "card";

    const deadline = nextDeadline(item) || item.frist || "-";
    const infoLink = item.richtlinie_url
      ? `<a href="${item.richtlinie_url}" target="_blank" rel="noopener">Informationen</a>
         <button class="report-btn" data-field="Informationen" data-url="${item.richtlinie_url}" data-id="${item.programm_id || ""}" data-name="${item.programm_name || ""}" title="Link melden">!</button>`
      : "";
    const docLink = item.quelle_url && item.quelle_url !== item.richtlinie_url
      ? `<a href="${item.quelle_url}" target="_blank" rel="noopener">Dokumente</a>
         <button class="report-btn" data-field="Dokumente" data-url="${item.quelle_url}" data-id="${item.programm_id || ""}" data-name="${item.programm_name || ""}" title="Link melden">!</button>`
      : "";

    card.innerHTML = `
      <header class="card__head">
        <h3>${item.programm_name || "Programm"}</h3>
        <div class="card__pills">
          <span class="pill">${item.status || "n/a"}</span>
          <span class="pill">${item.kategorie || "n/a"}</span>
        </div>
      </header>

      <div class="card__metrics">
        <div><span>Foerderfaehige Summe</span><strong>${item.foerderhoehe || "k.A."}</strong></div>
        <div><span>Zuschuss / Foerdersatz</span><strong>${item.foerdersatz || "k.A."}</strong></div>
      </div>

      <div class="row"><strong>Traeger:</strong> ${item.traeger || "-"}</div>
      <div class="row"><strong>Foerderart:</strong> ${item.foerderart || "-"}</div>
      <div class="row"><strong>Thema:</strong> ${item.thema || "-"}</div>
      <div class="row"><strong>Projektart:</strong> ${item.projektart || "-"}</div>
      <div class="row"><strong>Zielgruppe:</strong> ${item.zielgruppe || "-"}</div>
      <div class="row"><strong>Frist:</strong> ${deadline}</div>
      <div class="row"><strong>Warum passt es?</strong> ${item.match_reason || "-"}</div>
      <div class="row"><strong>Was wird gefoerdert?</strong> ${item.foerdergegenstand || "-"}</div>

      <div class="links">
        ${infoLink}
        ${infoLink && docLink ? " | " : ""}
        ${docLink}
      </div>
    `;

    cardsEl.appendChild(card);
  }
}

function buildReportText() {
  if (!currentReport) return "";
  const comment = (reportCommentEl.value || "").trim();
  return [
    `programm_id: ${currentReport.programmId}`,
    `programm_name: ${currentReport.programmName}`,
    `feld: ${currentReport.field}`,
    `url: ${currentReport.url}`,
    `kommentar: ${comment || "-"}`,
    `timestamp: ${new Date().toISOString()}`
  ].join("\n");
}

function openReportModal(payload) {
  currentReport = payload;
  reportCommentEl.value = "";
  reportMetaEl.textContent = `${payload.programmName} | ${payload.field} | ${payload.url}`;
  reportModalEl.classList.remove("hidden");
  reportModalEl.setAttribute("aria-hidden", "false");
}

function closeReportModal() {
  reportModalEl.classList.add("hidden");
  reportModalEl.setAttribute("aria-hidden", "true");
  currentReport = null;
}

cardsEl.addEventListener("click", (event) => {
  const btn = event.target.closest(".report-btn");
  if (!btn) return;
  event.preventDefault();
  openReportModal({
    programmId: btn.dataset.id || "",
    programmName: btn.dataset.name || "",
    field: btn.dataset.field || "",
    url: btn.dataset.url || ""
  });
});

reportCloseBtn.addEventListener("click", closeReportModal);
reportModalEl.addEventListener("click", (event) => {
  if (event.target === reportModalEl) closeReportModal();
});

reportCopyBtn.addEventListener("click", async () => {
  const text = buildReportText();
  if (!text) return;
  await navigator.clipboard.writeText(text);
  reportCopyBtn.textContent = "Kopiert";
  setTimeout(() => { reportCopyBtn.textContent = "In Zwischenablage"; }, 1200);
});

reportSendBtn.addEventListener("click", () => {
  const text = buildReportText();
  if (!text) return;
  const subject = encodeURIComponent(`Linkmeldung ${currentReport.programmId} (${currentReport.field})`);
  const body = encodeURIComponent(text);
  window.location.href = `mailto:${REPORT_RECIPIENT}?subject=${subject}&body=${body}`;
});

function resetFilters() {
  companyTypeEl.value = "";
  objectiveEl.value = "";
  regionEl.value = "";
  foerderartEl.value = "";
  projektphaseEl.value = "";
  themaEl.value = "";
  statusEl.value = "";
  searchEl.value = "";
  onlyAmountEl.checked = false;
  onlyRateEl.checked = false;
  render();
}

[
  companyTypeEl,
  objectiveEl,
  regionEl,
  foerderartEl,
  projektphaseEl,
  themaEl,
  statusEl,
  searchEl,
  onlyAmountEl,
  onlyRateEl
].forEach(el => el.addEventListener("input", render));

resetBtn.addEventListener("click", resetFilters);

const base = window.location.origin;
const candidates = [
  `${base}/data/foerderprogramme.csv`,
  `${base}/docs/preview/../../data/foerderprogramme.csv`,
  "../../data/foerderprogramme.csv",
  "/data/foerderprogramme.csv"
];

async function loadCSV() {
  for (const url of candidates) {
    try {
      const r = await fetch(url, { cache: "no-store" });
      if (!r.ok) continue;
      const text = await r.text();
      if (text && text.trim().length > 0) return text;
    } catch (_) {
      // try next
    }
  }
  throw new Error("CSV not found or empty");
}

loadCSV()
  .then(text => {
    data = parseCSV(text);

    buildOptions(companyTypeEl, new Set(data.map(companyType)), "Alle Unternehmen");
    buildOptions(objectiveEl, new Set(data.flatMap(objectiveTags)), "Alle Vorhaben");
    buildOptions(regionEl, new Set(data.map(d => d.region)), "Alle Regionen");
    buildOptions(foerderartEl, new Set(data.map(d => d.foerderart)), "Alle Foerderarten");
    buildOptions(projektphaseEl, new Set(data.map(d => d.projektphase)), "Alle Projektphasen");
    buildOptions(themaEl, new Set(data.flatMap(d => splitValues(d.themen_schwerpunkt || d.thema))), "Alle Themen");
    buildOptions(statusEl, new Set(data.map(d => d.status)), "Alle Status");

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
