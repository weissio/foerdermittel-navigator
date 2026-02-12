#!/usr/bin/env python3
"""Check deadline consistency for foerderprogramme CSV."""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")


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
    return sorted(dates)


def main() -> int:
    today = dt.date.today()
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))

    open_without_deadline: list[str] = []
    open_past_deadline: list[str] = []
    planned_with_past_deadline: list[str] = []

    for row in rows:
        status = (row.get("status") or "").strip().lower()
        pid = (row.get("programm_id") or "").strip()
        title = (row.get("programm_name") or "").strip()
        date_values = [
            (row.get("call_deadline") or "").strip(),
            (row.get("call_close_date") or "").strip(),
            (row.get("frist") or "").strip(),
        ]
        dates: list[dt.date] = []
        for value in date_values:
            dates.extend(parse_dates(value))
        dates = sorted(set(dates))

        if status == "offen":
            if not dates:
                open_without_deadline.append(f"{pid} | {title}")
            elif dates[-1] < today:
                open_past_deadline.append(f"{pid} | {title} | last={dates[-1].isoformat()}")
        elif status == "geplant" and dates and dates[-1] < today:
            planned_with_past_deadline.append(f"{pid} | {title} | last={dates[-1].isoformat()}")

    print(f"Date: {today.isoformat()}")
    print(f"Checked rows: {len(rows)}")
    print(f"offen without deadline: {len(open_without_deadline)}")
    for item in open_without_deadline:
        print(f"- {item}")
    print(f"offen with only past deadline: {len(open_past_deadline)}")
    for item in open_past_deadline:
        print(f"- {item}")
    print(f"geplant with past deadline: {len(planned_with_past_deadline)}")
    for item in planned_with_past_deadline:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
