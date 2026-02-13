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

## Wichtige Dateien

- Daten: `data/foerderprogramme.csv`
- Update-Log: `data/update_log.csv`
- Status-Snapshot: `STATUS.md`
- Live-Log: `docs/live_log.md`
- Coverage-Snapshot: `docs/coverage_snapshot.md`
- Deadline-Snapshot: `docs/deadline_snapshot.md`
- Update-Prozess: `docs/update_process.md`
- QA-Kommandos: `docs/qa_commands.md`

## Skripte

- `scripts/validate_foerderprogramme.py`
- `scripts/check_deadlines.py`
- `scripts/report_coverage.py`
- `scripts/report_deadlines.py`
- `scripts/run_qa.sh`
- `scripts/run_monthly_batch.sh`
