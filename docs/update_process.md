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
4. Aenderungen in `data/update_log.csv` protokollieren.

## Aenderungsprotokoll
Jeder Update-Lauf erzeugt Eintraege in `data/update_log.csv` mit:
- `batch_date`
- `quelle`
- `anzahl_geprueft`
- `anzahl_geaendert`
- `kommentar`
