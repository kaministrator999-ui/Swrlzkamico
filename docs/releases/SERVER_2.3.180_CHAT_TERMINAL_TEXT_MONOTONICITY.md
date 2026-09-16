# Server 2.3.180 — Chat terminal text monotonicity

**Server Runtime:** 2.3.180  
**Web Chat:** 1.5.39  
**Stream Contract:** V2 unchanged  
**LALM:** unchanged  
**Deployment:** NONE  
**Restart:** NONE

## Incident

Production runtime logs for thread `thread:mu47hf94:17938016632857218406` showed assistant turns reaching `CHAT_GENERATION_TERMINAL` with `terminalType=COMPLETED`, non-empty text, `PRIVATE_ACCOUNT_BLOB` persistence, and advancing canonical revisions. User screenshots simultaneously showed the response briefly appearing and then being replaced by `No committed assistant text was received.`

Client debug logs showed same-tab canonical cache adoption and account-state reconciliation immediately around the destructive transition. The defect therefore belonged to Mask reconciliation rather than LALM generation.

## Change

The same-tab canonical reconciler now treats non-empty completed assistant text as monotonic for a request. If a newly hydrated/adopted snapshot contains the same completed assistant request but an empty text field while the live Mask still holds completed text, the reconciler preserves that completed text, restores complete terminal presentation metadata, writes the repaired snapshot back to the working browser cache, and emits a `completed-assistant-text-preserved` diagnostic event.

Correlation is request-ID first with message-ID fallback. The repair only applies to completed assistant turns and does not convert failed/cancelled turns into successful ones.

## Intended invariant

Once a request has visible, completed assistant text, a later same-tab cache/hydration snapshot for the same completed request may not downgrade that text to empty.

## Verification

Repository source and version authorities were updated on `runtime`. Live browser verification requires a fresh Chat request after the runtime asset refresh. The new diagnostic counter/event allows production logs to prove whether the guard fired.
