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
    protocol: str | None = None,
    op: str | None = None,
    ticker: str | None = None,
    token_amount: str | None = None,
    inscription_id: str | None = None,
    inscription_number: str | None = None,
    content_type: str | None = None,
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
        protocol=protocol,
        op=op,
        ticker=ticker,
        token_amount=token_amount,
        inscription_id=inscription_id,
        inscription_number=inscription_number,
        content_type=content_type,
    )


def _classify_event_type(protocol: str | None, op: str | None, content_type: str | None) -> EconomicEventType:
    if protocol in {"brc-20", "cbrc-20", "pipe", "tap", "runes"}:
        if op in {"deploy"}:
            return EconomicEventType.TOKEN_DEPLOY
        if op in {"mint"}:
            return EconomicEventType.TOKEN_MINT
        if op in {"transfer", "send", "token-transfer", "token-send"}:
            return EconomicEventType.TOKEN_TRANSFER
        if op in {"list"}:
            return EconomicEventType.TOKEN_LIST
        if op in {"delist"}:
            return EconomicEventType.TOKEN_DELIST
        if op in {"offer"}:
            return EconomicEventType.TOKEN_OFFER
        return EconomicEventType.TOKEN_EVENT

    # Default to NFT-ish for generic inscriptions.
    if content_type:
        if op in {"list"}:
            return EconomicEventType.NFT_LIST
        if op in {"delist"}:
            return EconomicEventType.NFT_DELIST
        if op in {"offer"}:
            return EconomicEventType.NFT_OFFER
        return EconomicEventType.NFT_MINT

    return EconomicEventType.INSCRIPTION


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

    inscriptions = detection.get("inscriptions") or []
    if inscriptions:
        for inscription in inscriptions:
            event_type = _classify_event_type(
                inscription.get("protocol"),
                inscription.get("op"),
                inscription.get("content_type"),
            )
            events.append(
                _build_event(
                    event_type,
                    txid,
                    when_ts,
                    block_height,
                    amount_sats=None,
                    fee_sats=None,
                    notes="inscription metadata",
                    evidence={**detection, "inscription": inscription},
                    protocol=inscription.get("protocol"),
                    op=inscription.get("op"),
                    ticker=inscription.get("ticker"),
                    token_amount=(
                        str(inscription.get("amount")) if inscription.get("amount") is not None else None
                    ),
                    inscription_id=inscription.get("inscription_id"),
                    inscription_number=inscription.get("inscription_number"),
                    content_type=inscription.get("content_type"),
                )
            )
    elif detection.get("inscription_detected"):
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
