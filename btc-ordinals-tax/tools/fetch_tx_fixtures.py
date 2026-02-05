from __future__ import annotations

import argparse
import json
import os
import time
from typing import List

import requests


TXIDS: List[str] = [
    "9534a20107cd72b2c13efa99349a2b397d346a813fce2a0018301523b50930fa",
    "b501d02a542be006b5e58dfe90eb56b8c5b73a6158c4f122a62a8766af330f1f",
    "5c04f6aa929edf68cf035b2eedad77f907ce01a3a45d80a0adf6ca2f6db36565",
    "8002765ad3bb096ea5b76ed13f40d4b25a065b1e465fd6d17513f11db3850d3a",
    "fa2f1397c4b836ff42d489f0fa00f7e772f81c043f48abbc46507003b801050c",
]


def fetch_tx(txid: str, base_url: str, timeout: int = 20, retries: int = 3) -> dict:
    url = f"{base_url}/tx/{txid}"
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * attempt)
    if last_error is not None:
        raise last_error
    raise RuntimeError("Unknown error fetching transaction")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Esplora tx fixtures")
    parser.add_argument("--force", action="store_true", help="overwrite existing fixtures")
    args = parser.parse_args()

    base_url = os.environ.get("ESPLORA_BASE_URL", "https://mempool.space/api")
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")
    fixtures_dir = os.path.abspath(fixtures_dir)
    os.makedirs(fixtures_dir, exist_ok=True)

    for txid in TXIDS:
        path = os.path.join(fixtures_dir, f"{txid}.json")
        if os.path.exists(path) and not args.force:
            print(f"skip {txid} (exists)")
            continue
        print(f"fetch {txid}")
        data = fetch_tx(txid, base_url=base_url)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
