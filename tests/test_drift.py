import json
from pathlib import Path
from drift_sentinel.models import MetricContract, ContextEvent
from drift_sentinel.detector import detect_drift


def _load():
    registry = json.loads(Path("demo/current_registry.json").read_text())
    metrics = [MetricContract.from_dict(x) for x in registry["metrics"]]
    events = [ContextEvent.from_dict(json.loads(x)) for x in Path("demo/incoming_context.jsonl").read_text().splitlines()]
    return metrics, events


def test_detects_mrr_drift_but_not_stable_customer_definition():
    findings = detect_drift(*_load())
    assert len(findings) == 1
    assert findings[0].metric == "Monthly Recurring Revenue"
    assert findings[0].severity == "high"
    assert len(findings[0].generated_evals) >= 2
