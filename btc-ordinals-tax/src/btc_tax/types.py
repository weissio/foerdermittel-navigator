from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class EconomicEventType(str, Enum):
    FEE = "fee"
    OP_RETURN = "op_return"
    INSCRIPTION = "inscription"


@dataclass(frozen=True)
class EconomicEvent:
    type: EconomicEventType
    txid: str
    when_ts: int
    block_height: Optional[int]
    amount_sats: Optional[int]
    fee_sats: Optional[int]
    notes: str
    evidence: Dict[str, Any]
