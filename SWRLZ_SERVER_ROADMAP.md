# §wyrlz Server Roadmap & Version Ledger

**READ WITH:** `SWRLZ_HOTFIX_RULES.md`  
**Current overall server baseline:** `2.3.3`  
**Current Chat component:** `1.4.3`  
**Current LALM UI component:** `1.0.0`  
**Release policy:** every intentional update from this point forward gets an overall Server release/version entry plus independent component version changes where applicable.

## Version model

§wyrlz uses two levels of versioning:

1. **Overall Server version** — the release/version of the complete deployed server architecture.
2. **Independent component versions** — Chat, LALM/R39, Server/Infrastructure, Admin, and other independently maintained surfaces.

An update may change one component or several components, but the roadmap records the **overall Server version for every release** and records each component's version separately.

### Rule from here forward

**Every completed product update gets a new overall Server version and an update note.**

Component versions advance independently when that component actually changes. A component version does not need to advance merely because another component changed.

## Baseline reconciliation — Server 2.3.2 → 2.3.3

The live production screenshot established that the deployed stable server is currently reporting **Server 2.3.2** while the roadmap document was still carrying the older 2.2.0 baseline. The repository's `main/api/index.py` independently confirmed `VERSION = "2.3.2"`. This release closes that documentation/version-ledger drift without inventing missing intermediate release history.

Server `2.3.3` is the next versioned server development event. The event adds startup-time LALM/R39 hydration and readiness probing so a new server worker warms the inference engine before Chat traffic reaches it.

## What has been accomplished

- Established the unified §wyrlz Vercel server and separated major control-plane responsibilities.
- Established runtime-owned Chat/page source delivery.
- Established the `runtime` branch as the durable live application source of truth for hot application changes.
- Established `main` as the stable loader/infrastructure boundary.
- Built runtime page manifest routing through `runtime_pages/manifest.json`.
- Enabled runtime-owned HTML, JavaScript, CSS, page assets, and runtime-loadable LALM/inference updates without ordinary Vercel redeployment.
- Added cache-busted runtime source retrieval so current runtime commits are visible to new requests.
- Removed obsolete page-runtime, live-route, Chat UI injector, and legacy Chat hot-asset layers that could override runtime behavior.
- Restored Chat to the known-good pre-Google-account UI lineage when required and preserved the separate Google/account backend infrastructure.
- Recovered from the accidental Chat page overwrite by restoring the known-good runtime commit before continuing with the targeted version change.
- Established Chat stream UI ownership on `runtime`.
- Established runtime-owned Chat version display rather than a hardcoded version injected by `main`.
- Added the canonical hotfix rules and durable runtime update guide.
- Added the third project-start version/module evolution contract as the engineering curriculum foundation for the future programming-side LALM.
- Verified that runtime-only files can be created/changed/removed and served by production without creating a new Vercel deployment.
- Established the durability rule: GitHub `runtime` is source of truth; `/tmp`, memory, browser cache, and Vercel instance state are disposable.

## Component ownership

| Component | Source of truth | Versioning rule |
|---|---|---|
| Overall Server | `main/api/index.py` + this roadmap | Advances on every server development event |
| Chat | `runtime/web/chat*` and related runtime Chat assets | Advances when Chat UI/protocol/behavior/version plumbing changes |
| Chat Stream UI | `runtime/web/chat_stream_focus.js` and related assets | Advances when stream behavior changes |
| LALM/R39 | runtime LALM/inference source | Advances when LALM/inference behavior changes |
| Server/Infrastructure | `main/api/*`, deployment/configuration | Advances with stable infrastructure releases; this release is represented by overall Server 2.3.3 |
| Page system | `runtime_pages/manifest.json` + runtime page assets | Advances when page routing/system behavior changes |
| Admin | Admin-owned runtime/stable assets | Advances when Admin behavior changes |

## Hot-update boundary

These changes normally require **no Vercel deployment and no server restart**:

- Chat HTML/UI changes on `runtime`.
- Chat JavaScript changes on `runtime`.
- Chat CSS changes on `runtime`.
- Stream UI/enhancement changes on `runtime`.
- Chat version-display changes on `runtime`.
- Runtime page additions/removals through the runtime manifest.
- Runtime-owned page asset changes.
- Runtime-loadable LALM/R39/inference changes supported by the existing loader.

Procedure:

```text
FETCH current runtime file
        ↓
SMALLEST targeted edit
        ↓
COMMIT to runtime
        ↓
RELOAD / REQUEST
        ↓
VERIFY runtime source + behavior
        ↓
RECORD overall Server version + component version changes
```

## Deployment boundary

A Vercel deployment is required when the **stable loader/infrastructure** changes, including:

- Python API routes or middleware.
- Authentication/session/security boundaries.
- Runtime source-resolution/loading logic.
- Runtime hydration/synchronization mechanism.
- `vercel.json` or deployment/build configuration.
- New stable dependencies/capabilities required by the runtime loader.
- Any change that the existing deployed loader cannot serve from `runtime`.

Those changes belong on `main`, followed by a deployment and production verification.

## Release ledger

### Server 2.2.0 — Architecture baseline

**Status:** historical baseline  
**Chat:** `1.4.2` current hot-runtime Chat baseline at that time  
**Purpose:** stable server/runtime separation and durable hot-update architecture.

Key milestones are recorded above under “What has been accomplished.”

### Server 2.3.2 — Verified deployed baseline

**Status:** verified repository/deployed baseline before this event  
**Chat:** `1.4.3`  
**LALM UI:** `1.0.0`  
**Deployment:** existing production baseline  

**Reconciliation notes:**
- `main/api/index.py` reported `VERSION = "2.3.2"`.
- The live Chat screenshot reported `Server v2.3.2`, `Chat v1.4.3`, and `LALM v1.0.0`.
- The roadmap itself had not yet been advanced beyond 2.2.0; this entry records the verified 2.3.2 baseline without fabricating the missing historical release notes.

### Server 2.3.3 — Startup LALM Warm + Readiness

**Status:** implementation complete; deployment required for production activation  
**Chat:** `1.4.3` unchanged  
**LALM UI:** `1.0.0` unchanged  
**LALM/R39 engine:** unchanged; startup lifecycle now invokes its existing readiness probe  
**Server/Infrastructure:** changed; startup lifecycle integration  
**Deployment:** REQUIRED

**Update notes:**
- Added server-start LALM/R39 hydration from the durable `runtime` branch.
- Added server-start readiness probing before Chat traffic is handled.
- Populated the existing Chat/LALM readiness state from the startup probe so `/api/lalm/status` can report ready immediately instead of waiting for the first Chat interaction to trigger the probe.
- Kept the existing readiness path as a fail-open fallback if runtime hydration/probing fails.
- Reconciled the roadmap's stale 2.2.0 baseline to the verified 2.3.2 production baseline, then assigned this development event Server 2.3.3.
- No Chat component behavior change was made in this event.

**Verification plan:**
- Confirm production reports `Server v2.3.3`.
- Confirm `/api/lalm/status` reports readiness as checked/ready immediately after a fresh worker starts.
- Confirm Chat sidebar status no longer needs the first-message path to perform the initial LALM probe.
- Confirm first user message can enter a warm R39 model without the prior cold model-load delay.
- Confirm runtime hydration still sources `runtime` and does not create a competing Chat/runtime source.

**Failure/rollback:**
- Startup warm is fail-open. If hydration or probing fails, the existing lazy readiness/inference path remains available.
- No prior release history was rewritten; the 2.3.2 baseline is explicitly marked as a reconciliation point.

## Required release-entry format

For every update after `2.2.0`, append a new section:

```markdown
### Server X.Y.Z — Short release name

**Status:** complete
**Chat:** X.Y.Z
**Chat Stream:** X.Y.Z
**LALM/R39:** X.Y.Z
**Server/Infrastructure:** X.Y.Z
**Admin:** X.Y.Z
**Page Runtime:** X.Y.Z
**Deployment:** NONE / REQUIRED

**Update notes:**
- What changed.
- Why it changed.
- What was intentionally left untouched.
- Verification performed.
- Any migration/rollback note.
```

## Non-negotiable release discipline

- Never claim a release is complete without recording it here.
- Never silently change the overall Server version without a roadmap entry.
- Never bump a component version just to make numbers move; bump it because that component changed.
- Never deploy solely because a runtime component changed.
- Never allow `main` and `runtime` to become competing sources of truth for the same page-owned behavior.
- Never replace a complete page when a targeted file-level change is sufficient.
- Always preserve the known-good runtime state before risky edits.
- If a stable infrastructure deployment is required, verify that it still loads the current `runtime` source afterward.

## Canonical relationship

```text
                         §wyrlz RELEASE
                              │
                       Server X.Y.Z
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
        Chat               LALM/R39         Server/Infra
       X.Y.Z                X.Y.Z               X.Y.Z
          │                   │                   │
          └──────────── independent component ───┘

main    = stable infrastructure / deployed boundary
runtime = durable live application / hot-update source
```

**Bottom line:** from this point forward, every intentional §wyrlz update is treated as a real release: increment the overall Server version, update only the component versions that actually changed, write release notes here, and use the hotfix/deployment boundary defined in `SWRLZ_HOTFIX_RULES.md`.
