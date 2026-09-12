# §wyrlz Unified Vercel Server

- Server revision: **2.3.79**
- Chat UI revision: **1.4.71**
- LALM UI revision: **1.0.0**
- Server UI revision: **1.0.0**
- Frozen Web Collector revision: **1.0.0**
- Production deployment: **https://swrlzkamico-o3nu.vercel.app**
- Checkpoint lineage: `FROZEN-WEB-COLLECTOR-001`

This branch is the durable live application source for the unified §wyrlz Vercel server. Server 2.3.79 adds the Frozen Web Snapshot Collector while preserving Chat 1.4.71 and LALM Engine 2.1.30.

## Control planes

- `/server/` — infrastructure, routing, deployment/base-version receipts, capabilities, and scoped hot-sync controls.
- `/lalm/` — R39/LALM model/runtime status, native-backend receipt, readiness, verification, and LALM-scoped hot sync.
- `/api/chat` — stable conversational client surface.
- `/api/admin` — Admin workbench.
- `/api/pages` — live page manager.
- `/collector` — Frozen Web Snapshot Collector browser control room.
- `/api/collector/*` — authenticated collector status, lifecycle, frozen search, document, and snapshot routes.
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

## Frozen Web Snapshot Collector

The collector implements the controlled pipeline:

`registered source → bounded fetch → extract/canonicalize/deduplicate → quality + provenance → chunks + lexical index → immutable frozen snapshot → explicit training review`

Private Vercel Blob owns durable state and snapshot artifacts. Raw HTML is discarded after extraction, `/tmp` is never authoritative, robots compliance is fixed on, and every training acceptance requires an explicit rights/provenance confirmation. The stable host is deployed once; `web/collector.html` and compatible `runtime_hot/web_snapshot_collector.py` revisions remain hot-updatable from `runtime`.

## Chat boundary

Chat is **1.4.71** for Server 2.3.79 and is unchanged by the collector event. Server/LALM/collector work that does not change the Chat protocol or user-facing behavior does not advance the Chat version.

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

GitHub `runtime` remains the durable source for hot-editable assets. Vercel `/tmp` state is instance-local and ephemeral; runtime loaders reconstruct compatible page and engine code from the durable branch after worker replacement or cold start.

## Development / release flow

Use `runtime` for ordinary page and LALM-runtime iteration. `vercel.json` disables Git-triggered deployment; the stable production workflow is separately approval-gated.

Promote to `main` only when the stable server boundary changes, including Python routes, auth/session behavior, middleware, native build configuration, or deployment contracts.

Server 2.3.79 installs the stable collector host. Routine compatible collector, Chat, page, and LALM runtime work remains on `runtime` without redeploy/restart.

## Versioning contract

Every server runtime development event receives a new overall Server version, including failed attempts. Every module actually changed in that event receives its own module-version increment. The roadmap/release record is updated in the same event.

Modules that display another module's version must obtain it from the owning module's authoritative status/version source rather than maintaining a second stale literal. Chat currently resolves Server from `/api/server/status` and LALM UI from `/api/lalm/status`.

Canonical roadmap: `docs/ROADMAP.md`  
Latest release record: `docs/releases/server-2.3.79-frozen-web-collector.md`

## Contracts and records

- `docs/contracts/SWRLZ_CONTROL_PLANES_V2.md`
- `docs/contracts/SWRLZ_LIVE_PAGE_RUNTIME_V1.md`
- `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md`
- `docs/contracts/SWRLZ_HOT_RUNTIME_V1.md`
- `docs/releases/SERVER_2.2.0.md`
- `docs/releases/SERVER_2.2.8.md`
- `docs/releases/server-2.3.79-frozen-web-collector.md`
- `docs/ROADMAP.md`
- `SWRLZ_VERCEL_CHAT_CHANGELOG.md`

## Revision history

2.3.79 adds Frozen Web Collector 1.0.0, private durable snapshot storage, explicit training review, and the hot-update collector boundary. Earlier release records remain preserved in `docs/releases/`.

## Collector deployment status

The `/collector` page is live, but its stable backend installation is blocked by missing GitHub Actions secret `VERCEL_TOKEN` in run 34708124306. No collector build, deployment, or storage provisioning ran. The release record contains the exact recovery step.
