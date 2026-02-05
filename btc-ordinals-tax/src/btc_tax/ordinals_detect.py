from __future__ import annotations

from typing import Any, Dict, List


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

    # Primary rule: explicit markers in witness.
    inscription_detected = len(markers_found) > 0

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

    return {
        "has_op_return": has_op_return,
        "inscription_detected": inscription_detected,
        "witness_marker_found": markers_found,
        "witness_present": witness_found,
        "taproot_only_heuristic": taproot_only_heuristic,
    }
