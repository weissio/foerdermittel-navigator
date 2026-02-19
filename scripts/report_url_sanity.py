#!/usr/bin/env python3
"""Generate URL sanity snapshot without external network calls."""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/url_sanity_snapshot.md")


GENERIC_PATTERNS = [
    "/foerderprogramme",
    "/foerderprogramme-a-z",
    "/service/downloads",
    "/download-center",
    "/downloads",
]

SPECIFIC_HINTS = [
    "/foerderprodukte/",
    "/produkt/",
    "/produktdetail",
    "/programmes/",
    "/calls",
    "/call",
    "/topic",
    "/eic-",
]

SPECIFIC_FILE_EXT = (
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
)

SPECIFIC_FRAGMENTS = {
    "downloads",
    "download",
    "dokumente",
    "formulare",
    "publikationen",
    "faq",
    "materialien",
    "onlineantrag",
    "foerderaufrufe",
}


def _looks_generic(url: str) -> bool:
    lower = url.lower()
    parsed = urlparse(lower)

    if parsed.path.endswith(SPECIFIC_FILE_EXT):
        return False
    if parsed.fragment and any(frag in parsed.fragment for frag in SPECIFIC_FRAGMENTS):
        return False
    if any(h in lower for h in SPECIFIC_HINTS):
        return False
    return any(p in lower for p in GENERIC_PATTERNS)


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    invalid = []
    non_https = []
    generic_info = []
    generic_docs = []
    host_counts = Counter()
    for r in rows:
        pid = (r.get("programm_id") or "").strip()
        is_overview = (
            pid.endswith("_PORTAL")
            or pid.endswith("_UEBERSICHT")
            or "_PORTAL_" in pid
            or "_UEBERSICHT_" in pid
        )
        info = (r.get("richtlinie_url") or "").strip()
        docs = (r.get("quelle_url") or "").strip()
        for label, url in [("Informationen", info), ("Dokumente", docs)]:
            p = urlparse(url)
            if not p.scheme or not p.netloc:
                invalid.append((pid, label, url))
                continue
            if p.scheme != "https":
                non_https.append((pid, label, url))
            host_counts[p.netloc.lower()] += 1
            if label == "Informationen" and _looks_generic(url) and not is_overview:
                generic_info.append((pid, url))
            if label == "Dokumente" and _looks_generic(url) and not is_overview:
                generic_docs.append((pid, url))

    lines: list[str] = []
    lines.append("# URL Sanity Snapshot")
    lines.append("")
    lines.append(f"- Erzeugt am: `{now}`")
    lines.append(f"- Datensaetze: `{len(rows)}`")
    lines.append(f"- Ungueltige URLs: `{len(invalid)}`")
    lines.append(f"- Nicht-HTTPS URLs: `{len(non_https)}`")
    lines.append(f"- Potenziell generische Informations-Links: `{len(generic_info)}`")
    lines.append(f"- Potenziell generische Dokumenten-Links: `{len(generic_docs)}`")
    lines.append("")
    lines.append("## Top Hosts")
    lines.append("")
    lines.append("| Host | Anzahl |")
    lines.append("|---|---:|")
    for host, count in host_counts.most_common(20):
        lines.append(f"| {host} | {count} |")

    lines.append("")
    lines.append("## Stichprobe: Generische Informations-Links")
    lines.append("")
    lines.append("| programm_id | URL |")
    lines.append("|---|---|")
    for pid, url in generic_info[:25]:
        lines.append(f"| {pid} | {url} |")

    lines.append("")
    lines.append("## Stichprobe: Generische Dokumenten-Links")
    lines.append("")
    lines.append("| programm_id | URL |")
    lines.append("|---|---|")
    for pid, url in generic_docs[:25]:
        lines.append(f"| {pid} | {url} |")

    lines.append("")
    lines.append("## Stichprobe: Ungueltige URLs")
    lines.append("")
    lines.append("| programm_id | Feld | URL |")
    lines.append("|---|---|---|")
    for pid, label, url in invalid[:25]:
        lines.append(f"| {pid} | {label} | {url} |")

    lines.append("")
    lines.append("Hinweis: Dieser Report prueft Syntax/Struktur, nicht HTTP-Statuscodes.")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
