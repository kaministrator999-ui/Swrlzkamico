# Server Runtime 2.3.107 / Web Chat 1.4.89

## Purpose
Make the generation-transcript continuity upgrade fail closed instead of silently falling back to legacy event replay.

## Changes
- `web/chat_transcript_sync.js` now requires `generation-transcript-v1`.
- Every new generation performs an initial transcript-contract verification rather than waiting until a foreground/network-resume event.
- Missing `/api/chat/transcript`, wrong transcript contracts, request identity mismatches, or transcript prefix mismatches are terminal compatibility errors for transcript continuity.
- The UI records `strict=true`, `verified=true/false`, and `requiredServerVersion=2.3.106` in transcript telemetry.
- On incompatibility the active browser request is aborted and the user sees an explicit transcript continuity contract/version error. The client does not report legacy event replay as successful transcript continuity.
- Runtime manifest advanced to v25 and documents the no-fallback contract.

## Version movement
- Server Runtime: 2.3.106 -> 2.3.107
- Web Chat: 1.4.88 -> 1.4.89
- LALM Engine: unchanged at 2.1.37

## Stable server dependency
The authoritative transcript endpoint remains a prepared stable-server change on `main` targeting Server 2.3.106. Production stable server was not deployed by this runtime event. Until the stable transcript endpoint is deployed, the strict client intentionally reports the contract mismatch instead of hiding it behind the old replay path.

## Deployment
NONE. Runtime-only Chat changes were published to the `runtime` branch. Stable production deployment remains approval-gated.

## Acceptance
A correct end-to-end deployment must show:
1. initial transcript contract verification succeeds for every new generation;
2. transcript telemetry reports `contract=generation-transcript-v1`, `strict=true`, `verified=true`;
3. app foreground/network recovery snapshot-syncs against server-owned transcript state;
4. no `fallback-event-replay` state appears;
5. an old/incompatible server produces a visible compatibility error rather than apparently working through an older path.
