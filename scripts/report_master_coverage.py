#!/usr/bin/env python3
"""Generate master coverage report for Bund/EU/Laender priorities."""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/master_coverage.md")

BUND_KEYS = [
    "BMWK",
    "BMBF",
    "BAFA",
    "KfW",
    "BMAS",
    "BMUV",
    "BMF",
    "BMDV",
    "BMEL",
]

EU_KEYS = [
    "Europaeische Kommission",
    "EIC",
    "EISMEA",
    "EACEA",
    "CINEA",
    "EUREKA",
    "EUIPO",
    "EUSPA",
]

LAENDERBANK_KEYS = [
    "L-Bank",
    "LfA",
    "ILB",
    "IBB",
    "NRW.BANK",
    "NBank",
    "WIBank",
    "ISB",
    "SAB",
    "IB.SH",
    "IFB Hamburg",
    "SIKB",
    "BAB",
    "TAB",
    "LFI M-V",
    "Investitionsbank Sachsen-Anhalt",
]


def count_for(rows: list[dict[str, str]], key: str) -> int:
    kl = key.lower()
    return sum(1 for r in rows if kl in (r.get("traeger") or "").lower())


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    lines: list[str] = []
    lines.append("# Master Coverage")
    lines.append("")
    lines.append(f"- Erzeugt am: `{now}`")
    lines.append(f"- Datensaetze gesamt: `{len(rows)}`")
    lines.append("")
    lines.append("## Bund (Prio 1)")
    lines.append("")
    lines.append("| Traeger/Familie | Datensaetze |")
    lines.append("|---|---:|")
    for key in BUND_KEYS:
        lines.append(f"| {key} | {count_for(rows, key)} |")
    lines.append("")
    lines.append("## EU (Prio 2)")
    lines.append("")
    lines.append("| Traeger/Familie | Datensaetze |")
    lines.append("|---|---:|")
    for key in EU_KEYS:
        lines.append(f"| {key} | {count_for(rows, key)} |")
    lines.append("")
    lines.append("## Laender/Landesbanken (Prio 3)")
    lines.append("")
    lines.append("| Traeger/Familie | Datensaetze |")
    lines.append("|---|---:|")
    for key in LAENDERBANK_KEYS:
        lines.append(f"| {key} | {count_for(rows, key)} |")
    lines.append("")
    lines.append("## Hinweis")
    lines.append("")
    lines.append("Ziel ist Vollstaendigkeit auf Programmebene, nicht kuenstliche Aufblaehung ueber Dubletten.")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
