# HANDOVER

## Projekt
- Name: Foerdermittel-Navigator
- Repo: https://github.com/weissio/foerdermittel-navigator.git

## Aktueller Stand
- Branch: `main`
- Letzter geplanter Fokus: Datenausbau in stark frequentierten Bundesprogrammen
- QA-Standard: `make qa`
- Status-Update: `make status`

## Naechste Schritte (aktuell)
1. Weitere stark frequentierte Bundesprogramme in `data/foerderprogramme.csv` ergaenzen.
2. Quellen in `docs/quellen.md` nachziehen.
3. `make qa` laufen lassen.
4. Ergebnisse in `docs/live_log.md` dokumentieren.
5. Commit + Push.

## Wichtige Dateien
- `STATUS.md`
- `docs/live_log.md`
- `data/foerderprogramme.csv`
- `docs/quellen.md`
- `docs/update_process.md`
- `docs/qa_commands.md`

## Copy/Paste Prompt Fuer Neue Codex-Session
Nutze den folgenden Text in einer neuen Codex-Session:

```text
Arbeite im Repo foerdermittel-navigator auf Branch main.
Bitte zuerst:
1) git pull
2) STATUS.md lesen
3) docs/live_log.md lesen (letzte Eintraege)
4) HANDOVER.md lesen

Danach ohne Rueckfragen mit dem naechsten Datenausbau-Block weitermachen:
- Fokus: stark frequentierte Bundesprogramme zuerst
- Danach: make qa
- Dann: docs/live_log.md aktualisieren
- Dann: Commit + Push

Wichtig: keine Infrastruktur-/UI-Nebenbaustellen, sofern nicht fuer Datenqualitaet zwingend notwendig.
```
