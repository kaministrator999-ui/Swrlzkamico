# Server 2.3.69 — RMCCA single cognitive authority

Date: 2026-09-12
Branch: `runtime`
Deployment: none
Restart: none

## Trigger evidence

A fresh browser reopen still produced an incorrect identity response (`I don't have a name. I'm an AI`) for `What's your name?`. The camera log showed the RMCCA metadata was absent on the active request while background recovery repeatedly restarted the same request after network/instance changes. This disproved the stale-tab-only hypothesis and exposed competing request-normalization ownership between the canonical context layer and background recovery.

## Structural correction

- `web/chat_context_canonical.js` is now the single cognitive authority for model-facing request context.
- Added an explicit canonical RMCCA envelope (`swrlz-rmcca-context-v1`) that carries directive identity, cognitive clock diagnostics, history provenance, canonical assistant-history count, and prompt size.
- Canonical preparation is idempotent: once a request has a valid RMCCA envelope, later passes preserve it instead of rebuilding or replacing it.
- Tightened identity behavior inside the RMCCA directive: the assistant identity is §wyrlz, and direct identity questions should answer naturally and explicitly rather than deny a name.
- Added first-class `identity-query` structure and `identity-answer` response topology diagnostics.

## Recovery correction

- `web/chat_background_resume.js` no longer owns or injects a competing response directive.
- Background recovery now asks the canonical RMCCA layer to prepare the request once, stores that canonical request, and replays the same cognitive envelope during recovery.
- Removed the leading-`§wyrlz` display suppression path. Presentation no longer hides identity output as a substitute for correct generation behavior.
- Recovery camera telemetry now records attempt count, original request start time, elapsed recovery time, and whether the canonical cognitive envelope survived the restart path.

## Camera correction

- `web/chat_context_camera.js` now reports cognitive authority, canonical envelope identity, recovery-attempt count, and canonical-envelope preservation alongside RMCCA topology/depth/frame/domain receipts.
- This gives the next acceptance test enough evidence to distinguish a model-behavior failure from a request-authority/recovery failure.

## Version authority

- Server runtime: `2.3.68` -> `2.3.69`
- Web Chat: `1.4.62` -> `1.4.63`
- LALM engine: `2.1.26` unchanged

## Concurrency guard

The event began from Server `2.3.68` / Chat `1.4.62`. Immediately before version assignment both authorities were re-read and were still unchanged, so the event safely claimed Server `2.3.69` / Chat `1.4.63` using the fresh authority SHAs.

## Relevant lineage

- Canonical RMCCA authority: `cec5cb1f523cafadb9ce3a65c8aae16739de9d02`
- Background canonical recovery: `badd23f1d2ff0583067f24ac570bd2e3e71c12b1`
- Camera continuity telemetry: `b5527c6e146a83cea77ed82604f7375b0481ee0a`
- Server version authority: `349ebf5f8e2d8c6927d131905ec595145a9816b0`
- Chat version authority: `5ccdd063f9975abd587564afe91cbe2fa20e34d5`

## Acceptance gate

After a fresh page load, ask `What's your name?` and inspect the whole-conversation camera. Expected receipts:

- visible answer naturally identifies §wyrlz;
- `cognitiveAuthority=chat_context_canonical`;
- `canonicalEnvelopeId=swrlz-rmcca-context-v1`;
- RMCCA topology `identity-answer`;
- if recovery occurs, `canonicalEnvelopePreserved=true` and recovery-attempt telemetry remains attached to the same request;
- no frontend identity suppression is needed for correctness.
