# QA Commands

## Standardlauf

```bash
cd "/Users/jonasweiss/Documents/New project"
scripts/run_qa.sh
```

## Einzelchecks

```bash
cd "/Users/jonasweiss/Documents/New project"
python3 scripts/validate_foerderprogramme.py
python3 scripts/check_deadlines.py
python3 scripts/report_coverage.py
```

## Erwartung

- `validate_foerderprogramme.py`: `Validation OK`
- `check_deadlines.py`: keine `offen`-Calls mit nur abgelaufener Frist
- `report_coverage.py`: aktualisiert `/Users/jonasweiss/Documents/New project/docs/coverage_snapshot.md`
