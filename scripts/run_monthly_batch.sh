#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SOURCE_LABEL="${1:-manueller_batch}"
CHANGED_COUNT="${2:-0}"
COMMENT="${3:-Monatslauf mit QA}"

today="$(date +%F)"

scripts/run_qa.sh

checked_count="$(
python3 - <<'PY'
import csv
rows=list(csv.DictReader(open("data/foerderprogramme.csv", encoding="utf-8")))
print(len(rows))
PY
)"

printf '%s,%s,%s,%s,"%s"\n' \
  "$today" "$SOURCE_LABEL" "$checked_count" "$CHANGED_COUNT" "$COMMENT" \
  >> data/update_log.csv

echo "Monthly batch logged:"
tail -n 1 data/update_log.csv
