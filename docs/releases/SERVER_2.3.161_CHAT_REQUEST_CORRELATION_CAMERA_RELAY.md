# §wyrlz Server 2.3.161 — Request correlation + Whole Conversation Camera relay

**Overall Server Runtime:** 2.3.161  
**Web Chat:** 1.5.31  
**Runtime manifest:** 99  
**Deployment:** NONE  
**Restart:** NONE  
**Source authority:** `runtime`

## Trigger / prior verification defect

Phase 2A production acceptance on the prior runtime showed repeated browser diagnostics:

`hydrate-deferred: local-stream-unresolved`

at server account-state revisions 114, 115, and 116 even after the server had already persisted a terminal assistant response for the same logical request.

Evidence for request `web:mu2ptj1y:9318516982430135816` showed different browser-cache and canonical-server assistant message IDs:

- browser cache assistant: `message:mu2ptj1y:38483045661260136905`
- canonical server assistant: `assistant:2ef52c9c6308a8c641f8f74d5715`
- stable identity shared by both: request ID `web:mu2ptj1y:9318516982430135816`

The prior hydration guard matched the assistant by message ID only. That could therefore classify a locally stale `streaming` presentation record as unresolved even though server authority already had the terminal assistant record.

## Correction

`web/chat_account_state_sync_v1.js` now uses request identity as the primary assistant correlation key during server-state hydration. Message ID remains a secondary fallback only.

A remote assistant is terminal when the server state reports a terminal state (`complete`, `cancelled`, or `failed`) or terminal server commit metadata. Once that terminal assistant exists for the same request ID, stale browser `streaming` state no longer blocks server hydration.

Canonical thread/message identity, text, role, state, pin state, and server metadata remain server-owned. Browser-only activity/presentation diagnostics are overlaid locally after server hydration by request identity so rich client evidence is not destroyed when canonical state repairs the cache.

## Whole Conversation Camera diagnostic relay

The runtime now exposes the diagnostic contract:

`swrlz-whole-conversation-camera-v1`

Camera evidence is sent through the existing bounded `/api/chat/client-debug` channel. It does not create a new persistence authority and it does not restore whole-state browser writes.

Automatic captures occur on:

- local assistant terminal transition;
- genuine unresolved hydration detection;
- successful metadata mutation completion;
- successful server hydration repair.

A manual browser diagnostic capture is also exposed as:

`window.__swrlzWholeConversationCamera.capture('manual')`

The relay reports bounded evidence for the active thread (up to the latest 8 messages, with explicit truncation flags):

- thread ID, title, message count, current runtime mode/revision;
- message ID, role, state, timestamp, pin state, visible text;
- request ID and current phase;
- first-delta and total latency;
- activity/trail text;
- terminal integrity;
- response presence;
- Context Camera receipt;
- temporal context receipt;
- network continuity;
- generation transcript synchronization;
- turn integrity;
- bounded raw message state;
- bounded raw thread state.

Nested diagnostic structures are serialized into bounded chunks before entering the stable debug endpoint so the existing server-side diagnostic sanitizer/depth limits do not erase the useful evidence.

Potential credential-bearing keys such as token, secret, password, credential, authorization, cookie, access token, and ID token are removed by the client diagnostic sanitizer before relay. The stable debug boundary continues to apply its own size/depth sanitation.

## Authority / cognition boundary

The camera is observation only. It does not participate in LALM prompting, intent classification, semantic interpretation, canonical message persistence, or account-state authority.

- Mask: observes and relays presentation/transport diagnostics.
- Server: owns canonical conversation/account state.
- LALM: remains cognitive authority.

## Lineage

- Runtime sync correction + camera relay: `59c5e25706c9341c1219bb5efb1f7b2d0b434c4e`
- Server Runtime 2.3.161 authority: `4f81d790dc4807ccb241f81e86566f29e1df6ab8`
- Web Chat 1.5.31 authority: `ba9ba7dabdcc17b08dcdd664551ed99665f6188c`
- Runtime manifest 99: `58584a23a528031d94255db431c7f919e14830a5`

## Verification

Repository/source verification:

- runtime source serves `swrlz-chat-account-state-sync-v3`;
- runtime source serves `swrlz-whole-conversation-camera-v1`;
- request-ID-first terminal correlation is present;
- local diagnostic overlay is restricted to presentation/diagnostic metadata;
- manifest 99 is served live from GitHub runtime authority;
- no deployment or restart was performed.

Browser acceptance remains pending a fresh manifest-99 Chat boot. Acceptance requires:

1. boot receipt revision 99 with no script load/fatal error;
2. after a terminal response, server hydration must not falsely remain deferred merely because local and server assistant message IDs differ;
3. genuine in-flight generation may still defer hydration until server terminal authority exists;
4. `conversation-camera` / `whole-thread` and `conversation-camera` / `message` receipts must appear in runtime logs;
5. those receipts must expose the bounded thread/message/activity/integrity evidence above without credentials;
6. metadata mutations must continue using narrow `POST /api/chat_state`, with browser snapshot authority remaining retired.
