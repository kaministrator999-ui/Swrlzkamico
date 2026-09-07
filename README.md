# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.1.16**  
Chat UI revision: **1.3.13**  
Production deployment: **https://swrlzkamico-o3nu.vercel.app**  
Checkpoint lineage: `INT-VERCEL-CHAT-001A`

This repository is the unified §wyrlz Vercel SERVER. The stable deployment owns authentication, API/security contracts, filesystem confinement, Chat stream semantics, R39 transport/execution, and bundled fallbacks. Presentation pages and supported live assets are sourced from the non-deploying `dev` branch so they can iterate without redeploying the stable server.

## Current control planes

- `/api/admin` — Dragon Jester Admin workbench.
- `/api/chat` — §wyrlz Chat.
- `/api/pages` — authenticated live page manager and runtime mutation tools.
- `/api/hot` — narrow hot Chat/R39 runtime control.
- `/live/` — live launchpad/index.
- `/live/pages/*` — additional GitHub-backed pages from `runtime_pages/pages/*`.
- `/api/health` — server health receipt.
- `/api/lalm` — R39 load/transport state.

## Live page architecture — current

Durable page source lives on GitHub `dev`, where `vercel.json` disables Vercel deployment.

Server 2.1.13 changed the live read path so core pages/assets resolve directly from GitHub `dev` on request with a short in-instance cache and bundled fallback. Normal live reads no longer depend on whichever Vercel instance owns an ephemeral `/tmp` copy.

Core mappings:

- `web/admin.html` -> `/api/admin`
- `web/chat.html` -> `/api/chat`
- `web/chat_enhancements.css` -> `/api/chat/assets/enhancements.css`
- `web/chat_enhancements.js` -> `/api/chat/assets/enhancements.js`
- `runtime_pages/index.html` -> `/live/`
- `runtime_pages/pages/<path>` -> `/live/pages/<path>`

This means supported page/UI work follows:

`edit GitHub dev -> refresh live URL -> receive current dev source`

No `/api/pages` sync and no Vercel server redeploy are required for ordinary GitHub-backed page changes. `/api/pages` remains useful for authenticated runtime editing, receipts, and optional push-back workflows.

### Proven no-redeploy receipt

The Chat UI was deliberately bumped on `dev` while the deployed server stayed on Server 2.1.13. Refreshing `/api/chat` advanced the visible Chat version through 1.3.7 and 1.3.8 without server promotion or sync. This is the acceptance receipt for the GitHub-backed live-source path.

## GitHub write credentials

GitHub write capability remains server-side. Resolution precedence is:

1. `/tmp/swrlz-admin/runtime/github-content-token.txt`
2. `SWRLZ_GITHUB_CONTENT_TOKEN`
3. `SWRLZ_GITHUB_TOKEN`

The Page Manager reports whether write capability is configured but never echoes the secret value.

## Chat authorization — 2.1.15+

`SWRLZ_WEB_CHAT_TOKEN` remains the server-side root Chat secret. Normal browser Chat no longer needs the user to paste that key or open Admin first.

When `/api/chat` loads, the server issues a bounded HttpOnly, Secure, SameSite=Strict signed cookie scoped to `/api/chat`. The root Chat secret never enters browser JavaScript or browser storage. The legacy direct Chat-token header and explicit Admin session endpoint remain compatibility fallbacks.

Chat 1.3.13 preserves server-managed authorization. The normal Chat Settings UI does not expose a credential input.

## Chat UI — 1.3.13 lineage

Recent Chat repairs include:

- base New/Delete thread controls restored by removing conflicting enhancement interception;
- mobile drawer scrim moved into the app stacking context so the drawer remains undimmed;
- authoritative `/api/chat/ops` status and persistent Chat/Server version receipt;
- non-blocking status path that does not load/inspect R39 merely to render UI state;
- Stream Camera copy/clear, context inspection, generation controls, retry/fork, and Send to Workbench;
- Chat Settings status panel showing route, server instance/version, model readiness, engine source/ID, model SHA, and blocker;
- server-managed Chat authorization so sending no longer opens settings because a browser token is absent.

## Local R39 inference

The proven transport path remains:

`Forge chunks -> wrapper ZIP -> nested verified R39 gzip -> raw R39 -> SHA-256 -> Gate 5`

The compute path remains:

`SWRLZX TOC -> TOKENIZER + TENSOR_DIRECTORY + TENSOR_DATA -> local executor -> NDJSON DELTA`

Authoritative raw R39 SHA-256:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

Server 2.1.16 keeps the canonical Python/NumPy reference executor but reduces avoidable prefill overhead on the Vercel route. The hot path now uses 16 MiB bounded dequantization batches, caches small decoded tensors per model instance, and compacts only the stock bridge response directive before tokenization. Whole-model dequantization is intentionally avoided so memory remains bounded.

Blocking local compute remains wrapped with periodic heartbeat STATUS events. Heartbeat intervals restart after real engine/progress events; this protects connection idleness but does not reset Vercel's hard function-duration limit. The 2.1.16 optimization is therefore a latency reduction, not a claim that the reference executor is equivalent to a compiled production inference backend.

## Chat routing / Truth Firewall

Routing remains deterministic:

`complete proof-bound upstream -> upstream proxy`

`no upstream URL -> LOCAL_R39`

`upstream URL present but incomplete proof config -> explicit failure`

Only `DELTA.text` may enter assistant prose. STARTED, STATUS, ROUTE, RESET, heartbeat, timing, blockers, failures, model identity, and terminal metadata remain operational evidence. Compacting the stock local model directive does not weaken this boundary because routing/status separation is enforced by the bridge and event contract rather than by generated prose.

## Development / release flow

Use `dev` for normal page/UI changes. These do not deploy Vercel and are read live by the deployed server.

Promote to `main` only when the stable server boundary changes: Python/backend routes, auth/session behavior, middleware, inference plumbing, deployment configuration, or other server-owned contracts.

`/tmp` remains ephemeral and instance-local; it is not the durable live-page source of truth. GitHub `dev` is.

## Contracts and records

- `docs/contracts/SWRLZ_LIVE_PAGE_RUNTIME_V1.md`
- `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md`
- `docs/contracts/SWRLZ_HOT_RUNTIME_V1.md`
- `docs/contracts/SWRLZ_CONTROL_PLANES_V1.md`
- `SWRLZ_VERCEL_CHAT_CHANGELOG.md`
- `docs/releases/`

## Revision history

2.0.5 unified the API runtime and colocated Gate 5 with R39 load/verify. 2.0.6 added response-safe chunked downloads. 2.0.7 hardened Admin token normalization and diagnostics. 2.1.0 added the R299-derived Vercel Chat bridge/UI. 2.1.1 introduced Dragon Jester Admin. 2.1.2 added `/live/*`, runtime Chat-token override, and dev deployment suppression. 2.1.3 paired Chat/Admin control planes. 2.1.4 wired local R39 inference. 2.1.5 resolved producer-specific BPE tokenizer labels. 2.1.6 added automatic R39 initialization and heartbeat-protected streaming. 2.1.7 added narrow hot Chat/R39 overrides. 2.1.8 introduced the live Page Manager/source layer. 2.1.9 repaired unified live/UI boundaries. 2.1.10 added query-decoration tolerance. 2.1.11 made Chat status non-blocking and added initial Admin-session bootstrap. 2.1.12 repaired per-request Admin auth. 2.1.13 made live page reads GitHub-backed and instance-independent. 2.1.14 made explicit Chat sessions stateless across Vercel instances. 2.1.15 made normal same-origin Chat authorization server-managed with an HttpOnly signed cookie while keeping the permanent Chat secret server-side. **2.1.16 reduces local R39 reference prefill overhead with larger bounded dequant batches, small-tensor decode caching, and compact stock local prompt directives.**
