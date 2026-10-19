# §E / Model Atelier — Acceptance ledger through development v11.49

**Source of truth:** owner-supplied private `SE_Model_Atelier_Design_Spec.docx` / `SE_Model_Atelier_Design_Spec.md` dated 17 October 2026. These are implementation design targets, not permission to claim any missing capabilities exist. Preserve the private specification and original asset lineage.

**Production:** sealed v11.20, 90 original patches, original 283-part anatomy model, source manifest and `DEPLOY_REQUEST.json` unchanged. All new work remains separate draft preview code.

**Previously hosted and fully verified:** v11.47 isolated [precision preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-47/index.html?project=model-atelier), [six-shard and hosted exact-byte receipt](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39186091212).

## Current incremental topology/UV deliverables

- [#256 v11.46](https://github.com/kaministrator999-ui/Swrlzkamico/pull/256): actual local indexed adaptive triangle subdivide with conforming shared-edge splits; dedicated tests [PASS 39185575646](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39185575646).
- [#257 v11.47](https://github.com/kaministrator999-ui/Swrlzkamico/pull/257): manual front/side profile U/depth landmark matching to actual UV sheet vertices; [dedicated PASS 39186011336](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39186011336) and [full hosted PASS 39186091212](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39186091212).
- [#258 v11.48](https://github.com/kaministrator999-ui/Swrlzkamico/pull/258): explicit one-loop non-branching near-planar hole cap with face-winding opposite neighbor edges, tested proper convex/concave ear-clipped triangle construction and strict zero-area/non-manifold/nonplanar/self-intersecting refusal; [dedicated PASS 39189116836](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39189116836). Full cumulative/hosted [39189536597](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39189536597) must complete before calling it released.
- [#259 v11.49](https://github.com/kaministrator999-ui/Swrlzkamico/pull/259): actual triangle-UV relative area/stretch/zero-area diagnostic and opt-in safe XY/XZ/YZ planar UV reproject with normalized UV and optional U flip. Only operates on separately baked indexed mesh. Explicitly rejects near-edge-on/folded projections; saved textures may be repositioned, no arbitrary atlas unwrap. Full cumulative/hosted [39189711030](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39189711030) pending acceptance.

For all new operations: preview nonmutating; atomic native Undo/Redo commit; source procedural mesh unchanged; stale two-level runtime LOD discarded on geometry/UV changes; field/schema/cap validation and desktop/Android browser replay plus native Save/Reload required. Do not claim a full professional-modeler repair suite.

## Remaining owner-spec acceptance areas (all OPEN)

1. §2 True camera ray-occluded on-surface brush, accurate screen-space sizing and separate influence/selection rings; curved falloff and independent symmetry/asymmetry, concave visibility.
2. §3 Feature-preserving UV/material seam-aware curvature-based QEM retopology, arbitrary mesh local tessellation, real adaptive game LOD pipeline with seam-free transitions and deployable export formats.
3. §4 Safe inside/outside visibility and proper backface/interior ray selection on concave/hollow dense shells.
4. §5 Brush-painted and topology-following lasso region masks; concave wrapping; attached-pin normal offsets and local patch welding/rollback/feather blending as true multi-layer topology.
5. §6 In-viewport hit-testable 3D translate/rotate/scale gizmos with world/local/surface orientation, snapping, group transforms and zoom culling for the two pin families.
6. §7 Independent multi-window floating image docks, real adjustable reference camera lens/pose calibration, overlay/silhouette checks, cropped image reference handling.
7. §8 True freehand alpha-feather cutout, arbitrary silhouette, full nostrils/lips/ears and jaw/cranium/neck skin, profile joint image-depth registration, manifold/UV validated head volume and likeness signoff. Current v11.47 is **manual landmark-linked depth only**.
8. §9–12 Real owner-guided workflow from photos to edited closed head to deployable bounded LOD; large-scene mobile frame-rate/GPU memory/cancellation tests; QA and final owner release approval.

**Release boundary:** no merge, `source-manifest.json`, sealed patch, main/root static update or `DEPLOY_REQUEST.json` production change without full original-spec acceptance and explicit owner-governed release.
