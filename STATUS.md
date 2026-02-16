# Status (Live Snapshot)

Stand: 2026-02-16

## Datenbestand

- Datensaetze: 904
- Eindeutige `programm_id`: 904
- Status: `laufend=557`, `offen=342`, `geplant=5`

## QA

- `scripts/validate_foerderprogramme.py`: OK
- `scripts/check_deadlines.py`: siehe `docs/deadline_snapshot.md`
- `scripts/report_coverage.py`: aktualisiert `docs/coverage_snapshot.md`
- `scripts/report_deadlines.py`: aktualisiert `docs/deadline_snapshot.md`
- `scripts/report_open_calls.py`: aktualisiert `docs/open_calls.md`
- `scripts/report_gaps.py`: aktualisiert `docs/data_gaps.md`
- Snapshot-Dateien:
  - `docs/coverage_snapshot.md`
  - `docs/deadline_snapshot.md`
  - `docs/open_calls.md`
  - `docs/data_gaps.md`

## Preview

- URL: `http://localhost:8000/docs/preview/`
- Fristlogik:
  - offene Calls sortiert nach naechster zukuenftiger Frist
  - offene Programme ohne fixes Datum als `rollierend` markiert

## Schnellkommandos

- `make qa` -> kompletter QA-Lauf
- `make batch` -> Monatsbatch inkl. `update_log`-Eintrag
- `make status` -> Snapshot-Reports + `STATUS.md`
- `make preview` -> lokaler Preview-Server
