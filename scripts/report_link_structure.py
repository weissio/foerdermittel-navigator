#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / 'data' / 'foerderprogramme.csv'
OUT_PATH = ROOT / 'docs' / 'link_structure_snapshot.md'


def _norm_base(url: str) -> tuple[str, str, str]:
    p = urlsplit(url)
    return (p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/'))


def main() -> int:
    rows = list(csv.DictReader(CSV_PATH.open(encoding='utf-8', newline='')))

    missing_info = []
    missing_docs = []
    identical = []
    same_base_with_param = []
    same_base_no_param = []
    host_counts = Counter()

    for r in rows:
        pid = (r.get('programm_id') or '').strip()
        info = (r.get('richtlinie_url') or '').strip()
        docs = (r.get('quelle_url') or '').strip()

        if info:
            host_counts[urlsplit(info).netloc.lower()] += 1
        if docs:
            host_counts[urlsplit(docs).netloc.lower()] += 1

        if not info:
            missing_info.append(pid)
        if not docs:
            missing_docs.append(pid)
        if not (info and docs):
            continue

        if info == docs:
            identical.append(pid)
            continue

        if _norm_base(info) == _norm_base(docs):
            p_docs = urlsplit(docs)
            p_info = urlsplit(info)
            if p_docs.query or p_docs.fragment or p_info.query or p_info.fragment:
                same_base_with_param.append(pid)
            else:
                same_base_no_param.append(pid)

    lines = []
    lines.append('# Link Structure Snapshot')
    lines.append('')
    lines.append(f'- Datensaetze: `{len(rows)}`')
    lines.append(f'- Fehlende Informationen-Links: `{len(missing_info)}`')
    lines.append(f'- Fehlende Dokumente-Links: `{len(missing_docs)}`')
    lines.append(f'- Identische Informationen/Dokumente-Links: `{len(identical)}`')
    lines.append(f'- Gleicher Basispfad mit Query/Fragment: `{len(same_base_with_param)}`')
    lines.append(f'- Gleicher Basispfad ohne Query/Fragment: `{len(same_base_no_param)}`')
    lines.append('')
    lines.append('## Top Hosts')
    lines.append('')
    lines.append('| Host | Anzahl Links |')
    lines.append('|---|---:|')
    for host, count in host_counts.most_common(20):
        lines.append(f'| {host} | {count} |')

    lines.append('')
    lines.append('## Stichprobe: Gleicher Basispfad ohne Query/Fragment')
    lines.append('')
    lines.append('| programm_id |')
    lines.append('|---|')
    for pid in same_base_no_param[:100]:
        lines.append(f'| {pid} |')

    OUT_PATH.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Wrote {OUT_PATH.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
