# Server 2.3.86 — Frozen Web Collector hotfix-loader correction

**Status:** correction event; live verification required before closure  
**Overall Server:** `2.3.86`  
**Frozen Web Collector:** `1.0.2`  
**API schema:** `1` unchanged  
**State schema:** `1` unchanged  
**Deployment:** NONE — runtime-hot source only  
**Restart:** NONE

## Preserved failed lineage

Server `2.3.85` / Frozen Web Collector `1.0.1` attempted to repair the false durable-state conflict using a pinned source-string replacement wrapper. That event failed live verification because `/api/collector/readiness` returned HTTP 503 after the runtime update. The failed event remains preserved in `releases/server-2.3.85-frozen-web-collector-state-write.md`; this correction does not rewrite or hide it.

## Correction

Collector `1.0.2` removes the brittle source-string replacement mechanism. It loads the known-good Collector 1.0.0 implementation from immutable runtime commit `4b4d548c6519bec8c0b52ef524fa55e5a6c7ab88`, executes that pinned implementation, and then overrides only `_save_state` in the loaded module namespace.

The intended state-write repair remains:
- missing ETag is not treated as proof that `swrlz/collector/control/state.json` is absent;
- the collector performs a cache-bypassed durable re-read before deciding create vs overwrite;
- if existing durable revision differs from the loaded revision, the write fails as a genuine concurrency conflict;
- a truly absent state object still uses immutable create semantics;
- after writing, the collector reads the durable object back and verifies both revision and exact canonical JSON, preserving fail-loud behavior if another worker supersedes the write;
- when a usable ETag exists, the existing conditional `x-if-match` path remains in use.

## Compatibility

No API or state schema migration. Existing source registry, control state, snapshots, training review queue, and immutable evidence artifacts remain compatible and are not reset or rewritten by this source update.

## Verification plan

1. Confirm runtime authorities advance from Server `2.3.85` / Collector `1.0.1` to Server `2.3.86` / Collector `1.0.2`.
2. Confirm `/api/collector/readiness` returns HTTP 200 and reports module version `1.0.2` from `github-runtime`.
3. Confirm no Vercel production redeployment occurred for this compatible runtime-only event.
4. Operator reloads the authenticated collector UI and retries `Start new`.
5. Success criterion: `POST /api/collector/action` succeeds rather than returning the prior false `STATE_WRITE_CONFLICT`; durable revision and snapshot lifecycle advance.

## Event baseline / concurrency receipts

Immediately before preparing this event:
- Server Runtime `2.3.85`, blob `1f90007610b39490819557455e7601be0f09c661`
- Frozen Web Collector `1.0.1`, blob `aa0f33202fbec1ff8d5fded73671921e015ac37e`
- Failed wrapper blob `de69037bc5928f83c9f2b9fc466d81ea41fb60a3`
- Runtime branch head `e7e17dadd3299ad6e78602405d550f08e8b61e0c`
- Runtime branch tree `90f137a0f7ac5fb9906c6cd8b4a7a3e0dff6ee76`

These authorities must be re-read immediately before moving the runtime ref. If they advance concurrently, reconcile from the newest authority instead of publishing the stale planned versions.
