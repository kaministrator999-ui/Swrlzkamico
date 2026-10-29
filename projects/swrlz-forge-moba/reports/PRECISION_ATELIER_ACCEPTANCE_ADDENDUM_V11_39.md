# §E Model Atelier — topology/LOD and manual facial-landmark addendum v11.38–v11.39

18 October 2026. Source: owner-private `SE_Model_Atelier_Design_Spec.docx` (17 October 2026), sections 3 and 8. Continue the [v11.36 acceptance report](PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_36.md). These are **bounded improvements toward**, not completion of, the complete owner design.

## Exact draft implementation

- [PR #248](https://github.com/kaministrator999-ui/Swrlzkamico/pull/248) — first **actual indexed topology and LOD authoring**.
- [PR #249](https://github.com/kaministrator999-ui/Swrlzkamico/pull/249), stacked on #248 — first **manually mapped facial feature depths**.
- Both inherit the owner-reviewable v11.37 published preview in [PR #247](https://github.com/kaministrator999-ui/Swrlzkamico/pull/247). No production v11.20 manifest, original 283 parts, Hugging Face production root, or final `DEPLOY_REQUEST.json` are modified.

### 1. Native low-poly topology copy and OBJ LOD

The selected *real evaluated triangle surface* is spatially clustered in 3D and retriangulated with degenerate/duplicate faces removed. Result is an explicit indexed vertex/UV/triangle list, not a cosmetic render mode or merely parametric U/V metadata. A measured preview reports **actual** old/new triangle counts and surviving vertices. The user may download the selected reduction as UV-indexed OBJ or Bake as a separately editable, validated `topologyMesh` object; original geometry remains intact, with whole-model Undo and serialized import/export. Complex multi-material/morph-target meshes are explicitly rejected; the reducer caps source at 180k triangles and stored copy at 9k indexed vertices/16k triangles.

Dedicated [CI 39174180762 PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39174180762): synthetic 6,016→2,056 triangles, 1,047 surviving vertices; real canonical **original head 48,768→7,347 triangles** at a requested 15% triangle ratio, measured native real desktop **and Android**, correct exported OBJ triangle/UV counts, additional baked object while preserving all original part IDs, Undo, Save/Reload. The result depends on actual source topology and is approximate, not exact requested count.

**Not yet:** a manifold-certified quadric-error / feature-preserving decimator, dedicated edge/face insert/delete tools, runtime distance-based LOD switching, adaptive tesselation and safe transition between automatically switched LOD meshes. This reduced topology can be visualized, edited, exported and saved, but is **not** an automatic game-runtime LOD platform.

### 2. Manual image-space facial landmark sculpt

Opt-in `faceSheet.landmarks` supports 12 named independently editable front-image features: brows, eyes, nose bridge/tip, cheeks, mouth corners, chin and jaw. Each saved landmark has normalized source-image UV coordinates, bounded radius and signed depth, evaluated as smooth Gaussian-like compact-support local z displacement of the **real front UV face sheet vertices**. The original reference image/UV mapping is preserved. Positive values raise the nose/cheeks, negative values recess eye sockets; optional existing manually controlled rear head closure remains available. Inspector Apply, Remove, numeric fields, Undo and native Save/Reload are validated on desktop and touch.

Dedicated [CI 39174476579 PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39174476579): real nose raise, eye recession, UV nonmutation and geometry measurements, closed head with existing rear depth, exact JSON replay, invalid values rejected; real desktop+Android original 283-part starter and separate face-sheet creation/landmark use/Undo/native import.

**Not yet:** tracing an actual image cutout into a custom silhouette, direct draggable feature markers on image, calibrated dual-camera lens/depth triangulation, feature topology extrusion rather than smooth radial displacement, profile-specific depth measurements and an independently verified accurate fully closed neck/skull/ears. Nor does this claim automated portrait likeness reconstruction or a completed Codex sculpting session.

## Integrated preview gate

A new `verify-preview-atelier-v11-39.yml` rebuilds the original sealed v11.20 engine with the cumulative, versioned additive preview overlay; it runs all previous geometry and desktop/Android sculpt/surface/reference/topology tests plus the two new modules, and publishes **only** to `/atelier-precision-v11-39/` after all gates pass. The exact hosted HTML, SOURCE receipt and original anatomical scene SHA must match uploaded bytes.

**Status: verified isolated preview published.** [Full consolidated Actions run 39174642704 PASSED](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39174642704) at tested source SHA `36625d26589dfeef9f72b69baf73e22425c5b06c`: cumulative geometry/schema and all four real desktop/Android sculpt, reference/face, surface and topology groups passed. Hosted exact upload of `https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-39/index.html?project=model-atelier` verified original v11.20 anatomy scene and receipt; preview index HTML 2,807,431 bytes, SHA-256 `bde7825a8073e5dc2cd0faa1f4509fd74b83e652e74e8da0398dcec3df5ce8b1`, 90 sealed base patches + one additive overlay, 43 original assets. **Not merged into production root; not a completed design spec.** For production deployment, also require full historical compatibility, version and source-manifest sync, owner visual acceptance, governed merge, final deploy-trigger mutation and independent hosted audit.

## Source-of-truth rule

The original v11.20 starter, model assets, all prior native projects and original image reference assets remain independent. Inconsistent/unknown polygon manifold behavior or incorrect photo orientation must reject or be explicitly identified, not silently represented as production-ready topology/automatic multi-photo reconstruction.
