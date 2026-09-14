# Chat Account State Route Correction — 2026-09-14

The first stable attempt created `api/chat_state.py` as a separate file-routed function. Production retained the project's two-function layout, so `/api/chat_state` remained 404. That failed attempt remains lineage as Server Runtime event 2.3.148.

Correction event: Server Runtime 2.3.149. `api/chat_state.py` was converted to an installable router and included by the existing stable `api/index.py` entrypoint. Web Chat remains 1.5.25 and runtime manifest remains 94.

Live production verification after deployment commit `30168f73bc6744fd8a13baa7a08b5f7e009e5826`:

- `/api/chat_state` returns `401 ACCOUNT_SESSION_INVALID` without an authenticated account session, proving the route exists and fails closed rather than exposing state.
- `/api/server/status` returns 200 and advertises `chat-account-state` ready=true, contract `swrlz-chat-account-state-v1`, access `private`, authority `server`, browserLocalStorageAuthoritative=false.
- `/live/manifest.json` returns revision 94 and publishes `web/chat_account_state_sync_v1.js`.
- `/live/assets/chat_account_state_sync_v1.js?v=94` returns 200 from `github-runtime` with immutable revisioned caching.
- Production deployment `dpl_3DboXSShdwbHPAnYgAmH8AXJ7vxc` is READY.

A later concurrent runtime event advanced the canonical overall Server Runtime authority beyond 2.3.149 after this correction was committed; this record preserves the event's own lineage rather than overwriting the newer authority.
