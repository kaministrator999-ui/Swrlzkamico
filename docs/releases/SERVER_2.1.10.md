# §wyrlz Server 2.1.10

## Purpose

Make the parent UI guards tolerant of harmless URL query decoration so tracked or shared links cannot silently bypass the live Chat/Page Manager serving layer.

## Trigger receipt

The 2.1.9 runtime index loaded correctly, but links carrying harmless query parameters such as `utm_source=chatgpt.com` caused both `/api/pages` and `/api/chat` to fall through to their older handlers because the parent guards required an entirely empty query string.

That produced exactly the observed receipts:

- Page Manager rendered the old token-entry UI and initially showed `invalid or missing SWRLZ_ADMIN_TOKEN` before Admin authentication.
- Chat rendered without the enhancement/version layer, leaving the drawer dimming/status behavior unchanged.

## Changes

1. `/api/pages` parent UI guard now serves the current manager for every GET to the exact `/api/pages` path regardless of harmless query decoration. Operational actions remain POST-only, and `/api/pages/public` remains a separate path.
2. `/api/chat` parent UI guard now serves the current Chat page when `action` is absent or `action=page`, while ignoring unrelated query keys such as UTM tracking parameters. Functional actions such as `action=status` still pass through to the Chat application.
3. Server version advances from 2.1.9 to 2.1.10. Chat UI remains 1.3.4 until the hot-update proof.

## Validation targets

1. `/api/health` reports `2.1.10`.
2. `/api/pages?utm_source=test` still renders the current credential-status manager.
3. `/api/chat?utm_source=test` still injects the enhancement CSS/JS and displays `CHAT v1.3.4 · SERVER v2.1.10`.
4. `SYNC DEV → RUNTIME` remains deployment-free.
5. After those receipts pass, bump Chat 1.3.4 → 1.3.5 on `dev` only and prove Server remains 2.1.10 without redeployment.
