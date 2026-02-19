# QM Policy (Links)

## Ziel
- Keine defekten oder falschen Programm-Links in produktiven Datensaetzen.
- Jede Aenderung muss vor Merge durch technische Gates.

## Datenklassen
- `link_klasse` (Pflichtfeld je Datensatz):
  - `programm_spezifisch`
  - `call_spezifisch`
  - `dokument_spezifisch`
  - `portal_uebersicht`

## Exceptions
- Datei: `data/link_exceptions.csv`
- Felder: `programm_id, feld, url, grund, gueltig_bis, owner, status`
- Nur `status=active` und gueltige Frist zaehlen.

## Gates
1. `make qa`
- Schema/Status/Kategorie/Blocklists/Domain-Konsistenz.

2. `make gate_changed`
- Prueft nur geaenderte Datensaetze gegen `origin/main`.
- Merge nur bei `Fehlgeschlagene Links = 0`.

3. `make links_live`
- Voll-/Stichprobencheck fuer operative Qualitaetsmessung.

## Merge-Regel
- Kein Push auf `main`, wenn `make gate_changed` fehlschlaegt.

## KPI
- `docs/live_link_health_snapshot.md`: Gesamtzustand.
- `docs/changed_link_health_snapshot.md`: Merge-relevanter Delta-Zustand.
