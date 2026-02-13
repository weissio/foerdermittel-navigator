#!/usr/bin/env python3
"""Generate simple gap report for dataset expansion priorities."""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/data_gaps.md")


def top(counter: Counter[str], limit: int = 15) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]


def bottom(counter: Counter[str], limit: int = 15) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda kv: (kv[1], kv[0]))[:limit]


def table(rows: list[tuple[str, int]], c1: str, c2: str = "Anzahl") -> list[str]:
    out = [f"| {c1} | {c2} |", "|---|---:|"]
    out.extend([f"| {k} | {v} |" for k, v in rows])
    return out


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    region = Counter((r.get("region") or "").strip() for r in rows)
    traeger = Counter((r.get("traeger") or "").strip() for r in rows)
    thema = Counter((r.get("thema") or "").strip() for r in rows)
    status = Counter((r.get("status") or "").strip() for r in rows)

    lines: list[str] = []
    lines.append("# Data Gaps")
    lines.append("")
    lines.append(f"- Erzeugt am: `{now}`")
    lines.append(f"- Datensaetze: `{len(rows)}`")
    lines.append("")
    lines.append("## Status-Verteilung")
    lines.append("")
    lines.extend(table(sorted(status.items(), key=lambda kv: kv[0]), "Status"))
    lines.append("")
    lines.append("## Unterrepraesentierte Regionen")
    lines.append("")
    lines.extend(table(bottom(region), "Region"))
    lines.append("")
    lines.append("## Dominierende Regionen")
    lines.append("")
    lines.extend(table(top(region), "Region"))
    lines.append("")
    lines.append("## Unterrepraesentierte Traeger")
    lines.append("")
    lines.extend(table(bottom(traeger), "Traeger"))
    lines.append("")
    lines.append("## Unterrepraesentierte Themen")
    lines.append("")
    lines.extend(table(bottom(thema), "Thema"))
    lines.append("")
    lines.append("## Priorisierungsregel")
    lines.append("")
    lines.append("1. Zuerst offene Calls in unterrepraesentierten Regionen/Themen.")
    lines.append("2. Danach laufende Kernprogramme pro Landesbank/Landesfoerderinstitut vervollstaendigen.")
    lines.append("3. Zuletzt Portaleintraege in konkrete Einzelprogramme herunterbrechen.")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
