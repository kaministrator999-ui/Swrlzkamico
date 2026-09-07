# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.1.6**  
Chat revision: **1.3.2**  
Checkpoint lineage: `INT-VERCEL-CHAT-001A`

This repository is the unified §wyrlz Vercel SERVER. It preserves the R39 transport/runtime workbench, Dragon Jester Admin control plane, runtime-published `/live/*` workspace, and R299-derived web chat while adding a truthful local R39 inference path. A configured proof-bound upstream remains supported; when no upstream is configured Chat routes to the local R39 reference engine.

Included:
- unified FastAPI/Vercel entrypoint at `api/index.py`;
- preserved 2.1.3 runtime implementation in `api/server_v213.py` behind the thin release wrapper;
- `/api/health`, `/api/admin`, `/api/lalm`, `/api/chat`, and `/live/*`;
- exact repaired R39 size/SHA verification and Forge chunked transport reconstruction;
- canonical SWRLZX v1 header/TOC parsing and section-bound validation;
- tokenizer, tensor-directory and tensor-data payload-location reconstruction;
- local R39 reference inference with BPE tokenization, recurrent/GQA execution, quantized tensor readers, sampling, incremental UTF-8 decoding, cancellation, and NDJSON DELTA streaming;
- automatic instance-local R39 readiness initialization on first local status/use, so manual LOAD / VERIFY and Gate 5 are diagnostics rather than required chat startup steps;
- periodic compute-heartbeat STATUS events while blocking local inference work is running, preventing long prefill/generation gaps from looking like an idle stream;
- fail-closed graph/tensor/profile checks rather than synthetic output on incompatible artifacts;
- browser-local chat threads, repaired New Conversation/delete controls, response evidence, trace export, retry/fork, context inspection, stream camera with COPY TEXT/CLEAR, thread search, generation controls, and Send to Workbench;
- compact mobile TOOLS UI and corrected sidebar layering so the background is dimmed without dimming the drawer itself;
- runtime status paint that promotes LOCAL_R39 readiness from amber to ready when the local engine is verified;
- strict `swrlz_llm_stream_v2` DELTA/RESET/terminal semantics;
- independent fail-closed `SWRLZ_WEB_CHAT_TOKEN` with runtime override support;
- Admin-authenticated runtime Chat-token set/change/generate/clear controls;
- optional proof-bound Android SERVER upstream headers injected only on the server side;
- runtime web publishing from `/tmp/swrlz-admin/web` to `/live/*`;
- Live Web manager, capability registry, health/release status, instance-change warnings, web snapshots/rollback, activity timeline, and promote manifests;
- `dev` branch deployment suppression so incremental work does not trigger Vercel production deployments.

## Runtime boundary

`api/index.py` is the authoritative Vercel entrypoint. Release 2.1.6 keeps the proven Admin/runtime implementation isolated in `api/server_v213.py`; `/api/chat` is mounted by that preserved base and extended by `api/chat_extensions.py`.

The proven R39 transport path remains:

`Forge chunks -> wrapper ZIP -> nested verified R39 gzip -> raw R39 -> SHA-256 -> Gate 5`

The compute path is:

`SWRLZX TOC -> TOKENIZER + TENSOR_DIRECTORY + TENSOR_DATA -> local reference executor -> NDJSON DELTA`

Authoritative raw R39 SHA-256:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

## Local R39 inference

`swyrlz/r39_inference.py` is the reference executor. It reconstructs active physical sections from the canonical SWRLZX header/TOC, maps tensors through their declared `dataSectionId`, validates physical ranges, and fails closed if the artifact does not match the supported LFM2 reference profile.

The reader supports `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k` storage used by this lineage. The executor preserves recurrent short-convolution and GQA KV state, performs bounded local sampling, and decodes output incrementally.

Release 2.1.6 automatically probes/initializes the local engine once per fresh runtime instance. Opening Chat/status can therefore reconstruct and validate R39 without requiring the operator to press Admin LOAD / VERIFY or Gate 5 first. Those Admin controls remain explicit diagnostics/recovery tools.

Long local compute stages are wrapped by the Chat bridge with heartbeat STATUS events while the blocking model generator advances on a worker. This keeps the NDJSON connection active during expensive prefill/generation work without converting operational status into assistant prose.

## Chat routing and Truth Firewall

Routing is deterministic:

`complete proof-bound upstream configuration -> upstream proxy`

`no upstream URL -> local R39 reference inference`

`upstream URL present but proof configuration incomplete -> explicit configuration failure`

Only `DELTA.text` may become assistant prose. STARTED, STATUS, ROUTE, RESET, timing, blockers, failures, model identity, heartbeats, and terminal metadata remain operational evidence.

## Admin workbench

Open `/api/admin`. Admin actions require `SWRLZ_ADMIN_TOKEN` through `x-swrlz-admin-token`. The workbench supports runtime state, R39 load/verify, Gate 5 execution, file management, runtime logs, Live Web publishing, runtime Chat-token management, snapshots, rollback, activity receipts, capability discovery, health state, release receipts, and promote manifests.

The Admin page never reads secret Chat-token values back. A generated token is returned once to the authenticated Admin caller. Runtime Chat-token precedence is runtime override first, then deployment environment fallback.

## Runtime web workspace

Admin uploads and edits under `/tmp/swrlz-admin/web` are exposed through `/live/*`. Vercel `/tmp` remains ephemeral and instance-local, so durable accepted changes still belong in GitHub.

## Web chat configuration

Open `/api/chat`. Browser-to-Vercel auth is separate from Admin:

- `SWRLZ_WEB_CHAT_TOKEN` — browser Chat token;
- `/tmp/swrlz-admin/runtime/web-chat-token.txt` — optional runtime override;
- `SWRLZ_CHAT_UPSTREAM_URL` — optional reachable HTTPS SWRLZ SERVER gateway;
- `SWRLZ_CHAT_UPSTREAM_NODE_ID` — proof-bound CLIENT node ID when upstream mode is used;
- `SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF` — server-side proof when upstream mode is used;
- `SWRLZ_CHAT_UPSTREAM_BEARER` — optional gateway bearer;
- `SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS` — optional 10–290 second upstream idle timeout.

Chat 1.3.2 keeps the 1.3 local-R39 path while repairing browser-local thread creation/deletion, adding Stream Camera copy/clear controls, correcting ready-state paint, improving mobile drawer layering, and emitting compute-heartbeat status during long local inference gaps.

## Development / release flow

Incremental source work occurs on `dev`. `vercel.json` disables Vercel deployments for that branch. `main` remains the deliberate production/release branch.

## Verification

Run:

```bash
python scripts/verify_vercel_chat.py
python scripts/verify_runtime_web.py
python scripts/verify_control_planes.py
python scripts/verify_r39_inference.py
```

## Revision history

2.0.5 unified the API runtime and colocated Gate 5 with R39 load/verify. 2.0.6 added response-safe chunked downloads. 2.0.7 hardened Admin token normalization and diagnostics. 2.1.0 added the R299-derived Vercel chat bridge/UI. 2.1.1 introduced the responsive Dragon Jester Admin dashboard. 2.1.2 added `/live/*`, runtime Chat-token override, and dev-branch deployment suppression. 2.1.3 turned Chat and Admin into paired control planes. 2.1.4 / Chat 1.3.0 wired local R39 inference. 2.1.5 / Chat 1.3.1 resolved producer-specific BPE tokenizer labels and cleaned up the mobile tools bar. **2.1.6 / Chat 1.3.2 adds automatic per-instance R39 initialization, heartbeat-protected local streaming, repaired New/Delete thread controls, Stream Camera copy/clear, ready-state paint, and corrected mobile drawer dimming.**
