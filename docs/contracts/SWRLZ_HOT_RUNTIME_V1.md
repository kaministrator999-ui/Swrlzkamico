# SWRLZ Hot Runtime V1

Server revision: **2.1.7**  
Chat revision: **1.3.3**

## Purpose

Shorten the development loop for Chat presentation and R39 inference experiments without redeploying the stable Vercel server for every change.

## Stable deployment boundary

Deployment-controlled code remains authoritative for authentication, filesystem confinement, Admin authorization, the Chat stream contract, Truth Firewall semantics, routing, cancellation, and the bundled fallback implementation.

## Hot boundary

Authenticated Admin can call `POST /api/hot/sync?branch=dev`. The server fetches a fixed allowlist from the repository's non-deploying `dev` branch and atomically writes runtime copies under:

- `/tmp/swrlz-admin/runtime/hot/chat/`
- `/tmp/swrlz-admin/runtime/hot/inference/`

Current hot sources are Chat HTML/CSS/JS and `runtime_hot/r39_engine.py`.

Chat resolution is deterministic:

`runtime Chat override -> bundled Chat fallback`

Inference resolution is deterministic:

`runtime R39 engine override -> bundled R39 engine fallback`

The hot inference module must expose `ENGINE_ID`, `MODEL_SHA256`, `inspect_engine()`, and `generate_events()` or loading fails closed.

## Runtime controls

- `GET /api/hot` — small hot-runtime control page.
- `GET /api/hot/status` — current override status.
- `GET /api/hot/pages` — discovers live HTML pages in `/tmp/swrlz-admin/web`.
- `POST /api/hot/sync?branch=dev` — authenticated hot sync.
- `POST /api/hot/clear` — authenticated clear; immediately restores bundled fallback.
- `POST /api/hot/rollback?backupId=...` — authenticated runtime rollback.

## Temporary runtime index

`/live/` is generated as a temporary §wyrlz Runtime Index. It links Admin, Chat, Health, LALM, hot-runtime controls, and every additional `.html` file currently present under `/tmp/swrlz-admin/web`.

## Timeout semantics

`COMPUTE_HEARTBEAT` resets the response-idle interval after each real engine event/progress event and continues approximately every eight seconds while a blocking inference step is active. It can keep an idle stream alive but **does not reset Vercel's maximum function execution duration**.

## Durability

All `/tmp` hot state is instance-local and ephemeral. `dev` remains the durable hot source. A fresh runtime can resync from `dev`; deleting/clearing the override returns to the bundled deployment immediately.
