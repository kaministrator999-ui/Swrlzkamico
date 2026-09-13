# Server Runtime 2.3.122 — Manifest Authority Hardening

Date: 2026-09-13

## Versions

- Server Runtime: 2.3.122
- Stable deployable server: 2.3.110 on `main`
- Web Chat: 1.5.2
- Deployment Control: 1.0.7
- Runtime manifest: v35

## Problem

After Server 2.3.109 enabled manifest-versioned immutable browser assets, production continued serving runtime manifest v33 even though the `runtime` branch had advanced to v35. The asset file itself was reachable, but `/chat` still injected v33 URLs and therefore did not load the new `chat_turn_integrity_v1.js` layer.

This proved that raw GitHub branch delivery could be stale long enough to violate the manifest-as-cache-revision-authority contract.

## Stable infrastructure changes prepared on `main`

### `api/live_source_guard.py`

- Manifest reads now resolve through GitHub repository-content authority (`github-contents-api-v1`) instead of trusting the raw branch CDN as the sole manifest source.
- The authoritative manifest is cached in-worker for 60 seconds to bound external authority traffic while keeping runtime updates redeploy-free.
- If manifest authority is unavailable after the cache expires, Chat fails closed rather than silently serving a potentially stale raw manifest.
- `/live/manifest.json` exposes:
  - `X-SWRLZ-Manifest-Authority: github-contents-api-v1`
  - `X-SWRLZ-Manifest-Revision: <revision>`
- Versioned asset requests bypass manifest lookup entirely and remain on the fast raw-GitHub path with immutable browser caching.
- Raw source requests now send stronger no-cache/no-store request directives.

Prepared commit:
- `bf2b48e00c19175d22d1990ef1e446b7728f5935`

### `api/index.py`

- Stable server version prepared as 2.3.110.
- Adds capability `runtime-manifest-authority` with contract `github-contents-manifest-v1`.
- Declares failure policy `fail-closed-no-stale-raw-manifest`.

Prepared commit:
- `13781f86632421f480057f09920734bf8cd858ec`

### Production verification

The deployment verifier now requires:

- Server 2.3.110
- `runtime-manifest-authority.ready == true`
- contract `github-contents-manifest-v1`
- live-source authority `github-contents-api-v1`
- failure policy `fail-closed-no-stale-raw-manifest`
- `/live/manifest.json` HTTP 200 with the manifest-authority header
- manifest revision >= 35
- `web/chat_turn_integrity_v1.js` present in the live Chat script list

Prepared workflow commit:
- `cecbb468d28288c1b036996a7a20fc36bb094216`

## Runtime state preserved

Manifest v35 remains the runtime authority and already includes `chat_turn_integrity_v1.js`, which addresses:

- stale Stop button after terminal transcript recovery,
- stale activity-log phase after completion,
- request-time temporal evidence being overwritten by foreground resume,
- false follow-up customer-service closures on simple greetings.

## Safety

- Existing immutable versioned asset caching is preserved.
- Shared transcript continuity remains unchanged.
- No silent manifest fallback is introduced.
- No production deployment was triggered by this preparation event; activation requires explicit production deployment approval.
