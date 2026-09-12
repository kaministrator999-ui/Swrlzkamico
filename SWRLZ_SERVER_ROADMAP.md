# §wyrlz Server Roadmap & Version Ledger

**READ WITH:** `SWRLZ_HOTFIX_RULES.md`  
- **Current overall server baseline:** `2.3.91`
**Current Chat component:** `1.4.77`  
**Current Web Frontend component:** `1.0.3`  
**Current LALM UI component:** `1.0.0`  
- **Current Frozen Web Collector component:** `1.0.5`
- **Current Deployment Control component:** `1.0.3`
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

### Server 2.3.91 — Collector deployment recovery

**Deployment Control:** 1.0.3; **Collector:** 1.0.5 unchanged. **Deployment / restart:** NONE.

Production already has the stable collector host. Public readiness/UI/runtime-source receipts and anonymous rejection pass; private Blob provisioning succeeded during the original job's second attempt. That job failed before deployment because uv was missing. This event installs pinned uv in future manual builds, accepts compatible current collector versions, and removes the fragile page-check pipeline. Current collector tests and isolated revision-continuity regression pass. Authenticated production storage/collection acceptance remains pending secure admin sign-in.

The current authority was Server 2.3.90 even though this roadmap's header still showed 2.3.79. Intervening releases remain in their existing Git/release history; no missing event details are invented here. See [complete event receipt](docs/releases/SERVER_2.3.91_COLLECTOR_DEPLOYMENT_RECOVERY.md).


### Server 2.2.0 — Architecture baseline

**Status:** historical baseline  
**Chat:** `1.4.2`  
**Purpose:** stable server/runtime separation and durable hot-update architecture.

Key milestones are recorded above under “What has been accomplished.”

### Server 2.3.2 — Verified deployed baseline

**Status:** verified repository/deployed baseline before the 2.3.3 event  
**Chat:** `1.4.3`  
**LALM UI:** `1.0.0`  
**Deployment:** existing production baseline

**Reconciliation notes:**
- `main/api/index.py` reported `VERSION = "2.3.2"`.
- The live Chat screenshot reported `Server v2.3.2`, `Chat v1.4.3`, and `LALM v1.0.0`.
- The roadmap itself had not yet been advanced beyond 2.2.0; this entry records the verified 2.3.2 baseline without fabricating missing historical release notes.

### Server 2.3.3 — Startup LALM Warm + Readiness

**Status:** implementation complete and deployed  
**Chat:** `1.4.3` unchanged  
**LALM UI:** `1.0.0` unchanged  
**LALM/R39 engine:** unchanged; startup lifecycle now invokes its existing readiness probe  
**Server/Infrastructure:** changed  
**Deployment:** REQUIRED

**Update notes:**
- The server now prepares the runtime LALM/R39 engine during startup rather than waiting for the first Chat interaction to trigger readiness work.
- The existing readiness information is populated early so the LALM status endpoint can report actual startup readiness.
- The previous lazy path remains available as a fail-open fallback if startup preparation cannot complete.
- No Chat component behavior change was intended in this event.

**Verification state:** production reported Server `2.3.3`; LALM readiness was subsequently confirmed through the status endpoint.

### Server 2.3.4 — Chat reports authoritative local LALM readiness

**Status:** attempted; verification exposed stale live Chat enhancement delivery  
**Chat:** `1.4.4`  
**LALM UI:** `1.0.0` unchanged  
**LALM/R39 engine:** unchanged  
**Deployment:** NONE

**Update notes:**
- Changed the Chat status experience so it asks the authoritative LALM status service whether the local LALM is ready instead of treating lack of an upstream bridge as proof that local inference is still pending.
- This was intended to make the visible Chat status reflect the actual local LALM state.
- Production verification showed that the affected Chat enhancement asset was still serving an older cached/propagated version, so the intended browser behavior could not be accepted as verified.

**Failure/attempt record:** this event is preserved because the source change existed but the live browser asset did not deterministically reflect it.

### Server 2.3.5 — Move readiness display into canonical Chat version layer

**Status:** attempted; live propagation remained stale  
**Chat:** `1.4.5`  
**LALM UI:** `1.0.0` unchanged  
**LALM/R39 engine:** unchanged  
**Deployment:** NONE

**Update notes:**
- Moved the local-LALM readiness display into the canonical runtime Chat version layer so the status correction would be carried by an asset already proven to be served from `runtime`.
- The Chat interface was intended to show clear ready/warming/unavailable states based on the authoritative LALM status endpoint.
- Source verification confirmed the new `1.4.5` code on `runtime`, but production still returned the previous `1.4.4` asset at verification time.

**Failure/attempt record:** live propagation remained stale, so this event was not treated as a completed browser-visible fix.

### Server 2.3.6 — Remove Chat readiness feedback loop

**Status:** source implementation complete; live browser verification pending  
**Chat:** `1.4.6`  
**LALM UI:** `1.0.0` unchanged  
**LALM/R39 engine:** unchanged  
**Server/Infrastructure:** unchanged  
**Deployment:** NONE

**Update notes:**
- Corrected the Chat readiness handling after the previous attempt revealed that the status watcher could react to the same interface changes it was making.
- The readiness display now checks the authoritative LALM status in a bounded, controlled polling cycle instead of creating a self-triggering browser update loop.
- The Chat can therefore continue loading normally while still showing whether the local LALM is ready, warming, or unavailable.
- The underlying LALM engine and its readiness state were not changed by this event; the correction is in the Chat presentation/interaction layer.

**Failure/attempt lineage:**
- `2.3.4` introduced the authoritative local-LALM status display, but the live enhancement asset remained stale during verification.
- `2.3.5` moved the same correction into the canonical Chat version layer, but live propagation still showed the prior version during verification.
- `2.3.6` addresses the newly identified browser-side feedback-loop behavior and is therefore a separate versioned correction.

**Verification state:** runtime source and version records were verified in `runtime`; the final browser/live-asset verification remains open and must be completed before this event is considered fully closed.

**Relevant lineage:**
- Chat enhancement correction: `34f57ab433226fa0a0a8f47e929ae17dbc0ce19a`
- Canonical Chat version correction: `4952fef7519946b8b04dece24077d3353df737ae`
- Roadmap update on runtime: `1c11066dee7867cee464f2051eeeebf828cd1bb5`

### Roadmap reconciliation note — versions 2.3.7 through 2.3.55

The authoritative runtime version files advanced beyond this roadmap while several runtime events were performed without corresponding roadmap entries. This is a documentation/process gap, not permission to invent missing history.

Before Server 2.3.56, the authoritative repository state was verified as:

- Overall Server: `2.3.55`
- Web Chat: `1.4.50`
- Deployment Control: `1.0.0`

The omitted individual release notes for `2.3.7` through `2.3.55` are intentionally **not fabricated** here. They require a separate evidence-based reconciliation from commit/history records if full backfill is desired.

### Server 2.3.56 — Concurrency-safe project contract + trigger-based deployment gate

**Status:** complete; repository verification complete  
**Chat:** `1.4.50` unchanged  
**LALM UI:** `1.0.0` unchanged  
**Deployment Control:** `1.0.1`  
**Server/Infrastructure runtime behavior:** unchanged  
**Deployment:** NONE  
**Restart:** NONE

**Update notes:**
- Corrected the governing project rules so deployment approval follows the **actual deployment trigger/configuration** rather than treating every `main` or documentation commit as deployment-capable.
- Recorded the currently verified Vercel state where Git-based deployment is disabled, while requiring future agents to re-check deployment configuration/workflows each event instead of assuming this forever.
- Added an optimistic-concurrency version protocol: capture authoritative Server/module versions and SHAs at event entry, re-read them immediately before version assignment/commit, and reconcile if another instance/process advanced the project meanwhile.
- Added stale-write protection guidance using repository SHA/precondition checks where supported.
- Added post-commit authority verification before closing a release.
- Extended the programming-LALM curriculum so future §wyrlz instances learn source-of-truth revalidation, multi-agent coordination, deployment-trigger reasoning, and project-specific rule adaptation.
- No Chat code, LALM engine behavior, API runtime, or production deployment was changed by this event.

**Verification state:**
- Pre-change authority baseline verified from `VERSION.txt`, `versions/server-runtime.txt`, and `versions/deployment-control.txt`.
- Authorities were re-read before version assignment; the baseline remained `Server 2.3.55` / `Deployment Control 1.0.0`.
- Post-change authority verification confirmed `Server 2.3.56` and `Deployment Control 1.0.1`.
- `web-chat` was independently re-read and remained `1.4.50`.
- Current Vercel configuration was verified with Git deployment disabled; no deployment or restart was performed.

**Relevant lineage:**
- Server version authority: `7987049e99f7eb90ea1eb91aceed499b85acdfb8`
- Deployment Control authority: `1495c21ecdd285d3f77308ce516326fbc1624fd2`
- Project Start contract: `039d39ae1ef0ef46aa13e8e2ef642a049e2698e3`
- Hotfix contract: `b3af696c88a5aecd0a807ee9c530a82d78eda934`
- Version/module evolution contract: `ee1199dbed8b1bca106eb2f32f524e4e239b5122`

**Rollback/migration notes:**
- No runtime migration is required.
- If automatic Git deployments are enabled in the future, the deployment-gate decision must automatically re-evaluate against that new configuration.

### Server 2.3.57 — Adult Ice Dragon dedicated wallpaper layer

**Status:** attempted; browser verification showed legacy chamber art still visible  
**Chat:** `1.4.51`  
**LALM UI:** `1.0.0` unchanged  
**Deployment Control:** `1.0.1` unchanged  
**Deployment:** NONE

**Update notes:**
- Added a dedicated `.messages::before` adult-art wallpaper layer and kept conversation content above it.
- Browser verification showed the baby companion artwork loaded but the adult wallpaper still did not replace the old Frozen Sanctum chamber appearance.
- The failed visual result is preserved as a separate release event rather than rewritten as successful.

**Failure/attempt lineage:**
- The generated adult layer existed, but the base Ice Dragon theme still retained old `body::before` frost texture and `.messages` procedural background ownership.

**Relevant lineage:**
- Adult-art CSS layer commit: `ebdb9eefdea066fee3ca2d318aabd3bb2790883e`
- Server authority commit: `a0be0e86a6e11a42a5d9303158c4659812f1c946`
- Chat authority commit: `9d934a35b2bebec8200c986854cddc9e477fd972`

### Server 2.3.58 — Remove legacy chamber wallpaper ownership

**Status:** source complete; browser verification pending  
**Chat:** `1.4.52`  
**LALM UI:** `1.0.0` unchanged  
**Deployment Control:** `1.0.1` unchanged  
**Deployment:** NONE

**Update notes:**
- Identified both remaining legacy Ice Dragon artwork owners: the fixed `body::before` frost-line texture and the original `.messages` gradient/stripe chamber background.
- The generated-art layer now explicitly disables both legacy body pseudo-art layers and forces `.messages` itself to have no background.
- The adult dragon remains the sole wallpaper source through `.messages::before`; `.messages::after` is reserved only for readability shading and `.message-stack` remains above both.
- This deliberately removes the old Frozen Sanctum procedural wallpaper from the generated-art theme path instead of allowing it to remain visible beneath a failed or delayed adult image.

**Verification state:**
- Runtime source change committed and authoritative Server/Chat versions advanced after revalidation from `2.3.57 / 1.4.51`.
- Live browser visual confirmation is still required before this event is marked complete.

**Relevant lineage:**
- Generated-art ownership fix: `0e454bdd926ea61925ca343a9e7fb1cbe7ee7490`
- Server version commit: `0c1c74b7ba0443afd578e963dc6089dcf62b66cc`
- Chat version commit: `e47741237a3f79651af09c8ea5bd2d430c94bc38`

### Server 2.3.59 — Canonical Ice Dragon theme package ownership

**Status:** source/live asset delivery verified; browser visual verification pending  
**Chat:** `1.4.53`  
**LALM UI:** `1.0.0` unchanged  
**Deployment Control:** `1.0.1` unchanged  
**Deployment:** NONE  
**Restart:** NONE

**Update notes:**
- Traced the live Chat loader and confirmed the Ice Dragon theme had accumulated two CSS owners and two JavaScript owners on top of the generic Chat page.
- Consolidated all Ice Dragon visual ownership into `ice-dragon-theme.css`; the old generated-art stylesheet is now only a compatibility shim and can no longer compete for the chamber background.
- Reduced the theme controller to theme selection/state only.
- Replaced the previous Blob/fallback rendering chain with one deterministic asset hydrator that exposes the companion and adult JPEGs as direct data-image CSS variables.
- The chamber wallpaper now has one owner: the Ice Dragon theme's `.messages::before` layer. The adult asset hydrator only supplies the image value; it no longer creates competing DOM image/fallback layers.
- The existing stable Chat injector remains unchanged and continues loading the same runtime asset paths, so this migration required no deployment or restart.
- Generic/default Chat layout remains in the base Chat page; theme-specific appearance is now isolated to the Ice Dragon package path.

**Verification state:**
- Entry and pre-version authority checks both confirmed `Server 2.3.58 / Chat 1.4.52`; no concurrent version advance was detected.
- Live Vercel requests returned the new canonical Ice Dragon CSS and deterministic v10 asset hydrator from the `runtime` branch with no-store delivery.
- Final visual confirmation of the adult wallpaper in the browser remains pending user refresh/screenshot.

**Relevant lineage:**
- Canonical theme CSS: `33de5406308d30844384f32bd5582b9b82ff09d7`
- Duplicate art CSS retired: `f334e45c4408ea522719d520a86743577c205ec6`
- Theme controller state-only migration: `5ba9d947496b22a378df4fca104f2bf08cb76606`
- Deterministic asset hydrator: `c069915cfd2e5cd4e1845c5ef823fcd4a4311645`
- Server authority: `a14329f7c6cea5fe5e931661475b1b761f173489`
- Chat authority: `97362a41154b8743e9ff7ab631e425c8e2499bb6`

**Rollback/migration notes:**
- No data migration is required.
- Rollback can restore the four Ice Dragon runtime assets and the two runtime version authorities to their 2.3.58 / 1.4.52 state.

### Roadmap reconciliation note — versions 2.3.60 through 2.3.77

The authoritative runtime version files and evidence-backed per-release records advanced beyond this canonical roadmap after Server 2.3.59. This gap is recorded explicitly rather than inventing summaries that were not reconstructed from their source evidence.

Immediately before the Server 2.3.78 event, the authoritative runtime state was re-read as:

- Overall Server: `2.3.77`
- Web Chat: `1.4.70`
- The concurrent event observed at that boundary was a Google Account Architecture advance.

Existing evidence-backed release files in `runtime/docs/releases/` remain the source for those individual events until a dedicated roadmap backfill is performed.

### Server 2.3.78 — Frontend-first Chat + persistent device theme cache

**Status:** source implementation complete; browser acceptance verification pending  
**Chat:** `1.4.71`  
**Web Frontend:** `1.0.0`  
**LALM/R39:** unchanged  
**Server/Infrastructure:** unchanged  
**Deployment Control:** unchanged  
**Deployment:** NONE  
**Restart:** NONE

**Update notes:**
- Established a new independently versioned `web-frontend` module so static/local-first browser architecture is no longer versioned only as a side effect of Chat behavior.
- Added a frontend-first boot controller that restores the locally selected theme before backend/account/LALM readiness and marks the shell ready independently.
- Removed the old 1.8-second full-page synchronization curtain and the art-dependent reveal gate; the local Chat shell is no longer intentionally hidden while remote/runtime state settles.
- Preserved the existing Chat API/inference boundary: connection state may still show connecting/unavailable, but it no longer owns whether the local interface can render.
- Added Ice Dragon asset hydrator v15 with persistent browser Cache Storage. The companion and reconstructed 864x1536 adult source are cached after first successful hydration and reused on later refreshes.
- Changed source fetch behavior away from `no-store`; six-part reconstruction is now a first-cache-fill fallback instead of an every-refresh requirement.
- Added non-blocking idle-time promotion to a cached 4320x7680 WebP on capable devices. The 8K tier is never required before the UI becomes usable; cached 864x1536 paints first when needed.
- Later visits prefer the cached 8K tier when it exists, matching the intended “download/build once, run from the user's device cache” model.
- Advanced the runtime page manifest to v11 with `chat_frontend_boot.js` first and Ice Dragon v15 as the active art loader.
- Preserved theme diagnostics so cache hits/misses, 8K promotion, and paint tier can be verified from the existing View Theme Logs UI.

**Verification state:**
- All new/modified JavaScript was syntax-checked before repository mutation.
- The runtime manifest was re-read after concurrent project activity and still contained the intended frontend-first script order and v15 loader.
- Version authorities were re-read immediately before assignment. The event-entry snapshot (`2.3.76 / 1.4.69`) had concurrently advanced to `2.3.77 / 1.4.70`, so this event reconciled forward and assigned `2.3.78 / 1.4.71` rather than overwriting the other event.
- Final browser acceptance remains user-visible verification: first load should populate cache; later refreshes should show cache hits and immediate shell rendering.

**Failure/attempt lineage:**
- The earlier full-resolution wallpaper fix solved visual quality but still reconstructed theme art from network-delivered Base64 chunks during refresh.
- Screenshots showed intermediate/base Chat states and occasional multiple-refresh convergence, motivating separation of static frontend readiness from §wyrlz service readiness.

**Relevant lineage:**
- Runtime release record: `runtime/docs/releases/server-2.3.78-frontend-first-device-cache.md`
- Frontend authority: `runtime/versions/web-frontend.txt`
- Runtime manifest: `runtime/runtime_pages/manifest.json` v11
- Ice Dragon loader: `runtime/web/themes/ice-dragon/ice-dragon-art-loader-v15.js`

**Rollback/migration notes:**
- No server data migration is required.
- Existing browser Cache Storage entries are disposable and version-keyed; a future theme-asset revision can advance cache keys without mutating prior entries in place.
- Rolling back v15 restores the prior v14 network reconstruction path; it does not require server restart or deployment.

### Server 2.3.79 — Frozen Web Snapshot Collector 1.0.0

- **Status:** source published and static verification complete; deployment blocked by missing VERCEL_TOKEN (run 34708124306)
- **Chat:** `1.4.71` unchanged
- **LALM/R39:** `2.1.30` unchanged
- **Server/Infrastructure:** stable authenticated collector host added
- **Frozen Web Collector:** `1.0.0`
- **Deployment Control:** `1.0.2`
- **Deployment:** REQUIRED and explicitly APPROVED

**Update notes:**
- Adds `/collector`, a professional browser control room for source registration, bounded collection, pause/continue/checkpoint operation, frozen evidence search, training review, manifest inspection, and safety configuration.
- Adds a runtime-owned engine that validates destinations, enforces mandatory robots/politeness and explicit budgets, extracts/canonicalizes/deduplicates text, records provenance and revisions, discards raw HTML, prepares chunks/search indexes, and seals immutable snapshots.
- Keeps frozen evidence separate from reviewed training corpora. Training acceptance requires an explicit decision and rights/provenance confirmation.
- Stores durable control state and immutable artifacts in private Vercel Blob; `/tmp` remains disposable cache state only.
- Installs a fixed authenticated stable host once. Compatible collector page and engine updates remain on `runtime` and require no later server redeployment.
- Preserves Chat 1.4.71, LALM Engine 2.1.30, RMCCA, Ice Dragon, and unrelated application behavior.

**Concurrency lineage:**
- Initial design baseline was Server `2.3.58`; the planned `2.3.59` event was never assigned.
- First revalidation found Server `2.3.67` / Chat `1.4.61` at runtime `26009037b55c158a0606e84bf69202b165e59057`.
- Final revalidation found Server `2.3.78` / Chat `1.4.71` / LALM `2.1.30` at runtime `3c2cc5efd320157ba67d888240f195344c015be7` and main `3f3d8eaeec4859099a3710155df8067577ca27fe`; earlier planned collector versions were discarded before publication.
- Reconciled checkpoints are runtime `7cc1ccb9eb09857f945dab2ea992b2809d8b50f1` and stable host `636321dcd9f204eae08f5e9cfc567ab1b2ac5c1d`.

**Verification state:**
- Focused runtime tests pass for storage transport, SSRF/redirect/robots safety, source policies, lifecycle/checkpointing, search, deterministic sealing, immutable evidence, rights confirmation, separate training corpora, and storage preflight.
- Browser-console contract tests pass with safe DOM rendering, session-only token handling, complete controls/API bindings, and runtime route ownership.
- Stable-host tests pass for fixed module contract, bounded readiness, authentication rejection, request limits, dispatch, and source receipts.
- Production workflow YAML parses successfully. Actual workflow/build/deployment/browser evidence is pending and will be appended after the approved trigger completes.

**Relevant lineage:**
- Contract: `docs/contracts/SWRLZ_FROZEN_WEB_COLLECTOR_V1.md`
- Checkpoint: `docs/checkpoints/FROZEN-WEB-COLLECTOR-001_CHECKPOINT.md`
- Release record: `docs/releases/SERVER_2.3.79_FROZEN_WEB_COLLECTOR.md`
- Final canonical/deployment commits: pending publication.

**Rollback/migration notes:**
- No existing collector-state migration is required; deployment does not configure sources or begin collection.
- Rollback restores the preceding production deployment and pre-event runtime authority. Operator-created immutable artifacts remain preserved unless separately removed with explicit authority.

## Required release-entry format

For every future Server development event, append a new section using this structure:

```markdown
### Server X.Y.Z — Short release name

**Status:** complete / attempted / failed / verification pending
**Chat:** X.Y.Z
**Chat Stream:** X.Y.Z
**LALM/R39:** X.Y.Z
**Server/Infrastructure:** X.Y.Z
**Admin:** X.Y.Z
**Page Runtime:** X.Y.Z
**Deployment Control:** X.Y.Z
**Deployment:** NONE / REQUIRED / APPROVED

**Update notes:**
- What the change accomplishes in human/project terms.
- Why the change was needed.
- What behavior or capability now results.
- What was intentionally left untouched.
- Verification performed and its current state.
- Any migration/rollback note.

**Failure/attempt lineage:**
- What failed or remained unverified, when applicable.
- Why the next version exists as a separate event.

**Relevant lineage:**
- Commit(s), source evidence, or other engineering references.
```

The detailed roadmap may include exact implementation mechanics and code-level evidence. The normal conversational update should summarize the accomplishment and resulting behavior in human language rather than reproducing code syntax.

## Non-negotiable release discipline

- Never claim a release is complete without recording it here.
- Never silently change the overall Server version without a roadmap entry.
- Never bump a component version just to make numbers move; bump it because that component changed.
- Never assign a planned version from a stale snapshot; re-read authority immediately before versioning/commit.
- Never deploy solely because a runtime component changed.
- Never treat a `main` or documentation commit as deployment-capable without checking the current deployment trigger/configuration.
- Never allow `main` and `runtime` to become competing sources of truth for the same page-owned behavior.
- Never replace a complete page when a targeted file-level change is sufficient.
- Always preserve the known-good runtime state before risky edits.
- If a stable infrastructure deployment is required, verify that it still loads the current `runtime` source afterward.
- Failed attempts and failed verification remain visible in the release lineage.
- The roadmap is the detailed engineering record; the user-facing update is the human-readable accomplishment summary.

## Canonical relationship

```text
                         §wyrlz RELEASE EVENT
                              │
                    capture authority baseline
                              │
                       make minimal change
                              │
                    revalidate authorities
                              │
                  reconcile if state advanced
                              │
                       Server X.Y.Z
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
        Chat               LALM/R39         Server/Infra
       X.Y.Z                X.Y.Z               X.Y.Z
          │                   │                   │
          └──────────── independent component ───┘

main    = stable infrastructure / engineering-contract boundary
runtime = durable live application / hot-update source
DEPLOY  = separate production action determined by current configuration

ROADMAP = detailed technical lineage
CHAT     = human-readable accomplishment/status
```

**Bottom line:** every §wyrlz server development event is a real versioned event. Read authoritative versions at entry, re-read them at the commit boundary, reconcile concurrent advances before assigning versions, increment the overall Server version, update only the component versions that actually changed, preserve failed attempts, write the detailed engineering record here, and communicate the resulting accomplishment to the human user in clear project language. Apply the Deployment Approval Gate to the action that actually triggers deployment, based on current deployment configuration/workflows.
## Publication, workflow, and live-page evidence — 2026-09-12

- Lifecycle: **BLOCKED — deployment credential required**; source publication and focused verification are complete.
- Canonical runtime source: `aabe9d94f5461750ad013206c62a410f4d7dc893` (tree `0bbc113bacabac87c1672a0c9e57a85328332f77`).
- Canonical stable source: `329f4222b6ed159f472f29b093aa789accc76263` (tree `57d85e02c3fa32f568b0a2abdc24115fce4ef2a6`).
- Approved trigger: `eedda9a3777c3d97da866673317a155cb745ca48`, submitted at `2026-09-12T17:24:12.116Z`. Its `SOURCE_REF` pins the stable source commit above.
- Workflow: [Manual Vercel Production Deploy, run 34708124306](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/34708124306).
- Authorization job `103591797259`: **success**.
- Deploy job `103591825615`: **failure** at **Verify deployment token exists**, `2026-09-12T17:24:40Z`. The runner received an empty `VERCEL_TOKEN` and reported that the repository secret is required.
- CLI installation, environment pull, private Blob provisioning, build, deployment, and workflow production acceptance checks were all **skipped**. No collector deployment was created by this attempt.
- Vercel still reports preceding production deployment `dpl_Gjsx9ttTfqazCfQYWtRrbgzSPb3q`, `READY`, built from `3f3d8eaeec4859099a3710155df8067577ca27fe`.
- Live page verified at [Collector overview](https://swrlzkamico-o3nu.vercel.app/collector#overview): correct title, rendered sidebar/control room, budget cards, and administrator connection prompt. Visual inspection confirms the desktop layout renders correctly.
- The page honestly reports **Collector host unavailable**. Both `/api/collector/readiness` and `/api/collector/status` return **404** on the preceding deployment. Production authentication and Blob operations therefore remain **unverified**; the local focused tests remain passing.
- Collector engine and stable host tests pass; console contract passes with 91 unique IDs; workflow YAML and all nine shell blocks parse. Local/remote release tree IDs match exactly.
- No source registration, collection, sealing, training acceptance, or data deletion occurred.

### Exact recovery step — historical, superseded

**Do not execute this historical step. The live recovery verification below records the installed host and current state.**

Configure a valid Vercel deployment credential for the existing team/project as the GitHub Actions secret `VERCEL_TOKEN` in `kaministrator999-ui/Swrlzkamico` (repository secret or the workflow's `production` environment). Enter credentials only in the provider's secure settings, never in chat or tracked files.

Then re-run the failed deploy job in workflow run `34708124306`. The retained successful authorization output pins source `329f4222b6ed159f472f29b093aa789accc76263`; the same approved collector installation is still pending. Do not alter deployment settings or start a crawl as a workaround. After the job succeeds, verify readiness/storage/auth responses and browser operation, then append the actual deployment ID and result here.

Approval is already on record for this bounded installation; the remaining prerequisite is credential configuration. This receipt records new evidence for the same Server 2.3.79 event and does not introduce another source change or version event.
