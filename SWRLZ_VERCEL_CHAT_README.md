# §wyrlz Vercel SERVER Chat

Chat revision: **1.0.0**  
Unified SERVER revision: **2.1.0**  
Checkpoint: `INT-VERCEL-CHAT-001A`  
Route: `/api/chat`

This integration adds a responsive web chat surface to the proven SERVER 2.0.7 runtime without replacing Admin, R39 transport, `/api/lalm`, `/api/health`, file operations, or Gate 5.

## Architecture

`api/index.py` remains the single Vercel FastAPI entrypoint and mounts `api/chat.py` at `/api/chat`. `web/chat.html` is served by that mounted application.

The browser consumes the `swrlz_llm_stream_v2` NDJSON contract. Only `DELTA` contributes assistant prose. `STATUS`, `ROUTE`, `RESET`, failures, timing, and execution phases remain separate UI state. This prevents operational chatter from being silently blended into model output.

Browser-local thread history is stored in `localStorage`. The browser chat token is stored only in `sessionStorage`. Conversation exports intentionally omit the access token, upstream device proof, and optional bearer credentials.

## Security boundary

Required for browser chat requests:

`SWRLZ_WEB_CHAT_TOKEN`

This secret is independent of `SWRLZ_ADMIN_TOKEN`. Browser requests send it as `x-swrlz-chat-token`.

Optional proof-bound upstream variables:

- `SWRLZ_CHAT_UPSTREAM_URL`
- `SWRLZ_CHAT_UPSTREAM_NODE_ID`
- `SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF`
- `SWRLZ_CHAT_UPSTREAM_BEARER`
- `SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS`

Node proof and bearer values are injected by the Vercel server only. They are never written into the HTML response or browser persistence.

## Local R39 boundary

Current SERVER evidence proves the R39 artifact can be reconstructed from Forge Git chunks, decompressed, matched to the authoritative raw SHA-256, and structurally inspected by Gate 5. Gate 5 currently reports:

- container verified;
- canonical header present;
- required sections registered;
- `oneTokenReady: false`;
- `interactiveReady: false`;
- blocker `SECTION_PAYLOAD_LOCATION_AND_INFERENCE_WIRING_PENDING`.

Therefore, when no upstream is configured, `/api/chat` operates in `LOCAL_R39_STATUS_ONLY` mode. It emits a truthful STARTED/STATUS/FAILED sequence and **never fabricates assistant DELTA text**.

## Live upstream mode

When all proof-bound upstream settings are present, the bridge forwards a bounded request to the configured SWRLZ SERVER stream endpoint and validates every incoming event before forwarding it to the browser. Events must match protocol V2, the expected stream contract, monotonically increasing sequence numbers, the original request ID, known event types, and consistent terminal flags.

Cancellation is forwarded to the matching upstream request ID. An unreachable or contract-invalid upstream becomes an explicit FAILED terminal event rather than a synthetic answer.

## Browser features

The R299-derived page includes:

- responsive desktop/mobile conversation layout;
- local thread creation, rename, pin, and delete;
- message copy/bookmark;
- bounded recent-history submission;
- live committed DELTA rendering;
- RESET handling;
- stream phase trace and latency display;
- cancellation;
- JSON evidence export;
- R39 verification button;
- explicit runtime/setup state.

## Deployment

After SERVER 2.1.0 is deployed, configure `SWRLZ_WEB_CHAT_TOKEN` in the same Vercel project/environment. A live upstream is optional until chat inference is available; without it the page still loads and accurately reports the current inference boundary.

Open:

- `/api/admin` for Admin/R39/Gate 5 controls;
- `/api/chat` for chat;
- `/api/chat?action=status` for non-secret chat bridge configuration state.

See `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md` and `docs/checkpoints/INT-VERCEL-CHAT-001A_CHECKPOINT.md` for the integration contract and receipts.
