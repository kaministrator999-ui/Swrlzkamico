# Server Runtime 2.3.119 — Turn Integrity Reconciliation

Date: 2026-09-13

## Module versions

- Server Runtime: 2.3.119
- Web Chat: 1.5.2
- Runtime manifest: v35
- Stable production server remains 2.3.109; no new deployment required for this runtime-hot event.

## Evidence that triggered this event

A foreground-resume camera log showed all of the following at the same time:

- the authoritative generation transcript was terminal-synced, strict, verified, and sourced from `durable-blob`;
- the assistant message state was complete and its raw phase was COMPLETE;
- browser network continuity still said `waiting-network` with a stale HTTP 409;
- the base Chat active request could therefore remain alive and render the Stop button after the response had already completed;
- the top-level display phase could remain `ANALYZING_REQUEST`, leaving the Activity log summary stale;
- foreground resume rewrote the visible temporal receipt with the resume-time clock even though the generation itself belonged to the original request;
- a simple `Hey 👋` social opener produced a false follow-up closure: “anything else I can help with”.

## Runtime change

Added `web/chat_turn_integrity_v1.js` and activated it in manifest v35.

Contract: `turn-integrity-v1`.

### Terminal UI authority

When `generation-transcript-v1` is `terminal-synced`, `strict:true`, and `verified:true`:

- assistant state is reconciled to complete;
- display/raw phase is reconciled to COMPLETE;
- stale message errors are cleared;
- response presence is settled to `✅ Response complete`;
- stale `waiting-network` / reconnect errors are retired;
- the base active request is retired so the composer returns to Send instead of showing Stop;
- the stale browser stream controller is aborted only after terminal transcript authority exists, and subsequent saves re-assert the terminal state.

### Activity log presentation

- Activity trace is hidden while the response is still empty and waiting.
- The expressive waiting bubble owns the initial visible activity state.
- Once terminal, the trace is collapsed and its summary settles to `Activity log · Response complete`.

### Request-time temporal evidence

- The approved device-time context is snapshotted at the original request boundary as `request-time-anchor-v1`.
- Foreground/reconnect transport may perform later HTTP work, but terminal reconciliation restores the camera-visible temporal receipt to the original request-time evidence.
- This prevents resume time from masquerading as generation request time.

### Social opener quality

Pure greetings such as `Hey 👋` now receive a bounded response directive:

- respond naturally to the greeting;
- time-of-day greeting is allowed when approved temporal context exists;
- do not say “anything else I can help with” or otherwise imply prior assistance;
- do not use generic customer-support closure language.

## Preserved contracts

No change to:

- `resumable-v1`
- `generation-transcript-v1`
- `shared-private-blob-v1`
- `rmcca-direct-v1`
- terminal committed-output semantics
- Server 2.3.109 runtime-delivery optimization

This is a runtime-hot Chat behavior correction and does not require a Vercel redeployment.
