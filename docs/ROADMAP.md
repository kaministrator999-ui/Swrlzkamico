# §wyrlz Server Roadmap

## Current release

**Server v2.3.4**

This is the current runtime development release. Stable deployed infrastructure remains Server v2.3.3 until a future stable-infrastructure deployment changes it.

### Module state

- **Chat v1.4.4** — sidebar LALM status now reflects the authoritative `/api/lalm/status` readiness state instead of labeling local R39 as pending merely because no upstream bridge is configured.
- **LALM UI v1.0.0** — unchanged in this release.
- **LALM engine hot revision** — `2.1.18-hot-boundary-v9-effective-receipt`; unchanged in this release.
- **Server UI v1.0.0** — unchanged in this release.

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

Server 2.3.3's startup-warm path therefore remains valid; this 2.3.4 event corrects the Chat presentation layer so the UI reports the actual LALM state.

### Failure / history

- Server 2.3.3 startup warm was initially interpreted as unsuccessful because the Chat sidebar continued to display **Local inference pending**.
- Direct production status verification showed the LALM/R39 engine was actually ready and resident, isolating the remaining defect to Chat status presentation rather than model warming.
- No LALM engine failure occurred in this event.
- No stable-infrastructure change was made.

### Verification state

- Current production `/api/lalm/status` was queried directly before the fix.
- Verified production response reported `engineSource: runtime-override`, `interactiveReady: true`, `warmModelResident: true`, and the expected R39 model identity.
- Updated `runtime/web/chat_enhancements.js` to consume `/api/lalm/status` and override the misleading sidebar state.
- Updated `runtime/web/chat_version.js` from Chat `1.4.3` to `1.4.4`.
- Runtime branch remains the live application source of truth.
- **Deployment:** NONE required for these runtime-owned changes.
- **Server restart:** NONE.
- Final browser-side verification should confirm the sidebar changes from the misleading pending label to **Local LALM ready** when the status endpoint reports readiness.

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