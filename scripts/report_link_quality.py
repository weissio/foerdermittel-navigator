#!/usr/bin/env python3
"""Generate link quality snapshot for Informationen/Dokumente fields."""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/link_quality_snapshot.md")


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    same = 0
    missing_info = 0
    missing_docs = 0
    domains = Counter()

    for r in rows:
        info = (r.get("richtlinie_url") or "").strip()
        docs = (r.get("quelle_url") or "").strip()

        if not info:
            missing_info += 1
        if not docs:
            missing_docs += 1
        if info and docs and info == docs:
            same += 1

        for url in [info, docs]:
            if "://" in url:
                host = url.split("://", 1)[1].split("/", 1)[0].lower()
                domains[host] += 1

    lines: list[str] = []
    lines.append("# Link Quality Snapshot")
    lines.append("")
    lines.append(f"- Erzeugt am: `{now}`")
    lines.append(f"- Datensaetze: `{len(rows)}`")
    lines.append(f"- Fehlend Informationen: `{missing_info}`")
    lines.append(f"- Fehlend Dokumente: `{missing_docs}`")
    lines.append(
        f"- Informationen = Dokumente (identische URL): `{same}` "
        f"({same / max(len(rows), 1) * 100:.1f}%)"
    )
    lines.append("")
    lines.append("## Top Domains")
    lines.append("")
    lines.append("| Domain | Verwendungen |")
    lines.append("|---|---:|")
    for host, cnt in domains.most_common(20):
        lines.append(f"| {host} | {cnt} |")
    lines.append("")
    lines.append("## Prioritaet")
    lines.append("")
    lines.append("1. Datensaetze mit identischer URL fuer Informationen/Dokumente zuerst trennen.")
    lines.append("2. Danach 404-Checks auf allen geaenderten Datensaetzen ausfuehren.")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
