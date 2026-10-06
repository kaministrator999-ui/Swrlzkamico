# §wyrlz Knowledge Acquisition Snapshots

## Purpose

Knowledge-acquisition snapshots are a learning/review surface, not runtime diagnostics. They remain separate from `runtime-diagnostics/online-research/` so debugging telemetry can stay exhaustive while knowledge review remains compact.

## Runtime location

The runtime branch stores one folder per research-triggering request:

`runtime-diagnostics/knowledge-snapshots/<request-id>/`

Files:

- `knowledge-snapshot.json` — triggering user request, bounded research evidence, compact search trace, widget kinds, final §wyrlz answer, review state.
- `followup-1.json` through `followup-3.json` — up to the next three user turns when they occur, allowing review to detect correction, satisfaction, disagreement, clarification, or a useful continuation.

## Promotion boundary

A snapshot is **not local knowledge merely because a search succeeded**. New snapshots begin with:

`review.state = PENDING`
`review.promoteToLocalKnowledge = false`

A later review/distillation process may reject garbage, remove irrelevant material, reconcile contradictions, classify freshness, and promote only useful supported knowledge into the local knowledge layer.

## Size and relevance rules

The snapshot is intentionally bounded:

- triggering user text: 4,000 characters maximum;
- final answer: 16,000 characters maximum;
- at most 12 source records;
- source snippets: 900 characters maximum;
- at most 32 compact search-trace events;
- at most 8 widget kinds;
- at most 3 subsequent user turns.

Do not copy full webpages into snapshots. Store only evidence relevant to the question and enough provenance to revisit the source.

## Privacy boundary

Snapshots do not store precise coordinates, private reasoning, or full conversation history. The trigger and optional follow-up turns are stored because they are required to evaluate what was researched and whether the user subsequently corrected or refined it.

## Intended learning loop

`intent → knowledge/coverage check → targeted research → snapshot → answer → follow-up feedback → review → distill → promote/reject → local retrieval → freshness check → research delta`

Promotion and local-knowledge retrieval are a separate lifecycle and must not be simulated by marking a snapshot successful.
