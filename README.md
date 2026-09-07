# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.1.4**  
Chat revision: **1.3.0**  
Checkpoint lineage: `INT-VERCEL-CHAT-001A`

This repository is the unified §wyrlz Vercel SERVER. It preserves the R39 transport/runtime workbench, Dragon Jester Admin control plane, runtime-published `/live/*` workspace, and R299-derived web chat while adding a **truthful local R39 inference path**. A configured proof-bound upstream remains supported; when no upstream is configured Chat now routes to the local R39 reference engine instead of the former status-only dead end.

Included:
- unified FastAPI/Vercel entrypoint at `api/index.py`;
- preserved 2.1.3 runtime implementation in `api/server_v213.py` with a thin 2.1.4 release wrapper;
- `/api/health`, `/api/admin`, `/api/lalm`, `/api/chat`, and `/live/*`;
- exact repaired R39 size/SHA verification and Forge chunked transport reconstruction;
- ZIP-wrapper support for `lalm§wyrlz.zip` containing the verified R39 `.gz`;
- canonical SWRLZX v1 header/TOC parsing and section-bound validation;
- tokenizer, tensor-directory and tensor-data payload-location reconstruction;
- local R39 reference inference with BPE tokenization, LFM2 recurrent/GQA execution, quantized tensor readers, sampling, incremental UTF-8 decoding, cancellation, and NDJSON DELTA streaming;
- fail-closed graph/tensor/profile checks rather than synthetic output on incompatible artifacts;
- binary-safe Admin file manager/viewer/editor with chunked large-file upload/download;
- responsive Dragon Jester Admin dashboard and engineering control plane;
- browser-local chat threads, response evidence, trace export, retry/fork, context inspection, stream camera, thread search, generation controls, and Send to Workbench;
- strict `swrlz_llm_stream_v2` DELTA/RESET/terminal semantics;
- independent fail-closed `SWRLZ_WEB_CHAT_TOKEN` with runtime override support;
- Admin-authenticated runtime Chat-token set/change/generate/clear controls;
- optional proof-bound Android SERVER upstream headers injected only on the server side;
- runtime web publishing from `/tmp/swrlz-admin/web` to `/live/*` with safe path handling, MIME detection, index resolution, and no-store responses;
- Live Web manager, capability registry, health/release status, instance-change warnings, web snapshots/rollback, activity timeline, and promote manifests;
- `dev` branch deployment suppression so incremental work does not trigger Vercel production deployments.

## Runtime boundary

`api/index.py` is the authoritative Vercel entrypoint. Release 2.1.4 intentionally wraps the proven 2.1.3 Admin/runtime implementation in `api/server_v213.py`; this keeps the already-tested control plane intact while adding the local-R39 capability at the release boundary. `/api/chat` is mounted by that preserved base and extended by `api/chat_extensions.py`.

The proven R39 transport path remains:

`Forge chunks -> wrapper ZIP -> nested verified R39 gzip -> raw R39 -> SHA-256 -> Gate 5`

2.1.4 advances the compute path to:

`Gate 5 -> SWRLZX TOC -> TOKENIZER + TENSOR_DIRECTORY + TENSOR_DATA -> local reference executor -> NDJSON DELTA`

Authoritative raw R39 SHA-256:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

## Local R39 inference

`swyrlz/r39_inference.py` is the reference executor. It reconstructs active physical sections from the canonical 128-byte SWRLZX header and 128-byte TOC entries, maps each tensor through its declared `dataSectionId`, validates tensor ranges, and fails closed if the artifact does not match the supported LFM2 reference profile.

The current reference reader supports `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k` tensor storage used by the supplied R39 lineage. The executor preserves recurrent short-convolution state and GQA KV state across tokens, performs bounded local sampling, and decodes output through an incremental UTF-8 decoder so split multibyte sequences are not emitted incorrectly.

Readiness means the structural execution path is available. **It is not a latency claim.** Vercel cold-start, R39 reconstruction, Python/NumPy execution cost, and the 300-second function limit still need live deployment receipts. Any unsupported graph/tensor/profile state becomes an explicit FAILED event rather than fabricated assistant text.

## Chat routing and Truth Firewall

Chat routing is deterministic:

`complete proof-bound upstream configuration -> upstream proxy`

`no upstream URL -> local R39 reference inference`

`upstream URL present but required proof configuration incomplete -> explicit configuration failure`

Only `DELTA.text` may become assistant prose. STARTED, STATUS, ROUTE, RESET, timing, blockers, failures, model identity, and terminal metadata remain operational evidence. This invariant is enforced by the bridge extension before browser delivery.

## Admin workbench

Open `/api/admin`. Admin actions require `SWRLZ_ADMIN_TOKEN` through `x-swrlz-admin-token`. The workbench supports runtime state, R39 load/verify, Gate 5 execution, directory browsing, arbitrary binary upload, text editing, SHA-256, rename/delete, folder creation, runtime logs, chunked downloads, Live Web publishing, runtime Chat-token management, snapshots, rollback, activity receipts, capability discovery, health state, release receipts, and promote manifests.

The Admin page never reads secret Chat-token values back. A generated token is returned once to the authenticated Admin caller. Runtime Chat-token precedence is runtime override first, then deployment environment fallback.

## Runtime web workspace

Admin uploads and edits under `/tmp/swrlz-admin/web` are exposed through `/live/*`. Directory requests resolve `index.html`; paths are confined to the dedicated web root and served with no-store headers. Vercel `/tmp` remains ephemeral and instance-local, so durable accepted changes still belong in GitHub.

See `docs/contracts/SWRLZ_RUNTIME_WEB_WORKSPACE_V1.md` and `docs/contracts/SWRLZ_CONTROL_PLANES_V1.md`.

## Web chat configuration

Open `/api/chat`. Browser-to-Vercel auth is deliberately separate from Admin:

- `SWRLZ_WEB_CHAT_TOKEN` — browser Chat token;
- `/tmp/swrlz-admin/runtime/web-chat-token.txt` — optional runtime override;
- `SWRLZ_CHAT_UPSTREAM_URL` — optional reachable HTTPS SWRLZ SERVER gateway;
- `SWRLZ_CHAT_UPSTREAM_NODE_ID` — proof-bound CLIENT node ID when upstream mode is used;
- `SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF` — server-side proof when upstream mode is used;
- `SWRLZ_CHAT_UPSTREAM_BEARER` — optional gateway bearer;
- `SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS` — optional 10–290 second upstream idle timeout.

Chat 1.3.0 preserves the 1.2 control-plane UX and adds local R39 execution behind the same V2 stream contract. Upstream mode remains available and is still fully validated before any upstream DELTA is admitted.

## Development / release flow

Incremental source work occurs on `dev`. `vercel.json` disables Vercel deployments for that branch. `main` remains the deliberate production/release branch.

Runtime page iteration can bypass source deployment after the runtime-web release is live:

`Admin upload/edit -> /tmp/swrlz-admin/web -> /live/* -> refresh`

## Verification

Run:

```bash
python scripts/verify_vercel_chat.py
python scripts/verify_runtime_web.py
python scripts/verify_control_planes.py
python scripts/verify_r39_inference.py
```

The R39 verifier checks the release version, local/upstream route selection, Truth Firewall DELTA projection, canonical TOC parsing, data-section routing, supported quantizers, reference LFM2 profile, incremental UTF-8 decoding, Gate 5 payload reconstruction, and fail-closed behavior.

See:
- `SWRLZ_VERCEL_CHAT_README.md`;
- `SWRLZ_VERCEL_CHAT_CHANGELOG.md`;
- `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md`;
- `docs/contracts/SWRLZ_RUNTIME_WEB_WORKSPACE_V1.md`;
- `docs/contracts/SWRLZ_CONTROL_PLANES_V1.md`;
- `docs/checkpoints/INT-VERCEL-CHAT-001A_CHECKPOINT.md`.

## Revision history

2.0.5 unified the API runtime and colocated Gate 5 with R39 load/verify. 2.0.6 added response-safe chunked downloads. 2.0.7 hardened Admin token normalization and diagnostics. 2.1.0 added the R299-derived Vercel chat bridge/UI. 2.1.1 introduced the responsive Dragon Jester Admin dashboard. 2.1.2 added `/live/*`, runtime Chat-token override, and dev-branch deployment suppression. 2.1.3 turned Chat and Admin into paired control planes with evidence/fork/retry/context diagnostics, Live Web management, snapshots, activity receipts, and release/capability state. **2.1.4 / Chat 1.3.0 reconstructs canonical R39 payload locations and wires the local R39 reference executor into the Chat stream while preserving proof-bound upstream mode and the Truth Firewall.**
