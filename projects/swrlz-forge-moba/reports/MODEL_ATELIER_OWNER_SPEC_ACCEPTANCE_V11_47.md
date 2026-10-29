# §E Model Atelier — Original owner-specification acceptance tracker (17 October 2026)
## Current development: v11.46–v11.47, additive previews, NOT full acceptance

**Private source:** `SE_Model_Atelier_Design_Spec.docx` / `SE_Model_Atelier_Design_Spec.md`, 17 October 2026. Designed by Kami + §wyrlz. This tracker stays in the private project; do not publish the proprietary contents externally.

**Production preservation:** official main/static root §E v11.20 is sealed and original 283-part anatomical model must remain intact. Latest independently verified isolated preview prior to this work: [v11.45](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-45/index.html?project=model-atelier). These new features remain **stacked draft, unmerged PRs** and may be released only after terminal combined checks.

## Newly implemented, bounded slices

### v11.46 — local adaptive indexed tessellation (PR #256)
- User picks explicit object-local XYZ selection center, radius and *maximum triangle edge length*. The tool chooses actual faces by centroid/radius and edge-length threshold, counts modified neighboring faces and resulting native triangles/vertices, and previews without mutation.
- On Commit, all marked physical edges are split across adjacent triangles. Collinear fan splits are avoided by adding interior triangle center and using a proper face fan; existing position and UV seams remain supported, with actual midpoint interpolation and bounded output.
- Atomic Undo/Redo, validated native JSON and Save/Reload, original procedural source untouched. Any stale low runtime LOD profile is deliberately invalidated and must be regenerated after actual high topology edits.
- [Dedicated geometry and real desktop/Android CI **PASS 39185575646**](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39185575646): two-triangle test selects ONE triangle, stitches its unselected shared-edge neighbor, grows 2→10 real indexed faces, verifies signed surface area, no degenerate/nonmanifold triangles, UV correspondence, pre-apply unchanged source, Undo/Redo and reimport.
- **Limits:** one bounded local refinement pass on a separate baked indexed mesh, not arbitrary continuous/remeshed quad topology, fitted curvature-based QEM, paint-boundary selection or assured manifold preservation on all unusual multi-material source geometry.

### v11.47 — manually calibrated side-reference feature depth (PR #257)
- Two image references remain separate. Creator selects a true left/right profile image; calibrates normalized profile front-plane origin, normalized-image-unit → world depth scale and nose direction. Link existing *named front-image* feature marks (nose/eye/brows/cheeks/mouth/chin) to numeric side-image U positions.
- Native landmark `profileU` is optional. `faceSheet.profileGuide` is strict; derived depth must be finite, ≤.4 world units and exactly consistent with image calibration. Recalibrating adjusts only linked landmarks, retaining original front-face photo/UVs and independent unrelated landmark depths. Clear/unlink actions preserve current sculpted depth, with native Undo.
- This is explicit guided 3D sculpting, **not** automatic computer-vision, perspective calibration or a guaranteed head likeness.
- **PASS** [targeted native geometry and desktop/Android browser workflow 39186011336](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39186011336), including two image references, native nose/eye depth links, re-calibrated depth, invalid input rejection and Save/Undo/Reload. **PASS** [full cumulative six-browser-shard+CPU integration and hosted publication 39186091212](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39186091212) at tested code SHA `d27cc62a73c1cedd911753b3f5654a5da95d36c3`. Isolated [v11.47 preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-47/index.html?project=model-atelier) HTML 2,852,736 bytes, SHA256 `5a49c4886db81403a516d18fdf69dbed0ebba6ad8e6355fd9d0db606b9ef76f7`; exact hosted HTML, SOURCE receipt and original v11.20 anatomical model scene matched; 91 patch steps (90 original + additive overlay) and 43 original packaged assets.

## Exact remaining feature ownership (not validated complete)

| Original spec | Incomplete acceptance criteria |
|---|---|
| §2 Surface brush | Actual camera-ray/per-visible-triangle occlusion instead of approximate facing/shell; screen-space brush radius and independent custom curved falloff; separate front/rear/connected toggles; tapered selection rings and weight visualization on dense meshes |
| §3 Mesh density, QEM and LOD | Curvature-aware adaptive multilevel tessellation on all supported mesh kinds; genuine UV/material seam-preserving feature decimation; multiple game LOD levels with seamless transitions and external engine deployment format; exact targets where realizable and progressive mobile cancellation |
| §4 Interior sculpt | Folded concave double shells and true visible/front/back ray confirmation, robust inside/outside interaction at production mesh density |
| §5 Editable lasso | Brush-painted selections, topology-aware wrapping on concave/hollow geometry, optional pin normal offsets, post-drag local topology regeneration, full temporary/edit-layer/permanent transitions, per-layer weighted blending and crack-free transition controls |
| §6 Mesh/pin gizmos | Truly visible and touch-hit-tested 3D translation, rotation and scale manipulators for each pin family; world/object/surface orientation and zoom-based pin culling/selected-only performance |
| §7 Reference studio | Multiple separate independently docked panels, true silhouette overlays and image-to-mesh lens/camera calibration including perspective uncertainties, independent crop and missing-file UI, mobile one-thumbnail safety |
| §8 Photo to anatomical head | Freehand image cutout with feather/alpha, arbitrary silhouette contour rather than only 12 radii, actual face features/ears/nostrils and neck topology, photo-specific UV repair, calibrated joint front/profile image-space alignment and complete inspected skull-neck closure and likeness |
| §9–12 Complete workflow | Owner-guided actual front and profile asset→silhouette→edited face region→front/profile relief→closed head→topology/UV test→editable saved layers→runtime LOD/export→Undo/Reload; verify deterministic regression, all 283 parts, 1.6M-triangle mobile GPU/memory/frame-time caps, manual artistic signoff, then formal governed production promotion |

**Acceptance protocol:** Every remaining row stays OPEN until executable unit + desktop/Android browser + dense-mesh performance + real user visual evidence match the original specification. Independent desktop/mobile target tests of slices are not evidence of full design completion. New preview publication must verify hosted index HTML, SOURCE receipt and original anatomical scene digests and never mutate main/root or `DEPLOY_REQUEST.json` prematurely.

## Stage result: published isolated preview, original design still incomplete

**[v11.47 hosted review preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-47/index.html?project=model-atelier) VERIFIED**. Both feature PRs remain draft and unmerged into the sealed production branch. Art and native model workflow still require owner visual validation. Do not announce all requirements or production as finished.

## Stage handoff
- [Draft #256 local adaptive indexed subdivision](https://github.com/kaministrator999-ui/Swrlzkamico/pull/256).
- [Draft #257 manual profile-linked depth](https://github.com/kaministrator999-ui/Swrlzkamico/pull/257).
- New isolated [v11.47 end-to-end verification Actions](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39186091212). DO NOT claim publish until final SHA checks.
