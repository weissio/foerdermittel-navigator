#!/usr/bin/env python3
"""Gate: changed records must have healthy links."""

from __future__ import annotations

import argparse
import csv
import io
import socket
import ssl
import subprocess
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "foerderprogramme.csv"
OUT_PATH = ROOT / "docs" / "changed_link_health_snapshot.md"


@dataclass
class Result:
    programm_id: str
    field: str
    url: str
    ok: bool
    status: str
    detail: str


def _load_csv_from_text(text: str) -> dict[str, dict[str, str]]:
    rows = list(csv.DictReader(io.StringIO(text)))
    return {r["programm_id"]: r for r in rows}


def _load_current_csv() -> dict[str, dict[str, str]]:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))
    return {r["programm_id"]: r for r in rows}


def _load_base_csv(base_ref: str) -> dict[str, dict[str, str]]:
    proc = subprocess.run(
        ["git", "show", f"{base_ref}:data/foerderprogramme.csv"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return _load_csv_from_text(proc.stdout)


def _changed_ids(base: dict[str, dict[str, str]], cur: dict[str, dict[str, str]]) -> list[str]:
    ids = sorted(set(base) | set(cur))
    changed = []
    for pid in ids:
        if pid not in base or pid not in cur:
            changed.append(pid)
            continue
        if base[pid] != cur[pid]:
            changed.append(pid)
    return changed


def _check_url(url: str, timeout: float, insecure: bool) -> tuple[bool, str, str]:
    headers = {"User-Agent": "FoerdermittelNavigatorChangedGate/1.0"}
    context = ssl._create_unverified_context() if insecure else None
    req = urllib.request.Request(url, method="HEAD", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            code = int(getattr(resp, "status", None) or resp.getcode())
            return (200 <= code < 400, str(code), "")
    except Exception:
        req = urllib.request.Request(url, method="GET", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
                code = int(getattr(resp, "status", None) or resp.getcode())
                return (200 <= code < 400, str(code), "")
        except urllib.error.HTTPError as e:
            code = int(e.code)
            if 300 <= code < 400:
                return (True, str(code), "redirect")
            return (False, str(code), "http_error")
        except urllib.error.URLError as e:
            return (False, "url_error", str(e.reason))
        except socket.timeout:
            return (False, "timeout", "socket timeout")
        except ssl.SSLError as e:
            return (False, "ssl_error", str(e))
        except Exception as e:  # pragma: no cover
            return (False, "error", str(e))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--insecure", action="store_true")
    args = parser.parse_args()

    base = _load_base_csv(args.base_ref)
    cur = _load_current_csv()
    ids = _changed_ids(base, cur)

    links: list[tuple[str, str, str]] = []
    for pid in ids:
        row = cur.get(pid)
        if not row:
            continue
        info = (row.get("richtlinie_url") or "").strip()
        docs = (row.get("quelle_url") or "").strip()
        if info:
            links.append((pid, "Informationen", info))
        if docs:
            links.append((pid, "Dokumente", docs))

    def run_one(item: tuple[str, str, str]) -> Result:
        pid, field, url = item
        ok, status, detail = _check_url(url, args.timeout, args.insecure)
        return Result(pid, field, url, ok, status, detail)

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        results = list(pool.map(run_one, links))

    failed = [r for r in results if not r.ok]

    lines = []
    lines.append("# Changed Link Health Snapshot")
    lines.append("")
    lines.append(f"- Base Ref: `{args.base_ref}`")
    lines.append(f"- Geaenderte Datensaetze: `{len(ids)}`")
    lines.append(f"- Gepruefte Links (geaenderte Datensaetze): `{len(results)}`")
    lines.append(f"- Fehlgeschlagene Links (geaenderte Datensaetze): `{len(failed)}`")
    lines.append("")
    lines.append("| programm_id | Feld | Status/Typ | URL | Detail |")
    lines.append("|---|---|---|---|---|")
    for r in failed:
        detail = r.detail.replace("|", "/")
        lines.append(f"| {r.programm_id} | {r.field} | {r.status} | {r.url} | {detail} |")
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"Changed IDs: {len(ids)}")
    print(f"Failed changed links: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
