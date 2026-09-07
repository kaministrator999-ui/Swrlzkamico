# §wyrlz Vercel SERVER Chat

Chat revision: **1.3.0**  
Unified SERVER revision: **2.1.4**  
Checkpoint lineage: `INT-VERCEL-CHAT-001A`  
Route: `/api/chat`

The web Chat surface runs on the same unified Vercel SERVER as Admin, R39 transport, `/api/lalm`, `/api/health`, file operations, Gate 5, and `/live/*`. Release 1.3.0 preserves the V2 streaming and presentation contract while adding a local R39 executor for deployments that do not use a proof-bound upstream.

## Architecture

`api/index.py` is the release entrypoint. SERVER 2.1.4 wraps the preserved 2.1.3 runtime in `api/server_v213.py`; that base mounts `api/chat.py` at `/api/chat`, while `api/chat_extensions.py` adds the 1.3.0 operational/control-plane extensions and local inference route.

The browser consumes `swrlz_llm_stream_v2` NDJSON. Only `DELTA.text` contributes assistant prose. `STARTED`, `STATUS`, `ROUTE`, `RESET`, failures, timing, identity, execution phases, and terminal metadata remain separate operational evidence.

Browser-local thread history is stored in `localStorage`. The browser Chat token is stored only in `sessionStorage`. Exports intentionally omit Chat/Admin tokens, upstream device proof, and optional bearer credentials.

## Security boundary

Browser Chat requests require `SWRLZ_WEB_CHAT_TOKEN`, independent of `SWRLZ_ADMIN_TOKEN`, sent as `x-swrlz-chat-token`. An authenticated Admin may place a runtime override at `/tmp/swrlz-admin/runtime/web-chat-token.txt`; environment configuration remains the fallback.

Optional proof-bound upstream variables:
- `SWRLZ_CHAT_UPSTREAM_URL`
- `SWRLZ_CHAT_UPSTREAM_NODE_ID`
- `SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF`
- `SWRLZ_CHAT_UPSTREAM_BEARER`
- `SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS`

Proof/bearer values are injected by the Vercel server only and are never returned to browser persistence.

## Local R39 mode

When no upstream URL is configured, the bridge reports/runs `LOCAL_R39`. Gate 5 and `swyrlz/r39_inference.py` reconstruct the active SWRLZX TOKENIZER, TENSOR_DIRECTORY, and TENSOR_DATA locations from the canonical TOC and map tensor descriptors through their declared data sections.

The reference executor supports the supplied LFM2 profile and its `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k` tensor storage. It performs BPE tokenization, recurrent short-convolution/GQA execution, sampling, cancellation checks, and incremental UTF-8 decoding. Generated text is emitted only as DELTA events.

If the R39 graph, required tensors, tokenizer, quantizer, section mapping, or physical ranges do not match the supported profile, local inference fails closed with an explicit code. No synthetic answer is substituted.

## Optional live upstream mode

When all proof-bound upstream settings are present, the bridge forwards the normalized request to the configured SWRLZ SERVER stream endpoint and validates every incoming event before forwarding it to the browser. Events must match protocol V2, the expected stream contract, increasing sequence numbers, the original request ID, known event types, and consistent terminal flags.

If an upstream URL is present but required proof configuration is incomplete, the request fails explicitly rather than silently falling back to another identity. Cancellation is forwarded upstream in upstream mode and arms the local runtime request in local mode.

## Truth Firewall

Only committed `DELTA.text` is answer text. `RESET` clears the current assistant revision. STARTED/STATUS/ROUTE/reasons/categories/errors/timing remain evidence. A FAILED or CANCELLED terminal event preserves any already committed DELTA text but does not merge failure diagnostics into prose.

## Browser features

The R299-derived page includes responsive desktop/mobile conversation layout, local thread creation/rename/pin/delete, message copy/bookmark, bounded context submission, live DELTA rendering, RESET handling, cancellation, evidence/trace export, R39 verification, runtime mode/instance evidence, retry/fork, context inspection, stream camera, generation controls, thread search, and Send to Workbench.

## Deployment truth

Source readiness is not deployment proof. After SERVER 2.1.4 is promoted/deployed, verify `/api/health`, `/api/chat?action=status`, the Chat Verify R39 action, and an actual streamed request. A successful live proof requires at least one valid local `ROUTE`/`DELTA` sequence or a valid upstream sequence under the selected route.

See `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md`, `SWRLZ_VERCEL_CHAT_CHANGELOG.md`, and `docs/checkpoints/INT-VERCEL-CHAT-001A_CHECKPOINT.md`.
