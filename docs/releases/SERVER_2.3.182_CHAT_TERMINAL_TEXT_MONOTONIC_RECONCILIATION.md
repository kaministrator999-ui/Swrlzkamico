# Server 2.3.182 — Chat terminal text monotonic reconciliation

**Web Chat:** 1.5.41  
**Deployment:** NONE  
**Restart:** NONE  
**Path:** runtime-hot

## Incident

Production evidence showed a completed assistant response persisted by the server while the browser same-tab canonical reconciliation path could adopt a completed assistant message whose canonical snapshot text was empty. The loaded page could therefore replace already-visible response text with an empty completed message.

## Change

The same-tab reconciler now treats non-empty local assistant text as monotonic evidence when the incoming canonical message is COMPLETED but has empty text. The local message no longer has to already be marked complete: streaming/local non-empty text for the same request/message may repair the empty completed canonical snapshot before it is adopted into the live Mask.

The repair is requestId-first, falls back to message identity, records the prior local state, writes the repaired snapshot back to the local cache, and emits the v2 monotonic repair diagnostic. No LALM/Brain behavior, server inference, stream protocol, stable loader, API, auth, or deployment configuration changed.

## Verification

Repository source mutation completed on `runtime`. Version authorities advanced to Server 2.3.182 and Web Chat 1.5.41. Live browser reproduction remains required to close user-visible verification.
