# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.1.7**  
Chat revision: **1.3.3**  
Checkpoint lineage: `INT-VERCEL-CHAT-001A`

This repository is the unified §wyrlz Vercel SERVER. It preserves the R39 transport/runtime workbench, Dragon Jester Admin control plane, runtime-published `/live/*` workspace, and R299-derived web chat while adding a truthful local R39 inference path. A configured proof-bound upstream remains supported; when no upstream is configured Chat routes to the local R39 reference engine.

Included:
- unified FastAPI/Vercel entrypoint at `api/index.py`;
- preserved 2.1.3 runtime implementation in `api/server_v213.py` behind the thin release wrapper;
- `/api/health`, `/api/admin`, `/api/lalm`, `/api/chat`, `/api/hot`, and `/live/*`;
- exact repaired R39 size/SHA verification and Forge chunked transport reconstruction;
- canonical SWRLZX v1 header/TOC parsing and section-bound validation;
- tokenizer, tensor-directory and tensor-data payload-location reconstruction;
- local R39 reference inference with BPE tokenization, recurrent/GQA execution, quantized tensor readers, sampling, incremental UTF-8 decoding, cancellation, and NDJSON DELTA streaming;
- automatic instance-local R39 readiness initialization on first local status/use, so manual LOAD / VERIFY and Gate 5 are diagnostics rather than required chat startup steps;
- periodic compute-heartbeat STATUS events while blocking local inference work is running, with the idle heartbeat interval restarting after each real progress event;
- hot-swappable Chat HTML/CSS/JS and R39 runtime engine override loaded from instance-local `/tmp` with deterministic bundled fallback;
- authenticated hot sync from the non-deploying `dev` branch, plus clear and rollback controls;
- temporary `/live/` Runtime Index that discovers links to every additional live HTML page on the current instance;
- fail-closed graph/tensor/profile checks rather than synthetic output on incompatible artifacts;
- browser-local chat threads, response evidence, trace export, retry/fork, context inspection, stream camera with COPY TEXT/CLEAR, thread search, generation controls, and Send to Workbench;
- compact mobile TOOLS UI and runtime status paint for LOCAL_R39 readiness;
- strict `swrlz_llm_stream_v2` DELTA/RESET/terminal semantics;
- independent fail-closed `SWRLZ_WEB_CHAT_TOKEN` with runtime override support;
- Admin-authenticated runtime Chat-token set/change/generate/clear controls;
- optional proof-bound Android SERVER upstream headers injected only on the server side;
- runtime web publishing from `/tmp/swrlz-admin/web` to `/live/*`;
- Live Web manager, capability registry, health/release status, instance-change warnings, web snapshots/rollback, activity timeline, and promote manifests;
- `dev` branch deployment suppression so incremental work does not trigger Vercel production deployments.

## Runtime boundary

`api/index.py` is the authoritative Vercel entrypoint. Release 2.1.7 keeps authentication, routing, filesystem confinement, Admin authorization, the Chat stream contract, and the bundled fallback implementation deployment-controlled. `/api/chat` remains mounted by the preserved base and extended by `api/chat_extensions.py`.

The proven R39 transport path remains:

`Forge chunks -> wrapper ZIP -> nested verified R39 gzip -> raw R39 -> SHA-256 -> Gate 5`

The compute path remains:

`SWRLZX TOC -> TOKENIZER + TENSOR_DIRECTORY + TENSOR_DATA -> local executor -> NDJSON DELTA`

Authoritative raw R39 SHA-256:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

## Local R39 inference

`swyrlz/r39_inference.py` remains the bundled reference executor. It reconstructs active physical sections from the canonical SWRLZX header/TOC, maps tensors through their declared `dataSectionId`, validates physical ranges, and fails closed if the artifact does not match the supported LFM2 reference profile.

The reader supports `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k` storage used by this lineage. The executor preserves recurrent short-convolution and GQA KV state, performs bounded local sampling, and decodes output incrementally.

Long local compute stages are wrapped by the Chat bridge with heartbeat STATUS events while the blocking model generator advances on a worker. The heartbeat timer restarts after every actual engine event/progress event. This protects the idle stream, but does not reset Vercel's hard maximum function duration.

## Hot runtime development

Release 2.1.7 adds a narrow runtime-development boundary so UI and LALM experiments no longer require a full SERVER redeploy each iteration.

Authenticated sync:

`POST /api/hot/sync?branch=dev`

copies the approved Chat frontend and hot R39 engine entrypoint from the non-deploying `dev` branch into:

- `/tmp/swrlz-admin/runtime/hot/chat/`
- `/tmp/swrlz-admin/runtime/hot/inference/`

Resolution is deterministic:

`runtime Chat override -> bundled Chat fallback`

`runtime R39 engine override -> bundled R39 fallback`

The hot engine contract is intentionally narrow: `ENGINE_ID`, `MODEL_SHA256`, `inspect_engine()`, and `generate_events()`. Runtime clear or a missing override immediately restores the deployed implementation. `/api/hot` provides a temporary control surface and `/live/` provides the temporary Runtime Index.

## Chat routing and Truth Firewall

Routing is deterministic:

`complete proof-bound upstream configuration -> upstream proxy`

`no upstream URL -> local R39 inference`

`upstream URL present but proof configuration incomplete -> explicit configuration failure`

Only `DELTA.text` may become assistant prose. STARTED, STATUS, ROUTE, RESET, timing, blockers, failures, model identity, heartbeats, and terminal metadata remain operational evidence.

## Admin workbench

Open `/api/admin`. Admin actions require `SWRLZ_ADMIN_TOKEN` through `x-swrlz-admin-token`. The workbench supports runtime state, R39 load/verify, Gate 5 execution, file management, runtime logs, Live Web publishing, runtime Chat-token management, snapshots, rollback, activity receipts, capability discovery, health state, release receipts, and promote manifests.

Hot-runtime controls use the same Admin authorization boundary through `/api/hot` and `/api/hot/*`. The Admin token is never stored in the runtime index beyond browser `sessionStorage`.

## Runtime web workspace

Admin uploads and edits under `/tmp/swrlz-admin/web` are exposed through `/live/*`. The generated `/live/` index discovers every other `.html` page currently present under that root and links the core Admin, Chat, Health, LALM, and hot-runtime surfaces.

Vercel `/tmp` remains ephemeral and instance-local, so durable accepted changes still belong in GitHub. `dev` is the durable hot source; `main` remains the deliberate deployment branch.

## Web chat configuration

Open `/api/chat`. Browser-to-Vercel auth is separate from Admin:

- `SWRLZ_WEB_CHAT_TOKEN` — browser Chat token;
- `/tmp/swrlz-admin/runtime/web-chat-token.txt` — optional runtime override;
- `SWRLZ_CHAT_UPSTREAM_URL` — optional reachable HTTPS SWRLZ SERVER gateway;
- `SWRLZ_CHAT_UPSTREAM_NODE_ID` — proof-bound CLIENT node ID when upstream mode is used;
- `SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF` — server-side proof when upstream mode is used;
- `SWRLZ_CHAT_UPSTREAM_BEARER` — optional gateway bearer;
- `SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS` — optional 10–290 second upstream idle timeout.

Chat 1.3.3 preserves LOCAL_R39 streaming while allowing runtime UI and inference overrides to be selected without weakening the Truth Firewall or upstream proof boundary.

## Development / release flow

Normal source work occurs on `dev`. `vercel.json` disables Vercel deployments for that branch. For hot-safe files, Admin may sync `dev` directly into `/tmp` and test immediately. Stable SERVER changes are still verified and promoted once to `main` for production deployment.

## Verification

Run:

```bash
python scripts/verify_vercel_chat.py
python scripts/verify_runtime_web.py
python scripts/verify_control_planes.py
python scripts/verify_r39_inference.py
python scripts/verify_hot_runtime.py
```

See `docs/contracts/SWRLZ_HOT_RUNTIME_V1.md` for the hot boundary.

## Revision history

2.0.5 unified the API runtime and colocated Gate 5 with R39 load/verify. 2.0.6 added response-safe chunked downloads. 2.0.7 hardened Admin token normalization and diagnostics. 2.1.0 added the R299-derived Vercel chat bridge/UI. 2.1.1 introduced the responsive Dragon Jester Admin dashboard. 2.1.2 added `/live/*`, runtime Chat-token override, and dev-branch deployment suppression. 2.1.3 turned Chat and Admin into paired control planes. 2.1.4 / Chat 1.3.0 wired local R39 inference. 2.1.5 / Chat 1.3.1 resolved producer-specific BPE tokenizer labels and cleaned up the mobile tools bar. 2.1.6 / Chat 1.3.2 added automatic R39 initialization and heartbeat-protected local streaming. **2.1.7 / Chat 1.3.3 adds the hot Chat/R39 runtime override boundary, authenticated dev-branch sync/rollback, and the temporary live runtime index.**
