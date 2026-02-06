from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

from btc_tax.fetch_esplora import fetch_tx
from btc_tax.parse_tx import parse_tx
from btc_tax.ordinals_detect import detect_metadata
from btc_tax.normalize import normalize


def _load_fixture(txid: str) -> Dict[str, Any]:
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")
    fixtures_dir = os.path.abspath(fixtures_dir)
    path = os.path.join(fixtures_dir, f"{txid}.json")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _events_to_dict(events):
    return [
        {
            "type": event.type.value,
            "txid": event.txid,
            "when_ts": event.when_ts,
            "block_height": event.block_height,
            "amount_sats": event.amount_sats,
            "fee_sats": event.fee_sats,
            "notes": event.notes,
            "evidence": event.evidence,
            "protocol": event.protocol,
            "op": event.op,
            "ticker": event.ticker,
            "token_amount": event.token_amount,
            "inscription_id": event.inscription_id,
            "inscription_number": event.inscription_number,
            "content_type": event.content_type,
        }
        for event in events
    ]

def _format_ts(ts: int) -> str:
    if not ts:
        return ""
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _events_to_rows(
    events,
    wallet_id: str | None,
    wallet_address: str | None,
    eur_rate: Optional[float],
    csv_lang: str,
    datev: bool = False,
) -> List[Dict[str, Any]]:
    headers = _csv_headers(csv_lang, datev=datev)
    rows = []
    for event in events:
        amount_eur = ""
        fee_eur = ""
        if eur_rate is not None:
            if event.amount_sats is not None:
                amount_eur = (event.amount_sats / 100_000_000) * eur_rate
            if event.fee_sats is not None:
                fee_eur = (event.fee_sats / 100_000_000) * eur_rate

        if datev:
            rows.append(
                _datev_row(
                    event,
                    wallet_id=wallet_id,
                    wallet_address=wallet_address,
                    amount_eur=amount_eur,
                    fee_eur=fee_eur,
                )
            )
            continue

        rows.append(
            {
                headers["date_utc"]: _format_ts(event.when_ts),
                headers["type"]: event.type.value,
                headers["txid"]: event.txid,
                headers["wallet_id"]: wallet_id or "",
                headers["wallet_address"]: wallet_address or "",
                headers["protocol"]: event.protocol or "",
                headers["op"]: event.op or "",
                headers["ticker"]: event.ticker or "",
                headers["token_amount"]: event.token_amount or "",
                headers["inscription_id"]: event.inscription_id or "",
                headers["inscription_number"]: event.inscription_number or "",
                headers["content_type"]: event.content_type or "",
                headers["amount_sats"]: event.amount_sats if event.amount_sats is not None else "",
                headers["amount_eur"]: amount_eur,
                headers["fee_sats"]: event.fee_sats if event.fee_sats is not None else "",
                headers["fee_eur"]: fee_eur,
                headers["notes"]: event.notes or "",
                headers["evidence"]: json.dumps(event.evidence, sort_keys=True),
            }
        )
    return rows


def _csv_headers(lang: str, datev: bool = False) -> Dict[str, str]:
    if datev:
        return {
            "Buchungsdatum": "Buchungsdatum",
            "Belegdatum": "Belegdatum",
            "Buchungstext": "Buchungstext",
            "Betrag": "Betrag",
            "Waehrung": "Waehrung",
            "SollKonto": "SollKonto",
            "HabenKonto": "HabenKonto",
            "Belegfeld1": "Belegfeld1",
            "Belegfeld2": "Belegfeld2",
            "Kost1": "Kost1",
        }
    if lang == "de":
        return {
            "date_utc": "Datum_UTC",
            "type": "Ereignisart",
            "txid": "TxID",
            "wallet_id": "Wallet_ID",
            "wallet_address": "Wallet_Adresse",
            "protocol": "Protokoll",
            "op": "Operation",
            "ticker": "Ticker",
            "token_amount": "Token_Menge",
            "inscription_id": "Inscription_ID",
            "inscription_number": "Inscription_Nummer",
            "content_type": "Content_Typ",
            "amount_sats": "Betrag_sats",
            "amount_eur": "Betrag_EUR",
            "fee_sats": "Gebuehr_sats",
            "fee_eur": "Gebuehr_EUR",
            "notes": "Notizen",
            "evidence": "Nachweise",
        }
    return {
        "date_utc": "date_utc",
        "type": "type",
        "txid": "txid",
        "wallet_id": "wallet_id",
        "wallet_address": "wallet_address",
        "protocol": "protocol",
        "op": "op",
        "ticker": "ticker",
        "token_amount": "token_amount",
        "inscription_id": "inscription_id",
        "inscription_number": "inscription_number",
        "content_type": "content_type",
        "amount_sats": "amount_sats",
        "amount_eur": "amount_eur",
        "fee_sats": "fee_sats",
        "fee_eur": "fee_eur",
        "notes": "notes",
        "evidence": "evidence",
    }


def _datev_row(
    event,
    wallet_id: str | None,
    wallet_address: str | None,
    amount_eur: Any,
    fee_eur: Any,
) -> Dict[str, Any]:
    date_str = _format_ts(event.when_ts)
    amount_value = ""
    if fee_eur not in ("", None):
        amount_value = fee_eur
    elif amount_eur not in ("", None):
        amount_value = amount_eur

    return {
        "Buchungsdatum": date_str[:10] if date_str else "",
        "Belegdatum": date_str[:10] if date_str else "",
        "Buchungstext": event.type.value,
        "Betrag": _format_decimal_comma(amount_value),
        "Waehrung": "EUR",
        "SollKonto": "",
        "HabenKonto": "",
        "Belegfeld1": event.txid,
        "Belegfeld2": wallet_id or wallet_address or "",
        "Kost1": "",
    }


def _format_decimal_comma(value: Any) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.2f}".replace(".", ",")


def _year_bucket(ts: int) -> Optional[int]:
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).year


def _summary(event_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"by_year": {}, "totals": {}}
    totals = {
        "event_count": 0,
        "fee_sats": 0,
        "fee_eur": 0.0,
    }

    for record in event_records:
        event = record["event"]
        fee_eur = record.get("fee_eur")

        totals["event_count"] += 1
        if event.fee_sats:
            totals["fee_sats"] += event.fee_sats
            if fee_eur is not None:
                totals["fee_eur"] += fee_eur

        year = _year_bucket(event.when_ts)
        if year is None:
            year_key = "unknown"
        else:
            year_key = str(year)
        if year_key not in summary["by_year"]:
            summary["by_year"][year_key] = {
                "event_count": 0,
                "fee_sats": 0,
                "fee_eur": 0.0,
                "types": {},
            }
        bucket = summary["by_year"][year_key]
        bucket["event_count"] += 1
        if event.fee_sats:
            bucket["fee_sats"] += event.fee_sats
            if fee_eur is not None:
                bucket["fee_eur"] += fee_eur
        bucket["types"].setdefault(event.type.value, 0)
        bucket["types"][event.type.value] += 1

    summary["totals"] = totals
    return summary


def _collect_txids(args) -> List[str]:
    txids: List[str] = []
    if args.txid:
        txids.extend(args.txid)
    if args.txids:
        for part in args.txids.split(","):
            part = part.strip()
            if part:
                txids.append(part)
    if args.txids_file:
        with open(args.txids_file, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                txids.append(line)
    seen = set()
    unique = []
    for txid in txids:
        if txid not in seen:
            unique.append(txid)
            seen.add(txid)
    return unique


def _date_from_ts(ts: int) -> Optional[str]:
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def _coingecko_rate(date_str: str, api_key: Optional[str], pro: bool, base_url: Optional[str]) -> Tuple[float, str]:
    if pro:
        base = base_url or "https://pro-api.coingecko.com/api/v3"
        headers = {"x-cg-pro-api-key": api_key} if api_key else {}
    else:
        base = base_url or "https://api.coingecko.com/api/v3"
        headers = {"x-cg-demo-api-key": api_key} if api_key else {}

    # CoinGecko history endpoint supports date formats; try DD-MM-YYYY first.
    date_ddmm = datetime.fromisoformat(date_str).strftime("%d-%m-%Y")
    date_yyyymm = date_str

    for date_query in (date_ddmm, date_yyyymm):
        url = f"{base}/coins/bitcoin/history"
        resp = requests.get(url, params={"date": date_query, "localization": "false"}, headers=headers, timeout=20)
        if resp.status_code >= 400:
            continue
        data = resp.json()
        price = data.get("market_data", {}).get("current_price", {}).get("eur")
        if price is not None:
            return float(price), date_query
    raise RuntimeError("CoinGecko price not available for the requested date")


def _ecb_rate(date_str: str, currency: str) -> Tuple[float, str]:
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    namespaces = {"e": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}

    target_date = datetime.fromisoformat(date_str).date()
    best_date = None
    best_rate = None

    for cube in root.findall(".//e:Cube[@time]", namespaces):
        time_str = cube.attrib.get("time")
        if not time_str:
            continue
        day = datetime.fromisoformat(time_str).date()
        if day > target_date:
            continue
        rate = None
        for rate_node in cube.findall("e:Cube", namespaces):
            if rate_node.attrib.get("currency") == currency:
                rate = rate_node.attrib.get("rate")
                break
        if rate is None:
            continue
        if best_date is None or day > best_date:
            best_date = day
            best_rate = rate

    if best_rate is None or best_date is None:
        raise RuntimeError("ECB rate not available for the requested date")

    return float(best_rate), best_date.isoformat()


def _event_records(events, eur_rate: Optional[float]) -> List[Dict[str, Any]]:
    records = []
    for event in events:
        amount_eur = None
        fee_eur = None
        if eur_rate is not None:
            if event.amount_sats is not None:
                amount_eur = (event.amount_sats / 100_000_000) * eur_rate
            if event.fee_sats is not None:
                fee_eur = (event.fee_sats / 100_000_000) * eur_rate
        records.append(
            {
                "event": event,
                "amount_eur": amount_eur,
                "fee_eur": fee_eur,
                "eur_rate": eur_rate,
            }
        )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a Bitcoin tx via Esplora JSON")
    parser.add_argument("txid", nargs="*", help="transaction id(s)")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("ESPLORA_BASE_URL", "https://mempool.space/api"),
        help="Esplora base URL",
    )
    parser.add_argument(
        "--use-fixture",
        action="store_true",
        help="load tx JSON from tests/fixtures instead of network",
    )
    parser.add_argument(
        "--txids",
        default=None,
        help="comma-separated list of txids",
    )
    parser.add_argument(
        "--txids-file",
        default=None,
        help="file with one txid per line",
    )
    parser.add_argument(
        "--wallet-id",
        default=None,
        help="wallet identifier to include in output",
    )
    parser.add_argument(
        "--wallet-address",
        default=None,
        help="wallet address to include in output",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "datev"],
        default="json",
        help="output format",
    )
    parser.add_argument(
        "--csv-lang",
        choices=["en", "de"],
        default="en",
        help="CSV header language",
    )
    parser.add_argument(
        "--eur-rate",
        type=float,
        default=None,
        help="EUR per BTC rate for valuation",
    )
    parser.add_argument(
        "--rate-source",
        choices=["coingecko", "ecb"],
        default=None,
        help="auto-fetch EUR rate from source",
    )
    parser.add_argument(
        "--rate-date",
        default=None,
        help="override rate date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--rate-currency",
        default="USD",
        help="ECB currency code (for rate-source=ecb)",
    )
    parser.add_argument(
        "--coingecko-api-key",
        default=os.environ.get("COINGECKO_API_KEY"),
        help="CoinGecko API key (demo/pro)",
    )
    parser.add_argument(
        "--coingecko-pro",
        action="store_true",
        help="use CoinGecko pro API base and header",
    )
    parser.add_argument(
        "--coingecko-base-url",
        default=None,
        help="override CoinGecko API base URL",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="include yearly summary in JSON output",
    )
    args = parser.parse_args()

    txids = _collect_txids(args)
    if not txids:
        parser.error("No txids provided. Pass positional txid(s), --txids, or --txids-file.")

    results = []
    all_event_records: List[Dict[str, Any]] = []

    for txid in txids:
        if args.use_fixture:
            decoded_tx = _load_fixture(txid)
        else:
            decoded_tx = fetch_tx(txid, base_url=args.base_url)

        parsed = parse_tx(decoded_tx)
        detection = detect_metadata(decoded_tx, parsed)
        events = normalize(parsed, detection)

        eur_rate = args.eur_rate
        eur_rate_date_used = None
        if eur_rate is None and args.rate_source:
            rate_date = args.rate_date or _date_from_ts(parsed.get("when_ts", 0) or 0)
            if rate_date is None:
                raise RuntimeError("Rate date is required when tx has no timestamp. Use --rate-date.")
            if args.rate_source == "coingecko":
                eur_rate, eur_rate_date_used = _coingecko_rate(
                    rate_date,
                    api_key=args.coingecko_api_key,
                    pro=args.coingecko_pro,
                    base_url=args.coingecko_base_url,
                )
            else:
                if args.rate_currency.upper() == "BTC":
                    raise RuntimeError("ECB does not publish BTC rates. Use rate-source=coingecko for BTC/EUR.")
                eur_rate, eur_rate_date_used = _ecb_rate(rate_date, args.rate_currency.upper())

        event_records = _event_records(events, eur_rate)
        all_event_records.extend(event_records)

        if args.format in ("csv", "datev"):
            continue

        results.append(
            {
                "txid": parsed.get("txid"),
                "when_ts": parsed.get("when_ts"),
                "when_utc": _format_ts(parsed.get("when_ts", 0) or 0),
                "block_height": parsed.get("block_height"),
                "fee_sats": parsed.get("fee_sats"),
                "detection": detection,
                "wallet_id": args.wallet_id,
                "wallet_address": args.wallet_address,
                "eur_rate": eur_rate,
                "eur_rate_date_used": eur_rate_date_used,
                "rate_source": args.rate_source,
                "events": _events_to_dict(events),
            }
        )

    if args.format in ("csv", "datev"):
        rows: List[Dict[str, Any]] = []
        for record in all_event_records:
            rows.extend(
                _events_to_rows(
                    [record["event"]],
                    args.wallet_id,
                    args.wallet_address,
                    record["eur_rate"],
                    args.csv_lang,
                    datev=(args.format == "datev"),
                )
            )
        if rows:
            writer = csv.DictWriter(
                sys.stdout,
                fieldnames=list(rows[0].keys()),
                delimiter=";" if args.format == "datev" else ",",
            )
            writer.writeheader()
            writer.writerows(rows)
        return 0

    output = {
        "results": results,
    }
    if args.summary:
        output["summary"] = _summary(all_event_records)

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
