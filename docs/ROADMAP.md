# §wyrlz Server Roadmap

## Current release

**Server v2.2.8**

This is the current runtime version after the mobile Chat sidebar stacking fix and the establishment of authoritative cross-module version display.

### Module state

- **Chat v1.4.3** — mobile sidebar scrim layering fixed; Chat footer now resolves Server and LALM versions from authoritative status endpoints.
- **LALM UI v1.0.0** — unchanged in this release.
- **LALM engine hot revision** — `2.1.18-hot-boundary-v9-effective-receipt`; unchanged in this release.
- **Server UI v1.0.0** — unchanged in this release.

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
