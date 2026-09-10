# §wyrlz Unified Vercel Server

Server revision: **2.2.0**  
Chat/runtime hotfix rules: **SWRLZ_HOTFIX_RULES.md**  
Production deployment: **https://swrlzkamico-o3nu.vercel.app**  
Checkpoint lineage: `INT-VERCEL-CHAT-001A`

This repository is the unified §wyrlz Vercel server. The stable `main` branch provides the deployed loader/infrastructure; the `runtime` branch is the durable live application source for hot-editable pages, Chat, page-owned assets, and runtime LALM/inference.

## ⚠️ READ FIRST FOR CHAT / PAGE / LALM WORK

**Canonical hotfix instructions:** `SWRLZ_HOTFIX_RULES.md`

Normal runtime change:

`edit runtime → commit → reload/request → verify → NO VERCEL DEPLOY → NO SERVER RESTART`

Do not use `dev` for Chat/runtime hotfixes. Do not replace a complete page for a one-line change. Do not treat `/tmp` as durable source.

## Control planes

- `/server/` — stable infrastructure, routing, deployment/base-version receipts, and server capabilities.
- `/lalm/` — LALM/R39 status and verification surfaces.
- `/api/chat` — stable conversational transport surface.
- `/api/admin` — Admin workbench.
- `/live/` — runtime live launchpad/source surface.

## Runtime ownership

The `runtime` branch owns the live application source:

- Chat HTML/UI
- Chat JavaScript and CSS
- stream UI and Chat enhancements
- Chat version display
- runtime page routes via `runtime_pages/manifest.json`
- runtime page assets
- runtime-loadable LALM/R39 inference code

These changes are designed to be served from current `runtime` source without a Vercel deployment or server restart.

## Stable boundary / deployment ownership

`main` owns the stable infrastructure that loads and serves `runtime`.

A Vercel deployment is required when changing the stable boundary itself, such as:

- Python API routes or middleware
- authentication/session/security behavior
- runtime loader/source-resolution logic
- runtime hydration/sync mechanism
- `vercel.json` or build/runtime configuration
- new bundled dependencies or stable server capabilities
- a capability the existing runtime loader cannot serve

## Durable vs ephemeral state

GitHub `runtime` is durable source of truth. `/tmp`, memory caches, loaded Python module objects, and Vercel instance state are disposable execution/cache state. A restart/cold start must recreate active runtime state from the durable `runtime` source.

## LALM / R39 runtime

The runtime-loadable LALM/R39 source belongs to `runtime`. Changing inference internals does not require changing the Chat version unless user-facing Chat behavior or protocol actually changes.

Authoritative raw R39 SHA-256 currently recorded by the project:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

## Page lifecycle

Add/remove/update pages through the runtime source and `runtime_pages/manifest.json`. See `HOT_RUNTIME_UPDATE_GUIDE.md` on `runtime` for the exact workflow.

## Verification

Before declaring a runtime hotfix complete:

- fetch the current target file first;
- make the smallest targeted edit;
- commit to `runtime`;
- confirm no Vercel deployment was created;
- request/reload the affected route;
- verify the live response comes from current `runtime` source;
- verify browser behavior/version;
- verify no legacy injector or loader overrides the change.

## Key records

- `SWRLZ_HOTFIX_RULES.md` — canonical future-§wyrlz hotfix instructions.
- `HOT_RUNTIME_UPDATE_GUIDE.md` — runtime workflow and page lifecycle guide.
- `docs/contracts/SWRLZ_HOT_RUNTIME_V1.md`
- `docs/contracts/SWRLZ_LIVE_PAGE_RUNTIME_V1.md`
- `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md`
- `SWRLZ_VERCEL_CHAT_CHANGELOG.md`
