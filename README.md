# Semantic Drift Sentinel

A deliberately small, runnable prototype for **Upsolve AI**: turn changing business context into semantic-drift alerts and new regression/eval cases before a data agent silently answers with stale definitions.

> Built from public information about Upsolve AI as a 2–3 hour engineering exercise. Not affiliated with Upsolve AI and uses synthetic data only.

## Why this problem

Upsolve publicly describes the production failure mode clearly: the underlying model may be capable, but business context changes — metric definitions, fiscal rules, permissions and institutional knowledge — and agents can then give technically plausible but business-wrong answers.

A trustworthy data-agent platform therefore needs more than a semantic layer. It needs a **change-detection loop** that notices when the world has moved underneath that layer and turns those changes into testable contracts.

This prototype explores that loop.

## What it does

Given a versioned metric registry and incoming context events from places such as Slack/Notion, it:

1. maps context to governed metrics;
2. detects likely definition drift;
3. scores severity/confidence;
4. emits a review/block decision; and
5. generates candidate regression evals, including temporal and boundary-condition tests.

The included demo catches a finance policy change where **MRR stops including one-time onboarding fees**, while ignoring a second event that merely restates the existing Active Customer definition.

## Run it

Requires Python 3.11+ and no API key.

```bash
python -m drift_sentinel \
  --registry demo/current_registry.json \
  --events demo/incoming_context.jsonl \
  --out output/drift_report.json
```

Expected top-level decision:

```json
{
  "decision": "BLOCK_AND_REVIEW",
  "summary": {"high": 1, "medium": 0, "total": 1}
}
```

## Why deterministic instead of calling an LLM?

For a 2–3 hour artifact, I wanted the failure modes to be visible and the project runnable by anyone without credentials. The matcher/detector is intentionally heuristic.

In production I would replace only the **candidate extraction + entity-resolution** layer with structured LLM calls, while keeping policy gating, provenance, versioning and eval promotion deterministic and auditable.

## Production version

See [ARCHITECTURE.md](ARCHITECTURE.md). The next meaningful increment is not a prettier UI; it is a **shadow-evaluation runner** that executes the current and candidate semantic context against representative queries and quantifies answer/SQL deltas before promotion.

## Deliberately left out

- real Slack/Notion/dbt connectors;
- warehouse execution;
- LLM extraction;
- RBAC/tenant isolation;
- persistent registry/version store;
- UI;
- distributed workflow orchestration.

Those are intentionally omitted because this is meant to demonstrate the architectural idea, not pretend a small prototype is production infrastructure.
