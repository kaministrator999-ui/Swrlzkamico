# v214 — §E editor/starter project-aware GitHub assistant release

Date: 2026-10-11 (America/Chicago). This is an engineering-source and guarded Chat-tools release, **not** a game engine or new playable starter deployment.

## Product objective

Make the §wyrlz AI reliably participate in §E editor work, create native starter-scene drafts, then progress toward full starter-mode/game and core-engine updates. The immediate goal is source-aware project context and a safe first authoring loop; multi-file mode/runtime patching and full engine automation remain future verified stages.

## Concurrent source reconciliation

- Production was already on [GitHub general project workbench v213](https://github.com/kaministrator999-ui/Swrlzkamico/pull/112) source `002f4bde2b2d142647019b22da21382c7047b2d6`. It includes OAuth-bound repo overview, code search, PR/CI triage, user-confirmed exact single-line source edits, and draft PRs.
- An independent §E-focused v213 prototype [draft PR #113](https://github.com/kaministrator999-ui/Swrlzkamico/pull/113) was based on older published v212 source. **It was NOT released over v213.**
- Instead, the published [integrated draft PR #114](https://github.com/kaministrator999-ui/Swrlzkamico/pull/114) `feature/forge-engine-agent-v214-integrated@344d2e47a678c05e05c319ed716028a99b524604` starts exactly on the v213 release SHA. It preserves all general project workbench code, previous v212 workflow tools, v211 model-guided progress, first-message native Chat persistence, model identity work and encrypted Google account state. Shared account CI contains both v213 and §E v214 tests.
- This release keeps §wyrlz Chat source separate from actual engine source on `main:projects/swrlz-forge-moba`.

## Implemented v214 tools and boundaries

- `hf_space/forge_project_tools_v213.py` (module name preserved for lineage) accesses the real selected canonical repository `kaministrator999-ui/Swrlzkamico` and its verified `main` source—not an outdated separate Chat release branch.
- `@GitHub engine status`: verify current engine `source-manifest.json`, 60-patch ordering/version, scene inventory, dedicated release request, and strict §E-vs-Chat deployment boundary.
- `@GitHub engine starters`: list existing native saved scenes and sizes. Explicitly distinguish a GitHub file from a registered Projects starter or bundled mode.
- `@GitHub engine plan GOAL`: data-backed plan for editor improvement, starter pack/game mode, or engine-core patch based on actual source paths and required Save/Load, Undo/Redo, desktop/mobile Playwright, sealed build and separate deployment evidence. Plans do not claim work executed.
- `@GitHub engine clone sheep-tag-meadow as arena-draft on feature/arena`: preview a safe copy of compatible original native scene JSON. One-use explicit `@GitHub confirm CODE` rechecks Google owner+selected repo, actual write OAuth scope/role, main HEAD, review branch HEAD, source blob SHA and destination nonexistence. Only creates **one new native-scene draft** on existing feature branch; it does not overwrite, register a Projects card, implement novel gameplay, alter the 60-patch engine, merge or deploy.
- `@GitHub engine review feature/arena`: snapshot exact bounded engine-only file changes, reject unrelated or direct deployment-request changes, require one-use explicit approval, recheck main/ref/diff and prepare a **draft PR**. No automatic merge or §E deployment.
- `hf_space/station.py`, canonical `hf_space/github_connection.py` and Chat `index.html` route direct and conservatively matched natural engine/editor queries with server-verified GitHub evidence and real status events. Selected local model can propose allowlisted engine **read** tools within existing v213 bounded tool plan; it cannot authorize writes or change OAuth. Chat Settings adds a §E editor/engine help control. Chat source version **1.1.11**.

**Limits:** This is the first safe vertical slice, not full autonomous engine authoring. Multi-file diff generation, gameplay-mode registration, patch serialization/re-sealing, automated browser gameplay repair loops and live engine deployment orchestration are not yet provided by v214.

## Verified source CI

All three at pinned published SHA `344d2e47a678c05e05c319ed716028a99b524604`:
- [GitHub/account and v213+§E v214 regressions #38201458286](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38201458286): **SUCCESS**
- [HF Candidate Offline Validation #38201487551](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38201487551): **SUCCESS**
- [Mobile Lyric Reader Integrity #38201487572](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38201487572): **SUCCESS**

Initial independent prototype CI caught a status assertion wording problem; it was corrected and source tests passed. The integrated source preserves both v213 project and v214 engine tests. Tests are synthetic GitHub mocks; they do not execute authenticated owner scene writes or prove playable gameplay.

## Canonical Chat Space publication

- `main:.deploy/HF_SPACE_REQUEST.txt`, nonce `2026-10-11-v214-forge-engine-editor-starter-agent-001`, request commit `3846c9d1ac52dc9ab950892bd35851cd48c2840b`, pinned source `344d2e47a678c05e05c319ed716028a99b524604`.
- [Guarded HF release #38201554915](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38201554915) **COMPLETED/SUCCESS**, both request and deploy jobs. Existing `kamiloki/Swyrlz` Space updated to revision `dd1f94c96e39327f5e58b04ae806d274bd7a1ae4`, previous rollback `c88edf6c652d27831b43120ee80648cfd54bf8e4`. Release artifact `hf-release-checkpoint` ID `11725987150`; rollback artifact `hf-rollback-checkpoint` ID `11725927233`. Receipt `DEPLOYED_UNVERIFIED`; no owner live acceptance fabricated.
- Dedicated game engine `kamiloki/swrlz-forge-moba` was **not deployed or modified**. Only source-only governance docs `docs/engineering/SWRLZ_ENGINE_AGENT_V214_BUILD_LADDER.md` and `§tart_§E.md` cross-reference were updated on main without touching source manifest, engine runtime or `DEPLOY_REQUEST.json`.

## Runtime version authority

Atomic guarded `runtime@4216f510b83be2523102ce65f567cff37c510c24`, registered affected modules:
| Module | Before | After |
|---|---|---|
| Repository Work | 1.0.156 | 1.0.157 |
| Server Runtime | 2.3.368 | 2.3.369 |
| Web Chat | 1.5.106 | 1.5.107 |
| LALM Engine / GitHub tool router | 2.1.192 | 2.1.193 |

Google Account Architecture **1.0.15 unchanged** (reuses existing OAuth identity/grants); Runtime Manifest, §E engine release and other authorities unchanged. `runtime:VERSION.txt` registry unchanged.

## Next tier and user acceptance

On the existing Chat Space, signed into the same Google account with selected repository `kaministrator999-ui/Swrlzkamico`, try `@GitHub engine help`, `@GitHub engine status`, `@GitHub engine starters`, and `@GitHub engine plan make a MOBA starter pack`. Verify genuine read results and visible phases. Optionally, the user may explicitly approve a draft copy on a disposable review branch and inspect the resulting GitHub file/PR—no live write was attempted by this release.

The next meaningful tier is **reviewed multi-file engine/editor patch planning + sandbox validation**, followed by authored Projects hub/game rules integration and governed §E-specific build/test/deploy. Preserve the original engine, starter assets and signed-in Chat history and distinguish all evidence levels. See `docs/engineering/SWRLZ_ENGINE_AGENT_V214_BUILD_LADDER.md`.

**Status:** SOURCE/CI/CHAT DEPLOYMENT/REGISTERED VERSIONS COMPLETE; LIVE OWNER TOOL/CHAT ACCEPTANCE PENDING. PLAYABLE NEW STARTER OR §E ENGINE UPDATE NOT CLAIMED.
