from __future__ import annotations

from typing import Any, Dict, List, Optional


def _extract_when_ts(decoded_tx: Dict[str, Any]) -> int:
    status = decoded_tx.get("status") or {}
    if "block_time" in status and status["block_time"] is not None:
        return int(status["block_time"])
    if "time" in decoded_tx and decoded_tx["time"] is not None:
        return int(decoded_tx["time"])
    return 0


def parse_tx(decoded_tx: Dict[str, Any]) -> Dict[str, Any]:
    txid = decoded_tx.get("txid", "")
    when_ts = _extract_when_ts(decoded_tx)
    status = decoded_tx.get("status") or {}
    block_height = status.get("block_height")

    vins: List[Dict[str, Any]] = []
    for vin in decoded_tx.get("vin", []):
        prevout = vin.get("prevout") or {}
        prevout_value = prevout.get("value")
        vins.append(
            {
                "prevout_value": prevout_value if prevout_value is None else int(prevout_value),
            }
        )

    vouts: List[Dict[str, Any]] = []
    total_vout = 0
    for vout in decoded_tx.get("vout", []):
        value = int(vout.get("value", 0))
        total_vout += value
        scriptpubkey_type = vout.get("scriptpubkey_type")
        is_op_return = scriptpubkey_type == "op_return"
        vouts.append(
            {
                "n": int(vout.get("n", 0)),
                "value": value,
                "scriptpubkey_type": scriptpubkey_type,
                "is_op_return": is_op_return,
            }
        )

    fee_sats: Optional[int] = None
    if vins:
        prevout_values = [v["prevout_value"] for v in vins]
        if all(value is not None for value in prevout_values):
            total_vin = sum(int(value) for value in prevout_values if value is not None)
            fee_sats = total_vin - total_vout

    return {
        "txid": txid,
        "when_ts": when_ts,
        "block_height": block_height,
        "vin": vins,
        "vout": vouts,
        "fee_sats": fee_sats,
    }
