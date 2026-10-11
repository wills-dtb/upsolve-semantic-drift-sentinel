# Architecture notes

## V0 flow

`context event -> metric matcher -> drift detector -> severity gate -> generated evals -> review/block decision`

This prototype deliberately keeps the classifier deterministic so the demo runs without API keys and its decisions are inspectable.

## Production shape

1. **Context ingestion** — Slack, Notion, dbt, warehouse metadata, metric catalogs and validated SQL emit versioned events.
2. **Entity resolution** — map loose language ("MRR", "recurring revenue") to governed semantic objects.
3. **LLM-assisted diff** — structured extraction proposes a candidate semantic patch with source citations and confidence.
4. **Policy gate** — critical metrics require human approval; lower-risk changes can enter a staging context automatically.
5. **Eval synthesis** — generate golden queries, temporal boundary cases and permission-sensitive cases from the diff.
6. **Shadow execution** — run current vs candidate context against representative workloads; compare answers, SQL, latency and cost.
7. **Promotion** — merge the context version only if required evals pass; retain provenance and rollback metadata.

## Reliability principles

- Semantic context is versioned, never silently overwritten.
- Every candidate change carries source provenance and an effective date.
- High-criticality metrics fail closed.
- Generated evals are additive; humans can promote useful cases into the permanent golden set.
- The system should measure false-positive drift alerts because noisy governance gets bypassed.
