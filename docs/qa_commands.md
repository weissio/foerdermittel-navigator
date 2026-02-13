# QA Commands

## Standardlauf

```bash
cd "/Users/jonasweiss/Documents/New project"
scripts/run_qa.sh
```

Alternative:

```bash
cd "/Users/jonasweiss/Documents/New project"
make qa
```

Weitere Shortcuts:

```bash
cd "/Users/jonasweiss/Documents/New project"
make status      # coverage + deadline + open_calls
make open_calls  # nur open_calls.md
make gaps        # data_gaps.md
```

`make status` erzeugt:
- `docs/coverage_snapshot.md`
- `docs/deadline_snapshot.md`
- `docs/open_calls.md`
- `docs/data_gaps.md`
- `STATUS.md`

## Monatsbatch (QA + update_log)

```bash
cd "/Users/jonasweiss/Documents/New project"
scripts/run_monthly_batch.sh "manueller_batch" 0 "Monatslauf mit QA"
```

Alternative:

```bash
cd "/Users/jonasweiss/Documents/New project"
make batch
```

## Einzelchecks

```bash
cd "/Users/jonasweiss/Documents/New project"
python3 scripts/validate_foerderprogramme.py
python3 scripts/check_deadlines.py
python3 scripts/report_coverage.py
python3 scripts/report_deadlines.py
python3 scripts/report_open_calls.py
```

## Erwartung

- `validate_foerderprogramme.py`: `Validation OK`
- `check_deadlines.py`: keine `offen`-Calls mit nur abgelaufener Frist
- `report_coverage.py`: aktualisiert `/Users/jonasweiss/Documents/New project/docs/coverage_snapshot.md`
- `report_deadlines.py`: aktualisiert `/Users/jonasweiss/Documents/New project/docs/deadline_snapshot.md`
- `report_open_calls.py`: aktualisiert `/Users/jonasweiss/Documents/New project/docs/open_calls.md`
- `report_gaps.py`: aktualisiert `/Users/jonasweiss/Documents/New project/docs/data_gaps.md`
