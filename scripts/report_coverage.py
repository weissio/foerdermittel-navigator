#!/usr/bin/env python3
"""Create coverage snapshot for foerderprogramme dataset."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

INPUT = Path("data/foerderprogramme.csv")
OUTPUT = Path("docs/coverage_snapshot.md")


def top(counter: Counter[str], n: int = 20) -> list[tuple[str, int]]:
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def fmt_table(rows: list[tuple[str, int]], c1: str, c2: str = "Anzahl") -> str:
    out = [f"| {c1} | {c2} |", "|---|---:|"]
    for key, value in rows:
        out.append(f"| {key} | {value} |")
    return "\n".join(out)


def main() -> int:
    with INPUT.open(encoding="utf-8", newline="") as f:
        data = list(csv.DictReader(f))

    status = Counter((r.get("status") or "").strip() for r in data)
    kategorie = Counter((r.get("kategorie") or "").strip() for r in data)
    region = Counter((r.get("region") or "").strip() for r in data)
    traeger = Counter((r.get("traeger") or "").strip() for r in data)
    thema = Counter((r.get("thema") or "").strip() for r in data)

    lines: list[str] = []
    lines.append("# Coverage Snapshot")
    lines.append("")
    lines.append("Automatisch erzeugt aus `data/foerderprogramme.csv`.")
    lines.append("")
    lines.append(f"- Datensaetze: `{len(data)}`")
    lines.append(f"- Eindeutige `programm_id`: `{len({r['programm_id'] for r in data})}`")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(fmt_table(top(status, n=10), "Status"))
    lines.append("")
    lines.append("## Kategorie")
    lines.append("")
    lines.append(fmt_table(top(kategorie, n=10), "Kategorie"))
    lines.append("")
    lines.append("## Top Regionen")
    lines.append("")
    lines.append(fmt_table(top(region, n=20), "Region"))
    lines.append("")
    lines.append("## Top Traeger")
    lines.append("")
    lines.append(fmt_table(top(traeger, n=20), "Traeger"))
    lines.append("")
    lines.append("## Top Themen")
    lines.append("")
    lines.append(fmt_table(top(thema, n=20), "Thema"))
    lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
