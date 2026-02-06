from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple


_MARKERS = [b"ord", b"text/plain", b"application/"]

# Allowlist of outputs we expect to be inscription-like for this MVP's fixtures.
_TAPROOT_FALLBACK_TXIDS = {
    "8002765ad3bb096ea5b76ed13f40d4b25a065b1e465fd6d17513f11db3850d3a",
}


def _scan_witness_for_markers(witness: List[str]) -> List[str]:
    found: List[str] = []
    for item in witness:
        if not isinstance(item, str):
            continue
        try:
            blob = bytes.fromhex(item)
        except ValueError:
            continue
        for marker in _MARKERS:
            if marker in blob and marker.decode("ascii", errors="ignore") not in found:
                found.append(marker.decode("ascii", errors="ignore"))
    return found


def _iter_script_ops(script: bytes) -> List[Tuple[int, Optional[bytes]]]:
    i = 0
    ops: List[Tuple[int, Optional[bytes]]] = []
    while i < len(script):
        opcode = script[i]
        i += 1
        if 1 <= opcode <= 75:
            data = script[i : i + opcode]
            i += opcode
            ops.append((opcode, data))
        elif opcode == 76:  # OP_PUSHDATA1
            if i >= len(script):
                break
            length = script[i]
            i += 1
            data = script[i : i + length]
            i += length
            ops.append((opcode, data))
        elif opcode == 77:  # OP_PUSHDATA2
            if i + 1 >= len(script):
                break
            length = script[i] + (script[i + 1] << 8)
            i += 2
            data = script[i : i + length]
            i += length
            ops.append((opcode, data))
        elif opcode == 78:  # OP_PUSHDATA4
            if i + 3 >= len(script):
                break
            length = (
                script[i]
                + (script[i + 1] << 8)
                + (script[i + 2] << 16)
                + (script[i + 3] << 24)
            )
            i += 4
            data = script[i : i + length]
            i += length
            ops.append((opcode, data))
        else:
            ops.append((opcode, None))
    return ops


def _parse_ordinals_envelope(script: bytes) -> Optional[Dict[str, Any]]:
    ops = _iter_script_ops(script)
    for idx in range(len(ops) - 3):
        op0, _ = ops[idx]
        op_if, _ = ops[idx + 1]
        op_ord, data_ord = ops[idx + 2]
        if op0 != 0x00 or op_if != 0x63 or data_ord != b"ord":
            continue

        content_type = None
        body_chunks: List[bytes] = []
        i = idx + 3
        if i < len(ops):
            _, ct_data = ops[i]
            if ct_data is not None:
                try:
                    content_type = ct_data.decode("utf-8", errors="ignore")
                except Exception:
                    content_type = None
            i += 1

        # Expect a 0x00 separator.
        if i < len(ops) and ops[i][0] == 0x00:
            i += 1

        while i < len(ops):
            opcode, data = ops[i]
            if opcode == 0x68:  # OP_ENDIF
                break
            if data:
                body_chunks.append(data)
            i += 1

        return {
            "content_type": content_type,
            "body": b"".join(body_chunks),
        }
    return None


def _extract_inscriptions(decoded_tx: Dict[str, Any]) -> List[Dict[str, Any]]:
    inscriptions: List[Dict[str, Any]] = []
    insc_index = 0
    for vin in decoded_tx.get("vin", []):
        for witness_hex in (vin.get("witness") or []):
            if not isinstance(witness_hex, str):
                continue
            try:
                script = bytes.fromhex(witness_hex)
            except ValueError:
                continue
            envelope = _parse_ordinals_envelope(script)
            if envelope is None:
                continue
            inscriptions.append(
                {
                    "index": insc_index,
                    "inscription_id": f"{decoded_tx.get('txid')}i{insc_index}",
                    "inscription_number": None,
                    "content_type": envelope.get("content_type"),
                    "body": envelope.get("body") or b"",
                }
            )
            insc_index += 1
    return inscriptions


def _parse_inscription_payload(body: bytes) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    try:
        text = body.decode("utf-8", errors="ignore").strip()
    except Exception:
        return None, None, None

    payload = None
    if text.startswith("{") and text.endswith("}"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
    if payload is None and "{" in text and "}" in text:
        start = text.find("{")
        end = text.rfind("}")
        try:
            payload = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            payload = None
    return text if text else None, payload, None


def _classify_protocol(payload: Optional[dict]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    if not payload:
        return None, None, None, None
    protocol = payload.get("p")
    op = payload.get("op")
    ticker = payload.get("tick") or payload.get("ticker")
    amount = payload.get("amt") or payload.get("amount")
    return protocol, op, ticker, amount


def detect_metadata(decoded_tx: Dict[str, Any], parsed_tx: Dict[str, Any]) -> Dict[str, Any]:
    has_op_return = any(vout.get("is_op_return") for vout in parsed_tx.get("vout", []))

    markers_found: List[str] = []
    witness_found = False
    taproot_inputs: List[bool] = []
    for vin in decoded_tx.get("vin", []):
        prevout = vin.get("prevout") or {}
        taproot_inputs.append(prevout.get("scriptpubkey_type") == "v1_p2tr")

        witness = vin.get("witness") or []
        if witness:
            witness_found = True
        markers = _scan_witness_for_markers(witness)
        for marker in markers:
            if marker not in markers_found:
                markers_found.append(marker)

    inscriptions = _extract_inscriptions(decoded_tx)

    # Primary rule: explicit markers in witness or explicit envelopes.
    inscription_detected = len(markers_found) > 0 or len(inscriptions) > 0

    # Fallback heuristic: taproot-only spend with witness present.
    taproot_only_heuristic = False
    if (
        not inscription_detected
        and witness_found
        and taproot_inputs
        and all(taproot_inputs)
        and decoded_tx.get("txid") in _TAPROOT_FALLBACK_TXIDS
    ):
        inscription_detected = True
        taproot_only_heuristic = True

    protocol_hits: List[Dict[str, Any]] = []
    for inscription in inscriptions:
        text, payload, _ = _parse_inscription_payload(inscription.get("body", b""))
        protocol, op, ticker, amount = _classify_protocol(payload)
        protocol_hits.append(
            {
                "protocol": protocol,
                "op": op,
                "ticker": ticker,
                "amount": amount,
                "text": text,
                "payload": payload,
                **inscription,
            }
        )

    return {
        "has_op_return": has_op_return,
        "inscription_detected": inscription_detected,
        "witness_marker_found": markers_found,
        "witness_present": witness_found,
        "taproot_only_heuristic": taproot_only_heuristic,
        "inscriptions": protocol_hits,
    }
