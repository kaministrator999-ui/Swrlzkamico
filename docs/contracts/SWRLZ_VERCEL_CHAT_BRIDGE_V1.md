# SWRLZ Vercel Chat Bridge V1

Contract ID: `swrlz_vercel_chat_bridge_v1`  
Stream contract: `swrlz_llm_stream_v2`  
SERVER: `2.1.15`  
Chat: `1.3.12`

## Purpose

Define the boundary between the browser Chat surface, the unified Vercel SERVER, local R39 inference, and an optional proof-bound SWRLZ SERVER upstream. Presentation may never silently upgrade structural/readiness evidence into model output.

## Browser -> Vercel authorization

`SWRLZ_WEB_CHAT_TOKEN` remains the server-side root Chat secret and is separate from `SWRLZ_ADMIN_TOKEN`.

Normal same-origin browser use no longer requires the user to paste that secret into Chat. Loading `/api/chat` receives a bounded signed browser session cookie with these properties:

- HttpOnly;
- Secure;
- SameSite=Strict;
- scoped to `/api/chat`;
- eight-hour maximum lifetime;
- signed from the server-side Chat secret;
- verifiable across Vercel instances when the durable environment token is configured.

The permanent Chat secret never enters browser JavaScript or browser storage. The historical `x-swrlz-chat-token` path and explicit Admin session endpoint remain compatibility fallbacks.

Accepted Chat request fields remain bounded/normalized: request ID, prompt, recent user/assistant history, optional thread/profile identifiers, and bounded generation controls. Browser code never receives upstream device proof or gateway bearer credentials.

## Route resolution

Route selection is deterministic:

1. If a complete proof-bound upstream configuration is present, use the upstream stream/cancel routes.
2. If no upstream URL is configured, use `LOCAL_R39`.
3. If an upstream URL is configured but required proof fields are missing, fail explicitly with `UPSTREAM_CONFIGURATION_INCOMPLETE`; do not silently substitute another route/identity.

## Status boundary

Status is a receipt, not a model-load trigger. `/api/chat/ops` and ordinary status reads must not inspect/load R39 merely to render UI state. Model verification and generation own heavy model work.

Chat Settings presents operational Chat/model state separately from assistant prose, including route, server version/instance, model readiness, engine identity/source, model SHA evidence, and blockers.

## Local R39 contract

The local executor must establish all of the following before claiming one-token readiness:
- canonical `SWRLZX\r\n` header at offset 0;
- valid SWRLZX v1 header fields and 128-byte TOC entries;
- active TOKENIZER, TENSOR_DIRECTORY, and TENSOR_DATA sections;
- tokenizer vocabulary/merge availability;
- each required tensor descriptor mapped through its declared `dataSectionId` and physical range;
- a supported quantizer for every required tensor;
- the supported LFM2 reference graph/tensor profile.

Any mismatch fails closed with a diagnostic category. No placeholder/synthetic DELTA may be emitted as a substitute.

The current reference path supports `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k` storage, BPE tokenization, recurrent short-convolution state, GQA KV state, bounded sampling, cancellation checks, and incremental UTF-8 decoding.

## Vercel -> proof-bound upstream

When configured, Vercel sends the normalized request to the SWRLZ SERVER V2 stream and injects server-side identity/proof headers plus request/idempotency IDs. The configured URL must be HTTP(S), contain no embedded credentials/query/fragment, and resolves to the V2 stream route unless already supplied.

## Stream validation

Every admitted upstream event must be a bounded JSON object using protocol V2, contract `swrlz_llm_stream_v2`, a supported schema version, known event type, strictly increasing sequence, matching request identity, string text for DELTA, and consistent terminal flags. Contract-invalid output becomes explicit FAILED evidence.

Local events are projected through the same bridge event schema before browser delivery.

## Presentation invariant / Truth Firewall

Only `DELTA.text` may be appended to the assistant message. `RESET` clears the current committed assistant revision. STARTED, STATUS, ROUTE, timing, errors, blockers, categories, model identity, heartbeat, and terminal metadata remain operational UI state.

FAILED or CANCELLED may preserve already committed DELTA text but their diagnostics are never concatenated into assistant prose.

## R39 verification action

The verification action reuses the transport loader and Gate 5/engine probes. It returns non-secret integrity/readiness evidence and explicitly distinguishes container verification, payload-location reconstruction, one-token structural readiness, and interactive readiness.

## Cancellation

The browser cancels by request ID. Upstream mode forwards cancellation to the corresponding V2 cancel route. Local mode arms a best-effort cancellation flag scoped to the current runtime instance and the local executor checks it during prefill/generation.

## Persistence and evidence

Browser conversation content may be stored in `localStorage`. The server-managed Chat session is an HttpOnly cookie and is not readable by Chat JavaScript. Compatibility markers/tokens are not conversation content and must never be exported. Exports may include bounded conversation/stream/runtime metadata but exclude Chat/Admin secrets, upstream device proof, and gateway bearer credentials.

## Live presentation source

Chat HTML/CSS/JS presentation is sourced from GitHub `dev` through the live-source guard. Supported Chat UI changes may therefore update live without deploying the stable SERVER. Backend/auth/inference changes still require `main` deployment.

## Non-claims

This contract does not claim:
- that source readiness equals a successful production deployment;
- that Vercel can reach a configured upstream until a request is admitted;
- that local R39 execution completes within platform duration limits until measured;
- that any unsupported artifact/profile is usable merely because its container hash is valid;
- that possession of a public Chat URL constitutes user identity; the same-origin browser session is an application access mechanism, not an identity provider.
