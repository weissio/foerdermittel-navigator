#!/usr/bin/env python3
"""Report where Informationen and Dokumente point to the same URL."""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter, defaultdict
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/info_link_overlap.md")


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    same_rows = []
    by_url = Counter()
    by_url_ids: dict[str, list[str]] = defaultdict(list)

    for r in rows:
        info = (r.get("richtlinie_url") or "").strip()
        docs = (r.get("quelle_url") or "").strip()
        if info and docs and info == docs:
            same_rows.append(r)
            by_url[info] += 1
            by_url_ids[info].append(r["programm_id"])

    lines: list[str] = []
    lines.append("# Informationen/Dokumente Overlap")
    lines.append("")
    lines.append(f"- Erzeugt am: `{now}`")
    lines.append(f"- Datensaetze gesamt: `{len(rows)}`")
    lines.append(f"- Gleicher Link in Informationen und Dokumente: `{len(same_rows)}`")
    lines.append(
        f"- Anteil: `{(len(same_rows) / max(len(rows), 1)) * 100:.1f}%`"
    )
    lines.append("")
    lines.append("## Top Overlap-URLs")
    lines.append("")
    lines.append("| URL | Anzahl Datensaetze | Beispiel-IDs |")
    lines.append("|---|---:|---|")
    for url, count in by_url.most_common(30):
        sample = ", ".join(by_url_ids[url][:4])
        lines.append(f"| {url} | {count} | {sample} |")
    lines.append("")
    lines.append("## Regel fuer Bereinigung")
    lines.append("")
    lines.append("1. Wenn moeglich: `Informationen` auf Programmseite, `Dokumente` auf Formular/Downloadseite.")
    lines.append("2. Falls kein separater Dokumentenbereich vorhanden: Programmseite in beiden Feldern belassen.")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
