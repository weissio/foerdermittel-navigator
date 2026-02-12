#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/3] validate_foerderprogramme.py"
python3 scripts/validate_foerderprogramme.py

echo
echo "[2/3] check_deadlines.py"
python3 scripts/check_deadlines.py

echo
echo "[3/3] report_coverage.py"
python3 scripts/report_coverage.py

echo
echo "QA run completed."
