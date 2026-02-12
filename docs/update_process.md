# Update-Prozess (monatlich)

Ziel: Vollstaendige, nachvollziehbare Aktualitaet der Programme und Calls.

## Datenprinzip
- `letzte_pruefung`: Datum der letzten aktiven Pruefung je Programm.
- `richtlinie_stand`: Stand/Datum der Richtlinie oder Call-Dokumente.
- `status` + `kategorie`:
  - `laufend` = Antrag jederzeit moeglich
  - `offen` = Call/Einreichfenster offen
  - `zukuenftig` = angekuendigt, noch nicht offen

## Monatlicher Ablauf (Batch)
1. Programme mit `status=laufend` pruefen (Richtlinie, Antragslage, Stand).
2. Programme mit `status=offen` pruefen (Fristen, Call-Status, etwaige Updates).
3. `letzte_pruefung` aktualisieren.
4. QA-Checks gesammelt ausfuehren: `scripts/run_qa.sh`.
   Artefakte:
   - `docs/coverage_snapshot.md`
   - `docs/deadline_snapshot.md`
5. Aenderungen in `data/update_log.csv` protokollieren.

## Frist-Logik
- `offen` mit konkreter Frist: Datumsfelder in `call_deadline`, optional `call_close_date`/`frist`.
- `offen` ohne fixes Datum: in `frist` als `rollierend (...)` kennzeichnen.
- `geplant` mit abgelaufener Frist bleibt als Historien-/Folgeaufruf-Hinweis zulaessig, muss aber im Check sichtbar sein.

## Schnellstart

```bash
cd "/Users/jonasweiss/Documents/New project"
scripts/run_qa.sh
```

## Aenderungsprotokoll
Jeder Update-Lauf erzeugt Eintraege in `data/update_log.csv` mit:
- `batch_date`
- `quelle`
- `anzahl_geprueft`
- `anzahl_geaendert`
- `kommentar`
