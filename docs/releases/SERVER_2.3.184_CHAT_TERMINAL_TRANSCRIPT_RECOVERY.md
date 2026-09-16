# Server 2.3.184 — Chat Terminal Transcript Recovery

## Scope
Runtime-hot Chat correction. No deployment or restart required.

## Production evidence
The 2026-09-16 reproduction showed the browser presenting `Stream ended without a terminal event` and `No committed assistant text was received` while production server logs recorded `CHAT_GENERATION_TERMINAL` with `terminalType=COMPLETED` and non-empty assistant text for the same request. The failure therefore occurred after canonical generation/persistence, inside Mask-side stream/state settlement.

## Correction
Added `web/chat_terminal_transcript_recovery_v1.js` and loaded it directly from Chat manifest v108. It detects an empty failed/complete assistant message with a request identity, asks the existing `/transcript` authority for that exact request, validates `generation-transcript-v1` identity plus a non-empty terminal `COMPLETED` snapshot, and restores only that canonical server text. It clears the synthetic local transport failure, settles the message complete, and records `terminal-recovery` camera receipts.

## Invariant
A local stream-close observation cannot erase or hide a non-empty canonical terminal assistant transcript already committed by the server. Canonical transcript recovery changes presentation/state only; it does not reinterpret, regenerate, or rewrite LALM output.

## Versions
- Server Runtime: 2.3.184
- Web Chat: 1.5.43
- Runtime manifest: 108
- LALM: unchanged
- Stream contract: unchanged
