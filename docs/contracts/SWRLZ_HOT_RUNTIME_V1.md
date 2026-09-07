# SWRLZ Hot Runtime V1

Server revision: **2.1.17**  
Chat revision: **1.3.13**

## Purpose

Shorten the development loop for Chat presentation and R39 inference experiments without redeploying the stable Vercel server for every change and without requiring a manual Hot Sync button press for normal operation.

## Stable deployment boundary

Deployment-controlled code remains authoritative for authentication, filesystem confinement, Admin authorization, the Chat stream contract, Truth Firewall semantics, routing, cancellation, the hot-loader contract, and bundled fallback implementations.

A server redeploy is still required when this stable boundary itself changes. Server 2.1.17 is the one-time boundary change that enables automatic hot hydration.

## Durable hot source

GitHub `dev` is the durable source of truth for the fixed hot allowlist:

- `web/chat.html`
- `web/chat_enhancements.css`
- `web/chat_enhancements.js`
- `runtime_hot/r39_engine.py`

Runtime copies live under:

- `/tmp/swrlz-admin/runtime/hot/chat/`
- `/tmp/swrlz-admin/runtime/hot/inference/`

`/tmp` remains only an instance-local cache. It is never the durable source.

## Automatic hydration / refresh

Hot reads are request-driven. The stable loader registers a server-owned refresher and checks it before resolving Chat assets or the R39 engine.

The policy is:

`active request -> refresh if due -> compare SHA-256 -> atomically replace changed allowlisted files -> invalidate R39 module only when engine changed -> serve runtime override`

If a fresh Vercel instance has no `/tmp` hot state, its first active Chat/R39 request hydrates from `dev` automatically. While the instance remains active, refresh checks are throttled to approximately **30 seconds** so multiple simultaneous page asset requests do not each fetch GitHub independently.

If GitHub/network refresh fails, the request path does not fail solely because the hot plane is unavailable. Existing hot files remain usable, or resolution falls back to the bundled deployment.

Chat resolution:

`current dev-derived runtime Chat override -> bundled Chat fallback`

Inference resolution:

`current dev-derived runtime R39 engine override -> bundled R39 engine fallback`

The hot inference module must expose `ENGINE_ID`, `MODEL_SHA256`, `inspect_engine()`, and `generate_events()` or loading fails closed.

## Manual controls

Manual Hot Sync is retained as a force-refresh/recovery control, not the normal update path.

- `GET /api/hot` — hot-runtime control/status page.
- `GET /api/hot/status` — override state plus auto-refresh receipts.
- `GET /api/hot/pages` — discovers live HTML pages in `/tmp/swrlz-admin/web`.
- `POST /api/hot/sync?branch=dev` — authenticated force sync; also resumes auto refresh after a clear/rollback suspension.
- `POST /api/hot/clear` — authenticated clear and suspend auto refresh so bundled fallback can be held intentionally.
- `POST /api/hot/rollback?backupId=...` — authenticated rollback and suspend auto refresh so the restored snapshot is not immediately overwritten.

## Temporary runtime index

`/live/` is generated as a temporary §wyrlz Runtime Index. It links Admin, Chat, Health, LALM, hot-runtime controls, and every additional `.html` file currently present under `/tmp/swrlz-admin/web`.

## Timeout semantics

`COMPUTE_HEARTBEAT` resets the response-idle interval after each real engine event/progress event and continues approximately every eight seconds while a blocking inference step is active. It can keep an idle stream alive but **does not reset Vercel's maximum function execution duration**.

## Durability

A redeploy or cold instance may erase `/tmp`, but normal operation rehydrates the hot allowlist from `dev` automatically. Therefore the expected lifecycle is:

`redeploy/cold start -> empty /tmp -> first active hot read -> automatic dev hydration -> runtime override active`

No manual button press is required in the normal path after Server 2.1.17 is deployed.
