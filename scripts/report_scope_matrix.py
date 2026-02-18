#!/usr/bin/env python3
"""Generate scope matrix for Bund/EU/Laender coverage checks."""

from __future__ import annotations

import csv
import datetime as dt
import re
from collections import Counter
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/scope_matrix.md")

GERMAN_STATES = [
    "Baden-Wuerttemberg",
    "Bayern",
    "Berlin",
    "Brandenburg",
    "Bremen",
    "Hamburg",
    "Hessen",
    "Mecklenburg-Vorpommern",
    "Niedersachsen",
    "Nordrhein-Westfalen",
    "Rheinland-Pfalz",
    "Saarland",
    "Sachsen",
    "Sachsen-Anhalt",
    "Schleswig-Holstein",
    "Thueringen",
]


def normalize(value: str) -> str:
    return (value or "").strip().lower()


def in_any(text: str, needles: list[str]) -> bool:
    return any(n in text for n in needles)


def is_eu_region(region: str) -> bool:
    # Match standalone EU marker, not substrings like "deutschland".
    return re.search(r"\beu\b", region) is not None


def bucket(row: dict[str, str]) -> str:
    region = normalize(row.get("region", ""))
    traeger = normalize(row.get("traeger", ""))

    if is_eu_region(region) or in_any(
        traeger,
        ["europ", "eic", "eismea", "eacea", "euspa", "cinea", "ha dea", "hadea"],
    ):
        return "EU"

    if "deutschland" in region and in_any(
        traeger,
        [
            "bmbf",
            "bmwk",
            "bmas",
            "bmuv",
            "bafa",
            "kfw",
            "bmf",
            "bund",
            "bsfz",
            "rentenbank",
        ],
    ):
        return "Bund"

    if row.get("region", "") in GERMAN_STATES:
        return "Laender/Landesbanken"

    return "Sonstige"


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    by_bucket = Counter(bucket(r) for r in rows)
    by_status = Counter((r.get("status") or "").strip() for r in rows)
    by_state = Counter((r.get("region") or "").strip() for r in rows)

    lines: list[str] = []
    lines.append("# Scope Matrix")
    lines.append("")
    lines.append(f"- Erzeugt am: `{now}`")
    lines.append(f"- Datensaetze gesamt: `{len(rows)}`")
    lines.append("")
    lines.append("## Bereichsabdeckung")
    lines.append("")
    lines.append("| Bereich | Anzahl |")
    lines.append("|---|---:|")
    for key in ["Bund", "EU", "Laender/Landesbanken", "Sonstige"]:
        lines.append(f"| {key} | {by_bucket.get(key, 0)} |")
    lines.append("")
    lines.append("## Status gesamt")
    lines.append("")
    lines.append("| Status | Anzahl |")
    lines.append("|---|---:|")
    for key in ["laufend", "offen", "geplant"]:
        lines.append(f"| {key} | {by_status.get(key, 0)} |")
    lines.append("")
    lines.append("## Bundeslaender-Abdeckung")
    lines.append("")
    lines.append("| Bundesland | Anzahl Datensaetze |")
    lines.append("|---|---:|")
    for state in GERMAN_STATES:
        lines.append(f"| {state} | {by_state.get(state, 0)} |")
    lines.append("")
    lines.append("## Zieldefinition 100% (operativ)")
    lines.append("")
    lines.append("1. Bund: offizielle, aktuell beantragbare Unternehmensprogramme enthalten.")
    lines.append("2. EU: relevante Calls/Programme fuer deutsche Unternehmen enthalten.")
    lines.append("3. Laender/Landesbanken: pro Bundesland Kernprogramme enthalten.")
    lines.append("4. Jeder Datensatz mit gueltigen Links fuer Informationen und Dokumente.")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
