from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class MetricContract:
    name: str
    definition: str
    owner: str
    aliases: list[str]
    criticality: str
    source: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "MetricContract":
        return cls(
            name=raw["name"],
            definition=raw["definition"],
            owner=raw.get("owner", "unknown"),
            aliases=raw.get("aliases", []),
            criticality=raw.get("criticality", "medium"),
            source=raw.get("source", "registry"),
        )


@dataclass(frozen=True)
class ContextEvent:
    source_type: str
    source_id: str
    timestamp: str
    text: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ContextEvent":
        return cls(**raw)


@dataclass
class DriftFinding:
    metric: str
    severity: str
    confidence: float
    current_definition: str
    candidate_update: str
    evidence: str
    source_id: str
    reason: str
    generated_evals: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
