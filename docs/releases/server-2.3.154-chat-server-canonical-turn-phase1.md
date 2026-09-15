# Server 2.3.154 — Server-canonical Chat turn phase 1

**Overall Server:** 2.3.154  
**Web Chat:** 1.5.27  
**Web Frontend:** 1.0.4  
**Stream Contract:** V2 unchanged  
**Google Account:** unchanged  
**LALM:** unchanged

## Purpose

Move authenticated Chat message ownership toward the Mask / Human / Brain contract used by the SERVER APK: the browser presents and relays the turn, while the server durably owns the canonical user/assistant message lifecycle.

## Stable server work staged on `main`

- Added `api/chat_turn_state.py` with account-scoped, private-Blob canonical message commits.
- User-message commit is idempotent by account/thread/message identity and verifies the written message is still present after the Blob write; bounded retries reconcile simple overwrite races.
- Updated the already-installed Chat middleware so an authenticated stream request follows this sequence:

```text
private Chat token accepted
    -> exact message receipt
    -> durable USER message commit
    -> generation/stream start
    -> terminal stream observation
    -> durable ASSISTANT message commit
```

- If an authenticated durable USER commit fails, generation fails closed instead of starting inference on a message that the server did not save.
- Signed-out/no-account sessions remain on the existing client compatibility path for this phase rather than being silently assigned an unstable identity.
- Structured private runtime events now distinguish `CHAT_MESSAGE_ACCEPTED`, `CHAT_MESSAGE_COMMITTED`, `CHAT_GENERATION_STARTED`, and `CHAT_GENERATION_TERMINAL` using the same request/thread/message correlation.
- Terminal assistant persistence handles COMPLETED, CANCELLED, FAILED, RESET, and accumulated DELTA text without altering the V2 stream returned to the browser.

### Main lineage

- canonical turn store: `b9856ae567ad8ecbbb434767548f95c750fe7af9`
- Chat middleware transaction/lifecycle integration: `3bb8b9e54a7166e513f20c1083a26da6a5934758`

## Runtime work on `runtime`

- `chat_account_state_sync_v1.js` now attaches the browser-created USER and ASSISTANT message IDs plus their timestamps to the outgoing stream request. This lets server canonical state and the currently visible browser state refer to the same message records instead of creating duplicate IDs.
- `chat_runtime_loader_v3.js` no longer hardcodes child assets to revision `93`; it derives the revision from its manifest-versioned loader URL, with `95` only as the fallback.
- `chat_stream_incremental.js` fixes the waiting-state `txt` temporal-dead-zone crash that previously prevented visible stream rendering while server work could continue.
- Runtime manifest advanced from 94 to 95 so changed assets receive a new immutable cache key.
- Existing whole-state browser synchronization remains temporarily enabled as compatibility transport. It is not accepted as the final message authority.

### Runtime lineage

- canonical-turn ID transport: `ddc5a5272860b4939ed8ad8b4e8dd1ac06e31b47`
- manifest-derived asset revision: `b88ddf6b81ae75d361222cad4d236392e4ab91b3`
- incremental renderer TDZ repair: `16891c6f138cc68ac2737720fcc6c972e92d86bb`
- manifest 95: `00667fe2899b1b938a0eb0d0566a2b9776ec2e3e`
- Server 2.3.154 authority: `d70c390757c4691d182f5ba3c6eddb27f0bae8ad`
- Web Chat 1.5.27 authority: `2b828613e11e8158d29a6ec85632da9b12194e7c`
- Web Frontend 1.0.4 authority: `1dd27c8c60c9b14f6f9d73cbcaba9e1418be1641`

## Deployment state

- Runtime-owned Web Chat/frontend changes: no Vercel deployment or restart required.
- Stable Python server transaction changes: source staged on `main`; production deployment is required before commit-before-generation becomes live.
- No production deployment was triggered by this event. Current `vercel.json` has Git deployment disabled and the manual production workflow only auto-triggers from `.deploy/REQUEST.txt`.

## Verification state

- Repository/source ownership and version-authority checks: complete.
- Runtime live-source verification: pending after manifest propagation/request.
- Stable canonical USER/ASSISTANT turn persistence: pending a separately authorized/manual production deployment and a signed-in test turn.
- Structured lifecycle log correlation: pending the same deployment/test.

## Phase 2 after stable deployment verification

Once the server transaction is proven in production, retire browser message writes as authority:

1. make server canonical messages the read/hydration source;
2. restrict browser state writes to explicitly allowed presentation/thread actions or server operations;
3. stop whole-state browser snapshots from replacing message history;
4. preserve localStorage only as a disposable cache/offline presentation surface;
5. add deletion/tombstone operations so stale clients cannot resurrect server-deleted state.

## Architecture result targeted

```text
MASK / browser
    -> relay text + factual IDs
HUMAN / server
    -> authenticate
    -> commit USER
    -> invoke/transport generation
    -> commit ASSISTANT terminal
BRAIN / LALM
    -> interpret/reason/generate
MASK
    -> render server truth
```
