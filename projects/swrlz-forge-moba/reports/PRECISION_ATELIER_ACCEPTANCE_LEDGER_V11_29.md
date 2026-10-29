# §E Model Atelier — Precision Design Acceptance Ledger (v11.29 draft)
Date: 2026-10-18. Owner design basis: `SE_Model_Atelier_Design_Spec.docx` (2026-10-17).

**Status: INCOMPLETE FEATURE CANDIDATE. Not a production §E release, art approval, or Codex-operated character sculpt.**

## Authority and preservation
- Production/source-manifest authority remains v11.20 `V11_20_ANATOMICAL_HEAD`; original 283 editable scene parts, eleven anatomical-head sections and 1,623,252 full-scene measured triangles are historical baseline. No production source, sealed manifest, deploy trigger, reference images, model starter assets or unrelated AI Chat code were rewritten by these draft branches.
- Draft lineage: [#219](https://github.com/kaministrator999-ui/Swrlzkamico/pull/219) v11.23 → [#229](https://github.com/kaministrator999-ui/Swrlzkamico/pull/229) v11.24 → [#230](https://github.com/kaministrator999-ui/Swrlzkamico/pull/230) v11.25 → [#231](https://github.com/kaministrator999-ui/Swrlzkamico/pull/231) v11.26 → [#232](https://github.com/kaministrator999-ui/Swrlzkamico/pull/232) v11.27 → [#233](https://github.com/kaministrator999-ui/Swrlzkamico/pull/233) v11.28 → [#234](https://github.com/kaministrator999-ui/Swrlzkamico/pull/234) v11.29. **These are stacked draft pull requests, not a release history.**
- Candidate changes compose the sealed v11.20 editor and opt-in modules through `patches/v11_21_vertex_sphere_brush_preview.py`; tests operate the built editor. `DEPLOY_REQUEST.json` remains untouched.

## Feature status against the owner design
| Slice / area | Implemented and specifically tested | Explicit limits |
| --- | --- | --- |
| A references | Existing floating local front/profile image references, camera match, transform/opacity and native image save/reload | Full floating multi-panel grid, perspective lens matching, resizable/dockable overlays, complete missing-image workflow unfinished |
| B vertex selection | Existing mapped 📍 vertex points, touch move gizmo, source-index numeric group translate/rotate/scale, Undo | Visual multi-axis rotation/scale handles, arbitrary insert/delete mesh vertices and selected-only culling unfinished |
| C surface brush | v11.27 push/pull + smooth/flatten/inflate/pinch/translate, flat/sharp/smooth/soft falloff, plateau/taper, limited local-X mirrored brush. v11.25 explicit opposite-normal Inside shell, v11.29 conservative Nearest shell, existing front/connected/through | Mirrored strokes preserve existing asymmetry (do NOT force a fully symmetric base), custom curve falloff, continuous stroke painting and true screen-camera occlusion tests unfinished |
| D lasso | Existing surface-attached 📌 editable polygon and freehand samples, named regions, pin add/remove/drag, region morph and Undo/JSON | Brush-painted/topology-following boundaries, Boolean add/subtract/intersect, pin group transforms and smooth edge interpolation unfinished |
| E localized detail | Conforming triangle patch layer(s), UV/color interpolation, reversible visibility/order/remove, native state, v11.26 measured pre-commit region budget. v11.28 true parametric sphere/loft U/V presets and generator-measured vertex/triangle preview | No arbitrary exact vertex total guarantee, general mesh decimation, adaptive tessellation, temporary/permanent topology bake, complete layer blend/lock/duplicate and runtime LOD exports unfinished |
| F face starter | Existing UV-mapped face sheet, oval/rectangle crop, saved front-image UV, separate manually closed oval head volume and stretch heatmap | Hand-cut silhouette, semantic landmarks, camera-calibrated multi-view/profile reconstruction, neck and true anatomically verified final head geometry unfinished |
| Mobile and render | Existing single-finger orbit, two-finger pinch/pan, inside camera clipping/reset, shaded/wire/X-Ray and independent colors/textures | Dense scene device memory profiling, all possible cross-tool interactions and owner visual acceptance unfinished |

## Grounded acceptance receipts
- v11.24 freehand desktop + real Android-touch native roundtrip: [39139677634](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39139677634).
- v11.25 interior shell and exact camera restoration desktop + Android: [39143770620](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39143770620).
- v11.26 local detail preview true **48,768 → 50,454** head triangles desktop + Android: [39144264793](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39144264793).
- v11.27 new brush ops, virtual seam smoothing, legacy equivalence and desktop/Android roundtrip: [39145218894](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39145218894).
- v11.28 non-mutating density profiles, native U/V **192×128 → 96×64** in tested head metadata, desktop/Android JSON/Undo: [39145853534](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39145853534). This is **not** proof of a low-triangle arbitrary-mesh decimator or exported runtime LOD.
- v11.29 synthetic same-facing stacked-plane depth isolation and real desktop/Android original head native roundtrip: [39146140320](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39146140320). A tangent-plane vertex-depth filter **is not true camera-occlusion accuracy**.
- Native v11.20 source seal, grounded anatomy, face/pose frame, geometry profiler and the broader anatomical studio regression run independently at current branch head. Check their terminal results separately before release.

## Preserved failure paths
- v11.24 first freehand browser tests tried empty camera space; later verified selected geometry by raycast and used real touch events.
- v11.25 mobile camera exit initially reset to fixed distance, violating pre-entry camera preservation. Code now restores actual orbit/target/pan/near/far; rerun passed.
- v11.26 first browser run attempted connection before the test HTTP server was ready; added bounded readiness wait.
- v11.27 first numeric flatten assertion assumed full displacement at a falloff-weighted vertex; test corrected to verify proportional movement, preserving falloff.
- v11.28 detected collision with the original `modelAtelierDensityPreset` ID; new controls now use `modelAtelierSculptDensity*` IDs and pass real browser tests. Never delete these prior CI failure receipts.

## Release and next engineering gates
1. Work through the remaining functionality **one coherent testable slice at a time**, without replacing existing editor architecture/part IDs or collapsing user reference data into assistant defaults.
2. Add true visible-only occlusion handling; arbitrary connected topological edits and boundary set operations; general reduction/runtime LOD authoring; multi-perspective face landmarks and manual skull/neck shaping controls. Preserve source mesh and historical edits.
3. Test cross-tool interaction combinations, dense mobile GPU/memory limits, native exact Undo/Redo & JSON/OBJ roundtrip, manifold boundaries, material/UV fidelity, inside/outside editing and real touch.
4. An actual Codex/browser interaction must use the real editor and capture before/after front/profile/rear images before declaring the character sculpt done. This ledger does **not** substitute for that session.
5. Only after full spec acceptance: sync release version, generator, manifest, README, Space README, ROADMAP, marker and workflows; merge validated commits, update `DEPLOY_REQUEST.json` as the **last repository mutation**, verify the exact triggered Actions run and exact live hosted marker/content. Until then: **NO MERGE / NO DEPLOY / NO CLAIM OF COMPLETENESS**.
