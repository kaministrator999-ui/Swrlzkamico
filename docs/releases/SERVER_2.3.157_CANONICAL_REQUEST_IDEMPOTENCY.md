# Server 2.3.157 — Canonical request idempotency across HTTP replays

**Status:** implementation staged; repository verification complete; production deployment pending explicit/manual action.

**Overall Server:** 2.3.157  
**Web Chat:** 1.5.27 unchanged  
**Stream contract:** unchanged  
**Deployment:** NOT PERFORMED by this event  
**Restart:** NONE

## Why this event exists

Production verification of Server 2.3.156 proved that the slash-redirect / nested-middleware duplicate admission was corrected, but exposed a second class of replay that request-scoped state cannot cover: the browser/resumable-generation layer may issue a later HTTP request using the same logical `requestId`.

For the verified `Hey 👋` turn, the same request ID was durably admitted at account-state revisions 92 and 93. Both requests used the same thread, user message ID, assistant message ID, role and text. This showed that the canonical Blob writer still treated an already-existing message as an update and advanced the revision again.

Server 2.3.157 is the corrective event.

## Correction

Canonical message persistence now treats request/message identity as immutable and idempotent:

- the same `requestId` + role may own only one canonical message identity;
- the same canonical message ID with the same role, text, state and required server metadata is acknowledged as an idempotent replay;
- an idempotent replay returns the existing account-state revision without another Blob write, revision increment, timestamp churn or message rewrite;
- reuse of the same request identity with a different thread/message identity is rejected;
- reuse of the same message identity with different content, state, role or required metadata is rejected as a canonical conflict.

This matches the Android SERVER reference model: stable message IDs are idempotent, while differing content under the same identity is a conflict rather than an overwrite.

## Production verification required after deployment

Send one fresh signed-in Chat turn and allow the normal resumable transport behavior. If the browser later replays the same request ID, verify that:

1. the initial USER commit advances the account-state revision once;
2. a replay of the same request/message/content returns the existing revision rather than creating another durable commit;
3. the assistant terminal commit advances the revision once;
4. no request-ID/message-ID content conflict occurs during normal replay;
5. the visible assistant response contains no server transport directive leakage.

Transport-level resume requests may still appear in logs; they must not create a second canonical message or a second state-revision advance.

## Source lineage

- Canonical durable-idempotency implementation: `d83c77796631196d109abad0cb53fc412b91433f`
- Server Runtime 2.3.157 authority: `74ac7616411eb397a8de7ab15a4bd81fd337f8e7`

## Deployment control

Current `vercel.json` still has Git deployment disabled. The production workflow deploys only by explicit approved workflow dispatch or an approved `.deploy/REQUEST.txt` change. No deployment-producing action was performed by this event.