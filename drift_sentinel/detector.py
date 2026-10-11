from __future__ import annotations
import re
from difflib import SequenceMatcher
from .models import MetricContract, ContextEvent, DriftFinding

CHANGE_MARKERS = {
    "now", "effective", "redefined", "definition", "means", "exclude", "excludes",
    "include", "includes", "instead", "no longer", "from today", "going forward",
    "fiscal", "timezone", "booked", "recognized", "recognised"
}

CRITICALITY_WEIGHT = {"low": 0.08, "medium": 0.16, "high": 0.26, "critical": 0.34}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9%£$._ -]+", " ", text.lower())).strip()


def _mentions(metric: MetricContract, text: str) -> bool:
    hay = _normalize(text)
    terms = [metric.name, *metric.aliases]
    return any(_normalize(t) in hay for t in terms if t)


def _change_signal(text: str) -> float:
    lower = text.lower()
    hits = sum(1 for marker in CHANGE_MARKERS if marker in lower)
    return min(0.45, hits * 0.075)


def _definition_distance(current: str, candidate: str) -> float:
    similarity = SequenceMatcher(None, _normalize(current), _normalize(candidate)).ratio()
    return 1.0 - similarity


def _candidate_sentence(text: str, metric: MetricContract) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    for sentence in sentences:
        if _mentions(metric, sentence):
            return sentence.strip()
    return text.strip()


def generate_evals(metric: MetricContract, candidate: str) -> list[dict]:
    name = metric.name
    evals = [
        {
            "id": f"{name.lower().replace(' ', '_')}_definition_grounding",
            "question": f"How is {name} defined?",
            "assertions": [
                "answer cites the active semantic contract",
                "answer does not blend superseded and current definitions",
                "answer exposes effective-date ambiguity instead of guessing",
            ],
        },
        {
            "id": f"{name.lower().replace(' ', '_')}_historical_consistency",
            "question": f"Compare {name} before and after the latest definition change.",
            "assertions": [
                "query applies the correct definition for each effective period",
                "result labels any restatement or non-comparability",
            ],
        },
    ]
    if any(token in candidate.lower() for token in ("exclude", "include", "recogn", "booked")):
        evals.append({
            "id": f"{name.lower().replace(' ', '_')}_boundary_case",
            "question": f"Calculate {name} for a record that sits on the newly changed inclusion boundary.",
            "assertions": [
                "boundary record follows the latest business rule",
                "reasoning references the governing context source",
            ],
        })
    return evals


def detect_drift(metrics: list[MetricContract], events: list[ContextEvent]) -> list[DriftFinding]:
    findings: list[DriftFinding] = []
    for event in events:
        for metric in metrics:
            if not _mentions(metric, event.text):
                continue
            candidate = _candidate_sentence(event.text, metric)
            change_signal = _change_signal(candidate)
            if change_signal == 0:
                continue
            distance = _definition_distance(metric.definition, candidate)
            confidence = min(0.99, 0.28 + change_signal + distance * 0.30 + CRITICALITY_WEIGHT.get(metric.criticality, 0.16))
            if confidence < 0.58:
                continue
            severity = "high" if metric.criticality in {"high", "critical"} or confidence >= 0.80 else "medium"
            findings.append(DriftFinding(
                metric=metric.name,
                severity=severity,
                confidence=round(confidence, 2),
                current_definition=metric.definition,
                candidate_update=candidate,
                evidence=event.text,
                source_id=event.source_id,
                reason="Business context mentions the metric with change-language and materially differs from the active contract.",
                generated_evals=generate_evals(metric, candidate),
            ))
    return sorted(findings, key=lambda f: (f.severity == "high", f.confidence), reverse=True)
