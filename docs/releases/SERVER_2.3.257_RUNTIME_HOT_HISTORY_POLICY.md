# Server 2.3.257 — Runtime-hot canonical history policy seam

## Status

**Source complete; deterministic history-policy behavior verified; production activation pending one stable Server deployment.**

- Overall Server event: `2.3.257`
- LALM Engine: `2.1.86` / v74 unchanged
- Chat: `1.5.75` unchanged
- New runtime-owned policy source: `runtime_hot/chat_history_policy.py`
- Stable bootstrap seam: source complete on `main`
- Deployment / restart: **NONE performed**

## Requested outcome

Make canonical Chat history reconstruction improvable through the `runtime` hot path instead of requiring a new Vercel production deployment for every history-recovery refinement.

## Architecture reconciliation

The durable conversation authority remains Human/Server owned. Authentication, Redis keys, durable message records, turn creation, terminal commits, and authorization stay in stable Server code.

The new hot boundary is deliberately narrower: a runtime-hot **read-only history policy** may enumerate and filter already-authoritative server message records into the bounded history supplied to cognition. It cannot accept browser history as authority and it does not own Redis writes.

Flow after activation:

```text
stable Server auth + durable Redis records
        ↓
stable hot-loader ABI
        ↓
runtime-hot chat_history_policy.py
        ↓
bounded canonical history
        ↓
v74 / later LALM cognition
```

This extends the existing hot-loader architecture rather than moving persistence into the Brain or creating a second conversation store.

## Stable bootstrap seam

`api/hot_loader.py` adds a dedicated `HOT_SERVER_DIR` and `HOT_CHAT_HISTORY_POLICY` slot with independent content-signature caching. The loader accepts a hot policy only when it exposes:

- `resolve_history`
- `inspect_policy`
- `CONTRACT_ID`
- `HOT_REVISION`

`inspect_policy()` must report `ok=true`; otherwise the hot module is rejected.

`api/runtime_hot.py` adds `runtime_hot/chat_history_policy.py` to the fixed hot-source allowlist, includes the Server hot directory in backup/rollback/clear lifecycle, invalidates only the history-policy cache when that source changes, and exposes the `hot-server-history-policy` Server capability as read-only with bundled fallback.

`api/chat_turn_state.py` routes Redis history reconstruction through the hot policy when available. The stable Server still resolves the authenticated user and creates the Redis store. Hot output is defensively normalized and bounded again before being sent onward. Missing/invalid/failing hot policy falls back to the bundled canonical history reader.

## Runtime policy v1

`runtime_hot/chat_history_policy.py` revision `1.0.0-runtime-history-compat-v1`:

- reads both `message_index` and legacy `messages` sorted-set indexes;
- resolves every ID to the server-owned durable `MessageRecord`;
- rejects records outside the authenticated user/thread scope;
- deduplicates by message ID, preferring the most recently updated durable record;
- restores canonical creation order;
- excludes the current request;
- excludes empty, streaming, failed, and cancelled records;
- bounds selected history to 32 messages and 2,000 characters per message;
- emits count-only `SWRLZ_CHAT_HISTORY_HOT` telemetry without transcript content.

The stable loader emits complementary `SWRLZ_CHAT_HISTORY_POLICY` telemetry for source selection, bounded counts, and fallback/error class only.

## Deterministic verification

The history-policy acceptance case passed **6/6**:

1. legacy-indexed messages recovered;
2. user/assistant order preserved;
3. a record appearing in both indexes deduplicated;
4. current-request message excluded;
5. failed assistant message excluded;
6. current/legacy index counts remained correct.

Committed loader/history diffs were re-read after mutation. No CI workflow/status was attached to these commits, so production import/hydration remains an activation check rather than being represented as already live.

## Activation truth

The runtime policy source is already durable on `runtime`, but the currently deployed stable Server predates the new Server-policy hot-loader ABI. Therefore production cannot load this new hot slot yet.

One explicitly approved stable production deployment is required to install the bootstrap seam. After that deployment, later changes confined to `runtime_hot/chat_history_policy.py` can hydrate through the normal `runtime` refresh path without another Vercel deployment or restart.

The existing Server 2.3.256 bundled Redis compatibility reader remains the fallback, so the hot seam does not remove the stable safety path.

## Post-deployment acceptance

Acceptance requires production evidence that:

1. `/api/hot/status` exposes `chat_history_policy.py` / `hot-server-history-policy`;
2. the hot policy imports and its built-in self-test passes;
3. `SWRLZ_CHAT_HISTORY_POLICY` reports `policy-applied` with `source=runtime-override` on a normal authenticated Chat request;
4. legacy-indexed same-thread history can be recovered with nonzero bounded counts;
5. the follow-up `Can you add a error catch to that code?` receives the prior standalone code artifact;
6. v74 routes it as inherited lightweight standalone programming rather than existing-project architecture work;
7. v69 lightweight context compaction activates and the request completes normally.

## Version / concurrency

Version gate immediately before assignment remained:

- Server `2.3.256`
- LALM `2.1.86`
- Chat `1.5.75`

No concurrent authority advance was observed. This event therefore owns Server `2.3.257` only. LALM and Chat remain unchanged.

## Lineage

- runtime history policy: `1581935d99194c82cc3f298d29db00c6b94c63f1`
- stable hot-loader seam: `455c63166dc41f78a3c55cc87684102640eb9f7d`
- stable runtime hydrator extension: `fe5b3280c58c684749692e3d59a3ad6759f7f14d`
- stable canonical-history routing seam: `6346bf8522da7e769f71297ab4266fe9029b8aa2`
- Server authority: `40bac966a8d7a015483ff5b028e1185d15b57a45`

## Deployment boundary

No deployment or restart was performed. The stable bootstrap changes remain deployment-gated. Future history-policy-only changes become ordinary runtime-hot work only after that stable ABI is activated once.