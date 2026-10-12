# v213 — §E project-aware GitHub assistant: editor, starter scenes and engine updates

## Source of truth and deployment separation

§wyrlz AI Chat and §wyrl§ Engine share a GitHub repository, but do **not** share a deployable source tree. The engine is hosted from `main:projects/swrlz-forge-moba/` and governed by `main:§tart_§E.md`, `source-manifest.json`, `build_space.py`, `patches/`, `runtime/`, `scenes/` and `.github/workflows/deploy-swrlz-forge-moba.yml`. The engine goes to `kamiloki/swrlz-forge-moba`. The Chat/LALM source goes to `kamiloki/Swyrlz`. Neither should be silently published using the other's request file.

The v10.0 Sheep Tag scene is genuine native editor JSON: `project`, `editor.layers`, `scene` with game-mode-specific actor and rules fields. The packed HTML is reconstructed from six base payload chunks and 60 ordered patches; `build_space.py` verifies exact base and final SHA/byte counts, then bundles a *particular* list of asset files. A GitHub scene file is **not** automatically a selectable Projects card, a bundled scene, or a playable new mode. New modes need explicit engine patches, mode runtime logic, editor integration, state restoration and verified Play tests.

## Development-mission ladder

1. **Discover:** Verify selected GitHub repository identity, real main branch, current `source-manifest.json`, engine deployment request and starter scene inventory. Do not extrapolate from the Chat branch or old §E releases.
2. **Plan:** Identify whether the task is a **project/scene prototype**, **new playable game mode**, **editor feature**, **engine core upgrade**, **asset workflow**, or **§E release**. Select actual source files/patch order, established scene envelope, acceptance criteria and desktop/phone tests. Seek the user's decision only if the *fundamental game design* is genuinely unspecified.
3. **Draft starter:** Derive a compatible native scene from a verified seed on `main`, preserving actor/layer/game rules and adding only an isolated project name/ID and lineage. Create it solely on a verified feature branch with explicit one-time confirmation. A draft is not automatically registered, built or playable as a distinct game type.
4. **Develop actual mode:** Update the game's scene and runtime, register a Projects card/template, implement the gameplay and editor authoring tools, maintain Undo/Redo, Save/Load, pause/restart/stop invariants and all other editor projects. Use additive deterministic patch modules; do not edit compiled sealed HTML directly. This remains a **future coding capability**, not an autonomous write tool in v213.
5. **Verify:** Rebuild ordered source and checksum manifest, check generated JS/Python syntax and native scene validity, run relevant Playwright desktop/phone suites and preserve existing §E tests; distinguish synthetic CI from live gameplay acceptance.
6. **Review:** Summarize exact engine-only file changes in the feature branch and prepare a GitHub **draft PR** using a one-use owner-bound confirmation. Do not merge the PR or run any deployment automatically.
7. **Release (separate gate):** Only an approved §E workflow can merge, update `projects/swrlz-forge-moba/DEPLOY_REQUEST.json`, build and publish to the dedicated Space, and verify hosted marker, `SOURCE.json`, all assets and live interaction. No Chat/LALM deploy gate for §E.

The assistant should show meaningful observed states, confidence/unknowns, commit hashes, actual CI and host receipts. It must never present hidden chain-of-thought, silently acquire OAuth scopes, execute arbitrary model-generated GitHub writes, claim a seed copy is a fully implemented mode or pretend that CI proves real-world signed-in/editor gameplay acceptance.

## Commands in v213

- `@GitHub engine help`: command guide.
- `@GitHub engine status`: live read of engine source manifest and dedicated release request.
- `@GitHub engine starters`: live listing of native scene file names/sizes from engine main.
- `@GitHub engine plan build a MOBA starter pack`: evidence-backed mode/editor/build/review plan, **not** a mutation.
- `@GitHub engine plan add a new editor inspector tool`: targeted editor-authoring mission plan.
- `@GitHub engine clone sheep-tag-meadow as arena-draft on feature/arena`: a no-write scene proposal; `@GitHub confirm CODE` creates one copy on an *existing* review branch after rechecking GitHub OAuth/repo role, main head, branch head, source blob SHA and destination nonexistence.
- `@GitHub engine review feature/arena`: prepare a draft PR of bounded project-only added/modified files against current main; a distinct one-time `@GitHub confirm CODE` rechecks diff and branch heads.

The engine command owner is `hf_space/forge_project_tools_v213.py`, attached to the existing `hf_space/github_connection.py` user-scoped OAuth connection and `hf_space/station.py` NDJSON lifecycle. No extra stored tokens, Google identity forks or paid external inference. The planner uses actual main-branch files, not the Chat source tree.

## Reliability and explicit remaining work

v213 is **the first vertical slice**, not complete autonomous editor/engine development. It implements truthful project discovery and an approved native scene scaffold. It **does not yet** have a generic safe source patch editor, automated scene-to-Projects registration, mode builder, engine-patch generator or autonomous recovery runner. Those require gated generation/editing of multiple repo files, a diff preview, specific unit/Playwright verification, protected merge/deploy ownership, rollback and repeated actual-game tests. Preserve this distinction in user-facing answers.

Do not touch or claim a deployed §E starter during this Chat/LALM tool release. Stage separately governed §E engine enhancements on the appropriate engine branch and use its own deployment workflow. No static documentation text or model-produced plan is a credential, permission, or execution authorization.
