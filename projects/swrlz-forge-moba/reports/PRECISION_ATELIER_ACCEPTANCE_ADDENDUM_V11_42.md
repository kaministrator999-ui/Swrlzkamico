# §E Model Atelier — topology elements, image silhouette and touch landmarks (v11.40–v11.42)

Date: 18 October 2026. Based on the private owner's five-page **§E Model Atelier — Precision Mesh & Reference-Driven Sculpting** design, 17 October 2026, sections 3, 5, 6, 8, 9 and 12. Inherits the prior [v11.39 acceptance ledger](PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_39.md).

**Candidate status: targeted engineering acceptance PASS; full integrated preview verification in progress.** The three implementations are stacked draft PRs and do not update the v11.20 production main, source seal, original figure, deployment trigger or hosted root.

## v11.40: deliberate real topology edits

[PR #250](https://github.com/kaministrator999-ui/Swrlzkamico/pull/250), [Actions PASS 39178448956](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39178448956).

- New tool group **Actual vertex / edge / face topology tools** displays only on a selected **baked** `topologyMesh` part. User chooses actual zero-based indexed triangle, edge or vertex; direct commands:
  - **Split edge** inserts a true indexed midpoint with interpolated UV, updates one boundary triangle or both incident adjacent triangles, and rejects nonmanifold edge incidence >2. This avoids inserting a T-junction at the chosen shared edge.
  - **Move indexed vertex** changes the actual XYZ coordinate, with finite signed offsets bounded by 0.4, and preserves source UV.
  - **Remove face** intentionally opens a hole, removes only the chosen indexed triangle and compacts orphaned vertex/UV arrays.
- Each operation is validated against native portable bounds and rejects any resulting degenerate triangle before a single Undo checkpoint. Changes survive native Save/Reload/Redo. No feature silently alters the 283 original procedural meshes.
- Synthetic shared-edge and original anatomical-head/Android browser acceptance passed. Initial CI red runs were due to cross-realm JS test equality and an invalid assumption that every reduced-mesh edge is manifold and has exactly one incident triangle; tests corrected to locate valid edges and assert their actual incidence.
- **Not yet:** topology extrusion/inset/bevel, arbitrary welded vertex deletion, multi-material boundary editing, nonmanifold repair, QEM/remeshing and automatic distance-switched runtime LOD.

## v11.41: authored face silhouette in real UV geometry

[PR #251](https://github.com/kaministrator999-ui/Swrlzkamico/pull/251), [Actions PASS 39178476828](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39178476828).

- Oval-derived reference face sheets accept optional 12 evenly angular-spaced radial contour values in native JSON, each 0.35–1.00. Every radial ring is interpolated to that custom star-shaped outline, changing actual mesh triangles and the matched image-space UV registration; it is not a cosmetic mask.
- Inspector: **Shape face outline** / **Restore oval outline**, validates all twelve values and preserves original local source image and 283-part original anatomical scene. Existing optional nose/eye/cheek landmarks and closed rear volume remain compatible.
- Real desktop and Android creation, invalid edit rejection, Undo, reference and native Save/Reload acceptance passed.
- **Not yet:** freehand photographic cutout, true alpha/background feathering, arbitrary multiply-connected silhouettes and calibrated profile-to-front reconstruction.

## v11.42: mobile/desktop direct image-tap landmark placement

[PR #252](https://github.com/kaministrator999-ui/Swrlzkamico/pull/252), [Actions PASS 39178692047](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39178692047).

- Optional **Tap active image to place selected landmark** uses the image's real loaded intrinsic dimensions and the overlay's `object-fit: contain` rectangle to compute exact **bottom-up source-image UV coordinates**, including letterboxing.
- Taps reuse the same validated nose/eye/feature Apply checkpoint and real face deformation as manual numeric UVs. A held/moved pointer still pans the image normally. Requires the selected face sheet and overlay image to reference the same source.
- Reject taps when the reference is zoomed/panned/rotated/mirrored rather than silently saving bad landmark UVs; user may reset image transforms first. Reject clicks in letterboxing and unavailable image pixels.
- Actual Android touch and desktop source-image tap → native saved landmark → continued silhouette and nose/eye geometry Save/Undo/Reload passed.
- **Not yet:** draggable markers with live transformed-image calibration, on-canvas transform gizmos, user-authored opacity masks or freehand silhouette stroke editing.

## Consolidated release discipline

[Full cumulative v11.42 integration and gated preview workflow](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39178855114) rebuilds the byte-verified 90-patch sealed v11.20 engine and additive v11.21–v11.42 overlay. It validates CPU geometry/native serialization plus original editor controls in **four Playwright desktop and Android shards**: sculpt, surface/interior, reference/image/face and lasso/topology. New tools are appended to their relevant shards. Only after all pass may GitHub publish **isolated** `atelier-precision-v11-42/` to the existing Space and independently verify the hosted exact HTML, SOURCE receipt and original 283-part scene file by digest.

**No production release:** the existing live v11.20 root must not be overwritten and the owner's complete 17 October spec remains open. Remaining major priorities include manifold-preserving multi-material retopology/repair, adaptive tessellation and automatic game runtime LOD selection, arbitrary freehand face silhouette/alpha repair, paired calibrated front/profile depth and complete skull-neck mesh, and true camera-space surface occlusion, paint selection, visual pin gizmos and dense mobile performance profiling. These cannot be inferred complete from passing unit tests for these three specific tools.
