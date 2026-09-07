# Server 2.1.17 — Automatic Hot Runtime Hydration

Date: 2026-09-07  
Chat UI: 1.3.13  
Production route: `https://swrlzkamico-o3nu.vercel.app`

## Purpose

Remove the normal manual Hot Sync step from the Chat/R39 development loop while preserving the stable Vercel deployment as the security/routing/fallback boundary.

## Stable-boundary change

The deployment-owned hot loader now registers a narrow refresher callback. Before serving a hot Chat asset or resolving the R39 engine, it checks whether the dev-backed runtime cache needs hydration/refresh.

This is intentionally request-driven instead of relying on a background watcher because Vercel serverless instances can freeze or be replaced between requests.

## Refresh behavior

- durable source: GitHub `dev`;
- runtime cache: `/tmp/swrlz-admin/runtime/hot/*`;
- first hot read on a fresh instance hydrates automatically;
- active instances refresh at most about once every 30 seconds;
- the fixed allowlist is fetched before mutation;
- SHA-256 comparison determines which files changed;
- changed files are written atomically;
- R39 module invalidation occurs only when `runtime_hot/r39_engine.py` changes;
- refresh failure preserves existing runtime state or bundled fallback.

## Manual controls

`POST /api/hot/sync?branch=dev` remains a force-refresh/recovery action and resumes auto refresh after an intentional suspension.

`POST /api/hot/clear` and rollback now suspend auto refresh so the operator can intentionally hold bundled fallback or a restored snapshot.

## Version receipt repair

The server-managed Chat authorization shim no longer owns or rewrites the visible Chat UI version. Version ownership remains with the hot Chat enhancement asset, preventing the observed `Chat v1.3.13` / footer `CHAT v1.3.12` split.

## Deployment requirement

This release changes the stable loader/runtime contract, so it requires one Vercel deployment. After 2.1.17 is live, ordinary Chat UI and hot R39 engine changes should remain on `dev` and become active automatically without further redeploys or normal Hot Sync button presses.

## Acceptance targets

1. Production reports Server `2.1.17`.
2. A fresh/cold instance with empty `/tmp` serves current `dev` Chat assets after the first active Chat request without manual sync.
3. `/api/hot/status` reports automatic refresh state and the current dev branch.
4. Updating `dev/web/chat_enhancements.js` becomes visible on an active instance within the refresh window without Vercel redeploy.
5. Updating `dev/runtime_hot/r39_engine.py` causes the next eligible refresh to replace the engine and invalidate the module cache.
6. The sidebar shows one authoritative Chat version receipt rather than the auth shim repainting an older version.
