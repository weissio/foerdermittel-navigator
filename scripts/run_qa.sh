#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/4] validate_foerderprogramme.py"
python3 scripts/validate_foerderprogramme.py

echo
echo "[2/4] check_deadlines.py"
python3 scripts/check_deadlines.py

echo
echo "[3/4] report_coverage.py"
python3 scripts/report_coverage.py

echo
echo "[4/4] report_deadlines.py"
python3 scripts/report_deadlines.py

echo
echo "QA run completed."
