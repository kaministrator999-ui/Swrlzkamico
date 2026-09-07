# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.1.10**  
Chat UI revision: **1.3.4**  
Checkpoint lineage: `INT-VERCEL-CHAT-001A`

This repository is the unified §wyrlz Vercel SERVER. The stable deployment owns authentication, API/security contracts, filesystem confinement, Chat stream semantics, R39 transport, and bundled fallbacks. UI pages and the narrow hot R39 engine can iterate independently through the non-deploying `dev` branch.

## Current control planes

- `/api/admin` — Dragon Jester Admin workbench.
- `/api/chat` — §wyrlz Chat.
- `/api/pages` — live page source/runtime manager.
- `/api/hot` — narrow hot Chat/R39 runtime control.
- `/live/` — runtime launchpad/index.
- `/api/health` — server health receipt.
- `/api/lalm` — R39 load/transport state.

## Live page runtime — 2.1.10

Durable page source is kept on `dev`, where Vercel deployment is disabled. The running server can sync that source into instance-local `/tmp`, edit it immediately, and optionally push the accepted runtime copy back to `dev` without deploying the server.

Core mappings:

- `web/admin.html` -> runtime Admin -> `/api/admin`
- `web/chat.html` -> runtime Chat -> `/api/chat`
- `web/chat_enhancements.css` -> runtime Chat CSS
- `web/chat_enhancements.js` -> runtime Chat JS
- `runtime_pages/index.html` -> `/live/`

Any additional supported files under `runtime_pages/pages/` are discovered automatically and published below `/live/pages/`.

`/api/pages` provides the authenticated manager for `dev -> runtime` synchronization, runtime read/edit/save, runtime -> `dev` push-back, and page/source/runtime/live-URL receipts. GitHub write credentials remain server-side. Token precedence is runtime `/tmp/swrlz-admin/runtime/github-content-token.txt`, then `SWRLZ_GITHUB_CONTENT_TOKEN`, then `SWRLZ_GITHUB_TOKEN`; raw secret values are never returned to the browser.

`/tmp` remains ephemeral and instance-local. **GitHub `dev` is the durable page source-of-truth.**

### 2.1.9 / 2.1.10 boundary repairs

2.1.9 moved `/live/` onto the unified parent app, added a parent Chat UI guard, and added the credential-status Page Manager. 2.1.10 makes those parent UI guards tolerant of harmless URL query decoration such as tracking parameters. `/api/chat` still preserves functional `action=` behavior, while unrelated query keys no longer bypass the hot UI layer. `/api/pages` serves the current manager for the exact GET path regardless of harmless query decoration.

## Hot runtime development

The separate `/api/hot` boundary remains for the narrow R39 engine and Chat runtime override:

`runtime Chat override -> bundled Chat fallback`

`runtime R39 engine override -> bundled R39 fallback`

Stable auth/API/security changes still require a `main` deployment. Page/UI work and approved hot inference experiments can remain on `dev` and be pulled into the live instance.

## Chat 1.3.4

Chat keeps browser-local threads, streamed NDJSON evidence, Truth Firewall separation, Stream Camera copy/clear, generation controls, context inspection, retry/fork, and Send to Workbench. The 1.3.4 UI removes the enhancement-layer interception that was fighting the base New/Delete thread controls, repairs the mobile drawer stacking by moving the scrim into the app stacking context, makes LOCAL_R39 runtime status authoritative in the sidebar, and adds a persistent Chat/Server version receipt at the bottom of the drawer.

## Local R39 inference

The proven transport path remains:

`Forge chunks -> wrapper ZIP -> nested verified R39 gzip -> raw R39 -> SHA-256 -> Gate 5`

The compute path remains:

`SWRLZX TOC -> TOKENIZER + TENSOR_DIRECTORY + TENSOR_DATA -> local executor -> NDJSON DELTA`

Authoritative raw R39 SHA-256:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

The current reference engine supports the canonical LFM2 profile and quantized tensor readers used by this lineage. Blocking local compute is wrapped with periodic heartbeat STATUS events. The heartbeat idle interval restarts after each real engine/progress event; this protects the connection but does not reset Vercel's hard maximum function duration.

## Chat routing / Truth Firewall

Routing is deterministic:

`complete proof-bound upstream -> upstream proxy`

`no upstream URL -> LOCAL_R39`

`upstream URL present but incomplete proof config -> explicit failure`

Only `DELTA.text` may enter assistant prose. STARTED, STATUS, ROUTE, RESET, heartbeat, timing, blockers, failures, model identity, and terminal metadata remain operational evidence.

## Development / release flow

Incremental page/UI work goes to `dev`. `vercel.json` disables Vercel deployment for `dev`. Stable SERVER releases are promoted deliberately to `main`. Normal page/UI edits should not require promotion: update `dev`, then sync through `/api/pages`.

## Contracts

- `docs/contracts/SWRLZ_HOT_RUNTIME_V1.md`
- `docs/contracts/SWRLZ_LIVE_PAGE_RUNTIME_V1.md`
- existing Chat/R39/runtime contracts remain authoritative for their respective boundaries.

## Revision history

2.0.5 unified the API runtime and colocated Gate 5 with R39 load/verify. 2.0.6 added response-safe chunked downloads. 2.0.7 hardened Admin token normalization and diagnostics. 2.1.0 added the R299-derived Vercel chat bridge/UI. 2.1.1 introduced Dragon Jester Admin. 2.1.2 added `/live/*`, runtime Chat-token override, and dev deployment suppression. 2.1.3 paired Chat/Admin control planes. 2.1.4 wired local R39 inference. 2.1.5 resolved producer-specific BPE tokenizer labels. 2.1.6 added automatic R39 initialization and heartbeat-protected streaming. 2.1.7 added narrow hot Chat/R39 runtime overrides. 2.1.8 / Chat UI 1.3.4 promoted Admin, Chat, the runtime index, and future pages into a source-managed live page layer. 2.1.9 repaired the unified `/live/` and parent UI boundaries. **2.1.10 makes those UI guards tolerant of harmless query decoration so shared/tracked URLs cannot fall back to stale handlers.**
