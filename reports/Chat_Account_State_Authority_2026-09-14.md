# Chat Account State Authority — 2026-09-14

## Resulting lineage

- Overall Server Runtime authority: `2.3.148`
- Web Chat authority: `1.5.25`
- Runtime manifest: `94`
- Stable server capability: `api/chat_state.py` contract `swrlz-chat-account-state-v1`

## Change

Added a private, authenticated, account-scoped durable Chat state boundary backed by the existing connected Vercel Blob store. It is intentionally separate from generation transcript checkpoints. The durable record contains bounded thread/message presentation state; browser `localStorage` is retained only as a fast cache.

Added runtime client synchronization in `web/chat_account_state_sync_v1.js`. It authenticates through the existing server-verified account session cookie, hydrates remote state into the browser cache, merges thread/message IDs on conflicts, and pushes later local changes with optimistic revision checks. No Chat prompt interpretation or response cognition moved into the client.

Runtime manifest 94 publishes the synchronization asset in addition to the existing cooperative Chat loader.

## Deployment

The stable `api/chat_state.py` file requires one production Vercel deployment. User explicitly approved proceeding in the active Chat thread. Runtime assets themselves remain hot-runtime owned and do not require a restart.

## Verification plan

1. Deploy `main` through the approved production deployment gate.
2. Verify `/api/chat_state` is present and rejects unauthenticated reads with 401 rather than exposing state.
3. Verify `/api/account/status` remains healthy.
4. Verify runtime manifest reports version 94 and includes `web/chat_account_state_sync_v1.js`.
5. With an authenticated Chat session, create/send a turn, then load Chat in another authenticated browser and confirm the thread/message state hydrates from server authority.

## Rollback

Remove `web/chat_account_state_sync_v1.js` from the runtime manifest to disable client synchronization immediately without redeploying. The private server state endpoint can remain inert, or a later approved stable deployment can remove it. Existing local browser state is not destroyed by this release.
