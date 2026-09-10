# §wyrlz Server Roadmap

## Current release

**Server v2.3.6**

This is the current runtime development release. Stable deployed infrastructure remains Server v2.3.3 until a future stable-infrastructure deployment changes it.

### Module state

- **Chat v1.4.6** — fixed a browser-side status MutationObserver loop and kept authoritative local LALM readiness display guarded against redundant DOM writes.
- **LALM UI v1.0.0** — unchanged in this release.
- **LALM engine hot revision** — `2.1.18-hot-boundary-v9-effective-receipt`; unchanged in this release.
- **Server UI v1.0.0** — unchanged in this release.

## Server v2.3.6 — 2026-09-10

### Changed

- Fixed `web/chat_enhancements.js` so its local LALM status updater no longer installs a `MutationObserver` that observes the same DOM nodes it rewrites.
- The previous observer could repeatedly trigger itself because `paint()` changed `#nodeTitle` / `#nodeDetail`, which generated new mutation records and re-entered the observer. This is the likely cause of the Chat page appearing stuck/loading while the LALM indicator itself showed ready.
- Replaced the observer with a bounded 15-second status poll and guarded text writes so unchanged values do not create unnecessary DOM mutations.
- Bumped Chat from `v1.4.5` to `v1.4.6` because the user-facing Chat runtime implementation changed again.
- Bumped overall Server from `v2.3.5` to `v2.3.6` because this is a new server runtime development event.
- LALM UI and LALM/R39 engine versions remain unchanged because their source/behavior did not change in this event.
- Kept the correction entirely on the `runtime` branch; no stable infrastructure deployment or server restart is required.

### Failure / history

- Server 2.3.4 added local LALM readiness handling to `web/chat_enhancements.js`.
- Server 2.3.5 moved authoritative readiness presentation into `web/chat_version.js` after production asset propagation for the separate enhancement asset was found stale.
- Inspection of the 2.3.4 enhancement implementation exposed a self-triggering `MutationObserver`: it watched `#nodeTitle` and `#nodeDetail`, then its own `paint()` function wrote to those nodes. That creates a recurring mutation cycle and can monopolize browser work.
- Server 2.3.6 records this as a new corrective runtime event rather than rewriting the earlier release history.

### Verification state

- The production LALM backend remains independently verified as `interactiveReady: true` and `warmModelResident: true`; the defect isolated here is browser-side Chat behavior, not LALM readiness.
- `web/chat_enhancements.js` now contains no `MutationObserver`; its updater performs a direct status fetch and bounded polling.
- `web/chat_version.js` canonical Chat version/status source is now Chat `v1.4.6` in `runtime`.
- Runtime commits:
  - `34f57ab433226fa0a0a8f47e929ae17dbc0ce19a` — enhancement observer-loop fix.
  - `4952fef7519946b8b04dece24077d3353df737ae` — canonical Chat version/status bump to v1.4.6.
- **Deployment:** NONE required.
- **Server restart:** NONE.
- Final browser verification remains required: reload the live Chat page and confirm it remains responsive instead of appearing stuck/loading while the green **Local LALM ready** indicator remains stable.

## Server v2.3.5 — 2026-09-10

### Changed

- Moved the authoritative local LALM status presentation into `web/chat_version.js`, the canonical Chat version/status asset that was verified live after the 2.3.4 runtime update.
- The Chat sidebar now directly queries `/api/lalm/status` and displays:
  - **Local LALM ready** when `interactiveReady` is true.
  - **Local LALM warming** while readiness is not yet established.
  - **Local LALM unavailable** when the status probe reports an error or cannot be reached.
- Bumped Chat from `v1.4.4` to `v1.4.5` because the Chat runtime implementation changed again.
- Bumped overall Server from `v2.3.4` to `v2.3.5` because this is a new server runtime development event.
- LALM UI and LALM/R39 engine versions remain unchanged because their source/behavior did not change.
- Kept the correction entirely on the `runtime` branch; no stable loader/infrastructure deployment is required.

### Failure / history

- Server 2.3.4 correctly identified the root cause and added the status override to `web/chat_enhancements.js`, but production verification showed that asset still serving the older 519-byte runtime content while the canonical `chat_version.js` had already propagated to Chat `1.4.4`.
- Rather than depend on the separate enhancement asset's propagation state, Server 2.3.5 places the same status correction in the canonical version/status asset already confirmed live.
- This preserves the versioning rule: the incomplete 2.3.4 attempt remains recorded; the next corrective attempt receives a new Server and Chat version.

### Verification state

- Production `/api/lalm/status` was verified to report `engineSource: runtime-override`, `interactiveReady: true`, `warmModelResident: true`, native backend availability, and the expected R39 model identity.
- Production `/live/assets/chat_version.js` was verified serving Chat `1.4.4` after the 2.3.4 merge, proving that the runtime branch hot path is active for that canonical asset.
- The status presentation is now implemented in that verified-live asset and will query the same authoritative LALM endpoint directly.
- **Deployment:** NONE required.
- **Server restart:** NONE.
- Final user-side verification: reload Chat and confirm the sidebar indicator is green with **Local LALM ready** instead of **Local inference pending**.

## Server v2.3.4 — 2026-09-10

### Changed

- Corrected the Chat sidebar's local inference status so it is sourced from the authoritative `/api/lalm/status` readiness object.
- A ready local R39 worker now displays **Local LALM ready** with a green indicator and the resident/native-backend detail.
- A warming worker displays **Local LALM warming** rather than incorrectly implying that local inference is simply pending configuration.
- An actual LALM status error displays **Local LALM unavailable** with an error indicator.
- Bumped Chat from `v1.4.3` to `v1.4.4` because the user-facing Chat status behavior changed.
- Bumped overall Server from `v2.3.3` to `v2.3.4` because this is a new server runtime development event.
- LALM UI and LALM/R39 engine versions were intentionally left unchanged because their behavior/source did not change in this event.
- Kept the change entirely inside runtime-owned Chat assets so the existing hot-runtime path can serve it without a Vercel deployment or server restart.

### Root-cause clarification

The previous screenshot's **Local inference pending** label was not evidence that R39 itself was unready. The live production `/api/lalm/status` response was verified with `interactiveReady: true` and `warmModelResident: true` while reporting `engineSource: runtime-override`. The base Chat page was instead using the absence of an upstream SERVER bridge to choose the misleading local-inference label.

Server 2.3.3's startup-warm path therefore remains valid; this 2.3.4 event corrected the Chat presentation layer. Its first asset implementation was not deterministically visible in the final production verification path, so the follow-up correction is recorded as Server 2.3.5 rather than silently rewriting 2.3.4.

### Failure / history

- Server 2.3.3 startup warm was initially interpreted as unsuccessful because the Chat sidebar continued to display **Local inference pending**.
- Direct production status verification showed the LALM/R39 engine was actually ready and resident, isolating the remaining defect to Chat status presentation rather than model warming.
- No LALM engine failure occurred in this update.
- No stable-infrastructure change was made.

### Verification state

- Current production `/api/lalm/status` was queried directly before the fix.
- Verified production response reported `engineSource: runtime-override`, `interactiveReady: true`, `warmModelResident: true`, and the expected R39 model identity.
- `runtime/web/chat_enhancements.js` was updated to consume `/api/lalm/status`, but production verification found the older asset content still being served.
- `runtime/web/chat_version.js` was updated from Chat `v1.4.3` to `v1.4.4` and was verified live.
- Runtime branch remains the live application source of truth.
- **Deployment:** NONE required for these runtime-owned changes.
- **Server restart:** NONE.

## Server v2.2.8 — 2026-09-10

### Changed

- Fixed mobile Chat sidebar stacking so the background Chat interface is dimmed while the sidebar remains bright above the scrim.
- The targeted CSS change is in `web/chat_enhancements.css` and removes the mobile `.app` stacking context that trapped the sidebar beneath the root-level scrim.
- Bumped Chat from `v1.4.2` to `v1.4.3` because user-facing Chat behavior/visuals changed.
- Bumped Server from `v2.2.7` to `v2.2.8` because a server runtime event occurred.
- Chat version rendering now retrieves:
  - Server version from `/api/server/status` → `version`.
  - LALM UI version from `/api/lalm/status` → `uiVersion`.
- Added mandatory version/roadmap rules to the runtime update guide and the project hotfix rules so future module updates preserve lineage and do not require duplicate hardcoded display values.

### Failure / history

- The original sidebar fix was committed as runtime commit `2b4bed5d175368278834a8d086b03537577fcfea` before the new version/roadmap contract was formalized.
- This release record retroactively closes that runtime event into the versioned Server v2.2.8 / Chat v1.4.3 lineage rather than erasing the earlier commit history.
- No LALM failure occurred in this update.

### Verification state

- Runtime source was fetched before the targeted CSS and version-source edits.
- `runtime` remains the live application source of truth.
- No Vercel deployment was created for the runtime Chat fix.
- No server restart was performed for the runtime Chat fix.
- The updated Chat version source was committed and can resolve live Server/LALM status versions automatically.
- Live browser verification remains the final user-side check for the visual sidebar result.

## Mandatory roadmap/version law

Every server runtime development event gets a new overall Server version, including a failed attempt.

Every module actually changed gets its own version increment in that Server event.

A module's version must be updated at every canonical location where that module owns its version. Other modules that display the version must query the owning module's authoritative status/version source rather than maintaining stale copies.

Every event must update this roadmap/release lineage with:

1. Server version.
2. Affected module versions.
3. What changed.
4. Failed attempts, if any.
5. Verification state.
6. Relevant commit lineage.

### Example

```text
Server v5.5.6

Chat v5.5.5
- Sidebar fix.

LALM v5.5.4
- No change.
```

Next LALM-only event:

```text
Server v5.5.7

LALM v5.5.5
- Inference fix.
```

If that fails:

```text
Server v5.5.8

LALM v5.5.6
- Failed inference attempt recorded.
```

The next fix receives another Server version and another LALM version increment.

## Roadmap direction

### Server

- Preserve runtime hot-update/no-redeploy workflow for runtime-owned application changes.
- Keep stable infrastructure changes isolated to `main` and the deployment boundary.
- Maintain complete Server release lineage.

### Chat

- Continue user-facing Chat/runtime fixes as targeted runtime hot updates.
- Keep Chat version display authoritative and self-refreshing from server/module status.
- Preserve stream, request, session, and Truth Firewall boundaries.
- Keep local LALM readiness presentation tied to `/api/lalm/status`, not upstream bridge configuration.

### LALM

- Continue R39/native inference work independently of Chat where the user-facing Chat protocol is unchanged.
- Expose authoritative LALM UI/runtime version and revision information through status endpoints.
- Preserve correctness/reference fallback while native runtime work evolves.

## Version ownership map

| Module | Canonical owner | Cross-module consumers |
|---|---|---|
| Server | `api/index.py` → `VERSION` | Chat, LALM/status, admin/status surfaces |
| Chat | `web/chat_version.js` → `CHAT_VERSION` | Chat itself |
| LALM UI | `api/control_plane.py` → `LALM_UI_VERSION` → `/api/lalm/status` | Chat and other status surfaces |
| LALM engine | `runtime_hot/r39_engine.py` → `HOT_REVISION` / `HOT_SERVER_VERSION` | LALM status and diagnostics |

**Rule:** consumers query the owner. They do not copy another module's version into a second manually maintained constant.
