# Bitcoin Ordinals Tax MVP

This package fetches decoded Bitcoin transactions (Esplora-compatible JSON), parses UTXO outputs and fees, detects OP_RETURN outputs and Ordinals-style inscriptions in witness data, and normalizes metadata-only tax events for Germany (MVP).

## What it does (MVP)
- Fetches transactions from an Esplora-compatible REST endpoint.
- Parses vin/vout, computes fee when input values are available.
- Detects `op_return` outputs.
- Detects ordinals-style inscriptions by scanning witness blobs for ASCII markers.
- Normalizes to metadata-only economic events: `fee`, `op_return`, `inscription`.

## Setup
```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
```

## Fetch fixtures
```bash
python tools/fetch_tx_fixtures.py
```

You can override the default Esplora base URL:
```bash
ESPLORA_BASE_URL=https://mempool.space/api python tools/fetch_tx_fixtures.py
```

## Run tests
```bash
pytest -q
```

## Analyze a transaction
```bash
python tools/analyze_tx.py <txid>
```

Use a local fixture instead of a network call:
```bash
python tools/analyze_tx.py <txid> --use-fixture
```

Include wallet metadata and output as CSV:
```bash
python tools/analyze_tx.py <txid> --wallet-id mywallet --wallet-address bc1... --format csv
```

German CSV headers and EUR valuation:
```bash
python tools/analyze_tx.py <txid> --wallet-id mywallet --wallet-address bc1... --format csv --csv-lang de --eur-rate 42000
```

DATEV-friendly CSV export (semicolon, decimal comma):
```bash
python tools/analyze_tx.py <txid> --format datev --eur-rate 42000
```

JSON output with yearly summary:
```bash
python tools/analyze_tx.py <txid> --summary --eur-rate 42000
```

Batch analysis with multiple txids:
```bash
python tools/analyze_tx.py <txid1> <txid2> --format csv --csv-lang de
```

Batch analysis from file (one txid per line):
```bash
python tools/analyze_tx.py --txids-file txids.txt --format csv
```

Auto-fetch BTC/EUR rate from CoinGecko for each tx date:
```bash
python tools/analyze_tx.py <txid> --rate-source coingecko --summary
```

ECB rates are only for fiat currencies (not BTC):
```bash
python tools/analyze_tx.py <txid> --rate-source ecb --rate-currency USD --summary
```

## Notes
- OP_RETURN and inscription detections are metadata-only and do not create transfer events.
- Miner fees are emitted as their own `fee` event when computable.
- Inscription detection uses explicit witness markers; for taproot-only inputs with witness present, a fallback heuristic marks an inscription if no marker is found (to handle marker-less fixtures in this MVP).
