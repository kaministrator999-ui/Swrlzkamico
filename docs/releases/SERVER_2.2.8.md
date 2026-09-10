# Server v2.2.8

**Date:** 2026-09-10  
**Branch:** `runtime`  
**Previous Server:** `2.2.7`

## Module versions

- Chat: **1.4.3** (from 1.4.2)
- LALM UI: **1.0.0** (unchanged)
- LALM engine hot revision: **2.1.18-hot-boundary-v9-effective-receipt** (unchanged)
- Server UI: **1.0.0** (unchanged)

## Release purpose

Versioned closure of the mobile Chat sidebar stacking fix plus the new authoritative cross-module version display/roadmap contract.

## Changes

### Chat v1.4.3

- Fixed the mobile sidebar layering behavior so the background Chat workspace is dimmed by the scrim while the sidebar remains bright above it.
- Added automatic footer resolution of the current Server version from `/api/server/status`.
- Added automatic footer resolution of the current LALM UI version from `/api/lalm/status`.
- Chat does not maintain copied Server/LALM version literals.

### Server v2.2.8

- Incremented the canonical server `VERSION` in `api/index.py`.
- Preserved existing 2.2.7 runtime/inference behavior.
- Kept the control-plane status endpoints as the authoritative Server/LALM version surfaces.

### LALM

- No LALM code change in this release.
- No LALM version increment.
- No model/runtime revision change.

### Documentation / roadmap

- Added `docs/ROADMAP.md` as the versioned Server/module roadmap.
- Updated `HOT_RUNTIME_UPDATE_GUIDE.md` with mandatory Server/module version increments, roadmap updates, failure lineage, and automatic cross-module version lookup rules.
- Updated `SWRLZ_HOTFIX_RULES.md` on `main` with the same project-start/hotfix versioning contract.

## Historical lineage

The original sidebar CSS fix was committed first as:

`2b4bed5d175368278834a8d086b03537577fcfea`

The subsequent version-source and documentation commits formally establish that work as the Server v2.2.8 / Chat v1.4.3 event rather than deleting or rewriting the historical commit.

## Verification

- Target files were fetched before editing.
- Runtime-only Chat changes remain on `runtime`.
- No Vercel deployment was created for the Chat hotfix.
- No server restart was performed for the Chat hotfix.
- Chat version source was updated and committed.
- Server version source was updated and committed.
- Roadmap/release record was added and committed.
- Cross-module version display is designed to resolve current authoritative status values automatically.
- Final visual verification requires reloading the live Chat route and opening the mobile sidebar.

## Next update rule

The next server-side change, successful or failed, must increment the overall Server version again. Only modules actually changed in that event receive module-version increments. The roadmap must be updated in the same event.
