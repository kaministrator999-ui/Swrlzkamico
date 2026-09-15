# Server 2.3.155 — Browser-session canonical Chat ingress correction

**Overall Server:** 2.3.155  
**Web Chat:** 1.5.27 unchanged  
**Web Frontend:** 1.0.4 unchanged  
**Stream Contract:** V2 unchanged  
**Google Account:** unchanged  
**LALM:** unchanged

## Verification trigger

Production Server 2.3.154 was deployed and the runtime Chat was refreshed. A new browser camera run (`5fb9782e-e584-4ab4-8e30-9658bde4c9c4`) reached `visual-ready` on runtime revision 95. The previous `chat_stream_incremental.js?v=93` temporal-dead-zone error no longer appeared in the refreshed session.

The remaining 409 responses observed before that new v95 boot belonged to older resumable-generation attempts. The refreshed v95 session itself proved that the runtime renderer/cache-revision correction was active.

## Root cause discovered during 2.3.154 verification

The canonical-turn middleware's ingress predicate still accepted only the legacy `x-swrlz-chat-token` header. Normal current browser Chat authentication uses the signed HttpOnly `swrlz_chat_session` cookie (or `x-swrlz-chat-session`) established by `api/chat_admin_session.py`.

This created an authority mismatch:

```text
Chat route authorization
    -> signed browser session accepted

canonical turn admission
    -> legacy permanent-token header only
```

A valid modern browser request could therefore pass the actual Chat route while skipping `CHAT_MESSAGE_ACCEPTED`, commit-before-generation, server canonical-history replacement, and terminal assistant persistence.

## Correction

Stable `api/chat_admin_session.py` now bridges canonical-turn ingress to the same signed browser-session validator already used by the Chat route.

- A valid `swrlz_chat_session` cookie or `x-swrlz-chat-session` header now qualifies as canonical Chat ingress.
- The legacy `x-swrlz-chat-token` check remains a fallback for compatible non-browser callers.
- The already-imported post-redirect receipt helper is aligned to the same browser-session-aware ingress predicate.
- Google account authentication remains separately authoritative for account-scoped durable user state; a browser Chat session alone does not fabricate an account identity.
- Signed-out sessions continue through the existing compatibility path if no account session is available.

## Architecture result

```text
MASK / browser
    -> signed browser Chat session + factual turn
HUMAN / server
    -> authorize with the same Chat-session authority
    -> authenticate account for durable ownership
    -> commit USER
    -> rebuild canonical server history
    -> generate
    -> commit ASSISTANT terminal
BRAIN / LALM
    -> interpret / reason / generate
```

The diagnostic/persistence path and the operational Chat route now share one browser-session authorization boundary instead of disagreeing about what counts as an authenticated Chat request.

## Lineage

- Stable auth-boundary correction: `bcb0b687ebeb50c5103c2b5b5f01b01762224e3a`
- Server 2.3.155 authority: `19ed039acb5830ceae78646a0346cd92a03a2ea6`

## Deployment state

- `main/vercel.json` currently has `git.deploymentEnabled=false`.
- The manual production workflow deploys only through explicit workflow dispatch approval or a `.deploy/REQUEST.txt` push event.
- These source/version commits did **not** trigger a production deployment.
- A production deployment is required before the stable 2.3.155 auth-boundary correction becomes active.

## Verification pending after deployment

After an explicitly authorized/manual deployment of current `main`:

1. open/reload Chat and confirm runtime revision 95 or newer;
2. send one new signed-in turn with a fresh requestId;
3. verify one correlated sequence containing:
   - `CHAT_MESSAGE_ACCEPTED`
   - `CHAT_MESSAGE_COMMITTED`
   - `CHAT_HISTORY_CANONICALIZED`
   - `CHAT_GENERATION_STARTED`
   - `CHAT_GENERATION_TERMINAL`;
4. verify user state revision advances before generation and assistant state revision advances at terminal;
5. verify the request no longer falls through the canonical-turn layer solely because the browser used the signed Chat-session cookie.
