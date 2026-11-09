# §E v11.361 — WebXR starter repair + native Quest 2 controllers

## What changed

The previous v11.358 WebXR hand starter project cards were present but could fail to open in the Model Studio workflow. The v11.361 entry point now intercepts starter selection through the existing project modal and global template loader, validates the loaded source, routes to the existing native Modeling workspace, and checks that the editor actually opened before reporting success. It gives a visible failure message instead of silently presenting an empty game/world view. The old hand model assets and their MIT license remain unchanged.

The two newly introduced controllers are `webxr-touch-left` and `webxr-touch-right` under Projects → Starter Models and can also open through `?project=...`. Both use actual source geometry and the embedded color artwork from the public WebXR Input Profiles `oculus-touch-v3` left/right GLBs for **Quest 2** (not Quest 3S Touch Plus). Each contains seven individually editable native parts (shell divided into two pieces to stay below the engine's per-part vertex limit, plus trigger, grip, thumbstick and two face buttons). Parts remain grouped as one controller assembly. Their original UV data is retained, adapted for the native TextureLoader flip convention; a 512px PNG is stored on the individual parts to preserve paint in portable saved model projects.

## Licensing and provenance

Both GLBs are covered by the upstream MIT license. The source package `packages/assets/LICENSE.md` is copied to `assets/models/webxr-touch-v3/LICENSE.md` with attribution. The source blobs (GitHub SHA IDs) are embedded in their converted JSON data. The conversion bakes the glTF hierarchy's transforms into native part coordinates, scales/centers the controller for the Model Studio workspace, and preserves the complete triangle sets and UV texture. This is a static editable modeling reference and **does not** drive Meta runtime inputs, tracking, button animation or the headset's native renderer.

## Regression boundaries

All earlier hand starters, Rock Hand, Plain Hand, Arcane Gloves, game projects, VR controls and UV painting are preserved. No replacement of existing project records, new editor layer/popup, or extra renderer. The original hand mesh geometry remains distinct from the controller models.

## Validation target

- Both hands open the existing native model view, not the game scene.
- Both Touch controllers open with exactly seven selectable native mesh parts and a grouped assembly.
- Both have a texture image, positions, UVs, valid triangle indexing, and are persistable through existing save/export.
- Model tab classification is unambiguous; hands/controllers are not duplicated or moved into Games.
- Source manifest, output size and SHA-256 match the built editor; bundled assets and MIT notice are present.
- Physical device acceptance is done by the owner after production deployment.
