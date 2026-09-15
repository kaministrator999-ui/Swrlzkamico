# Server 2.3.159 — Phase 2A client coordination repair

**Status:** runtime correction implemented and versioned; live runtime verification pending refreshed browser acceptance.

**Overall Server:** 2.3.159  
**Web Chat:** 1.5.29  
**Stable API:** 2.3.158 deployment unchanged  
**Runtime manifest:** 97  
**Deployment:** NONE  
**Restart:** NONE

## Production evidence that triggered this correction

The 2.3.158 deployment correctly moved Chat to server-owned canonical state and rejected whole-browser snapshot writes. A fresh canonical `Hey 👋` turn still completed exactly once.

During the follow-up metadata acceptance test, however, rename/pin/select/delete changes were visible locally but no expected `POST /api/chat_state` mutation receipts appeared. Client diagnostics repeatedly reported hydration deferred because a cached assistant remained marked as locally streaming even though the server had already committed the terminal assistant state.

## Root causes

### 1. Mutation flush deadlock

`flushMutations()` could fire while hydration held the client sync lock. In that case it returned immediately without scheduling another flush. The queued mutations remained pending. Hydration then saw the pending queue and deferred itself as well, leaving both sides waiting.

### 2. Stale local streaming cache could block hydration indefinitely

Hydration previously deferred whenever any browser-cached assistant message had `state=streaming`. If the browser missed the terminal UI transition but the server already held the canonical completed/failed/cancelled assistant message, that stale local state could keep blocking the very hydration needed to repair it.

## Runtime correction

`runtime/web/chat_account_state_sync_v1.js` now:

- reschedules mutation flush when the sync lock is busy instead of silently returning;
- explicitly wakes mutation flushing when hydration sees queued metadata operations;
- emits `mutation-enqueued`, `mutation-deferred`, `mutation-complete`, and failure diagnostics for acceptance tracing;
- identifies local in-flight assistant messages by immutable message identity;
- defers hydration only while the matching server message is still absent or non-terminal;
- allows server terminal state to overwrite and repair stale local `streaming` cache;
- preserves the Phase 2A server-authoritative state contract and retired whole-snapshot write boundary.

## Source lineage

Runtime:
- `d7722e88b062129915773d5b9b50d3f7cfe52028` — state mutation deadlock + stale-stream hydration repair
- `dc11e614c3bcd4c23a78a9579eeab7d493e9dc9c` — manifest 97
- `4be823231b37f9afe499bd21db49e9f1e38fa62c` — Server 2.3.159 authority
- `0a7f92ed031ec7d1ffa13429543d568e6e512a38` — Web Chat 1.5.29 authority

## Mask ownership-copy defect discovered during the same acceptance test

The base Chat page still contains legacy browser-authority wording from the pre-Phase-2A architecture, including:

- `Delete “…“ from this browser?`
- `Threads stay in this browser`
- `private on this device`
- export wording that calls the conversation browser-local.

Those statements are now architecturally incorrect because signed-in conversation state is server/account authoritative and browser state is cache/presentation only. This event records the defect but does not paper over it with a supplemental override. The canonical `runtime/web/chat.html` copy should be corrected directly in its own targeted UI event.

## Acceptance after runtime propagation

1. Refresh Chat and confirm manifest 97 / Web Chat 1.5.29.
2. Confirm a stale local streaming assistant is repaired once the server has its terminal state.
3. Rename/pin/select a thread and confirm `mutation-enqueued` followed by `POST /api/chat_state` and `mutation-complete`.
4. Delete a disposable thread and confirm `DELETE_THREAD` reaches the server and the tombstone prevents resurrection after refresh.
5. Confirm there are no successful whole-state `PUT /api/chat_state` writes.
6. Confirm canonical user/assistant generation remains exactly once.

## Remaining work

Correct the legacy browser-local ownership copy directly in the base Chat page, then complete the metadata command/tombstone acceptance test.