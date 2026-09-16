# Server 2.3.194 — Canonical Redis selection correction

**Status:** implementation staged on `main`; production verification pending manual deployment.  
**Server Runtime authority:** `2.3.194`.  
**Affected stable surface:** canonical Chat turn persistence selection.  
**Deployment:** REQUIRED to apply the stable Python API change; NOT performed by ChatGPT.  
**Restart:** none independently requested.

## Runtime evidence leading to this event

The production turn correlated by request ID `web:mu4qmc5l:24193323383090458455` was accepted, then failed before generation because canonical persistence attempted the legacy private Blob path and received HTTP 403. Generation remained fail-closed and did not start.

## Source diagnosis

`api/chat_turn_state.py` already contained the Redis canonical-turn adapter and policy switch, but the default policy was `blob`. Therefore configured Redis credentials alone did not select Redis unless `SWRLZ_CHAT_CANONICAL_BACKEND` was separately set. This allowed the live canonical turn path to continue entering the broken legacy Blob authority despite Redis support being present.

## Correction

The canonical backend policy now defaults to `auto` rather than `blob`:

- if canonical Redis is configured, Redis is selected;
- if Redis is not configured, legacy Blob remains the compatibility fallback;
- explicit `redis` remains fail-closed when Redis is unavailable;
- explicit `blob` remains available for rollback/migration diagnostics.

The same default is used by the backend-status report so diagnostics and execution agree.

## Scope

This event intentionally does not rewrite the separate legacy `/api/chat_state` presentation/mutation compatibility service. That service may still require a later migration if its private Blob authority remains unavailable. The immediate failure blocking generation is the canonical pre-generation turn commit, which is owned by `chat_turn_state`.

## Lineage

- Stable source commit: `4151f0d432afaa83996c933c44813a920bdfc099`
- Runtime version-authority commit: `6a3c1ec4c8e674a6bad05129cb6bebe8727bc96f`

## Verification plan after manual deployment

Send a fresh Chat turn and correlate its request ID in production logs. Acceptance requires:

1. `CHAT_MESSAGE_ACCEPTED`.
2. Canonical pre-generation commit succeeds without a `chat-state-blob` 403 on that turn.
3. `CHAT_MESSAGE_COMMITTED` and canonical history complete.
4. `CHAT_GENERATION_STARTED` reports `generationStarted:true`.
5. R39/LALM events execute.
6. Terminal assistant state commits successfully.

If the canonical turn still selects Blob after this deployment, inspect the explicit `SWRLZ_CHAT_CANONICAL_BACKEND` environment value because an explicit `blob` setting intentionally overrides the new `auto` default.
