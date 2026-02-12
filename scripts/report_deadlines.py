#!/usr/bin/env python3
"""Generate deadline snapshot for foerderprogramme dataset."""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("docs/deadline_snapshot.md")


def parse_dates(raw: str) -> list[dt.date]:
    if not raw:
        return []
    out: list[dt.date] = []
    for token in raw.split("|"):
        value = token.strip()
        if not value:
            continue
        try:
            out.append(dt.date.fromisoformat(value))
            continue
        except ValueError:
            pass
        try:
            out.append(dt.datetime.strptime(value, "%d.%m.%Y").date())
        except ValueError:
            continue
    return sorted(set(out))


def first_last_dates(row: dict[str, str]) -> tuple[dt.date | None, dt.date | None]:
    values = [
        (row.get("call_deadline") or "").strip(),
        (row.get("call_close_date") or "").strip(),
        (row.get("frist") or "").strip(),
    ]
    dates: list[dt.date] = []
    for value in values:
        dates.extend(parse_dates(value))
    uniq = sorted(set(dates))
    if not uniq:
        return None, None
    return uniq[0], uniq[-1]


def md_list(items: list[str]) -> list[str]:
    if not items:
        return ["- keine"]
    return [f"- {i}" for i in items]


def main() -> int:
    today = dt.date.today()
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))

    open_with_fixed: list[str] = []
    open_rolling: list[str] = []
    open_past_only: list[str] = []
    planned_with_past: list[str] = []

    for row in rows:
        status = (row.get("status") or "").strip().lower()
        pid = (row.get("programm_id") or "").strip()
        name = (row.get("programm_name") or "").strip()
        frist_raw = (row.get("frist") or "").strip().lower()

        first_d, last_d = first_last_dates(row)
        if status == "offen":
            if last_d is None:
                if any(k in frist_raw for k in ["rollierend", "losverfahren", "programmabhaengig", "laufend"]):
                    open_rolling.append(f"`{pid}` | {name}")
                else:
                    open_rolling.append(f"`{pid}` | {name} (ohne Datum)")
            elif last_d < today:
                open_past_only.append(f"`{pid}` | {name} | letzte Frist `{last_d.isoformat()}`")
            else:
                open_with_fixed.append(
                    f"`{pid}` | {name} | naechste/letzte Frist `{first_d.isoformat()}` / `{last_d.isoformat()}`"
                )
        elif status == "geplant" and last_d and last_d < today:
            planned_with_past.append(f"`{pid}` | {name} | letzte Frist `{last_d.isoformat()}`")

    lines: list[str] = []
    lines.append("# Deadline Snapshot")
    lines.append("")
    lines.append(f"- Erzeugt am: `{today.isoformat()}`")
    lines.append(f"- Gepruefte Datensaetze: `{len(rows)}`")
    lines.append("")
    lines.append("## Offen Mit Datumsfrist")
    lines.append("")
    lines.extend(md_list(sorted(open_with_fixed)))
    lines.append("")
    lines.append("## Offen Rollierend")
    lines.append("")
    lines.extend(md_list(sorted(open_rolling)))
    lines.append("")
    lines.append("## Offen Nur Vergangene Fristen")
    lines.append("")
    lines.extend(md_list(sorted(open_past_only)))
    lines.append("")
    lines.append("## Geplant Mit Vergangener Frist")
    lines.append("")
    lines.extend(md_list(sorted(planned_with_past)))
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
