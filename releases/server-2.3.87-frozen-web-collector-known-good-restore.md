# Server 2.3.87 — Frozen Web Collector known-good runtime restoration

**Status:** recovery event; verify live readiness before closure  
**Overall Server:** `2.3.87`  
**Frozen Web Collector:** `1.0.3`  
**API schema:** `1` unchanged  
**State schema:** `1` unchanged  
**Deployment:** NONE — runtime-hot source only  
**Restart:** NONE

## Why this event exists

The original Collector `1.0.0` was live and readable but produced a false `STATE_WRITE_CONFLICT` when starting from an existing durable state object whose Blob read did not provide a usable ETag. Two runtime compatibility-wrapper repairs were attempted:

- Server `2.3.85` / Collector `1.0.1`: failed live readiness with HTTP 503.
- Server `2.3.86` / Collector `1.0.2`: simplified the wrapper but also failed live readiness with HTTP 503.

Both failed events remain preserved. This event restores the exact known-good Collector 1.0.0 implementation blob `0ce4e586922fd68fdda3ef4891db6c12c35266e2` at the canonical runtime path so the collector console is not left unavailable.

## Scope

- Restore `runtime_hot/web_snapshot_collector.py` to the exact known-good implementation from runtime commit `4b4d548c6519bec8c0b52ef524fa55e5a6c7ab88`.
- Do not alter the private Blob control state, source registry, snapshots, training review queue, or immutable evidence objects.
- Keep API schema 1 and state schema 1 unchanged.
- Record explicitly that the original Start/state-write bug is **not fixed** by this recovery event.

## Follow-up boundary

The remaining correction must modify the actual `_save_state` implementation directly or move that correction into the stable collector host. A stable-host correction belongs on `main` and requires an explicitly approved production deployment before it can affect production. No such deployment is authorized by this recovery event.

## Verification

1. `/api/collector/readiness` must return HTTP 200 again.
2. Live host must report Frozen Web Collector `1.0.3` from `github-runtime`.
3. No Vercel production redeployment or restart is performed.
4. Do not ask the operator to retry `Start new` as proof of the state-write fix; 1.0.3 deliberately restores availability, not the unresolved write bug.

## Baseline

Immediately before this recovery:
- Server Runtime `2.3.86`, blob `d7431a6905b373b9030f0e53069fa2eecdaa1e2a`
- Frozen Web Collector `1.0.2`, blob `afd4361c569076eea679aa8405ad22d0b9dd8921`
- Collector 1.0.2 wrapper commit `c074ef28e31276ac1f3249e63931e033701e2e07`
