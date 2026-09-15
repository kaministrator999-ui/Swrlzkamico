# Server 2.3.152 — Private Chat ingress message receipts

**Status:** source implementation complete; production deployment pending user action  
**Overall Server:** 2.3.152  
**Affected module:** stable Chat/server ingress diagnostics  
**Web Chat:** unchanged  
**LALM:** unchanged  
**Deployment:** REQUIRED to make the stable Python change live; user will deploy manually

## Purpose

Make an authenticated user message observable at the server ingress boundary before generation begins, so a message that disappears before normal generation can still leave a private structural receipt.

## Change

`main/api/chat_client_debug.py` now emits a private structured `SWRLZ_CHAT_MESSAGE` runtime-log record for authorized Chat stream requests before control reaches the generation route.

The receipt contains:

- `CHAT_MESSAGE_ACCEPTED` event type;
- UTC receipt timestamp;
- privacy-safe hash-derived account scope when a valid account session exists;
- thread ID;
- supplied message ID when available, otherwise a deterministic ingress message ID;
- request ID;
- user role;
- the accepted prompt text, bounded to the Chat prompt limit;
- UTF-8 text byte count;
- persistence surface (`VERCEL_RUNTIME_LOG`);
- `generationStarted: false` to make the pre-generation position explicit.

The receipt is emitted only after the existing private Chat token matches. It is not returned by the public Chat response and is intentionally separate from the browser diagnostic event buffer.

## Architecture

```text
Chat mask
   |
   | authenticated stream request
   v
stable server ingress
   |
   +--> private SWRLZ_CHAT_MESSAGE receipt  <-- before generation
   |
   v
normal Chat route / LALM handoff
```

This is an observability hardening event. It does not yet replace the durable account-state Blob with a normalized append-only message database, and it does not claim that Vercel runtime logs are the durable conversation authority.

## Lineage

- Stable source commit: `0c70f275c76fbbc70b0dfe3680dd18176fc55318`
- Runtime version-authority commit: `a204887b01ec32b88f7ca57e1f23cf7dd5e03b99`
- Baseline Server authority before assignment: 2.3.151 (`46d7e46481c4a6f3faa813eaeb24aeccf31d18fa`)
- Assigned Server authority: 2.3.152 (`2f62687ce89b037c1cd18d28b97b9833ec8b4a2b`)

## Verification

Repository-level source and authority updates completed. Production verification is intentionally pending because no deployment was performed by this event. After the user deploys, verify that a new Chat message produces `SWRLZ_CHAT_MESSAGE` before generation activity and that the record contains the expected request/thread/message correlation fields.

## Rollback

Revert the stable `api/chat_client_debug.py` change in a new versioned Server event. Do not rewrite or erase this lineage entry.
