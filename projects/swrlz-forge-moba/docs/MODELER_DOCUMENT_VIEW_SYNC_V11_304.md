# Already-open Modeler document synchronization — v11.304 source/browser verified; awaiting publication

Lifecycle: IMPLEMENTATION_APPROVED; SOURCE_VERIFIED; FRESH_BROWSER_VERIFIED. Strict verifier and actual single-process browser gate passed. Source publication/hosted confirmation and owner-device acceptance remain pending.

## Confirmed failure and bounded repair

The §c-authored Little Crystal Mage could load all saved native parts while an already-open Model Atelier retained its previous empty derived mesh scene. JSON contained the model but the production GLB exporter saw zero meshes. Read-only inspection and the existing `renderParts()` isolated the failure to document/view synchronization. The base `open()` returns early for an already-visible panel; closing/reopening on the direct Modeler route can initialize Game and change the active project.

The append-only runtime records the effective native/scratch model, parts array and model root after successful existing rendering. After legacy `syncProject()`, it rebuilds the existing scene, mesh list, inspector and camera only when the visible renderer projects a different effective document. It clears stale document-specific selection, component/drag references and helper overlays. Repeated synchronization preserves valid selection and display preferences. It retains the renderer, canvas, camera instance, animation loop, native document and Undo/Redo history. It does not author model geometry, checkpoint, mark dirty, close/open the editor or initialize Game.

## Integration and exact source

An earlier unpublished sync candidate used the then-free v11.298 identity over Engine v11.297 and passed the actual fresh-browser 59-part cloud-load/display check. Meanwhile owner releases v11.298–303 advanced the Vanguard image/UV, mesh, mapped PBR and anatomical portrait work. This candidate is rebased as **v11.304** on canonical main `d3a5f09e8819a7d2431befe0840584714ac24a0a`, preserving all 334 historical patches in order and every owner source file unchanged. Only the new sync patch appends at position 335. No runtime behavior was changed during renumbering.

The predecessor sealed Engine v11.303 has 8,375,417 HTML bytes and SHA-256 `7f7be6fdee1a05589d6eed3301b6d2192a3dfee15dfa362b65b5c69d72b01419`. The truthfully reconstructed candidate has **8,377,905 HTML bytes**, SHA-256 **`c2f005b86f9c6e925272c052d429d8b01139d30cb121af7553d38a61788eac5b`**, **335 patches** and **71 assets**. `DEPLOY_REQUEST.json` remains the owner's v11.303 request until source publication and its separate request-only commit.

## Bounded verification

The strict verifier rebuilds from original payload and every ordered patch, requires exact index/modeler identity and manifest/SOURCE bytes/SHA, checks all 71 assets, parses assembled JavaScript and retains character-tool and outward-loft regressions. It also checks current owner portrait source anchors and runs the existing v11.303 anatomical/UV regression. No unrelated Sheep Tag/game suites run.

The real-Three169 sync regression exercises the assembled model facade, scene/list/inspector rebuild and production GLB export with lightweight DOM/unrelated rig adapters. Cases include an open empty scratch→native load, another document reusing a part ID, replaced parts array, valid empty scratch, repeated sync, closed view and Game context. Assertions cover actual meshes/list/GLB counts, unchanged native data/history, renderer/canvas/camera reuse and no extra loop. The private final 59-part fixture checks all IDs and export mesh count and never enters Git/HF packaging.

```sh
python projects/swrlz-forge-moba/scripts/verify_v11_304_release.py --output /workspace/scratch/swrlz-mage-v11-304 --three-module /workspace/scratch/loft-295-candidate/three-0.169.0-esm.mjs --native-project /workspace/scratch/mage-evidence/Little_Crystal_Mage.native-project.json
```

Passed: exact 75-file package; three assembled scripts parsed (`shaderScriptChars=7926701`); v11.293 native character tools; v11.295 straight768/curved768/braid288 outward surfaces; native 59 scene/list/production GLB; v11.303 anatomical portrait11745vertices/16eye details/30Bezier details/768px atlas, armor/hands preserved. Index and Modeler bytes match; all 71 assets match SOURCE.

Evidence log: `/workspace/scratch/engine-sync-304-verify.log`. Candidate package: `/workspace/scratch/swrlz-mage-v11-304`. The pinned test dependency is byte/SHA-verified and excluded from output. Hosted receipts must be added only after publication; engineering checks do not establish owner phone/Quest appearance acceptance.

## Actual fresh-browser receipt — 2026-11-07

A fresh single-process Playwright session loaded exact sealed v11.304 at the direct Modeler route and imported the unchanged §c-created native-project file via canonical `#fileInput`. The existing open scene/list automatically populated all 59 native parts and 59 mesh rows, with the complete visible mage. No manual render/selection refresh or model-authoring injection was used. The real native JSON/GLB buttons emitted ordinary downloads:232,076-byte editable JSON, SHA-256 `5449fda0db2d1255bbde5fadabfccde69daf3648e7a52f90da987589362e6a7b`; 1,092,072-byte GLB SHA-256 `32cff7214f8a8ca7525f65973214a232fb444b6d3d8a447d7c95656966b2cb37`. GLB validation confirms59 exact mesh names matching the native document.

Evidence: `/workspace/scratch/mage-evidence/final304/verification.json` and `Little_Crystal_Mage-preview.png`. An earlier candidate had independently passed canonical cloud loading of the final durable59-part account revision 2. The final304 session's official account resume returned 401 after a later Chat release; therefore the304 gate proves canonical native-file import/display/export, not a new304 cloud authentication/readback. Single-process Playwright resolved an earlier CDP download TargetClosed harness failure; the actual app exports are sound.
