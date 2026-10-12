# §E native starter packs and reliable agent engineering — v215

**Project owner:** the existing §wyrl§ Engine source in `main:projects/swrlz-forge-moba/`. **Assistant owner:** §wyrlz's account-bound GitHub workbench from its separately published HF Chat source. These are two different Hugging Face Spaces and two different release gates. Always read `§tart_§E.md`, `projects/swrlz-forge-moba/source-manifest.json`, `build_space.py`, `DEPLOY_REQUEST.json`, project scene/mode code and the applicable tests from current GitHub main before editing.

## 1. Truthful engineering progression

A plan, an editor scene, a descriptor, a registered Projects card, a playable game mode, a sealed engine build and a deployed/accepted §E release are **different milestones**. Never collapse them into one success claim.

1. **Understand a task.** Identify editor behavior, existing-game map variant, new game mode, specialized per-game builder, game hub, or engine core change. Clarify only genuinely unresolved fundamental product decisions; other implementation work is the AI's job.
2. **Map authority.** Load manifest order, editor transaction APIs, native `project/editor/scene` JSON, target mode runtime, exact source Git blobs and CI/workflows. Keep engine core, per-game project data and UI mini-editors separate. For example §E builds games; the launcher selects each game; each game-specific map maker exposes just that game's permitted functions.
3. **Create a review branch.** Never force main/runtime/release branch writes or accept a model-proposed GitHub scope grant. Independently check OAuth and repository roles.
4. **Build a source-verified starter pack.** `@GitHub engine pack sheep-tag-meadow as my-meadow on feature/my-meadow` queues an owner-confirmed **atomic two-file draft**: `scenes/my-meadow.swyrl.json` (editable native scene) and `starter-packs/my-meadow.starter.json` (source/provenance descriptor). Only allow approved seed scene types, bounded actors/layers, valid layer references, an available destination and current branch/main/blob snapshots. Atomic Git tree/commit plus a non-forced ref update keep both files together. A confirmed pack preserves the original scene, actor IDs and gameplay kind.
5. **Verify before extending.** `@GitHub engine pack verify my-meadow on feature/my-meadow` rereads both GitHub files, validates their identities, saved actor/layer envelope and SHA-256. A test failure is not an invitation to silently modify production. Review affected paths and request a new explicit approval if source changed.
6. **Make it an actual engine starter.** Implement the Projects selector/card, loader and `build_space.py` scene/asset registry. If gameplay differs, implement distinct mode rules, prefabs, editor-specific tools, HUD and runtime scripts. A game-specific builder must be simpler than full §E and must not merge unrelated gameplay modes in one session.
7. **Add tests.** Validate actor/prefab references; native Save/Load/Undo/Redo and Play/Pause/Stop; desktop/phone editor mode; no overwriting author scenes from live Play state; all existing 60-patch engine suites; rebuild and JavaScript syntax. Add source checks for a new runtime/patch rather than asserting Play from the presence of JSON.
8. **Evolve engine core only when necessary.** A new function belongs in a governed ordered Python patch/runtime module with stable integration hooks, bounded performance and compatibility. Update `source-manifest.json` final bytes/SHA-256 after a successful deterministic rebuild; never edit the sealed HTML artifact directly or mutate previous source receipts.
9. **Review & release separately.** Use an engine-only DRAFT PR, inspect exact diff and test evidence; the owner authorizes merge/release. Only the dedicated `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` plus `.github/workflows/deploy-swrlz-forge-moba.yml` may trigger this engine's Hugging Face deployment. Require terminal job results and hosted marker/SOURCE/assets and actual gameplay acceptance. Never use `kamiloki/Swyrlz` Chat deploy to publish §E.
10. **Maintain lineage.** Record seed, branch, source SHA, pack SHA, changed files, CI receipts, released engine version, behavioral acceptance and rollback reference. Mark features as *proposed*, *source-only*, *CI-verified*, *published*, or *live accepted* as supported by evidence.

## 2. v215 starter descriptor (data-only)

Schema `swyrl-engine-starter-pack-v1`, stored below `projects/swrlz-forge-moba/starter-packs/<id>.starter.json`. It includes ID/name, explicit `status: draft-unregistered`, type `existing-mode-map-variant`, seed/manifest/main source Git identities, scene file path/content SHA-256, byte count, actor/layer counts, gameplay kind and the remaining engine-specific work. Its companion native scene is below `projects/swrlz-forge-moba/scenes/<id>.swyrl.json`.

The descriptor is documentation/provenance, **not** an active engine plugin, registry, executable script or guaranteed playable starter. A seed from Sheep Tag still uses Sheep Tag rules. Do not rename it MOBA/Maul/arena and claim the mechanics were created; that requires new runtime/editor code.

## 3. Agent tool boundary

As staged in the v215 GitHub assistant source: `engine pack help`, `engine pack SEED as ID on feature/branch`, `engine pack verify ID on feature/branch`. The exact source is validated before any proposed write, and again after the owner issues a short-lived one-use `@GitHub confirm CODE`. The commit must be a nonforced fast-forward of the same feature branch with exactly the two new files. If a ref, seed, manifest, selected repository, approved content hash or target path changed, fail closed. GitHub network uncertainty is not a confirmed mutation; inspect the branch before retrying.

This tier does **not** implement arbitrary model-generated multi-file runtime patches, automatic packaging/Projects registration, automatic PR merge, or autonomous §E production deployment. Those are separate subsequent engineering tiers requiring a safe workspace, deterministic execution/tests and explicit user-controlled gates.

## 4. Next concrete engine/editor engineering tiers

- **v216 validation:** an independent §E starter-pack validator for GitHub source and local CI; check file digests, actor/layer IDs and pack lineage, including negative tests. Add a read-only command to produce a deterministic validation evidence report.
- **v217 pack registration:** promote a verified pack into an editor-loadable Projects starter through a governed new ordered patch and explicit asset bundling; test round-trip save, undo/redo, Play/Stop, desktop/mobile.
- **v218 playable mode builder:** separate Sheep Tag, MOBA/angel arena, Maul, platformer, anime or adventure rule adapters with purpose-built per-game authoring menus. Let user choose game rules and themes; keep game hub as launcher, not one mixed gameplay loop.
- **v219 multi-file source workbench:** protected source transformation contracts, typed patch previews, exact Git blob range ownership, build/test sandbox, failure repair, review PR, lease-aware atomic Git commits. No model-authored arbitrary workflow execution or secret/production writes.
- **v220+ managed engine updates:** rebuild/seal manifest, run full existing engine suite plus new mode checks, dedicated guarded merge/release, hosted audit and rollback. Never call live-success without observed engine behavior.

**Bottom line:** §wyrlz should learn by operating on actual GitHub source, producing measurable artifacts, reading CI, and retaining verified boundaries—not by memorizing undocumented plans or treating model inference as permission to ship.
