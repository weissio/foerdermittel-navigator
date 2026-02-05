from __future__ import annotations

from typing import Any, Dict, List

from .types import EconomicEvent, EconomicEventType


def _build_event(
    event_type: EconomicEventType,
    txid: str,
    when_ts: int,
    block_height: int | None,
    amount_sats: int | None,
    fee_sats: int | None,
    notes: str,
    evidence: Dict[str, Any],
) -> EconomicEvent:
    return EconomicEvent(
        type=event_type,
        txid=txid,
        when_ts=when_ts,
        block_height=block_height,
        amount_sats=amount_sats,
        fee_sats=fee_sats,
        notes=notes,
        evidence=evidence,
    )


def normalize(parsed_tx: Dict[str, Any], detection: Dict[str, Any]) -> List[EconomicEvent]:
    events: List[EconomicEvent] = []
    txid = parsed_tx.get("txid", "")
    when_ts = parsed_tx.get("when_ts", 0) or 0
    block_height = parsed_tx.get("block_height")

    fee_sats = parsed_tx.get("fee_sats")
    if fee_sats is not None and fee_sats > 0:
        events.append(
            _build_event(
                EconomicEventType.FEE,
                txid,
                when_ts,
                block_height,
                amount_sats=None,
                fee_sats=int(fee_sats),
                notes="miner fee",
                evidence={"fee_computed": True, **detection},
            )
        )

    if detection.get("has_op_return"):
        events.append(
            _build_event(
                EconomicEventType.OP_RETURN,
                txid,
                when_ts,
                block_height,
                amount_sats=None,
                fee_sats=None,
                notes="op_return metadata",
                evidence={**detection},
            )
        )

    if detection.get("inscription_detected"):
        events.append(
            _build_event(
                EconomicEventType.INSCRIPTION,
                txid,
                when_ts,
                block_height,
                amount_sats=None,
                fee_sats=None,
                notes="inscription metadata",
                evidence={**detection},
            )
        )

    return events
