SHELL := /bin/bash

.PHONY: qa batch preview open_calls status gaps links_live

qa:
	scripts/run_qa.sh

batch:
	scripts/run_monthly_batch.sh "manueller_batch" 0 "Monatslauf mit QA"

preview:
	python3 -m http.server 8000 --bind 127.0.0.1 --directory "$(CURDIR)"

open_calls:
	python3 scripts/report_open_calls.py

status:
	python3 scripts/report_coverage.py
	python3 scripts/report_deadlines.py
	python3 scripts/report_open_calls.py
	python3 scripts/report_gaps.py
	python3 scripts/report_scope_matrix.py
	python3 scripts/report_link_quality.py
	python3 scripts/report_link_structure.py
	python3 scripts/report_url_sanity.py
	python3 scripts/report_master_coverage.py
	python3 scripts/report_info_link_overlap.py
	python3 scripts/report_status.py

gaps:
	python3 scripts/report_gaps.py

links_live:
	python3 scripts/report_live_link_health.py
