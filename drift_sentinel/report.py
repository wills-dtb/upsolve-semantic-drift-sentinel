from __future__ import annotations
from datetime import datetime, timezone


def summarize(findings: list) -> dict:
    high = sum(1 for f in findings if f.severity == "high")
    medium = sum(1 for f in findings if f.severity == "medium")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": "BLOCK_AND_REVIEW" if high else ("REVIEW" if medium else "PASS"),
        "summary": {"high": high, "medium": medium, "total": len(findings)},
        "findings": [f.to_dict() for f in findings],
    }
