# SWRLZ Vercel Chat Bridge V1

Contract ID: `swrlz_vercel_chat_bridge_v1`  
Stream contract: `swrlz_llm_stream_v2`  
SERVER: `2.1.0`  
Chat: `1.0.0`

## Purpose

Define the boundary between the browser chat surface, the unified Vercel SERVER, and an optional proof-bound SWRLZ SERVER inference upstream. The contract is designed so presentation cannot silently upgrade structural/readiness evidence into an inference claim.

## Browser -> Vercel

Chat requests are POSTed under `/api/chat` with `x-swrlz-chat-token`. `SWRLZ_WEB_CHAT_TOKEN` is a separate secret from `SWRLZ_ADMIN_TOKEN` and must be at least 16 characters.

Accepted stream request fields are bounded and normalized:

- `requestId`: 1–128 URL-safe characters; generated when absent;
- `prompt`: nonblank, maximum 16000 characters;
- `history`: maximum 32 retained user/assistant turns, each text field bounded to 2000 characters;
- `threadId`: optional bounded browser-local identifier;
- `profileId`: optional bounded route/profile hint.

The browser never receives the upstream device proof or optional bearer credential.

## Vercel -> proof-bound upstream

When configured, Vercel sends the normalized request to the SWRLZ SERVER V2 chat stream and injects server-side headers:

- `X-SWRLZ-Device-Node-Id`;
- `X-SWRLZ-Device-Proof`;
- optional `Authorization: Bearer ...`;
- `X-SWRLZ-Request-Id`;
- `Idempotency-Key`.

The configured URL must be HTTP(S), contain no embedded credentials, query, or fragment, and resolves to `/ai/swrlz-llm/v2/chat/stream` unless that stream path is already supplied.

## Stream validation

Every upstream NDJSON event must:

1. be a JSON object no larger than the bridge event bound;
2. use `protocolVersion: 2`;
3. use contract `swrlz_llm_stream_v2`;
4. use a supported schema version;
5. use a known event type;
6. have a strictly increasing integer `seq`;
7. carry an identity whose `requestId` equals the browser request;
8. use string text for DELTA;
9. mark terminal state consistently with COMPLETED, CANCELLED, or FAILED.

Contract-invalid upstream output becomes an explicit terminal FAILED event. It is never accepted as assistant prose.

## Presentation invariant

Only `DELTA.text` may be appended to the assistant message. `RESET` clears the current committed assistant revision. STARTED, STATUS, ROUTE, timing, errors, blockers, and terminal metadata remain operational UI state.

This is a hard separation between answer text and runtime/control-plane evidence.

## Local status-only mode

If no upstream is configured, the bridge reports `LOCAL_R39_STATUS_ONLY`. A chat request emits STARTED, STATUS, then FAILED with blocker:

`SECTION_PAYLOAD_LOCATION_AND_INFERENCE_WIRING_PENDING`

No DELTA is generated. This is intentional: the current Gate 5 proof establishes R39 container/integrity readiness but not one-token or interactive inference.

## R39 verification action

The chat verification action reuses the existing `ensure_r39()` loader and Gate 5 inspector. Returned data is sanitized to readiness/integrity fields and explicitly distinguishes container verification from inference readiness.

## Cancellation

The browser can cancel the active request by request ID. In upstream mode the bridge forwards cancellation to the corresponding V2 cancel route. In local status-only mode cancellation is quiescent because no inference owner exists.

## Persistence and evidence

Browser conversation content may be stored in localStorage. `SWRLZ_WEB_CHAT_TOKEN` is stored only in sessionStorage. Exports include bounded conversation/stream metadata but exclude chat tokens, Admin tokens, upstream device proof, and gateway bearer credentials.

## Non-claims

This contract does not claim:

- that Vercel can reach a configured upstream until stream evidence proves it;
- that a proof-bound upstream accepts the configured identity until a request is admitted;
- that R39 container verification implies token generation;
- that local inference is ready while Gate 5 reports `oneTokenReady:false` or `interactiveReady:false`.
