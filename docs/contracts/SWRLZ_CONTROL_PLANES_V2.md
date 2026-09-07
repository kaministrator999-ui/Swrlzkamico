# SWRLZ Control Planes V2

Server target: **2.2.0**

## Purpose

Server, LALM, and Chat are independent planes with explicit ownership. LALM/runtime work must not require Chat UI mutation.

## Server plane

Primary UI: `/server/`  
Status: `/api/server/status`  
Router: `/api/control/route` and `/route?client=...`

Owns deployment/base version, instance identity, routing, capability receipts, hot-sync controls, and links into Admin, LALM, and Chat.

## LALM plane

Primary UI: `/lalm/`  
Status: `/api/lalm/status`  
Verification: `POST /api/lalm/verify`

Owns R39 model identity, engine source/ID, hot runtime revision, native-backend availability, readiness, model-file presence, active inference streams, and LALM-scoped hot updates.

LALM hot sync:

`POST /api/control/hot/sync?scope=lalm&branch=dev`

The LALM scope may update only:

- `web/lalm.html`
- `runtime_hot/r39_engine.py`

It must return `chatTouched: false` and must not write Chat HTML/CSS/JS.

## Chat plane

Primary UI: `/api/chat`

Chat owns conversation/thread UX, request submission, NDJSON stream rendering, response reconnect, and the Truth Firewall. Chat is not the server dashboard and is not the model engineering dashboard.

R39 performance work, native-kernel work, model readiness work, and server routing work do not advance the Chat version unless the Chat protocol or user-facing Chat behavior itself changes.

## Authorization

Server/all scoped mutation requires Admin authorization. LALM-scoped hot sync and LALM verification may also accept a valid bounded signed browser Chat session presented through `x-swrlz-chat-session`. Permanent root secrets remain server-side.

## Storage and durability

Hot overrides are instance-local `/tmp` state and therefore ephemeral. GitHub `dev` remains the durable hot-source branch. Bundled files remain the fallback after instance replacement or hot clear.

## Deployment boundary

Server 2.2.0 must be deployed once to establish these routes and the scoped hot-sync contract. After that deployment, ordinary LALM engine/page iteration can use the LALM scope without redeploying the base server and without updating Chat.
