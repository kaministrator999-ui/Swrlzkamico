# §wyrlz Server 2.1.9

## Purpose

Repair the first live-page deployment receipts from Server 2.1.8 without changing the hot-page source-of-truth model.

## Receipts that triggered this release

- `/api/health` reported Server 2.1.8 and `routingReady: true`.
- `/live/` returned `{"detail":"Not Found"}`.
- `/api/chat` loaded but did not show the Chat UI version receipt and still rendered stale sidebar status/dimming behavior.
- `/api/pages` loaded and authenticated successfully, but the UI did not clearly surface the server-side GitHub credential state after Admin authentication.

## Root causes and changes

1. `vercel.json` still rewrote `/live` and `/live/:path*` to the older mounted Chat live route. 2.1.9 removes those rewrites and registers `/live`, `/live/`, and `/live/{path}` directly on the unified parent FastAPI app.
2. Chat enhancement injection previously depended on middleware inside the mounted Chat sub-application. 2.1.9 adds a parent-boundary Chat UI guard for `GET /api/chat`, selects the hot runtime `chat.html` when present, and guarantees the enhancement CSS/JS references are injected exactly once.
3. The Page Manager now shows `ADMIN · AUTHENTICATED`, `GITHUB WRITE · CONFIGURED/NOT CONFIGURED`, and the `dev` source branch immediately after Admin authentication. The raw GitHub secret is never returned to the browser.

## Version lineage

- Server: 2.1.8 → 2.1.9
- Chat UI remains 1.3.4 for this repair. The planned 1.3.5 bump remains the end-to-end hot-update proof after 2.1.9 is live.
- `dev` remains deployment-disabled and remains the durable source for live-managed pages.

## Validation targets

1. `/api/health` reports `2.1.9`.
2. `/live/` renders the runtime index instead of a 404.
3. `/api/pages` + Admin token reports GitHub write configured when `SWRLZ_GITHUB_CONTENT_TOKEN` is present.
4. `SYNC DEV → RUNTIME` followed by `/api/chat` shows `CHAT v1.3.4 · SERVER v2.1.9` and applies the drawer/status enhancement layer.
5. Only after those receipts pass, change Chat 1.3.4 → 1.3.5 on `dev`, sync runtime, and verify Server remains 2.1.9 without a Vercel redeploy.
