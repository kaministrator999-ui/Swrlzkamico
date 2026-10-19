# §E Model Atelier — private owner-spec implementation ledger through draft v11.54

Source: owner-provided **§E Model Atelier — Precision Mesh & Reference-Driven Sculpting** (17 October 2026), especially numbered sections 2–12 and acceptance slices A–F. This is a scoped code/validation ledger, **not** a declaration that every acceptance criterion is met.

## Immutable production boundary

- `main` continues to host the fully validated production **v11.20 anatomical-head** source. 90 sealed patches, 43 packaged assets and the owner source-manifest/DEPLOY_REQUEST protocol are intentionally preserved.
- New preview source remains linear draft PRs, not in `main`. The verified v11.51 preview is independent of the production root. Full promotion requires the original §tart §E source/asset/roadmap, complete native desktop/phone/browser regression, owner appearance signoff and **DEPLOY_REQUEST.json as the final main content mutation**.
- Never confuse green unit tests, browser tests, validated hosted preview, merged source, production publication, and artistic/owner acceptance.

## Verified v11.51 (feature slice)

- [PR #261](https://github.com/kaministrator999-ui/Swrlzkamico/pull/261): camera-ray first-triangle occlusion with bounded BVH, local-space stored eye, separate opt-in surface mode. Full [eight-job workflow success](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39195917627) including native desktop/Android and exact hosted integrity. [Isolated preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-51/index.html?project=model-atelier).
- This **does not** implement full geodesic plus ray occlusion for arbitrary concave shells or guarantee performance on physical phones. Hard budget enforced.

## Successor implementation candidates; verify each HEAD before publication

- **v11.52** [PR #262](https://github.com/kaministrator999-ui/Swrlzkamico/pull/262): camera-projected CSS pixel sizing for independent influence and selection radii; bake local values into deterministic saved native strokes. Perspective/ortho, invalid dimensions and head anisotropy are tested. **VERIFIED ISOLATED PREVIEW:** [all eight jobs PASS #39204722191](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39204722191); [hosted preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-52/index.html?project=model-atelier). The original 75px test exceeded the native 2.5-unit radius limit (measured 2.7422), so 18/22px radius acceptance preserves the cap; source SHA/hosted exact receipt `04557f3835d32369e447df7ae6fe3f33f569368676279097d5072e8cb41f1f5a`.
- **v11.53** [PR #263](https://github.com/kaministrator999-ui/Swrlzkamico/pull/263): additive/subtractive localized tangent-shell painted mask dabs for editable named lasso regions; preserves 📌 polygon and mesh, atomically records drag strokes and numeric paint taps in Undo, native model JSON. This is **not** arbitrary folded-surface geodesic paint or full alpha/UV painting. **VERIFIED ISOLATED PREVIEW:** [all eight jobs PASS #39204761514](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39204761514); [hosted preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-53/index.html?project=model-atelier), receipt `02d4a26670c844d25f6282845144ef42e006996e015dc85086c7fddc887ec7d2`. Existing pin/refinement operations, native desktop/Android Save/Undo/Reload tested.
- **v11.54** [PR #264](https://github.com/kaministrator999-ui/Swrlzkamico/pull/264): viewport rotation ring and scale grip (mouse/touch) for selected source vertices using existing real `atelierGroupEdit` in object/world/surface space, scoped native movement bounds, Undo and export/reimport. This is **not** complete per-axis 3D scene manipulation for both pin families.

## Outstanding owner-spec acceptance (do not claim DONE)

1. **§2** Full camera-aware connected/geodesic selection on highly folded and interior shells; exact screen-uniform falloff footprint, independent preserve-asymmetry methods, freely editable custom falloff curve and reliable preview rings for all surface modes.
2. **§3** Robust UV/material/seam-sensitive curvature-QEM adaptive decimation/retopology and actual game-export LOD pipeline. Current two-level preview/runtime LOD is a constrained starting point; still need complex topology and engine export tests.
3. **§4** Physically validated deep concave interior/backface picking, clipping and device interaction limits.
4. **§5** Folded-surface topology-following/brush-painted lasso masks, surface-attached pin normal offsets, local patch weld/rollback/feather transitions with strict nonmanifold guarantees under arbitrary edits, and real layered topology history.
5. **§6** Full independent selectable XYZ translation/rotation/scale manipulators for *both* 📌 boundary and 📍 actual mesh pins; visibility/culling and snapping in every frame/plane.
6. **§7** Independent simultaneous floating reference *windows*, per-image lens/pose calibration, transparency cutout and silhouette matching across front/profile/three-quarter/rear; missing-file lineage and mobile dock usability on actual devices.
7. **§8** Real freeform alpha-feather photographic face cutout, arbitrary silhouette-conforming UV triangulation, complete nostril/lip/ear and jaw/cranium/neck volume, connected-manifold closing, calibrated multiview reference depth and human likeness signoff. The preexisting 12-control outline and manual profile-depth links are **partial manual tools**, not automatic face reconstruction.
8. **§9–12** End-to-end native photographic head workflow, saved layers and final bounded runtime export, dense-scene physical Android GPU memory/FPS, cancellation budget checks, invalid object/schema fuzzing, exact build receipt audit, mobile multi-gesture regression, and owner appearance acceptance.

## Guardrails for each next implementation

Add one coherent native feature at a time. Preserve imported original references and v11.20 source geometry; no destructive schema replacement. Track measured geometry/UV/shading changes. Separate scene-data validation, input-error rejection, Undo transaction, Save/Reload consistency, desktop/mobile browser checks, and hosted exact-byte/audit from human judgment. Only promote when the owner approves final behavior and the complete production source/deploy protocol has been followed.
