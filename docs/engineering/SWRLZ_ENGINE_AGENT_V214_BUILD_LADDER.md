# §E autonomous engineering capability ladder — v214

**Purpose:** Make §wyrlz reliably work on the real §wyrl§ Engine editor, derive starter packs, build new playable modes from seeds, and eventually maintain its engine. The user owns game/product decisions; the AI engineering workflow owns implementation, verification, reviewed delivery and evidence.

## Non-negotiable two-project source boundary

- §wyrlz AI Chat + GitHub tools: source and guarded deployment for `kamiloki/Swyrlz`.
- §wyrl§ Engine/editor: `main:projects/swrlz-forge-moba/`, governed by `main:§tart_§E.md`, **independently** published to `kamiloki/swrlz-forge-moba` through `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` and `.github/workflows/deploy-swrlz-forge-moba.yml`.
- Treat any older Chat branch's lack of `projects/swrlz-forge-moba/` as evidence of *source lane separation*, not disappearance of the engine. Read engine files from the actual GitHub main ref. Read `§tart_§E.md` first for build/deployment contracts.

## Current verified source facts (2026-10-11)

Engine v10.0 uses an ordered `source-manifest.json` with **60 patches**, six base payload chunks, exact final-size/SHA-256 constraints and `build_space.py` deterministic HTML reconstruction. Scenes are saved native editor `.swyrl.json` records with a `project` envelope, `editor.layers` and `scene` actors/state. Existing mode files include `runtime/sheep_tag_game.js`, `runtime/sheep_tag_integration.js` and the `patches/v10_0_sheep_tag.py` integration. Native Sheep Tag is an existing editable starter; anime/studio scenes and spatial workspaces use other specialized behaviors.

A new `.swyrl.json` on GitHub is NOT automatically bundled or registered in the Projects hub. A rebranded scene without compatible mode logic is not a playable new mode. There is no generic safe inference-to-production code executor as of v214.

## Vertical-slice roadmap

| Stage | AI action | Evidence needed | v214 state |
|---|---|---|---|
| 1. Source discovery | Verify repo/main, manifest, patches, editor scenes, release authority | Live GitHub file/blob/branch receipts | **Implemented** |
| 2. Work-plan composition | Classify editor vs starter vs mode vs core; identify real files/tests | Current manifest and scene inventory | **Implemented**, deterministic |
| 3. Scene seed drafting | Clone compatible native scene into existing feature branch | Actual verified scene JSON, same-account approval, main/ref/blob CAS, no overwrite | **Implemented**, not registered |
| 4. Review handoff | Propose **draft** PR for changed engine-only files | Fresh compare, branch heads, one-use consent | **Implemented**, never auto merge |
| 5. Multi-file code authoring | Safely generate a diff spanning runtime, engine patch, starter scene/registry, tests | Sandbox/parser checks, source-range ownership, human diff approval, patch-level revert | **Not implemented** |
| 6. Starter-mode registration | Projects hub card, scene loader, gameplay/rules/prefabs/HUD and persistence | Native editor Play + Save/Load + Undo/Redo, desktop/mobile parity | **Not implemented** |
| 7. Engine upgrade | Add a governed ordered patch; reconstitute source, reconcile final SHA/bytes | Manifest/checksum, JS/Python parsing, performance and regressions | **Not implemented** |
| 8. CI repair loop | Scope changes, run applicable browser tests, decode failure artifacts, repair branch | Exact source SHA, passed suites, bounded retry | **Partially possible through general GitHub read tools; automation not implemented** |
| 9. Protected release | Merge reviewed engine work, dedicated deployment request, hosted audit/rollback | Terminal dedicated §E deployment, live SOURCE/assets/marker and gameplay acceptance | **Human-governed existing §E lane; NOT automated through general Chat GitHub tools** |

## Starter-pack construction from a seed

Separate **map data**, **editor authoring tools**, **gameplay logic**, and **engine-wide capability**:

1. Confirm whether the user wants a map variant of an existing game or an entirely new gameplay mode. This changes which files need work.
2. Clone existing native scene only when its actor/material/prefab schema is compatible. Keep original scene untouched.
3. Define rules and role/player controls; modes may require distinct classes, team rules, triggers, win conditions, upgrade economies and wave systems.
4. Add mode-specific prefabs/editor menus/inspector controls and preserve Undo/Redo, import/export, save/reload and paused-state behaviors.
5. Add Projects card/loader registration and include scene assets explicitly in engine packaging; preserve all existing starter cards.
6. Add Playwright acceptance with at least desktop/phone, mode Play/Pause/Stop, actor controls, transitions and history restoration; run old engine suites.
7. Only after authored source and tests pass, re-seal patch manifest and submit a draft PR. Release remains separately authorized.

Examples of possible later modes: MOBA/angel arena, sheep tag variants, single-player adventure, anime cinematic production and themed character builders. Their mechanics, rights, artwork and licensing are independent requirements; choosing a genre is not a license to bundle third-party proprietary assets.

## v214 available Chat tool commands

`@GitHub engine help`, `@GitHub engine status`, `@GitHub engine starters`, `@GitHub engine plan build a MOBA starter pack`, `@GitHub engine plan improve editor layers`.

For deliberately user-approved drafts: `@GitHub engine clone sheep-tag-meadow as arena-draft on feature/arena`, then a separate `@GitHub confirm CODE`; later `@GitHub engine review feature/arena`, with another confirmation for its draft PR. Both operate only on the selected verified canonical repo, with current effective OAuth permissions and fresh main/branch/blob/diff checks. They do **not** merge, activate, run, compile, or deploy a new game.

## Remaining implementation ownership

Prioritize the next smallest complete capability: a **multi-file diff/patch workbench** that prepares a verifiable engine change in an isolated feature branch, previews the exact diff, runs static/scene/engine tests and produces a bounded repair plan. It must be compatible with the v213 general single-line GitHub edit tool, not circumvent it. Respect branch protections, separate deployed source identity, rate/budget limits, owner approval and dual project release gates. Never describe unimplemented code editing or autonomous game generation as operational.

**Truth:** Source/CI publication of v214 GitHub tools is distinct from signed-in Google GitHub account acceptance, successful §E authoring, and hosted engine gameplay acceptance.
