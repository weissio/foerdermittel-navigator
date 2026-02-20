#!/usr/bin/env python3
"""Live HTTP health check for information/document links."""

from __future__ import annotations

import argparse
import csv
import time
import socket
import ssl
import threading
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "foerderprogramme.csv"
OUT_PATH = ROOT / "docs" / "live_link_health_snapshot.md"


@dataclass
class LinkResult:
    programm_id: str
    field: str
    url: str
    ok: bool
    status: str
    detail: str


def _is_transient(status: str, detail: str) -> bool:
    d = (detail or "").lower()
    if status.startswith("5"):
        return True
    if status == "timeout":
        return True
    if status == "url_error" and ("timed out" in d or "connection reset" in d):
        return True
    return False


def _check_url_once(url: str, timeout: float, insecure: bool) -> tuple[bool, str, str]:
    headers = {"User-Agent": "FoerdermittelNavigatorLinkCheck/1.0"}
    context = None
    if insecure:
        context = ssl._create_unverified_context()
    # Use GET directly to avoid server-side HEAD blocking/reset behavior.
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            return (200 <= int(code) < 400, str(code), "")
    except urllib.error.HTTPError as e:
        code = int(e.code)
        if 300 <= code < 400:
            return (True, str(code), "redirect")
        return (False, str(code), "http_error")
    except urllib.error.URLError as e:
        reason = str(e.reason)
        return (False, "url_error", reason)
    except socket.timeout:
        return (False, "timeout", "socket timeout")
    except ssl.SSLError as e:
        return (False, "ssl_error", str(e))
    except Exception as e:  # pragma: no cover
        return (False, "error", str(e))


def _check_url(url: str, timeout: float, insecure: bool, retries: int) -> tuple[bool, str, str]:
    ok, status, detail = _check_url_once(url, timeout, insecure)
    if ok:
        return ok, status, detail
    # Retry only transient transport failures.
    attempts_left = max(0, retries)
    while attempts_left > 0 and _is_transient(status, detail):
        time.sleep(0.4)
        ok, status, detail = _check_url_once(url, timeout, insecure)
        if ok:
            return ok, status, detail
        attempts_left -= 1
    return ok, status, detail


def iter_links(rows: Iterable[dict[str, str]]) -> Iterable[tuple[str, str, str]]:
    for row in rows:
        pid = (row.get("programm_id") or "").strip()
        info = (row.get("richtlinie_url") or "").strip()
        docs = (row.get("quelle_url") or "").strip()
        if info:
            yield pid, "Informationen", info
        if docs:
            yield pid, "Dokumente", docs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--limit", type=int, default=0, help="0 = alle Links pruefen")
    parser.add_argument("--insecure", action="store_true", help="SSL-Zertifikatspruefung deaktivieren")
    parser.add_argument("--retries", type=int, default=1, help="Anzahl Wiederholungen bei transienten Fehlern")
    parser.add_argument(
        "--per-host-delay",
        type=float,
        default=0.25,
        help="Mindestabstand in Sekunden zwischen Requests zum selben Host",
    )
    parser.add_argument("--max-fail-list", type=int, default=300)
    parser.add_argument("--fail-on-errors", action="store_true")
    args = parser.parse_args()

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8", newline="")))

    links = list(iter_links(rows))
    if args.limit and args.limit > 0:
        links = links[: args.limit]

    host_locks: dict[str, threading.Lock] = {}
    host_last_ts: dict[str, float] = {}
    lock_guard = threading.Lock()

    def run_one(entry: tuple[str, str, str]) -> LinkResult:
        pid, field, url = entry
        host = (urlsplit(url).hostname or "").lower()
        with lock_guard:
            if host not in host_locks:
                host_locks[host] = threading.Lock()
            host_lock = host_locks[host]
        with host_lock:
            now = time.monotonic()
            last = host_last_ts.get(host, 0.0)
            wait = args.per_host_delay - (now - last)
            if wait > 0:
                time.sleep(wait)
            ok, status, detail = _check_url(url, args.timeout, args.insecure, args.retries)
            host_last_ts[host] = time.monotonic()
        return LinkResult(
            programm_id=pid,
            field=field,
            url=url,
            ok=ok,
            status=status,
            detail=detail,
        )

    workers = max(1, args.workers)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(run_one, links))

    total = len(results)
    failures = [r for r in results if not r.ok]
    infos_fail = [r for r in failures if r.field == "Informationen"]
    docs_fail = [r for r in failures if r.field == "Dokumente"]
    hard_fail = [r for r in failures if not _is_transient(r.status, r.detail)]
    transient_fail = [r for r in failures if _is_transient(r.status, r.detail)]
    by_status = Counter(r.status for r in failures)

    lines: list[str] = []
    lines.append("# Live Link Health Snapshot")
    lines.append("")
    lines.append(f"- Gepruefte Links gesamt: `{total}`")
    lines.append(f"- Fehlgeschlagen gesamt: `{len(failures)}`")
    lines.append(f"- Davon harte Fehler (z. B. 404/DNS): `{len(hard_fail)}`")
    lines.append(f"- Davon transiente Fehler (Timeout/Reset): `{len(transient_fail)}`")
    lines.append(f"- Fehlgeschlagene Informationen-Links: `{len(infos_fail)}`")
    lines.append(f"- Fehlgeschlagene Dokumente-Links: `{len(docs_fail)}`")
    lines.append("")
    lines.append("## Fehler nach Status/Typ")
    lines.append("")
    lines.append("| Typ | Anzahl |")
    lines.append("|---|---:|")
    for key, count in by_status.most_common():
        lines.append(f"| {key} | {count} |")
    lines.append("")
    lines.append("## Fehlgeschlagene Links (Stichprobe)")
    lines.append("")
    lines.append("| programm_id | Feld | Status/Typ | URL | Detail |")
    lines.append("|---|---|---|---|---|")
    for r in failures[: args.max_fail_list]:
        detail = (r.detail or "").replace("|", "/")
        lines.append(f"| {r.programm_id} | {r.field} | {r.status} | {r.url} | {detail} |")

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"Checked links: {total}")
    print(f"Failed links: {len(failures)}")

    if args.fail_on_errors and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
