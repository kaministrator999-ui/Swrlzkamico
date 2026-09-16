# Server 2.3.187 — Chat Activity + Refresh Convergence

## Versions
- Server Runtime: 2.3.187
- Web Chat: 1.5.46
- Runtime manifest: 111

## Runtime changes
- Activity log expansion/collapse now owns the summary activation synchronously. The client prevents the native default, flips the details state once, and persists that exact user choice. This removes the fast-tap/native-toggle/rerender race.
- Removed `chat_transcript_sync.js` from the cooperative functional loader. Production logs showed repeated `POST /api/chat/transcript` 404 responses while this obsolete strict client was active. Current canonical account-state synchronization and bounded terminal transcript recovery remain loaded.
- Online research default-on behavior from the preceding release remains unchanged.

## Stable refresh-convergence correction staged on main
- `api/live_source_guard.py` reduced worker-local authoritative runtime-manifest caching from 60 seconds to 2 seconds.
- Root cause: the manifest revision is the cache-busting key for runtime JS/CSS. A worker retaining the prior manifest for 60 seconds can legitimately serve an old revision after a runtime update, causing repeated refreshes to land on old/new revisions depending on worker/cache age.
- Git deployment is disabled, so the main commit does not deploy automatically. The stable correction requires a separately approved production deployment before it affects production.

## Evidence
- Current stable source advertises manifest-versioned immutable assets and a GitHub contents manifest authority.
- Production runtime logs showed repeated `/api/chat/transcript` 404 requests in a tight burst during Chat use.
- Browser standards define `<details>` toggle notifications as asynchronous/coalesced; the user-owned click path avoids using that delayed notification as state authority.

## Deployment state
- Runtime changes: runtime-hot; no deployment or restart requested.
- Stable manifest-cache correction: committed/staged on main only; NOT deployed pending explicit deployment approval.
