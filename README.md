# §wyrlz Unified Vercel Server

Server revision: **2.2.8**  
Chat UI revision: **1.4.3**  
LALM UI revision: **1.0.0**  
Server UI revision: **1.0.0**  
Production deployment: **https://swrlzkamico-o3nu.vercel.app**  
Checkpoint lineage: `INT-VERCEL-CHAT-001A`

This repository is the unified §wyrlz Vercel server. Server 2.2.8 preserves the split control planes and records the mobile Chat sidebar fix plus authoritative cross-module version display.

## Control planes

- `/server/` — infrastructure, routing, deployment/base-version receipts, capabilities, and scoped hot-sync controls.
- `/lalm/` — R39/LALM model/runtime status, native-backend receipt, readiness, verification, and LALM-scoped hot sync.
- `/api/chat` — stable conversational client surface.
- `/api/admin` — Admin workbench.
- `/api/pages` — live page manager.
- `/live/` — live launchpad/index.

Status/API receipts:

- `/api/server/status`
- `/api/lalm/status`
- `/api/chat/ops`
- `/api/health`
- `/api/control/route?client=chat|lalm|server|admin`

Browser routing helper:

- `/route?client=chat`
- `/route?client=lalm`
- `/route?client=server`
- `/route?client=admin`

## Scoped hot architecture

The legacy `/api/hot` route remains for compatibility. Server 2.2.0 added the preferred scoped control endpoint:

`POST /api/control/hot/sync?scope=<scope>&branch=dev`

Scopes:

- `lalm` — updates only `web/lalm.html` and `runtime_hot/r39_engine.py`.
- `server` — updates only `web/server.html`.
- `all` — updates Server + LALM control assets, still without touching Chat.

The LALM scope returns `chatTouched: false` by contract. Ordinary R39/native/prefill/decode iteration should use this path after 2.2.0 is deployed.

## Chat boundary

Chat is **1.4.3** for Server 2.2.8. The mobile sidebar fix changed user-facing Chat behavior, so Chat received its own version increment. Server/LALM work that does not change the Chat protocol or user-facing behavior does not advance the Chat version.

Chat owns:

- browser conversation/thread UX;
- request submission;
- NDJSON stream rendering;
- reconnect/replay behavior;
- response evidence and Truth Firewall enforcement;
- its own canonical Chat version source and cross-module version display.

Chat does not own Server deployment state or LALM engineering state.

## LALM / R39 runtime

The proven transport path remains:

`Forge chunks -> wrapper ZIP -> verified R39 gzip -> raw R39 -> SHA-256 -> runtime`

The compute path remains:

`SWRLZX TOC -> TOKENIZER + TENSOR_DIRECTORY + TENSOR_DATA -> R39 executor -> NDJSON DELTA`

Authoritative raw R39 SHA-256:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

The preferred production engine is `swrlz_r39_native_qmatvec_v1`, using compiled direct-quantized matvec kernels for `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k`. The Python/NumPy reference executor remains the correctness/fallback oracle.

`/api/lalm/status` is deliberately non-blocking and does not perform model verification merely to paint the LALM page. Explicit verification is owned by `POST /api/lalm/verify`.

## Authorization

`SWRLZ_WEB_CHAT_TOKEN` remains server-side. Same-origin Chat may use the bounded signed browser session established by the server. The permanent root Chat secret is not exposed to browser JavaScript.

Server/all scoped hot mutation requires Admin authorization. The LALM scope and LALM verification may also accept a valid signed browser Chat session supplied through `x-swrlz-chat-session`.

## Durable vs ephemeral state

GitHub `dev` remains the durable source for hot-editable assets. Vercel `/tmp` hot overrides are instance-local and ephemeral. Bundled source remains the fallback after worker replacement, runtime clear, or cold start.

## Development / release flow

Use `dev` for ordinary page and LALM-runtime iteration. `vercel.json` disables automatic deployment from `dev`.

Promote to `main` only when the stable server boundary changes, including Python routes, auth/session behavior, middleware, native build configuration, or deployment contracts.

Server 2.2.8 preserves the architecture deployment that established the split control planes and LALM-scoped hot-sync contract. Routine runtime application work remains on `runtime` without redeploy/restart.

## Versioning contract

Every server runtime development event receives a new overall Server version, including failed attempts. Every module actually changed in that event receives its own module-version increment. The roadmap/release record is updated in the same event.

Modules that display another module's version must obtain it from the owning module's authoritative status/version source rather than maintaining a second stale literal. Chat currently resolves Server from `/api/server/status` and LALM UI from `/api/lalm/status`.

Canonical roadmap: `docs/ROADMAP.md`  
Latest release record: `docs/releases/SERVER_2.2.8.md`

## Contracts and records

- `docs/contracts/SWRLZ_CONTROL_PLANES_V2.md`
- `docs/contracts/SWRLZ_LIVE_PAGE_RUNTIME_V1.md`
- `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md`
- `docs/contracts/SWRLZ_HOT_RUNTIME_V1.md`
- `docs/releases/SERVER_2.2.0.md`
- `docs/releases/SERVER_2.2.8.md`
- `docs/ROADMAP.md`
- `SWRLZ_VERCEL_CHAT_CHANGELOG.md`

## Revision history

2.2.8 records the mobile Chat sidebar stacking fix, advances Chat to 1.4.3 and Server to 2.2.8, and establishes authoritative cross-module version rendering. 2.2.0 established the split Server/LALM/Chat control planes and scoped LALM hot mutation.
