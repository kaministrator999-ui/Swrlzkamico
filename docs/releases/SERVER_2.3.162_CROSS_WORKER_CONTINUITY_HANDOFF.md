# §wyrlz Server 2.3.162 — Cross-worker continuity handoff + active-only hydration deferral

**Overall Server Runtime:** 2.3.162  
**Web Chat:** 1.5.32  
**Runtime manifest:** 100  
**Stable deployment:** REQUIRED for the server half; NOT PERFORMED by this event  
**Restart:** NONE  
**Runtime source authority:** `runtime`  
**Stable source authority:** `main`

## Trigger / failed 2.3.161 acceptance

The first fresh manifest-99 acceptance request was:

- request ID: `web:mu2qytey:22930364892292571994`
- thread ID: `thread:mu2qyqou:35254907272677003622`
- canonical assistant ID: `assistant:f371f2348fe62ed46df000bdc2d7`

Production logs proved the original turn was admitted correctly:

1. `POST /api/chat/` returned 200 at 14:08:27 UTC.
2. The USER canonical commit landed at account-state revision 117.
3. Canonical history was rebuilt at revision 117.
4. `CHAT_GENERATION_STARTED` was emitted for the same request at revision 117.

The browser then moved to the background and returned to the foreground while generation remained active. The continuity client cancelled its current reader and attempted to resume the same request. That resume landed on another Vercel worker.

The resumable generation layer correctly detected that the durable generation transcript belonged to another worker and returned HTTP 409 with its existing `GENERATION_SESSION_REMOTE_OWNER` / remote-terminal semantics. However, two higher layers mishandled that valid ownership handoff:

- the browser reconnect loop treated HTTP 409 as a generic unavailable generation session and repeatedly re-POSTed the generation request;
- the canonical turn middleware treated the same 409 as a terminal generation failure and persisted an empty FAILED assistant at revision 118.

When the original generation owner later reached the real terminal assistant answer, that canonical assistant commit collided with the already-persisted empty FAILED assistant and logged:

`CHAT_TURN_MESSAGE_ID_CONTENT_CONFLICT`

This established the precise failure chain:

```text
original generation starts correctly @ revision 117
        ↓
foreground reconnect lands on another worker
        ↓
remote-owner 409 is returned
        ↓
old browser loops generation POSTs
        +
old canonical middleware persists empty FAILED assistant @ revision 118
        ↓
original owner later finishes real answer
        ↓
real terminal commit conflicts with poisoned assistant identity
```

The 2.3.161 Whole Conversation Camera relay itself passed its first live proof: `conversation-camera / whole-thread` and per-message receipts appeared in production logs with thread/message/request identity, message state/text, terminal-integrity data, and bounded raw state.

The same camera evidence also showed several stale local `streaming` records elsewhere in account cache. The previous hydration guard scanned every thread, allowing unrelated inactive stale entries to block server hydration globally.

## Stable server correction

### Remote-owner handoff is explicitly non-terminal

`main/api/chat_resume_sessions.py` now marks only these existing ownership conditions:

- `GENERATION_SESSION_REMOTE_OWNER`
- `GENERATION_SESSION_REMOTE_TERMINAL`

with:

`X-SWRLZ-Continuity-Handoff: non-terminal-v1`

The response also continues to identify the resumable generation and transcript contracts.

Request-ID/fingerprint conflicts such as `REQUEST_ID_REUSE_MISMATCH` do **not** receive this handoff marker and remain real errors.

### Canonical middleware no longer poisons the assistant on handoff

`main/api/chat_client_debug.py` now recognizes a 409 as non-terminal **only when** that explicit continuity-handoff header is present.

For a marked handoff it:

- leaves canonical assistant persistence unchanged;
- does not call `finish_turn(... FAILED ...)`;
- logs `CHAT_GENERATION_CONTINUITY_HANDOFF`;
- leaves the original generation owner responsible for the terminal canonical assistant commit.

All other HTTP error handling remains on the existing failure path.

## Runtime continuity correction

`runtime/web/chat_background_resume_v2.js` is now continuity version 6.

During reconnect, a 409 carrying `non-terminal-v1` no longer enters the generic retry loop. Instead Chat:

1. records a shared-transcript handoff in network-continuity/activity diagnostics;
2. asks the existing `generation-transcript-v1` continuity layer to synchronize the same request;
3. follows the shared private transcript until terminal synchronization is verified;
4. closes the browser continuity stream without starting another generation.

Compatibility is deliberate: before the stable server is manually deployed, production does not emit the handoff header, so the new runtime does not assume the new server behavior.

## Hydration correction

`runtime/web/chat_account_state_sync_v1.js` advances to account-state sync v4.

Server hydration is now deferred only for an unresolved local assistant whose request ID equals the **currently active Chat generation request**.

Inactive stale `streaming` / `cancelling` cache entries elsewhere in the account no longer freeze server hydration. They are classified as stale presentation cache and repaired from server authority. Whole Conversation Camera and account-state diagnostics report stale-stream repair counts without restoring browser state authority.

The request-ID-first correlation introduced in 2.3.161 remains in place.

## Authority boundaries

The correction preserves the project ownership contract:

- Browser/Mask: continuity presentation, transport relay, local diagnostic cache.
- Server/Body: canonical USER/ASSISTANT state and generation ownership/continuity authority.
- LALM/Brain: cognition and answer generation.

A worker-ownership handoff is a transport condition, not a semantic/model terminal.

## Lineage

Stable staging:

- initial broad 409 correction attempt: `2b76cba6cd6b6814072a5a8e52dd63e1b8fde6fe`
- resumable owner-specific handoff marker: `8633b7fa19e0191c9ff456f45ba2e4566f9c9627`
- canonical middleware narrowed to explicit handoff marker: `678c8b8f356bc57e2f0883d5c31e258795a6512b`

Runtime:

- shared-transcript reconnect handoff: `4e3894fe9e8d81004dac54c8cfd9f9c7e521862c`
- active-request-only hydration deferral: `29783b75553f0b0ab7f69be43e32d31bda757a23`
- Server Runtime 2.3.162 authority: `d605726295ed4c3ce953c1373ca0a4bf9e0bd9ae`
- Web Chat 1.5.32 authority: `5b4110e003f131ab3b58ef11a543ea68a249cb37`
- runtime manifest 100: `c979dc8d7a43e02d77740ef0e9bc9a68182ca96e`

## Deployment state

Git deployment remains disabled in current `vercel.json`; the stable `main` commits above did not deploy production.

A manual production deployment of current `main` is required before the `non-terminal-v1` handoff path can activate in production. The user must perform or explicitly approve that deployment separately.

## Acceptance plan after stable deployment

A production acceptance turn should prove:

1. one canonical USER commit before generation;
2. one generation owner starts the request;
3. if foreground/background or network continuity lands on another worker, the server logs `CHAT_GENERATION_CONTINUITY_HANDOFF` rather than a FAILED terminal;
4. the browser follows `/api/chat/transcript` instead of repeatedly POSTing `/api/chat/`;
5. no empty FAILED assistant is persisted for a remote-owner handoff;
6. the original owner can commit the real terminal assistant without content conflict;
7. canonical revision advances only for the USER and real terminal ASSISTANT commits;
8. unrelated stale local `streaming` cache entries do not globally block server hydration;
9. Whole Conversation Camera receipts remain visible and credential-safe;
10. whole-state browser snapshot authority remains retired.
