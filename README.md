# Foerdermittel-Navigator (Workspace)

Dieses Verzeichnis enthaelt den aktuellen Arbeitsstand fuer den Foerdermittel-Navigator (Deutschland, Unternehmen/KMU) inklusive Datenbasis, Preview und QA-Automation.

## Schnellstart

```bash
cd "/Users/jonasweiss/Documents/New project"
make preview
```

Preview im Browser:

- `http://127.0.0.1:8000/docs/preview/`
- alternativ: `http://localhost:8000/docs/preview/`

## QA und Batch

```bash
cd "/Users/jonasweiss/Documents/New project"
make qa
make batch
```

`make qa` erzeugt alle Snapshot-Reports:
- `docs/coverage_snapshot.md`
- `docs/deadline_snapshot.md`
- `docs/open_calls.md`
- `docs/data_gaps.md`

`make status` erzeugt:
- alle Snapshot-Reports (wie oben)
- `docs/scope_matrix.md` (Bund/EU/Laender-Matrix)
- `docs/link_quality_snapshot.md` (Informationen/Dokumente-Qualitaet)
- `docs/link_structure_snapshot.md` (Strukturcheck Informationen/Dokumente)
- `docs/url_sanity_snapshot.md` (URL-Format- und Spezifitaetscheck)
- `docs/master_coverage.md` (Prio-Abdeckung Bund/EU/Laenderbanken)
- `docs/info_link_overlap.md` (gleiche URL in Informationen/Dokumente)
- `STATUS.md` (automatisch aus aktuellem Datenstand)

## Wichtige Dateien

- Daten: `data/foerderprogramme.csv`
- Update-Log: `data/update_log.csv`
- Status-Snapshot: `STATUS.md`
- Live-Log: `docs/live_log.md`
- Coverage-Snapshot: `docs/coverage_snapshot.md`
- Deadline-Snapshot: `docs/deadline_snapshot.md`
- Open-Calls-Snapshot: `docs/open_calls.md`
- Scope-Matrix: `docs/scope_matrix.md`
- Link-Qualitaet: `docs/link_quality_snapshot.md`
- Link-Struktur: `docs/link_structure_snapshot.md`
- URL-Sanity: `docs/url_sanity_snapshot.md`
- Master-Coverage: `docs/master_coverage.md`
- Link-Overlap: `docs/info_link_overlap.md`
- Update-Prozess: `docs/update_process.md`
- QA-Kommandos: `docs/qa_commands.md`

## Operativer Einstieg

1. `STATUS.md` lesen
2. `docs/coverage_snapshot.md` und `docs/deadline_snapshot.md` pruefen
3. bei Bedarf `make qa` oder `make batch` ausfuehren

## Skripte

- `scripts/validate_foerderprogramme.py`
- `scripts/check_deadlines.py`
- `scripts/report_coverage.py`
- `scripts/report_deadlines.py`
- `scripts/run_qa.sh`
- `scripts/run_monthly_batch.sh`
