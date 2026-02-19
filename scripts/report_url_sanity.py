#!/usr/bin/env python3
"""Generate URL sanity snapshot without external network calls."""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/url_sanity_snapshot.md")


GENERIC_PATTERNS = [
    "/foerderprogramme",
    "/foerderprogramme-a-z",
    "/unternehmen/",
    "/service/downloads",
    "/download-center",
    "/downloads",
]


def _looks_generic(url: str) -> bool:
    lower = url.lower()
    return any(p in lower for p in GENERIC_PATTERNS)


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    invalid = []
    non_https = []
    generic_info = []
    generic_docs = []
    host_counts = Counter()
    by_host = defaultdict(int)

    for r in rows:
        pid = (r.get("programm_id") or "").strip()
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
            by_host[p.netloc.lower()] += 1
            if label == "Informationen" and _looks_generic(url):
                generic_info.append((pid, url))
            if label == "Dokumente" and _looks_generic(url):
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
