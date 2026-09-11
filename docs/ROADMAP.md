# §wyrlz Server Roadmap

## Current release

**Server v2.3.12**

This runtime event fixes Git-triggered Vercel deployment control for the `runtime` branch itself.

### Module state

- **Server runtime v2.3.12** — deployment-control configuration corrected on the runtime branch.
- **Chat v1.4.10** — unchanged.
- **LALM UI v1.0.0** — unchanged.
- **LALM engine v2.1.18** / revision `2.1.18-hot-boundary-v9-effective-receipt` — unchanged.

## Server v2.3.12 — 2026-09-10

### Accomplishment

- Corrected the `runtime` branch's own `vercel.json` so Git pushes from that branch no longer request Vercel Git deployments.
- The root cause was branch-local configuration drift: `main/vercel.json` had been changed to `git.deploymentEnabled=false`, but `runtime/vercel.json` still contained a branch map that disabled `dev`, explicitly enabled `main`, and did not disable `runtime` itself.
- Because Vercel builds a pushed branch using that branch's configuration, runtime commits continued creating Preview deployments even though `main` had the global disable rule.
- `runtime/vercel.json` now also uses `git.deploymentEnabled=false`, matching the intended repository-wide manual-deployment architecture.

### Verification / failure lineage

- Vercel deployment history confirmed Server v2.3.11 runtime commits created Preview deployments on the `runtime` branch.
- This corrects the earlier mistaken release note that automatic Git deployments were already disabled for runtime work.
- The first commit that changes `runtime/vercel.json` may itself still create one final Preview deployment because it is evaluated from the branch state that existed before the commit took effect.
- The subsequent Server v2.3.12 version-authority and roadmap commits are the verification actions: they should not create new Vercel deployments if the correction is effective.

### Deployment state

- **Production deployment:** NONE.
- **Server restart:** NONE.
- **Manual Vercel deployment:** NONE.
- Git-triggered deployment suppression is now configured on both `main` and `runtime`.

## Server v2.3.11 — 2026-09-10

### Accomplishment

- Chat no longer has to visibly fall back to a yellow/pending state on every refresh when that same browser tab has already verified the LALM as ready moments earlier.
- A recent verified-ready state is restored immediately from session state, while `/api/lalm/status` is still checked in the background so the UI does not blindly trust stale readiness forever.
- Status polling was reduced from every 15 seconds to every 60 seconds, with an additional check when the browser regains focus.
- The stable deployed server already warms the R39 model during each worker cold start through the startup warm path. This release did not alter that LALM engine behavior; it changed Chat readiness presentation.

### Verification evidence

- Live `/api/lalm/status` reported `interactiveReady: true` and `warmModelResident: true` with the runtime override/native backend active.
- Vercel deployment history later showed that the runtime commits for this event generated Preview deployments. That deployment behavior was unintended and is corrected by Server v2.3.12.

## Server v2.3.10 — 2026-09-10

### Purpose

- Incremented only the canonical Server runtime version authority to verify that Chat could dynamically display `v2.3.10` without changing Chat code.

### Verification state

- User-side verification confirmed Chat dynamically displayed Server runtime `v2.3.10`.
- The version-authority architecture itself worked correctly.

## Server v2.3.9 — 2026-09-10

### Architecture established

- Replaced the single value-bearing root `VERSION.txt` with an index that maps stable module IDs to independent canonical files under `versions/`.
- Added dedicated version authorities for Server runtime, Server UI, Web Chat, stream contract, LALM UI, LALM engine, Admin Web, Google Account architecture, Client APK, and Server APK.
- Chat resolves displayed Server runtime / Chat / Stream / LALM versions from the corresponding per-module files.
- Unverified APK versions remain `UNASSIGNED` instead of being fabricated.

## Earlier release lineage

The complete pre-2.3.9 lineage remains preserved in repository history. Server v2.3.8 and earlier established the initial shared registry, synchronized Chat/LALM status presentation, browser loading-loop corrections, runtime hot-update boundaries, and the mandatory roadmap/version law.

## Mandatory roadmap/version law

Every server development event gets a new overall Server runtime authority when project state changes, including failed attempts.

Every module actually changed gets its own version increment. A module that did not change keeps its version.

`VERSION.txt` is the module-authority router. It maps stable module IDs to their own `versions/<module-id>.txt` files and does not duplicate their values.

Consumers fetch the owning module authority when they need a version for display or update comparison. They do not maintain another module's version manually.

Every event records what changed, affected module versions, failed attempts where applicable, verification state, deployment/restart state, and relevant lineage.
