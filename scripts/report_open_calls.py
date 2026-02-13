#!/usr/bin/env python3
"""Generate compact open-calls report (dated vs rolling)."""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/open_calls.md")


def parse_dates(raw: str) -> list[dt.date]:
    if not raw:
        return []
    dates: list[dt.date] = []
    for token in raw.split("|"):
        value = token.strip()
        if not value:
            continue
        try:
            dates.append(dt.date.fromisoformat(value))
            continue
        except ValueError:
            pass
        try:
            dates.append(dt.datetime.strptime(value, "%d.%m.%Y").date())
        except ValueError:
            continue
    return sorted(set(dates))


def collect_dates(row: dict[str, str]) -> list[dt.date]:
    values = [
        (row.get("call_deadline") or "").strip(),
        (row.get("call_close_date") or "").strip(),
        (row.get("frist") or "").strip(),
    ]
    all_dates: list[dt.date] = []
    for value in values:
        all_dates.extend(parse_dates(value))
    return sorted(set(all_dates))


def is_rolling(row: dict[str, str]) -> bool:
    frist = (row.get("frist") or "").lower()
    return any(k in frist for k in ["rollierend", "losverfahren", "programmabhaengig", "laufend"])


def main() -> int:
    today = dt.date.today()
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    open_rows = [r for r in rows if (r.get("status") or "").strip().lower() == "offen"]

    dated: list[tuple[dt.date, str]] = []
    rolling: list[str] = []

    for row in open_rows:
        pid = (row.get("programm_id") or "").strip()
        name = (row.get("programm_name") or "").strip()
        url = (row.get("richtlinie_url") or row.get("quelle_url") or "").strip()
        dates = collect_dates(row)
        if dates:
            next_date = next((d for d in dates if d >= today), dates[-1])
            dated.append((next_date, f"- `{pid}` | {name} | Frist `{next_date.isoformat()}` | {url}"))
        elif is_rolling(row):
            rolling.append(f"- `{pid}` | {name} | rollierend | {url}")
        else:
            rolling.append(f"- `{pid}` | {name} | offen (ohne Datumsangabe) | {url}")

    dated.sort(key=lambda x: x[0])
    rolling.sort()

    lines: list[str] = []
    lines.append("# Open Calls")
    lines.append("")
    lines.append(f"- Erzeugt am: `{today.isoformat()}`")
    lines.append(f"- Offen gesamt: `{len(open_rows)}`")
    lines.append(f"- Mit Datumsfrist: `{len(dated)}`")
    lines.append(f"- Rollierend/ohne Datum: `{len(rolling)}`")
    lines.append("")
    lines.append("## Mit Datumsfrist (naechste Frist aufsteigend)")
    lines.append("")
    if dated:
        lines.extend(item for _, item in dated)
    else:
        lines.append("- keine")
    lines.append("")
    lines.append("## Rollierend / Ohne Datum")
    lines.append("")
    if rolling:
        lines.extend(rolling)
    else:
        lines.append("- keine")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
