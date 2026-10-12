# v215–v216 — §E engineering tools and verified starter-pack foundation

**Date:** 2026-10-12, America/Chicago. **Ownership:** §wyrlz Chat GitHub tools vs separately governed §wyrl§ Engine, both using the canonical GitHub repository `kaministrator999-ui/Swrlzkamico`.

## Intent and verified source

User requests that §wyrlz progress from reading GitHub to reliable direct engineering of the actual §E editor, constructing starter packs, and eventually upgrading the engine through reviewed source, tests and governed deployment.

Actual engine source: `main:projects/swrlz-forge-moba/`; `§tart_§E.md`; v10.0 ordered `source-manifest.json` (60 patches), deterministic `build_space.py`, native scenes under `scenes/`, separated mode runtime (e.g. `runtime/sheep_tag_integration.js`) and independent `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` → `.github/workflows/deploy-swrlz-forge-moba.yml` → `kamiloki/swrlz-forge-moba`. The Chat/LALM Space `kamiloki/Swyrlz` has independent guarded `main:.deploy/HF_SPACE_REQUEST.txt`.

## v215 — published Chat-side GitHub starter-pack tools

New `hf_space/engine_starter_pack_v215.py`, patched canonical `hf_space/github_connection.py` and `hf_space/forge_project_tools_v213.py`, Chat UI Starter packs button / progress labels / version `1.1.12`. Existing Google-owner encrypted OAuth, v210–v214 GitHub source tooling and one-use proposal mechanism reused; no new paid per-call service or independent assistant persona.

Commands:
- `@GitHub engine pack help` — current real scope and limitations.
- `@GitHub engine pack sheep-tag-meadow as new-meadow on feature/new-meadow` — proposes, does not immediately write, one existing-seed native scene plus one provenance descriptor in ONE atomic Git commit.
- `@GitHub confirm CODE` — a distinct verified Google-owner action; rechecks actual repo/role, current main and branch SHA, seed/manifest blob, derived SHA-256 and both destination paths, then stages exact two-file Git tree and one commit; advances branch with `force:false`; no overwrites, no direct main write.
- `@GitHub engine pack verify new-meadow on feature/new-meadow` — rereads actual scene/descriptor from GitHub branch and checks IDs, layers, actors, digest, bytes and declared game kind. A pack remains `draft-unregistered` and keeps original mode semantics. No fake new game, engine runtime patch, Projects card, merge or §E deployment.

Source [draft PR #115](https://github.com/kaministrator999-ui/Swrlzkamico/pull/115), pinned `feature/engine-starter-pack-atomic-v215@adb3a4d4a6bcbdc54062bc7af1324ebeaa07857e` on guarded-published v214 source `344d2e47a678c05e05c319ed716028a99b524604`. Synthetic 100% passing exact-source suites:
- [GitHub account/tool tests #38216951013](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38216951013), **SUCCESS**
- [Hugging Face offline candidate #38216953682](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38216953682), **SUCCESS**
- [Mobile integrity #38216953691](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38216953691), **SUCCESS**

Guarded existing `kamiloki/Swyrlz` Chat release [workflow #38217201271](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38217201271) terminal **SUCCESS** at exact candidate. Canonical request nonce `2026-10-12-v215-atomic-engine-starter-pack-github-tools-001`, main request commit `2dc7d4c7b62024112127de0eb561c018cdfb6a55`. Published Space revision `b05fbe767a3f225461d32cf5998e371e08f7f71a`; previous rollback revision `dd1f94c96e39327f5e58b04ae806d274bd7a1ae4`. Release artifact ID `11731119871`, rollback ID `11731539684`. Checkpoint **DEPLOYED_UNVERIFIED** until signed-in owner OAuth/pack write and readback are observed; the synthetic tests created no real pack.

Atomic runtime version authority `runtime@e5c92826f2bb2cabcc1e86d057589413c13c245c`: Repository Work **1.0.158**, Server Runtime **2.3.370**, Web Chat **1.5.108**, LALM Engine **2.1.194**. Google Account remains **1.0.15** (OAuth contract unchanged); unrelated module authorities unchanged.

## v216 — independent engine-side validator, reviewed source only

A separate engine branch `feature/forge-starter-pack-validation-v216`, [draft PR #116](https://github.com/kaministrator999-ui/Swrlzkamico/pull/116), adds:
- `projects/swrlz-forge-moba/tools/validate_starter_packs.py`: CLI for `--scene sheep-tag-meadow` and `--pack new-meadow`. Uses exact saved project/editor/scene structure and ID, source metadata SHA-1 identity shape, SHA-256 of actual scene bytes, bounded actors/layers and valid references, required `draft-unregistered` claim.
- `projects/swrlz-forge-moba/tests/test_starter_pack_validation_v216.py`: positive synthetic two-file pack, tampered hash/scene, provenance validation, duplicate/missing layer/actor checks, false playable-status rejection and actual current v10.0 Sheep Tag saved scene (66 actors, four layers).
- `projects/swrlz-forge-moba/starter-packs/README.md`: pack schema usage and future editor/runtime handoff.
- `.github/workflows/verify-forge-starter-packs.yml`: read-only GitHub Actions CI requiring no release secrets; checks validator syntax, tests and actual Sheep Tag scene. Existing governed engine patch/manifest and deployment request untouched.

Dedicated validator [#38217821003](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38217821003) passed on source `a104ab1c16f86b601a77d79dd53c14d092c41765`; other existing engine PR checks also run separately. A source-only PR is not an integrated or published §E engine release.

## Canonical knowledge and future engineering ladder

`main:§tart_§E.md` now references `main:docs/engineering/SWRLZ_ENGINE_PACK_AUTHORING_V215.md` in addition to the earlier v214 agent-build ladder. The agent must distinguish source discovery, work plan, atomic pack, pack CI, Projects registration, game-specific runtime/controls, patch/manifest reseal, browser editor save/history and Play tests, draft PR and dedicated §E deployment/hosted acceptance.

Next capabilities to implement, with separate approvals:
1. Integrate the engine-side validator into ordinary pack branches' CI and `@GitHub engine pack verify` evidence.
2. Implement explicit Projects registration/asset bundling and game-specific selective map maker UI from a validated pack.
3. Build a bounded multi-file source-edit and deterministic patch/test/repair workbench for runtime and core engine changes, without model-selected arbitrary GitHub writes.
4. Prove desktop/mobile editor Save/Load/Undo/Redo/Play/Stop plus mode-specific win/lose rules before a new mode is called playable.
5. Review/merge and release through **only** the guarded §E lane; require actual hosted marker, `SOURCE.json`, assets and gameplay, not CI alone.

**Status:** v215 Chat feature source/CI/deployment/version done; signed-in user acceptance pending. v216 engine validator source and CI validated on PR; merge, engine registration and live runtime deployment not performed.
