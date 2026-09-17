# §wyrlz Server Roadmap & Version Ledger

**READ WITH:** `SWRLZ_HOTFIX_RULES.md`  
- **Current overall server baseline:** `2.3.210`
**Current Chat component:** `1.5.59`  
**Current Web Frontend component:** `1.0.3`  
**Current LALM UI component:** `1.0.0`  
- **Current Frozen Web Collector component:** `1.0.8`
- **Current Deployment Control component:** `1.0.6`
**Release policy:** every server development event gets an overall Server release/version entry plus independent component version changes where applicable, including unsuccessful attempts.

## Version model

§wyrlz uses two levels of versioning:

1. **Overall Server version** — the chronological development/release event of the complete server architecture.
2. **Independent component versions** — Chat, Web Frontend, LALM/R39, Server/Infrastructure, Admin, Deployment Control, and other independently maintained surfaces.

An update may change one component or several components, but the roadmap records the **overall Server version for every server development event** and records each component's version separately.

### Rule from here forward

**Every server development event receives a new overall Server version and an update note.** Component versions advance independently when that component actually changes. A component version does not advance merely because another component changed.

A failed attempt is still a real versioned event. The next correction receives the next overall Server version.

Version authorities are read at event entry and re-read immediately before version assignment/commit. If another instance/process advanced a relevant authority in between, the event must reconcile from the newest state instead of writing a stale planned version.

## What has been accomplished

- Established the unified §wyrlz Vercel server and separated major control-plane responsibilities.
- Established runtime-owned Chat/page source delivery.
- Established the `runtime` branch as the durable live application source of truth for hot application changes.
- Established `main` as the stable loader/infrastructure and engineering-contract boundary.
- Built runtime page manifest routing through `runtime_pages/manifest.json`.
- Enabled runtime-owned HTML, JavaScript, CSS, page assets, and runtime-loadable LALM/inference updates without ordinary Vercel redeployment.
- Added cache-busted runtime source retrieval so current runtime commits are visible to new requests.
- Removed obsolete page-runtime, live-route, Chat UI injector, and legacy Chat hot-asset layers that could override runtime behavior.
- Restored Chat to the known-good pre-Google-account UI lineage when required and preserved the separate Google/account backend infrastructure.
- Recovered from the accidental Chat page overwrite by restoring the known-good runtime commit before continuing with targeted version changes.
- Established Chat stream UI ownership on `runtime`.
- Established runtime-owned Chat version display rather than a hardcoded version injected by `main`.
- Added the canonical hotfix rules and durable runtime update guide.
- Added the third project-start version/module evolution contract as the engineering curriculum foundation for the future programming-side LALM.
- Added the explicit reporting rule that technical implementation belongs in the roadmap while conversational updates describe the human-visible accomplishment and resulting behavior.
- Verified that runtime-only files can be created/changed/removed and served by production without creating a new Vercel deployment.
- Established the durability rule: GitHub `runtime` is source of truth; `/tmp`, memory, browser cache, and Vercel instance state are disposable.
- Added explicit optimistic-concurrency handling for version authorities so multiple §wyrlz instances/agents do not overwrite each other's release lineage.
- Corrected deployment-gate logic so approval follows the actual deployment trigger/configuration instead of treating every `main` or documentation commit as deployment-capable.
- Established generated Ice Dragon artwork ownership so the adult wallpaper can replace the legacy Frozen Sanctum procedural chamber art instead of stacking on top of it.
- Consolidated Ice Dragon theme ownership so future theme visual work has one canonical CSS owner and one deterministic asset hydrator instead of multiple competing wallpaper/style layers.
- Established a frontend-first Chat boot boundary: the local shell/theme renders independently while account, bridge, server, and LALM connectivity settle asynchronously.
- Added persistent device-side Ice Dragon asset caching, including an optional idle-time 4320x7680 cached WebP promotion tier on capable devices.
- Consolidated Android Chat geometry so the early shell and account identity module no longer independently own workspace/message/composer widths; runtime viewport CSS is the post-boot geometry authority while the early shell remains full-width and neutral.

## Component ownership

| Component | Source of truth | Versioning rule |
|---|---|---|
| Overall Server | `runtime/versions/server-runtime.txt` + this roadmap lineage | Advances on every server development event |
| Web Frontend | `runtime/web/chat_frontend_boot.js`, frontend boot/cache assets, and `runtime/versions/web-frontend.txt` | Advances when static/local-first frontend architecture changes |
| Chat | `runtime/web/chat*` and `runtime/versions/web-chat.txt` | Advances when Chat UI/protocol/behavior/version plumbing changes |
| Chat Stream UI | `runtime/web/chat_stream_focus.js` and related assets | Advances when stream behavior changes |
| LALM/R39 | runtime LALM/inference source | Advances when LALM/inference behavior changes |
| Server/Infrastructure | `main/api/*`, deployment/configuration | Advances with stable infrastructure releases |
| Deployment Control | `runtime/versions/deployment-control.txt` + governing contract/deployment configuration | Advances when deployment-control behavior/rules change |
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
- Version-authority changes already supported by the stable loader.
- `main` documentation/contract commits when current deployment configuration/workflows prove those commits do not trigger deployment.

Procedure:

```text
FETCH current source + VERSION.txt router + affected authorities
        ↓
CAPTURE authority values/SHAs as event baseline
        ↓
SMALLEST targeted edit
        ↓
RE-READ affected authorities before version assignment
        ↓
CHANGED? → reconcile from newest authority
        ↓
ASSIGN NEW SERVER VERSION
        ↓
BUMP ONLY AFFECTED MODULES
        ↓
UPDATE CANONICAL VERSION SOURCES
        ↓
UPDATE ROADMAP / RELEASE RECORD
        ↓
COMMIT with stale-write protection
        ↓
RE-READ authorities + verify assigned versions
        ↓
RELOAD / REQUEST when applicable
        ↓
VERIFY source + behavior
        ↓
REPORT human-readable accomplishment to user
```

## Deployment boundary

Deployment capability is determined from the **current deployment configuration and workflows**, not from branch name alone.

A production deployment is required when an actual deployment action is needed to apply stable loader/infrastructure changes, including cases such as:

- Python API routes or middleware.
- Authentication/session/security boundaries.
- Runtime source-resolution/loading logic.
- Runtime hydration/synchronization mechanism.
- `vercel.json` or deployment/build configuration.
- New stable dependencies/capabilities required by the runtime loader.
- Any change that the existing deployed loader cannot serve from `runtime`.

Those changes generally belong on `main`, but a `main` commit is not automatically a deployment. Under the currently verified Vercel configuration, Git-based deployment is disabled. Therefore documentation-only `main` commits are non-deployment mutations unless another workflow/automation is proven to deploy them. If an explicit deployment action is required, it must pass the Deployment Approval Gate before execution.

## Release ledger

### Server 2.3.210 — Chat single geometry authority correction

**Status:** source complete; production-source verification pending.  
**Chat:** `1.5.59`  
**Deployment / restart:** NONE.

The previous visual fix updated the canonical runtime viewport stylesheet, but Android first-paint and account identity layers still carried independent layout overrides. This event removes the account module's workspace/message/composer geometry injection and makes the early Ice Dragon shell full-width/neutral. `chat_mobile_viewport_fix.css` remains the runtime post-boot authority for content gutters and mobile geometry. Google identity/profile-photo behavior remains in the account module and was not moved into layout authority.

**Runtime lineage:** early-shell correction `5055c5bb3f7e24888c9d36749d1668649ba7edac`; account/layout separation `8542a779662692534856ed0c4f4559945ec2bade`; Server authority `98c00fc28f691fa1ef161285bebcf3d02fbb1d60`; Web Chat authority `790d4dacedfa79246a9bafe6dc2fe9a92dde2429`.

### Roadmap reconciliation note

Historical release entries before this event remain in Git history. This header and current event are reconciled to the authoritative runtime version files at event entry rather than fabricating omitted historical detail.
