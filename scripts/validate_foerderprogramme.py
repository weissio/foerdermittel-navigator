#!/usr/bin/env python3
"""Validate foerderprogramme CSV consistency."""

from __future__ import annotations

import csv
import datetime as dt
import sys
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS = {
    "programm_id",
    "programm_name",
    "status",
    "kategorie",
    "letzte_pruefung",
}

ALLOWED_STATUS = {"laufend", "offen", "geplant"}
ALLOWED_KATEGORIE = {"laufend", "offen", "zukuenftig"}
EXPECTED_KATEGORIE = {
    "laufend": "laufend",
    "offen": "offen",
    "geplant": "zukuenftig",
}

BLOCKED_DOC_URLS = {
    "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search",
    "https://www.foerderdatenbank.de/FDB/DE/Service/Onlineantrag/ESF/esf_node.html",
    "https://www.foerderdatenbank.de/FDB/DE/Service/Onlineantrag/EFRE/efre_node.html",
    "https://www.ibb.de/de/wirtschaftsfoerderung/download-center/download-center.html",
    "https://www.nbank.de/Service/Downloads/",
    "https://www.ib-sh.de/service/downloads/",
    "https://www.lfi-mv.de/service/downloads/",
    "https://www.aufbaubank.de/Service/Downloads",
    "https://www.ib-sachsen-anhalt.de/de/service/downloads",
    "https://www.lfa.de/website/de/service/downloads/index.php",
    "https://www.ilb.de/de/service/download-center/",
    "https://www.ilb.de/de/service/downloadcenter/",
    "https://www.sikb.de/foerderprodukte/unternehmensfoerderung",
    "https://isb.rlp.de/service/downloads.html",
    "https://www.wibank.de/wibank/infocenter/download-center/index.jsp",
    "https://www.bab-bremen.de/de/page/service/downloads",
    "https://www.europa-fuer-niedersachsen.de/foerderperiode-2021-2027/esfplus/",
    "https://www.foerderdatenbank.de/FDB/DE/Service/Onlineantrag/EFRE/efre_node.html#onlineantrag",
    "https://www.foerderdatenbank.de/FDB/DE/Service/Onlineantrag/ESF/esf_node.html#onlineantrag",
    "https://www.bafa.de/DE/Wirtschafts_Mittelstandsfoerderung/Beratung_Finanzierung/unternehmensberatung_node.html#formulare",
    "https://www.bafa.de/DE/Wirtschafts_Mittelstandsfoerderung/Invest/invest_node.html",
    "https://www.esf.bayern.de/imperia/md/content/stmas/stmas_inet/esf/dokumente/esfplus_foerderhinweise.pdf",
    "https://www.lfa.de/website/de/foerderangebote/innovationsfinanzierung/innovationskredit/index.php",
    "https://www.sab.sachsen.de/foerderprogramme#dokumente",
    "https://www.sikb.de/service/downloads",
}

BLOCKED_INFO_URLS = {
    "https://www.aktion-natuerlicher-klimaschutz.de",
    "https://www.chips-ju.europa.eu/calls-information_en",
    "https://www.bmel.de/DE/themen/laendliche-regionen/foerderung-des-laendlichen-raums/buleplus.html",
    "https://www.bmel.de/DE/themen/tiere/tierwohl/umbau-tierhaltung.html",
}


def _is_iso_date(value: str) -> bool:
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate(path: Path) -> int:
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 1

    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            print(f"ERROR: missing required columns: {sorted(missing)}")
            return 1

        rows = list(reader)

    errors: list[str] = []

    ids = [r["programm_id"].strip() for r in rows]
    duplicates = [k for k, v in Counter(ids).items() if v > 1]
    if duplicates:
        errors.append(f"duplicate programm_id: {duplicates}")

    for idx, row in enumerate(rows, start=2):
        programm_id = row["programm_id"].strip()
        status = row["status"].strip()
        kategorie = row["kategorie"].strip()
        letzte_pruefung = row["letzte_pruefung"].strip()
        traeger = row.get("traeger", "").strip()
        info_url = row.get("richtlinie_url", "").strip()
        quelle_url = row.get("quelle_url", "").strip()

        if not programm_id:
            errors.append(f"line {idx}: empty programm_id")

        if status not in ALLOWED_STATUS:
            errors.append(
                f"line {idx} ({programm_id}): invalid status '{status}'"
            )
        if kategorie not in ALLOWED_KATEGORIE:
            errors.append(
                f"line {idx} ({programm_id}): invalid kategorie '{kategorie}'"
            )

        expected = EXPECTED_KATEGORIE.get(status)
        if expected and kategorie != expected:
            errors.append(
                f"line {idx} ({programm_id}): expected kategorie '{expected}' for status '{status}', got '{kategorie}'"
            )

        if not letzte_pruefung:
            errors.append(f"line {idx} ({programm_id}): empty letzte_pruefung")
        elif not _is_iso_date(letzte_pruefung):
            errors.append(
                f"line {idx} ({programm_id}): invalid letzte_pruefung '{letzte_pruefung}'"
            )

        if quelle_url in BLOCKED_DOC_URLS:
            errors.append(
                f"line {idx} ({programm_id}): blocked quelle_url '{quelle_url}'"
            )

        if info_url in BLOCKED_INFO_URLS:
            errors.append(
                f"line {idx} ({programm_id}): blocked richtlinie_url '{info_url}'"
            )

        if "BMWK" in traeger:
            if "bmwe.de" in info_url:
                errors.append(
                    f"line {idx} ({programm_id}): BMWK record with BMWE info url '{info_url}'"
                )
            if "bmwe.de" in quelle_url:
                errors.append(
                    f"line {idx} ({programm_id}): BMWK record with BMWE docs url '{quelle_url}'"
                )

    print(f"Checked rows: {len(rows)}")
    print(f"Unique programm_id: {len(set(ids))}")
    print(f"Status counts: {dict(Counter(r['status'].strip() for r in rows))}")
    print(f"Kategorie counts: {dict(Counter(r['kategorie'].strip() for r in rows))}")

    if errors:
        print("\nValidation errors:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Validation OK")
    return 0


def main() -> int:
    arg = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/foerderprogramme.csv")
    return validate(arg)


if __name__ == "__main__":
    raise SystemExit(main())
