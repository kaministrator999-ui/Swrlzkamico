# §wyrlz Server Roadmap & Version Ledger

**READ WITH:** `SWRLZ_HOTFIX_RULES.md`  
- **Current overall server baseline:** `2.3.226`
**Current Chat component:** `1.5.60`  
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

Before implementing each feature/fix/optimization/refactor, the event must also perform the Project Start **Pre-Feature Architecture Reconciliation**: inspect the selected/affected architecture and existing related work, confirm the canonical owner/integration path, and avoid introducing duplicate or competing implementations. The reconciliation result is recorded with the event.

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
- Established the mandatory Pre-Feature Architecture Reconciliation so every feature checks the affected architecture and existing related implementations before implementation, reuses/reconciles canonical owners instead of stacking duplicate feature paths, and records that reconciliation in the roadmap/release lineage.
- Established generated Ice Dragon artwork ownership so the adult wallpaper can replace the legacy Frozen Sanctum procedural chamber art instead of stacking on top of it.
- Consolidated Ice Dragon theme ownership so future theme visual work has one canonical CSS owner and one deterministic asset hydrator instead of multiple competing wallpaper/style layers.
- Established a frontend-first Chat boot boundary: the local shell/theme renders independently while account, bridge, server, and LALM connectivity settle asynchronously.
- Added persistent device-side Ice Dragon asset caching, including an optional idle-time 4320x7680 cached WebP promotion tier on capable devices.
- Consolidated Android Chat geometry so the early shell and account identity module no longer independently own workspace/message/composer widths; runtime viewport CSS is the post-boot geometry authority while the early shell remains full-width and neutral.
- Routed Chat's visible component versions through the live `VERSION.txt` index and its mapped module files, removing the raw-GitHub version read as a separate version-delivery path.
- Made the Android phone thread drawer consume the full visual viewport instead of intentionally leaving a narrow underlying-Chat strip visible.

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
CHECK selected/affected architecture + existing related implementations
        ↓
CONFIRM canonical owner / integration path; reconcile duplicate or competing work
        ↓
SMALLEST targeted edit through the reconciled owner
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
UPDATE ROADMAP / RELEASE RECORD, INCLUDING ARCHITECTURE RECONCILIATION
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

### Server 2.3.226 — Mandatory pre-feature architecture reconciliation governance

**Status:** engineering-contract and roadmap source complete.  
**Affected module versions:** none; this event advances the overall Server/governed-project lineage only.  
**Deployment / restart:** NONE.

Project Start now requires a brief but complete architecture reconciliation before implementation of each feature, fix, optimization, refactor, subsystem, or substantial behavior/UI addition. The check begins with the selected/affected architecture and expands far enough to find existing implementations that share the same owner, source of truth, state, lifecycle, route, protocol, storage, authentication boundary, cache, loader, UI surface, tool/action path, version authority, or other directly interacting responsibility.

The new rule requires future work to search for existing/partial/retired implementations, identify neighboring behavior that shares the same architecture, deliberately choose reuse/extension/refactor/retirement rather than adding a parallel mechanism, and resolve competing ownership before implementation. Every governed event must record a brief architecture-reconciliation note alongside the existing Server/module version, verification, deployment, and progress record.

**Architecture reconciliation for this event:** checked the canonical Project Start Mask/Human/Brain ownership rules, module/version authority rules, Server roadmap/version workflow, current deployment workflow, and repository search for an existing dedicated architecture-reconciliation gate. Existing ownership rules defined where behavior belongs but did not require a per-feature inspection for overlapping or partial implementations. The canonical Project Start contract was therefore extended instead of creating a competing policy document.

**Version/concurrency:** the initial observed runtime Server authority had already advanced beyond the previous conversational baseline; the authority was re-read immediately before assignment at `2.3.225`, so this event correctly assigned Server `2.3.226` rather than a stale planned number. No component authority changed for this governance-only event.

**Deployment verification:** current production deployment is still based on `main` commit `8eff92be6b251fa05e708283f72fe6d7e7392f71`, while `main` had already advanced through later commits without automatic redeployment. The production workflow only pushes on `.deploy/REQUEST.txt` or explicit workflow dispatch, so these documentation commits do not cross the deployment approval boundary.

**Lineage:** Server authority commit `758e0ce13cc609e8a01f019c55a41eb25cc97104`; Project Start contract commit `d13c21fb1410ce51b1ed6be451afe8d925d8936e`.

### Server 2.3.211 — Chat live version authority + full phone drawer

**Status:** runtime source complete; rendered-device verification pending.  
**Chat:** `1.5.60`  
**Deployment / restart:** NONE.

Chat's visible version footer now begins at the production live `VERSION.txt` index and resolves the mapped module files through the same `/live/` runtime source path as the running Chat. This removes raw GitHub as a separate version-display delivery path while preserving `VERSION.txt` as the routing authority and each mapped `versions/*.txt` file as the value authority. Version values are refreshed on focus/visibility so a returning Chat surface converges without relying on an old footer value.

The Android phone thread drawer now uses the full visual viewport width and removes the narrow right-side scrim/underlying-Chat strip. This is a targeted interface correction to the defect visible in the device screenshot; larger desktop/tablet sidebar behavior remains separately governed.

**Runtime lineage:** Chat version routing `e222d08255e59cf252caeda018b8390df42c41c7`; phone drawer correction `bf13b411c47206118c996294937c61c5e75efeb0`; Server authority `81d8107e422677af523b6fe32ceff7645529ba07`; Web Chat authority `69e9bf5023c1455deeeb1ab26ecf57609cbc8d6c`.

### Server 2.3.210 — Chat single geometry authority correction

**Status:** source complete; superseded by 2.3.211 interface correction.  
**Chat:** `1.5.59`  
**Deployment / restart:** NONE.

The previous visual fix updated the canonical runtime viewport stylesheet, but Android first-paint and account identity layers still carried independent layout overrides. This event removes the account module's workspace/message/composer geometry injection and makes the early Ice Dragon shell full-width/neutral. `chat_mobile_viewport_fix.css` remains the runtime post-boot authority for content gutters and mobile geometry. Google identity/profile-photo behavior remains in the account module and was not moved into layout authority.

**Runtime lineage:** early-shell correction `5055c5bb3f7e24888c9d36749d1668649ba7edac`; account/layout separation `8542a779662692534856ed0c4f4559945ec2bade`; Server authority `98c00fc28f691fa1ef161285bebcf3d02fbb1d60`; Web Chat authority `790d4dacedfa79246a9bafe6dc2fe9a92dde2429`.

### Roadmap reconciliation note

Historical release entries omitted from this compact main-branch ledger remain in Git history and runtime release records. This header and Server 2.3.226 governance event are reconciled to the authoritative runtime Server version at event time rather than fabricating missing intermediate detail.
