# §wyrlz Server Runtime 2.3.90 — Frozen Web Collector Start Revision Continuity

Date: 2026-09-12

## Scope

This runtime-hot release repairs the remaining `Start new` false `STATE_WRITE_CONFLICT` in the Frozen Web Snapshot Collector without changing stable deployment code, API schema, state schema, or durable collector data.

## Root cause

Collector 1.0.4 correctly repaired the generic missing-ETag durable writer path, but a separate lifecycle defect remained. `_new_snapshot_state(previous)` created the next snapshot from `_default_state()`, which reset `stateRevision` to `0`. When Vercel Blob returned no usable ETag, `_save_state` re-read the existing durable state and correctly detected that its persisted revision was greater than zero. The new snapshot therefore conflicted with the state it was replacing even though no competing worker was involved.

## Repair

The canonical runtime source `runtime_hot/web_snapshot_collector.py` now carries the previous durable `stateRevision` into `_new_snapshot_state` before the first save. `_save_state` then advances that revision monotonically. Genuine concurrent revision changes remain conflict-protected.

## Versions

- Server Runtime: `2.3.90`
- Frozen Web Snapshot Collector: `1.0.5`
- Collector API schema: `1`
- Collector state schema: `1`

## Lineage

- `1.0.1` and `1.0.2`: failed compatibility-wrapper attempts; preserved as failed lineage.
- `1.0.3`: restored the last verified working implementation.
- `1.0.4`: direct canonical missing-ETag writer repair.
- `1.0.5`: direct canonical new-snapshot revision continuity repair.

No collector state, source registry, snapshots, review queue, or frozen artifacts were deleted or reset by this release.

## Deployment boundary

This is a compatible runtime-hot change. The stable collector host continues to fetch `runtime_hot/web_snapshot_collector.py` and `versions/frozen-web-collector.txt` from the `runtime` branch. No production Vercel deployment or restart is required or triggered by this release.

## Verification target

The public readiness route must report Collector `1.0.5`, `ready:true`, runtime branch/source receipts, configured private Blob storage, and `deploymentRequiredForRuntimeChanges:false`. The authenticated `Start new` action is the final behavioral receipt because it exercises the repaired durable write path.
