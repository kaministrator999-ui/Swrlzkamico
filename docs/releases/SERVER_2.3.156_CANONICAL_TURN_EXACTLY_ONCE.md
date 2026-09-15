# Server 2.3.156 — Canonical Chat exactly-once + transport/cognition separation

**Status:** implementation staged; repository verification complete; production deployment pending explicit/manual action.

**Overall Server:** 2.3.156  
**Web Chat:** 1.5.27 unchanged  
**Stream contract:** unchanged  
**Deployment:** NOT PERFORMED by this event  
**Restart:** NONE

## Why this event exists

Production verification of Server 2.3.155 proved the intended server-owned Chat lifecycle works: USER commit before inference, server-owned canonical history, generation start, and assistant terminal commit. The same verification also exposed two defects that must remain visible in lineage rather than being silently erased:

1. One logical request could enter canonical persistence more than once because `/api/chat` redirected to `/api/chat/` and the same canonical middleware could be present at nested application boundaries.
2. The stable Chat normalizer supplied a `responseDirective` containing transport/stream instructions to the LALM payload. The model repeated part of that operational instruction in visible assistant prose, violating the Mask/Human/Brain ownership rule.

Server 2.3.156 is the corrective event.

## Correction 1 — exactly one canonical transaction per logical request

The browser-session canonical-ingress bridge now:

- refuses canonical admission on the no-trailing-slash `/api/chat` POST so its 307 redirect cannot mutate conversation state;
- claims canonical admission in ASGI request-scope state on the canonical `/api/chat/` request;
- rejects later nested middleware attempts to claim the same request again;
- preserves signed HttpOnly browser-session authorization plus the legacy private header-token fallback.

Expected result after deployment: one request ID produces one USER commit, one canonical-history event, one generation-start event, and one assistant terminal commit.

## Correction 2 — transport instructions do not enter LALM cognition

The stable Chat extension boundary now removes `responseDirective` from the normalized payload before local or upstream LALM execution.

NDJSON/DELTA framing remains an operational server/transport responsibility. The Brain receives the user's factual turn/history and allowed generation metadata, not server prose telling it how transport should behave.

This follows the project architecture:

- Mask: sense / relay / present
- Human/server: authorize / persist / transport / execute
- Brain/LALM: interpret / reason / answer

## Source lineage

- Exactly-once ingress correction: `f9b19f7ae513937fedb596c12e036eb38c7990b6`
- Transport/cognition separation correction: `029fa22b42c9d4802e0e94b7050a25e633bc61b2`
- Server 2.3.156 version authority: `5ac50114c25d8cb66c2967455c5f00fdfdf27b9f`

## Verification performed before deployment

- Re-read `VERSION.txt`, `versions/server-runtime.txt`, and `versions/web-chat.txt` immediately before version assignment.
- Confirmed authority remained Server 2.3.155 / Web Chat 1.5.27 before assigning 2.3.156.
- Re-fetched the committed `api/chat_admin_session.py` exactly-once guard from `main`.
- Re-fetched the committed `api/chat_extensions.py` transport-directive removal from `main`.
- Current deployment configuration still has Git deployment disabled; ordinary `main` commits do not deploy. No `.deploy/REQUEST.txt` mutation or deployment action was performed.

## Production verification required after deployment

For one fresh signed-in Chat turn, verify the same request/thread/message identity yields exactly:

1. `CHAT_MESSAGE_ACCEPTED`
2. one `CHAT_MESSAGE_COMMITTED`
3. one `CHAT_HISTORY_CANONICALIZED`
4. one `CHAT_GENERATION_STARTED`
5. one `CHAT_GENERATION_TERMINAL`

There must be no canonical persistence on the preceding `/api/chat` 307 request, no duplicate state-revision advances for the same logical turn, and no visible assistant text containing transport directives such as instructions to stream as DELTA.
