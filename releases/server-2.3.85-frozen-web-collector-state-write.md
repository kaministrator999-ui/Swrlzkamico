# Server 2.3.85 — Frozen Web Collector durable state-write repair

**Status:** runtime implementation committed; live verification required before closure  
**Overall Server:** `2.3.85`  
**Frozen Web Collector:** `1.0.1`  
**API schema:** `1` unchanged  
**State schema:** `1` unchanged  
**Deployment:** NONE — runtime-hot source only  
**Restart:** NONE

## Incident

The authenticated collector console could read its durable private Blob state successfully, but `Start new` repeatedly returned HTTP 409 with `STATE_WRITE_CONFLICT` / “Collector state changed on another worker; reload and retry.” Production logs showed repeated `POST /api/collector/action` 409 responses while status/readiness calls remained healthy.

The 1.0.0 state writer treated `etag is None` as proof that `swrlz/collector/control/state.json` did not exist and therefore requested an immutable create. That inference is unsafe for an existing private Blob object when the read path does not expose a usable ETag. Vercel Blob then correctly rejects the create because the pathname already exists, and the collector surfaced the rejection as a concurrency conflict.

## Repair

- Preserve the verified Collector 1.0.0 implementation from runtime commit `4b4d548c6519bec8c0b52ef524fa55e5a6c7ab88` / Git blob `0ce4e586922fd68fdda3ef4891db6c12c35266e2`.
- Replace only `_save_state` through a pinned, hash-verified runtime compatibility wrapper.
- If no usable ETag is available, perform a consistent `cache=0` re-read before deciding create vs overwrite.
- Treat an absent durable object as a true immutable create.
- Treat an existing object with the expected revision as an overwrite candidate rather than a new object.
- Fail with a real conflict if the current revision advanced before the write.
- Read the object back consistently after the write and verify both the expected revision and the exact canonical JSON state so a superseding worker remains fail-loud.
- Keep the existing ETag conditional-write path when an ETag is available.

## Compatibility / migration

No API-schema or state-schema migration is required. Existing `state.json`, source registry, snapshots, training-review records, and immutable evidence artifacts remain compatible and untouched. The wrapper is intentionally temporary architecture: a future intentional collector revision should flatten this patch back into the full canonical source while preserving the corrected semantics.

## Verification plan

1. Confirm runtime authorities resolve to Server `2.3.85` and Frozen Web Collector `1.0.1`.
2. Confirm `/api/collector/readiness` serves Collector `1.0.1` from `github-runtime` without a production deployment.
3. Confirm the live runtime source is the pinned compatibility wrapper.
4. Operator retries `Start new` from the authenticated collector UI.
5. Success criterion: no false 409; snapshot transitions from `Not started` into a running/paused/ready state and durable state revision advances.

## Baseline / concurrency receipts

Event-entry authorities:
- `runtime/VERSION.txt` SHA `30ffd037ef7f75ed16e8781923e09145718f4ecf`
- Server Runtime `2.3.84`, blob `d81fdaa4bfa3ba458a2405f0742973b95da3d13d`
- Frozen Web Collector `1.0.0`, blob `75bbe7eaebb245e0a0c8b70aec57b6044dcebeab`
- Collector source blob `0ce4e586922fd68fdda3ef4891db6c12c35266e2`
- Runtime branch event baseline commit `4b4d548c6519bec8c0b52ef524fa55e5a6c7ab88`

Immediately before commit, these authorities must be re-read; if any changed, this release number must be reconciled before the branch ref is moved.
