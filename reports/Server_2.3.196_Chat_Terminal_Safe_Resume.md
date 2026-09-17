# Server 2.3.196 — Chat terminal-safe resume

- Overall Server: 2.3.196
- Web Chat: 1.5.50
- Runtime manifest: 115
- Deployment: none; runtime-hot event

## Evidence / reason
Production evidence for the 2026-09-16 19:10 local Chat turn showed visible assistant output followed by repeated reconnect/same-request activity. The prior continuity client intentionally cancelled a healthy stream on foreground, pageshow, and online events. That behavior could reopen the same request while canonical Redis/account reconciliation was still settling.

## Change
Added `web/chat_background_resume_v3.js` and load it before the cooperative runtime loader. It claims the legacy continuity install guard so the older foreground-cancellation implementation does not own the stream. Resume now occurs only after an actual stream interruption/EOF, preserves the exact original request payload for retries, ignores replayed sequence numbers, and treats complete/failed/cancelled terminal state as irreversible.

Server 2.3.195 remains the preceding event and supplies Redis-authoritative terminal reconciliation, timestamped Activity entries, and the canonical §wyrlz sigil UI contract.

## Verification state
Repository/source verification complete. Live browser verification pending a fresh Chat reload/request. No Vercel deployment or restart is required for this runtime-owned change.
