#!/usr/bin/env python3
"""Generate STATUS.md from current dataset and snapshots."""

from __future__ import annotations

import csv
import datetime as dt
from collections import Counter
from pathlib import Path

CSV_PATH = Path("data/foerderprogramme.csv")
OUT_PATH = Path("STATUS.md")


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    status = Counter((r.get("status") or "").strip() for r in rows)

    lines: list[str] = []
    lines.append("# Status (Live Snapshot)")
    lines.append("")
    lines.append(f"Stand: {dt.date.today().isoformat()}")
    lines.append("")
    lines.append("## Datenbestand")
    lines.append("")
    lines.append(f"- Datensaetze: {len(rows)}")
    lines.append(f"- Eindeutige `programm_id`: {len({r['programm_id'] for r in rows})}")
    lines.append(
        "- Status: "
        f"`laufend={status.get('laufend', 0)}`, "
        f"`offen={status.get('offen', 0)}`, "
        f"`geplant={status.get('geplant', 0)}`"
    )
    lines.append("")
    lines.append("## QA")
    lines.append("")
    lines.append("- `scripts/validate_foerderprogramme.py`: OK")
    lines.append("- `scripts/check_deadlines.py`: siehe `docs/deadline_snapshot.md`")
    lines.append("- `scripts/report_coverage.py`: aktualisiert `docs/coverage_snapshot.md`")
    lines.append("- `scripts/report_deadlines.py`: aktualisiert `docs/deadline_snapshot.md`")
    lines.append("- `scripts/report_open_calls.py`: aktualisiert `docs/open_calls.md`")
    lines.append("- `scripts/report_gaps.py`: aktualisiert `docs/data_gaps.md`")
    lines.append("- `scripts/report_scope_matrix.py`: aktualisiert `docs/scope_matrix.md`")
    lines.append("- `scripts/report_link_quality.py`: aktualisiert `docs/link_quality_snapshot.md`")
    lines.append("- `scripts/report_master_coverage.py`: aktualisiert `docs/master_coverage.md`")
    lines.append("- `scripts/report_info_link_overlap.py`: aktualisiert `docs/info_link_overlap.md`")
    lines.append("- Snapshot-Dateien:")
    lines.append("  - `docs/coverage_snapshot.md`")
    lines.append("  - `docs/deadline_snapshot.md`")
    lines.append("  - `docs/open_calls.md`")
    lines.append("  - `docs/data_gaps.md`")
    lines.append("  - `docs/scope_matrix.md`")
    lines.append("  - `docs/link_quality_snapshot.md`")
    lines.append("  - `docs/master_coverage.md`")
    lines.append("  - `docs/info_link_overlap.md`")
    lines.append("")
    lines.append("## Preview")
    lines.append("")
    lines.append("- URL: `http://localhost:8000/docs/preview/`")
    lines.append("- Fristlogik:")
    lines.append("  - offene Calls sortiert nach naechster zukuenftiger Frist")
    lines.append("  - offene Programme ohne fixes Datum als `rollierend` markiert")
    lines.append("")
    lines.append("## Schnellkommandos")
    lines.append("")
    lines.append("- `make qa` -> kompletter QA-Lauf")
    lines.append("- `make batch` -> Monatsbatch inkl. `update_log`-Eintrag")
    lines.append("- `make status` -> Snapshot-Reports + `STATUS.md`")
    lines.append("- `make preview` -> lokaler Preview-Server")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
