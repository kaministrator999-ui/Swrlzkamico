# §E v11.104 · Readable inspector forms and visible picked surface center

## Owner evidence
The owner showed an Android X-Ray screenshot of §E v11.103 with tiny mixed-size text, crammed controls and unclear grouping in floating Model Atelier tool panels. Separate user testing showed Pick center on mesh changed XYZ but never marked the selected surface location.

## Source diagnosis
- `atelierSculptPick` raycasts and saves local XYZ and normal into `atelierSculptHit`, then updates numeric inputs and status. No explicit picked-center helper geometry was created.
- Existing `atelierSurfacePreviewRefresh` draws influenced **vertices** only, with depth-tested points. It is not a picked-center marker.
- Modeling CSS includes older compact styling across sculpt fieldsets, pairs and action rows. Mobile overlay dimensions and drag constraints have been tuned in v11.103, and should not change here.

## Bounded implementation
- Add an editor-only Three.js group at the exact hit position transformed by the current object's world matrix. A high-contrast yellow torus ring, white crosshair and cyan outward-normal arrow render without depth testing and remain visible in X-Ray mode. The shape is aligned with the stored local normal using the world normal matrix.
- The helper is not inside `modelRoot`, not raycast for mesh selection and not included in native model serialization or GLB/OBJ exports.
- Lifecycle: when selection invalidates, the helper is removed and disposed; a repick replaces it. A compact live readout lists local XYZ and describes the marker/normal.
- Add CSS for clearer group/section hierarchy, typography, legends, contrast, consistent two-column form rows, checkbox alignment, readable 16px editing inputs and mobile-sized action controls across native inspector/context menus. Do not modify any existing tool values or handlers.
- Preserve the v11.103 mobile inspector dimensions and drag behavior, 380ms deliberate numeric hold, side swipe gutters, original sphere, 68 packaged assets and historical models. **Do not add a drilling/Boolean geometry operation in this presentation release.**

## Source receipt and acceptance
- 136 patches; 68 unchanged bundled assets.
- Compiled HTML: 6535811 bytes; SHA-256 `e205d04d8bd66d69994cbeca52b8a089468a6275146bfae59ba884bda6f443f1`.
- Release marker: `SWYRL_ENGINE_DEPLOY_MARKER: V11_104_PICK_MARKER_READABLE_MENUS`.
- Preflight source compilation produced the digest, then intentionally failed closed on the old manifest. Verify actual syntax, assets and hosted HTML in the separate final deployment.
- User Android acceptance: tap Pick center, choose a point distinct from the transform gizmo, see the yellow ring and cyan arrow, rotate X-Ray/Shaded camera and verify marker tracks the surface. Pick again and check the marker moves without duplicate markers. Inspect field spacing, scrollability, hold-to-edit and panel dragging.
