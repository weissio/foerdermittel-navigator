#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/7] validate_foerderprogramme.py"
python3 scripts/validate_foerderprogramme.py

echo
echo "[2/7] check_deadlines.py"
python3 scripts/check_deadlines.py

echo
echo "[3/7] report_coverage.py"
python3 scripts/report_coverage.py

echo
echo "[4/7] report_deadlines.py"
python3 scripts/report_deadlines.py

echo
echo "[5/7] report_open_calls.py"
python3 scripts/report_open_calls.py

echo
echo "[6/7] report_gaps.py"
python3 scripts/report_gaps.py

echo
echo "[7/7] report_status.py"
python3 scripts/report_status.py

echo
echo "QA run completed."
