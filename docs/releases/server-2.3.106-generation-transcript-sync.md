# Server Runtime 2.3.106 — Authoritative Generation Transcript Sync

Status: implementation complete; stable production deployment pending explicit approval.

## Versions

- Server Runtime: 2.3.105 -> 2.3.106
- Web Chat: 1.4.87 -> 1.4.88
- LALM Engine: unchanged from the active runtime authority

## Problem

A browser/network handoff could leave Chat showing `Reconnecting` for too long even while the detached R39 generation thread continued making progress on the server. The resumable-v1 implementation owned a sequenced event buffer, but Chat still needed to catch up through transport events before its visible answer reflected the current generation position.

## Architecture change

The server-owned generation session now maintains an append-only raw generation transcript in addition to its detailed event history:

- `transcript`: authoritative generated text so far
- `textRevision`: monotonically increasing DELTA revision
- `lastSeq`
- `lastDeltaSeq`
- `phase`
- `terminal` / `terminalType`
- latest stream identity

A new authenticated transcript snapshot endpoint returns contract `generation-transcript-v1` for an active requestId.

The browser-side `chat_transcript_sync.js` overlay is loaded after the existing Chat wrappers. It tracks the raw DELTA prefix already consumed by the browser. On foreground/pageshow/online it requests the authoritative server transcript, verifies that the browser raw prefix matches the server transcript prefix, and animates only the missing suffix through the existing semantic committed-output pipeline. It then suppresses duplicate replay events until the normal resumable stream reaches the synchronized sequence and continues live.

This preserves the existing final-copy rule:

- server transcript = authoritative generation state
- browser `message.text` = semantically accepted append-only final copy

The transcript snapshot never directly bypasses semantic staging.

## UX behavior

Expected foreground recovery:

1. `Synchronizing with §wyrlz…`
2. missing generated suffix is animated quickly into the same message
3. `Writing response…`
4. live stream continues without regeneration or replacement

The user should not need to wait for the complete missed event chain before seeing the response catch up.

## Stable server changes prepared on `main`

- `api/chat_resume_sessions.py`
  - generation transcript ownership
  - `POST /api/chat/transcript`
  - `generation-transcript-v1`
- `api/index.py`
  - stable Server 2.3.106
  - `chat-generation-transcript` capability
- `.github/workflows/manual-vercel-production.yml`
  - verifies Server 2.3.106
  - verifies `generation-transcript-v1`

## Runtime changes

- `web/chat_transcript_sync.js`
- `web/chat_committed_contract_bridge.js`
  - loads transcript sync after the Chat wrapper chain is installed
- `versions/server-runtime.txt` -> 2.3.106
- `versions/web-chat.txt` -> 1.4.88

## Deployment

No stable deployment was triggered by this event. The runtime browser overlay can hot-load, but the authoritative transcript endpoint becomes functional only after an explicitly approved Server 2.3.106 production deployment.

## Rollback

- Runtime UI rollback: restore the previous committed-contract bridge and remove/stop loading `chat_transcript_sync.js`.
- Stable rollback: restore the previous `api/chat_resume_sessions.py` and Server entrypoint; resumable-v1 event replay remains the fallback behavior.
