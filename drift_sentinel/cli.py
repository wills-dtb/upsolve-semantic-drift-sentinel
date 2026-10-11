from __future__ import annotations
import argparse
import json
from pathlib import Path
from .models import MetricContract, ContextEvent
from .detector import detect_drift
from .report import summarize


def load_registry(path: Path) -> list[MetricContract]:
    raw = json.loads(path.read_text())
    return [MetricContract.from_dict(x) for x in raw["metrics"]]


def load_events(path: Path) -> list[ContextEvent]:
    events = []
    for line in path.read_text().splitlines():
        if line.strip():
            events.append(ContextEvent.from_dict(json.loads(line)))
    return events


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect semantic drift and generate regression evals for data agents.")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--out", default="output/drift_report.json")
    args = parser.parse_args()

    findings = detect_drift(load_registry(Path(args.registry)), load_events(Path(args.events)))
    report = summarize(findings)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
