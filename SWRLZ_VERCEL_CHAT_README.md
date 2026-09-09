# §wyrlz Vercel SERVER Chat

Stable Chat revision: **1.3.26**
Chat review candidate: **1.4.0-rc.1**
Unified SERVER source baseline: **2.2.7**
Checkpoint lineage: `INT-VERCEL-CHAT-001A` → `SWRLZ-WEB-KNOWLEDGE-001A`
Route: `/api/chat`

The web Chat surface runs on the same unified Vercel SERVER as Admin, R39 transport, `/api/lalm`, `/api/health`, file operations, Gate 5, and `/live/*`. The stable offline path keeps the V2 streaming/Truth Firewall contract. The 1.4.0 review candidate adds explicit, disabled-by-default Online Evidence through a compatible V3 extension; it is source-ready only and is not a deployment claim.

## Online Evidence candidate

The composer keeps execution route and knowledge mode separate. `OFFLINE` is the default and sends the existing V2 payload. `ONLINE` requires V3 and composes local R39 with remote web evidence under the `LOCAL_R39+REMOTE_WEB_EVIDENCE` route identity.

The server derives a redacted query from the current prompt only, never the full thread; validates and pins public HTTPS targets; emits sources as non-prose `SOURCE` events; and attaches a request-scoped lineage receipt. Retrieved material is not persisted or training-eligible. No live provider adapter is registered in this checkpoint, so Online requests fail explicitly until a separately approved provider is installed and enabled.

See `docs/contracts/SWRLZ_ONLINE_EVIDENCE_V1.md`, `docs/contracts/SWRLZ_LLM_STREAM_V3.md`, and `docs/data/SWRLZ_ONLINE_KNOWLEDGE_DATA_POLICY_V1.md`.

## Architecture

`api/index.py` is the release entrypoint. SERVER 2.2.7 keeps the preserved 2.1.3 runtime in `api/server_v213.py`; that base mounts `api/chat.py` at `/api/chat`, while `api/chat_extensions.py` adds local inference, runtime evidence, automatic readiness, heartbeat-protected streaming, and the candidate Online Evidence orchestration.

The browser consumes `swrlz_llm_stream_v2` for Offline Chat and `swrlz_llm_stream_v3` only for explicit Online Evidence. Only `DELTA.text` contributes assistant prose. `STARTED`, `STATUS`, `ROUTE`, `SOURCE`, `RESET`, failures, timing, identity, execution phases, compute heartbeats, receipts, and terminal metadata remain separate operational evidence.

Browser-local thread history is stored in `localStorage`. The browser Chat token is stored only in `sessionStorage`. Exports intentionally omit Chat/Admin tokens, upstream device proof, and optional bearer credentials.

## Local R39 mode

When no upstream URL is configured, the bridge reports/runs `LOCAL_R39`. The local engine reconstructs active SWRLZX TOKENIZER, TENSOR_DIRECTORY, and TENSOR_DATA locations and maps tensor descriptors through their declared data sections.

The unified server automatically initializes/probes the local R39 engine once per fresh runtime instance. Manual Admin LOAD / VERIFY and Gate 5 controls remain useful diagnostics/recovery tools, but they are no longer intended as required steps before Chat use.

Long blocking local compute stages are advanced on one worker while the bridge emits periodic `COMPUTE_HEARTBEAT` STATUS events. This preserves the response connection during expensive prefill/generation gaps without placing operational text into the assistant response.

The reference executor supports the supplied LFM2 profile and its `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k` storage. It performs BPE tokenization, recurrent short-convolution/GQA execution, sampling, cancellation checks, and incremental UTF-8 decoding. Generated text is emitted only as DELTA events.

## Optional upstream mode

When all proof-bound upstream settings are present, the bridge forwards the normalized request to the configured SWRLZ SERVER endpoint and validates every incoming event. If an upstream URL is present but proof configuration is incomplete, the request fails explicitly rather than silently changing identity.

## Browser features

The R299-derived page includes responsive desktop/mobile conversation layout, browser-local threads, live DELTA rendering, RESET handling, cancellation, evidence/trace export, R39 verification, runtime mode/instance evidence, retry/fork, context inspection, generation controls, thread search, and Send to Workbench.

Chat 1.3.2 specifically repairs **New Conversation** and **Delete Conversation**, adds **COPY TEXT** and **CLEAR CAMERA** to Stream Camera, paints verified `LOCAL_R39` state as ready rather than perpetually amber, preserves the compact mobile TOOLS row, and separates the mobile drawer from its dimming backdrop so the drawer itself stays full brightness.

## Security boundary

Browser Chat requests require `SWRLZ_WEB_CHAT_TOKEN`, independent of `SWRLZ_ADMIN_TOKEN`, sent as `x-swrlz-chat-token`. An authenticated Admin may place a runtime override at `/tmp/swrlz-admin/runtime/web-chat-token.txt`; environment configuration remains the fallback.

Optional proof-bound upstream variables:
- `SWRLZ_CHAT_UPSTREAM_URL`
- `SWRLZ_CHAT_UPSTREAM_NODE_ID`
- `SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF`
- `SWRLZ_CHAT_UPSTREAM_BEARER`
- `SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS`

Proof/bearer values are injected by the Vercel server only and are never returned to browser persistence.

## Truth Firewall

Only committed `DELTA.text` is answer text. `RESET` clears the current assistant revision. STARTED/STATUS/ROUTE/reasons/categories/errors/timing/heartbeats remain evidence. FAILED or CANCELLED preserves any already committed DELTA text without merging diagnostics into prose.

## Deployment truth

Source readiness is not deployment proof. This review branch has not been merged or deployed. Backend V3 support must be promoted and verified before the GitHub `dev` live UI is allowed to offer Online Evidence. Provider selection, replay/persistence behavior, credentials, quotas, rights, and live verification remain separate approval gates.
