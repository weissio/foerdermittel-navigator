from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class EconomicEventType(str, Enum):
    FEE = "fee"
    OP_RETURN = "op_return"
    INSCRIPTION = "inscription"
    NFT_MINT = "nft_mint"
    NFT_TRANSFER = "nft_transfer"
    NFT_LIST = "nft_list"
    NFT_DELIST = "nft_delist"
    NFT_OFFER = "nft_offer"
    TOKEN_DEPLOY = "token_deploy"
    TOKEN_MINT = "token_mint"
    TOKEN_TRANSFER = "token_transfer"
    TOKEN_LIST = "token_list"
    TOKEN_DELIST = "token_delist"
    TOKEN_OFFER = "token_offer"
    TOKEN_EVENT = "token_event"


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
    protocol: Optional[str] = None
    op: Optional[str] = None
    ticker: Optional[str] = None
    token_amount: Optional[str] = None
    inscription_id: Optional[str] = None
    inscription_number: Optional[str] = None
    content_type: Optional[str] = None
