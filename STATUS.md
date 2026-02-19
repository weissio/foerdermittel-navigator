# Status (Live Snapshot)

Stand: 2026-02-19

## Datenbestand

- Datensaetze: 1024
- Eindeutige `programm_id`: 1024
- Status: `laufend=614`, `offen=405`, `geplant=5`

## QA

- `scripts/validate_foerderprogramme.py`: OK
- `scripts/check_deadlines.py`: siehe `docs/deadline_snapshot.md`
- `scripts/report_coverage.py`: aktualisiert `docs/coverage_snapshot.md`
- `scripts/report_deadlines.py`: aktualisiert `docs/deadline_snapshot.md`
- `scripts/report_open_calls.py`: aktualisiert `docs/open_calls.md`
- `scripts/report_gaps.py`: aktualisiert `docs/data_gaps.md`
- `scripts/report_scope_matrix.py`: aktualisiert `docs/scope_matrix.md`
- `scripts/report_link_quality.py`: aktualisiert `docs/link_quality_snapshot.md`
- `scripts/report_link_structure.py`: aktualisiert `docs/link_structure_snapshot.md`
- `scripts/report_url_sanity.py`: aktualisiert `docs/url_sanity_snapshot.md`
- `scripts/report_master_coverage.py`: aktualisiert `docs/master_coverage.md`
- `scripts/report_info_link_overlap.py`: aktualisiert `docs/info_link_overlap.md`
- Snapshot-Dateien:
  - `docs/coverage_snapshot.md`
  - `docs/deadline_snapshot.md`
  - `docs/open_calls.md`
  - `docs/data_gaps.md`
  - `docs/scope_matrix.md`
  - `docs/link_quality_snapshot.md`
  - `docs/link_structure_snapshot.md`
  - `docs/url_sanity_snapshot.md`
  - `docs/master_coverage.md`
  - `docs/info_link_overlap.md`

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
