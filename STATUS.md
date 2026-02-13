# Status (Live Snapshot)

Stand: 2026-02-13

## Datenbestand

- Datensaetze: 158
- Eindeutige `programm_id`: 158
- Status: `laufend=132`, `offen=21`, `geplant=5`

## QA

- `scripts/validate_foerderprogramme.py`: OK
- `scripts/check_deadlines.py`:
  - `offen without deadline = 0`
  - `offen with rolling/program-dependent deadline = 6`
  - `offen with only past deadline = 0`
  - `geplant with past deadline = 1` (`SA_INVESTIERT`)
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
- `make preview` -> lokaler Preview-Server
