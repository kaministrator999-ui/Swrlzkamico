# Server 2.3.89 — Frozen Web Collector 1.0.4

## Event
Direct canonical durable-state writer repair for the Frozen Web Snapshot Collector.

## Root cause
The collector previously treated `etag is None` as proof that `swrlz/collector/control/state.json` did not exist. On private Vercel Blob reads an existing object can be returned without a usable ETag, causing the writer to request an immutable create against an already-existing pathname. Vercel Blob correctly rejected that operation, which surfaced as a false `STATE_WRITE_CONFLICT` during mutations such as starting a new snapshot.

## Change
`runtime_hot/web_snapshot_collector.py` is repaired directly; no compatibility wrapper or secondary loader is used. Before a no-ETag write, the collector now re-reads canonical state. If state is absent it retains immutable first-create behavior. If state exists, its `stateRevision` must match the caller's pre-write revision before overwrite proceeds. After every write, the persisted object is read back and must match both the expected revision and the exact canonical JSON state.

## Versions
- Server Runtime: 2.3.89
- Frozen Web Collector: 1.0.4
- API schema: 1 (unchanged)
- State schema: 1 (unchanged)

## Intentionally unchanged
Source registry behavior, crawl guardrails, robots enforcement, frozen snapshot format, content-addressed immutable artifacts, training-review separation, storage budget behavior, and existing durable collector data are unchanged.

## Lineage
Failed compatibility-wrapper attempts Collector 1.0.1 / Server 2.3.85 and Collector 1.0.2 / Server 2.3.86 remain preserved. Collector 1.0.3 / Server 2.3.87 remains the known-good recovery event that restored readiness before this direct repair. Server 2.3.88 was unrelated concurrent Web Frontend work and is preserved.

## Deployment
Runtime-hot compatible change only. No Vercel production rebuild or redeployment is required or triggered by this release event.

## Verification target
Live `/api/collector/readiness` must report HTTP 200, `ready:true`, module version `1.0.4`, runtime branch `runtime`, canonical path `runtime_hot/web_snapshot_collector.py`, private Blob storage configured, and API/state schema 1. The state-write behavior is considered fully proven only after a live mutating collector action succeeds without the previous false conflict.
