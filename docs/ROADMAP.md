# §wyrlz Server Roadmap

## Current release

**Server v2.3.11**

This runtime event improves how Chat presents LALM readiness on refresh while preserving the existing worker-start LALM warmup architecture.

### Module state

- **Server runtime v2.3.11** — runtime development lineage advanced for this event.
- **Chat v1.4.10** — readiness display now restores a recent verified-ready state immediately on refresh, then verifies it in the background.
- **LALM UI v1.0.0** — unchanged.
- **LALM engine v2.1.18** / revision `2.1.18-hot-boundary-v9-effective-receipt` — unchanged.

## Server v2.3.11 — 2026-09-10

### Accomplishment

- Chat no longer has to visibly fall back to a yellow/pending state on every refresh when that same browser tab has already verified the LALM as ready moments earlier.
- A recent verified-ready state is restored immediately from session state, while `/api/lalm/status` is still checked in the background so the UI does not blindly trust stale readiness forever.
- Status polling was reduced from every 15 seconds to every 60 seconds, with an additional check when the browser regains focus. This reduces unnecessary serverless status invocations while preserving freshness.
- The stable deployed server already warms the R39 model during each worker cold start through the startup warm path. This release does not alter that LALM engine behavior; it removes the repeated UI-level pending delay on ordinary Chat refreshes.

### Verification evidence

- Live production `/api/lalm/status` reported `interactiveReady: true` and `warmModelResident: true` with the runtime override/native backend active.
- The same live response reported `warmModelAgeSeconds: 0.0`, which is consistent with the status request reaching a freshly initialized serverless worker. Vercel can create/reuse workers independently, so worker residency cannot be treated as one permanent process.
- Expected browser result: after one successful readiness check, refreshing the same Chat tab should render green readiness essentially immediately, then verify asynchronously.

### Deployment state

- **Deployment:** NONE.
- **Server restart:** NONE.
- Runtime-only Chat change; automatic Git deployments remain disabled.

## Server v2.3.10 — 2026-09-10

### Purpose

- Increment only the canonical Server runtime version authority and observe whether the live Chat footer changes from Server runtime `v2.3.9` to `v2.3.10` without changing Chat code or redeploying the server.
- This specifically validates the new per-module version-file architecture rather than another UI implementation change.

### Changed

- `versions/server-runtime.txt`: `VERSION=2.3.9` → `VERSION=2.3.10`.
- No other module version was incremented because no other module implementation changed.
- No application code was changed.

### Verification state

- Canonical Server runtime authority is now superseded by `2.3.11`.
- User-side verification confirmed Chat dynamically displayed Server runtime `v2.3.10` without a server redeploy.
- **Deployment:** NONE.
- **Server restart:** NONE.

## Server v2.3.9 — 2026-09-10

### Changed

- Replaced the single value-bearing root `VERSION.txt` with an index that maps stable module IDs to independent canonical files under `versions/`.
- Added dedicated version authorities for Server runtime, Server UI, Web Chat, stream contract, LALM UI, LALM engine, Admin Web, Google Account architecture, Client APK, and Server APK.
- Existing unversioned structures were enrolled with explicit baselines where the repository has an identifiable structure; APK entries remain `UNASSIGNED` rather than inventing versions for artifacts that are not verified in this repository.
- Changed Chat version presentation so it reads the root index and then fetches the specific Server runtime, Chat, stream-contract, and LALM version files needed for display.
- Advanced Chat from `v1.4.8` to `v1.4.9` because its version-resolution behavior changed.
- Advanced overall Server from `v2.3.8` to `v2.3.9` because this is a new runtime development event.
- No LALM behavior, Admin behavior, Google account behavior, Server UI behavior, or APK artifact behavior changed in this event.
- Kept the implementation entirely on `runtime`; no stable-infrastructure deployment or server restart is required.

### Architecture rule established

- Every independently evolvable structure gets its own canonical version file.
- `VERSION.txt` is an index of module IDs to version-file paths, not a duplicate list of version numbers.
- A display or update checker fetches only the module file(s) it needs.
- New structures must receive and register a version authority when they enter the project lifecycle.
- Installed clients may compare their local version against the hosted canonical module file to decide whether an update is available.

### Verification state

- `VERSION.txt` points to per-module files rather than embedding component version values.
- Chat reads its displayed Server runtime / Chat / Stream / LALM versions from the corresponding per-module files.
- Existing module values were preserved where already established; unverified APK versions were not fabricated.
- **Deployment:** NONE required.
- **Server restart:** NONE.

## Earlier release lineage

The complete pre-2.3.9 lineage remains preserved in repository history. Server v2.3.8 and earlier established the initial shared registry, synchronized Chat/LALM status presentation, browser loading-loop corrections, runtime hot-update boundaries, and the mandatory roadmap/version law.

## Mandatory roadmap/version law

Every server development event gets a new overall Server runtime authority, including a failed attempt when the event changes project state.

Every module actually changed gets its own version increment. A module that did not change keeps its version.

`VERSION.txt` is the module-authority router. It maps stable module IDs to their own `versions/<module-id>.txt` files and does not duplicate their values.

Consumers fetch the owning module authority when they need a version for display or update comparison. They do not maintain another module's version manually.

Every event records what changed, affected module versions, failed attempts where applicable, verification state, deployment/restart state, and relevant lineage.
