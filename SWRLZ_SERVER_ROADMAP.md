# §wyrlz Server Roadmap & Version Ledger

**READ WITH:** `SWRLZ_HOTFIX_RULES.md`  
**Current overall server baseline:** `2.2.0`  
**Current Chat component:** `1.4.2`  
**Release policy:** every intentional update from this point forward gets an overall Server release/version entry plus independent component version changes where applicable.

## Version model

§wyrlz uses two levels of versioning:

1. **Overall Server version** — the release/version of the complete deployed server architecture.
2. **Independent component versions** — Chat, LALM/R39, Server/Infrastructure, Admin, and other independently maintained surfaces.

An update may change one component or several components, but the roadmap records the **overall Server version for every release** and records each component's version separately.

### Rule from here forward

**Every completed product update gets a new overall Server version and an update note.**

Component versions advance independently when that component actually changes. A component version does not need to advance merely because another component changed.

Example:

```text
Server 2.2.1
├── Chat 1.4.3      ← changed
├── LALM/R39 1.x.x  ← unchanged
├── Server 2.2.1    ← infrastructure release
└── Admin 1.x.x     ← unchanged
```

If an update only changes Chat, the overall Server release still advances, while the Chat component receives its own version bump.

## Current baseline — Server 2.2.0

Server `2.2.0` is the established stable architecture baseline. The current hot runtime has Chat `1.4.2`.

### What has been accomplished

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
- Verified that runtime-only files can be created/changed/removed and served by production without creating a new Vercel deployment.
- Established the durability rule: GitHub `runtime` is source of truth; `/tmp`, memory, browser cache, and Vercel instance state are disposable.

## Component ownership

| Component | Source of truth | Versioning rule |
|---|---|---|
| Overall Server | `main` stable boundary + this roadmap | Advances on every intentional product release |
| Chat | `runtime/web/chat*` and related runtime Chat assets | Advances when Chat UI/protocol/behavior changes |
| Chat Stream UI | `runtime/web/chat_stream_focus.js` and related assets | Advances when stream behavior changes |
| LALM/R39 | runtime LALM/inference source | Advances when LALM/inference behavior changes |
| Server/Infrastructure | `main/api/*`, deployment/configuration | Advances when stable server boundary changes |
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

**Status:** established baseline  
**Chat:** `1.4.2` current hot-runtime Chat baseline  
**Purpose:** stable server/runtime separation and durable hot-update architecture.

Key milestones are recorded above under “What has been accomplished.” Future releases should use the format below.

### Server 2.2.1 — NEXT RELEASE

**Status:** reserved for the next completed update.  
**Chat:** record exact component version.  
**LALM/R39:** record exact component version.  
**Server/Infrastructure:** record exact component version.  
**Admin:** record exact component version.

**Update notes:**
- Add the exact user-requested change.
- Add verification result.
- Add whether deployment was required.
- Add any compatibility or migration notes.

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
