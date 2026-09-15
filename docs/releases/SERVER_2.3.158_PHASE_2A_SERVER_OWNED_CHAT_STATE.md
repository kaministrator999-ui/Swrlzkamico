# Server 2.3.158 — Phase 2A server-owned Chat state

**Status:** implementation complete in repository; runtime compatibility bridge live; stable API deployment pending explicit/manual action.

**Overall Server:** 2.3.158  
**Web Chat:** 1.5.28  
**Web Frontend:** 1.0.4 unchanged  
**Runtime manifest:** 96  
**Deployment:** NOT PERFORMED by this event  
**Restart:** NONE

## Goal

Move signed-in Web Chat from browser whole-snapshot authority to server-owned conversation state while preserving thread UX.

## Stable server changes

- Added `swrlz-chat-account-mutation-v1` to `/api/chat_state`.
- GET now advertises server state authority and retired snapshot-write authority.
- POST accepts bounded metadata mutations instead of browser message snapshots:
  - `UPSERT_THREAD`
  - `DELETE_THREAD`
  - `SET_CURRENT_THREAD`
  - `SET_MESSAGE_PINNED`
- Whole-state PUT now fails closed with `410 CHAT_STATE_SNAPSHOT_WRITE_RETIRED` after this stable API is deployed.
- Thread deletion creates bounded durable tombstones so stale clients cannot resurrect deleted conversation IDs.
- Canonical user/assistant commits preserve tombstones and reject turns targeting a tombstoned thread.

## Runtime Web Chat changes

`web/chat_account_state_sync_v1.js` now has two modes:

1. **Compatibility mode** — used while production still exposes the pre-Phase-2A state API. Existing merge/PUT behavior is retained so the live runtime update is safe before stable deployment.
2. **Server-authoritative mode** — activated only when GET advertises `swrlz-chat-account-mutation-v1`, `stateAuthority=server`, and `snapshotWriteAuthority=retired`.

In server-authoritative mode:

- remote state hydrates browser cache instead of merging browser messages upward;
- ordinary user/assistant/stream `saveState()` writes stay local cache only;
- thread create/rename/pin changes become `UPSERT_THREAD` commands;
- delete becomes `DELETE_THREAD`;
- thread selection becomes `SET_CURRENT_THREAD`;
- message bookmark state becomes `SET_MESSAGE_PINNED`;
- hydration defers while a local assistant message is actively streaming;
- mutation conflicts retry against the newest server revision;
- generation request identity attachment remains intact.

## Deletion semantics

Deletion tombstones are server-owned and kept outside the browser-visible state. Both the state mutation path and canonical-turn persistence preserve/enforce them. This prevents a stale browser snapshot or stale turn from recreating a deleted thread ID.

## Source lineage

Stable main:
- `1f3db794ca5ebda4ac07b6357c9901e12807ff9d` — server mutation API + tombstones + retire snapshot PUT
- `ae39d874e9ac0e15a9bf46e6b33416bea9940df5` — canonical turn tombstone preservation/enforcement

Runtime:
- `7cfd9569e120f4a9d1e98069a2457acdf3795403` — capability-gated server-authoritative account sync
- `7e2ddb3ad71a1039b97ab635295c4a65dda9e817` — manifest 96
- `87bb91cab20dcb090706866bfac5d0acc28dce14` — Server 2.3.158 authority
- `a8dd70681e5e47f8f60ce3b74deab98473bb6c8f` — Web Chat 1.5.28 authority

## Verification before deployment

- Required project-start, hotfix, version-evolution, roadmap, and Google OAuth/Chat auth runbook were re-read.
- Baseline authorities were captured as Server 2.3.157 / Web Chat 1.5.27 / Web Frontend 1.0.4 / manifest 95.
- Current deployment configuration still has Git deployment disabled; the manual workflow deploys only by explicit dispatch or approved `.deploy/REQUEST.txt` change.
- Python stable-source candidates were syntax-compiled before repository write.
- The runtime JavaScript candidate passed `node --check` before repository write.
- Authorities were re-read immediately before assignment and remained unchanged.
- Post-commit authorities confirm Server 2.3.158 / Web Chat 1.5.28 / manifest 96.

## Production acceptance after stable deployment

1. Refresh signed-in Chat and confirm runtime manifest 96.
2. GET `/api/chat_state` must advertise:
   - `mutationContract: swrlz-chat-account-mutation-v1`
   - `stateAuthority: server`
   - `snapshotWriteAuthority: retired`
3. Rename/pin/select a thread and confirm POST mutations advance canonical revision without any PUT snapshot.
4. Delete a test thread and confirm it remains deleted after refresh and from another stale/open tab.
5. Send a fresh message and confirm canonical turn lifecycle still passes exactly once.
6. Confirm browser message/stream `saveState()` activity does not produce whole-state PUTs.
7. Confirm assistant terminal persistence and server-canonical history remain intact.

## Known remaining limitation

The account state still uses a Blob snapshot with optimistic revision checks rather than a normalized append-only ledger with true storage-level compare-and-swap. Phase 2A removes browser authority and stale resurrection, but the longer-term SERVER-APK-style ledger/sequence/conflict model remains the stronger final storage architecture.
