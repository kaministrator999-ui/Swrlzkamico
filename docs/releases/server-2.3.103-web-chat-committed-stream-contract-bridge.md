# Server Runtime 2.3.103 / Web Chat 1.4.86

## Summary

Hot-runtime repair for the `Stream contract mismatch` exposed after Server 2.3.101 enabled resumable generation sessions and Committed Output v3 staged semantic output.

## Root cause

`web/chat_committed_output_v3.js` correctly withheld raw model DELTAs until prose/code passed semantic staging, but then attempted to commit approved text by calling the strict base stream consumer with synthetic objects such as `{type:"DELTA", text:"..."}`. Those synthetic objects did not contain the real stream envelope fields (`protocolVersion`, `schemaVersion`, `contractId`, `seq`, `identity`, `terminal`), so the core `swrlz_llm_stream_v2` validator rejected them as `Stream contract mismatch` even though the server-originated events were valid.

## Change

Added `web/chat_committed_contract_bridge.js` immediately before `web/chat_committed_output_v3.js` in runtime manifest v23.

The bridge preserves two boundaries:

- Real network/server events continue through the original strict stream validator unchanged.
- Local semantic commit units emitted by Committed Output v3, recognizable by the deliberate absence of all network-envelope fields, append directly to the already-owned assistant final-copy buffer and never impersonate transport events.

This retains append-only final-copy semantics without weakening validation of actual server traffic.

## Versions

- Server Runtime: 2.3.102 -> 2.3.103
- Web Chat: 1.4.85 -> 1.4.86
- LALM Engine: unchanged at 2.1.37 / v27
- Stable production server: unchanged at 2.3.101

## Deployment

NONE. This event is runtime-hot only and does not touch the stable deployment boundary.

## Live acceptance

The production `/chat` page was fetched after publication and confirmed to inject:

1. `web/chat_stream_incremental.js`
2. `web/chat_committed_contract_bridge.js`
3. `web/chat_committed_output_v3.js`

in that order.

Behavioral acceptance still requires a fresh user Chat generation to confirm that the first semantically committed prose/code unit becomes visible without a stream-contract failure.

## Rollback

Remove `web/chat_committed_contract_bridge.js` from the runtime manifest and restore manifest v22 / Web Chat 1.4.85 semantics. Git history preserves the prior state.
