# §E Model Atelier — v11.45 front/profile comparison and cumulative acceptance

18 October 2026. Owner's 17 October private design: §E Precision Mesh & Reference-Driven Sculpting, section 7/8. Continue [v11.44 acceptance](PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_44.md) and the previous [v11.42 baseline](PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_42.md).

**Development state:** [PR #255](https://github.com/kaministrator999-ui/Swrlzkamico/pull/255) is a DRAFT stacked on [v11.44 #254](https://github.com/kaministrator999-ui/Swrlzkamico/pull/254) → [v11.43 #253](https://github.com/kaministrator999-ui/Swrlzkamico/pull/253). Stable v11.20 and all original 283 parts were not modified.

## Verified reference-comparison controls

[Dedicated original-scene desktop and Android **PASS 39184002914**](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39184002914).

- The floating Model Atelier References dock now supports **simultaneous front/profile or other second-view comparison**, chosen from up to four imported local JPEG/PNG/WebP references. The secondary image is displayed inside the same pinned/resizable/collapsible overlay, not replacing the model or the primary image.
- Each image keeps its previously saved pan, zoom, opacity, mirror, rotation, visibility and named angle settings. Switching image tabs swaps comparison roles when needed and lets users edit the newly active image's transforms; secondary view reflects the other image independently.
- `referenceLayout.compareId` is **optional** and strictly validated: only a different existing reference ID; missing/self-referential IDs reject the imported native model, and deleting images cleans stale comparison state. Legacy one-image project layouts stay valid.
- Real desktop and Android tests imported distinct color-coded front/side photos, set comparison, independently adjusted a second image's opacity, swapped active tabs, verified two different image sources/geometry nonmutation, Undo, native JSON Save/Reload and preservation of the full 283-part anatomical scene.

**Limitations:** two images displayed inside ONE responsive overlay, not two independently draggable windows; no automatic perspective/lens calibration, no side image shape inference or anatomical accuracy guarantee. Grid displays image previews; generated skull/neck form and calibrated photo-to-depth remains incomplete.

## Full integration and speed

[Six-shard integrated v11.45 verification and gated isolated publication](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39184182978): native geometry/schema plus desktop and Android tests for surface, sculpt, reference core, reference face including new compare, topology regions, and new topology mesh/LOD/audit. Six independent Playwright shards shorten the longest queue compared with the v11.44 four-shard suite; this is a partitioning improvement, not a measured speed guarantee. New versioned `atelier-precision-v11-45/` preview is only considered released after all tests pass, upload succeeds, and served HTML/SOURCE/original anatomy scene digests match.

## Remaining full-spec blockers

The full design is **NOT** yet complete: true camera-space front visible-surface occlusion; separate screen/influence brush controls and custom falloff; paintable topology-following attached lassos on concave/interior geometry; manifold-preserving mesh retopology and edge extrusion/inset/bevel; adaptive tessellation and more than two production LOD levels with safe transitions; direct graphical vertex/pin translate/rotate/scale handles; independently docked reference windows with manually calibrated lens/pose/landmark overlays; unconstrained freehand photo-silhouette cutout, alpha/feather and UV repair; actual calibrated front/profile depth, complete skull/ears/neck anatomical modeling and artist-approved likeness. Dense mobile GPU/memory tests, cross-feature Save/Reload/OBJ comparison and production release governance remain release blockers.

**Never** merge, update sealed source manifest or mutate `DEPLOY_REQUEST.json` unless the full owner-spec, artistic approval and release gates are actually satisfied. The exact hosted review preview is not the production root.
