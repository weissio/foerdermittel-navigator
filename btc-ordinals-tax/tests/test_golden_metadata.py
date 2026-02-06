import json
import os

from btc_tax.ordinals_detect import detect_metadata
from btc_tax.parse_tx import parse_tx
from btc_tax.normalize import normalize
from btc_tax.types import EconomicEventType


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
EXPECTED_DIR = os.path.join(os.path.dirname(__file__), "expected")


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _event_types(events):
    return {event.type.value for event in events}


def _fee_event(events):
    for event in events:
        if event.type == EconomicEventType.FEE:
            return event
    return None


def test_golden_metadata():
    overrides_path = os.path.join(FIXTURES_DIR, "tx_overrides.json")
    overrides = None
    if os.path.exists(overrides_path):
        overrides = _load_json(overrides_path)

    for filename in os.listdir(FIXTURES_DIR):
        if not filename.endswith(".json"):
            continue
        txid = filename.replace(".json", "")
        if txid == "tx_overrides":
            continue
        fixture_path = os.path.join(FIXTURES_DIR, filename)
        expected_path = os.path.join(EXPECTED_DIR, f"{txid}.json")
        expected = _load_json(expected_path)

        decoded_tx = _load_json(fixture_path)
        parsed = parse_tx(decoded_tx)
        detection = detect_metadata(decoded_tx, parsed, overrides=overrides)
        events = normalize(parsed, detection)

        event_types = _event_types(events)

        for event_type in expected.get("must_have_types", []):
            assert event_type in event_types, f"{txid} missing {event_type}"

        for event_type in expected.get("must_not_have_types", []):
            assert event_type not in event_types, f"{txid} has unexpected {event_type}"

        if expected.get("fee_required_if_computable"):
            fee_sats = parsed.get("fee_sats")
            if fee_sats is not None and fee_sats > 0:
                fee_event = _fee_event(events)
                assert fee_event is not None, f"{txid} missing FEE event"
                assert fee_event.fee_sats == fee_sats, f"{txid} fee mismatch"
