# §wyrlz Server Roadmap & Version Ledger

**READ WITH:** `SWRLZ_HOTFIX_RULES.md`  
**Current overall server baseline:** `2.3.6`  
**Current Chat component:** `1.4.6`  
**Current LALM UI component:** `1.0.0`  
**Release policy:** every server development event gets an overall Server release/version entry plus independent component version changes where applicable, including unsuccessful attempts.

## Version model

§wyrlz uses two levels of versioning:

1. **Overall Server version** — the chronological development/release event of the complete server architecture.
2. **Independent component versions** — Chat, LALM/R39, Server/Infrastructure, Admin, and other independently maintained surfaces.

An update may change one component or several components, but the roadmap records the **overall Server version for every server development event** and records each component's version separately.

### Rule from here forward

**Every server development event receives a new overall Server version and an update note.** Component versions advance independently when that component actually changes. A component version does not advance merely because another component changed.

A failed attempt is still a real versioned event. The next correction receives the next overall Server version.

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
- Recovered from the accidental Chat page overwrite by restoring the known-good runtime commit before continuing with targeted version changes.
- Established Chat stream UI ownership on `runtime`.
- Established runtime-owned Chat version display rather than a hardcoded version injected by `main`.
- Added the canonical hotfix rules and durable runtime update guide.
- Added the third project-start version/module evolution contract as the engineering curriculum foundation for the future programming-side LALM.
- Added the explicit reporting rule that technical implementation belongs in the roadmap while conversational updates describe the human-visible accomplishment and resulting behavior.
- Verified that runtime-only files can be created/changed/removed and served by production without creating a new Vercel deployment.
- Established the durability rule: GitHub `runtime` is source of truth; `/tmp`, memory, browser cache, and Vercel instance state are disposable.

## Component ownership

| Component | Source of truth | Versioning rule |
|---|---|---|
| Overall Server | `main/api/index.py` + this roadmap | Advances on every server development event |
| Chat | `runtime/web/chat*` and related runtime Chat assets | Advances when Chat UI/protocol/behavior/version plumbing changes |
| Chat Stream UI | `runtime/web/chat_stream_focus.js` and related assets | Advances when stream behavior changes |
| LALM/R39 | runtime LALM/inference source | Advances when LALM/inference behavior changes |
| Server/Infrastructure | `main/api/*`, deployment/configuration | Advances with stable infrastructure releases |
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
ASSIGN NEW SERVER VERSION
        ↓
BUMP ONLY AFFECTED MODULES
        ↓
UPDATE CANONICAL VERSION SOURCES
        ↓
COMMIT to runtime
        ↓
RELOAD / REQUEST
        ↓
VERIFY runtime source + behavior
        ↓
RECORD detailed release entry
        ↓
REPORT human-readable accomplishment to user
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
**Deployment:** NONE / REQUIRED

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
- Never deploy solely because a runtime component changed.
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

ROADMAP = detailed technical lineage
CHAT     = human-readable accomplishment/status
```

**Bottom line:** every §wyrlz server development event is a real versioned event. Increment the overall Server version, update only the component versions that actually changed, preserve failed attempts, write the detailed engineering record here, and communicate the resulting accomplishment to the human user in clear project language. Use the hotfix/deployment boundary defined in `SWRLZ_HOTFIX_RULES.md`.
