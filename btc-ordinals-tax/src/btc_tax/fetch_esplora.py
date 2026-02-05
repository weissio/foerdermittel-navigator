from __future__ import annotations

from typing import Any, Dict

import requests


DEFAULT_BASE_URL = "https://mempool.space/api"


def fetch_tx(txid: str, base_url: str = DEFAULT_BASE_URL, timeout: int = 20) -> Dict[str, Any]:
    url = f"{base_url}/tx/{txid}"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()
