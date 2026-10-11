.PHONY: demo test

demo:
	python -m drift_sentinel --registry demo/current_registry.json --events demo/incoming_context.jsonl --out output/drift_report.json

test:
	python -c "import importlib.util,pathlib; p=pathlib.Path('tests/test_drift.py'); s=importlib.util.spec_from_file_location('t',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.test_detects_mrr_drift_but_not_stable_customer_definition(); print('ok')"
