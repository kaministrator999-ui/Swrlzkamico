# §E Model Atelier — Precision Acceptance Addendum v11.33–v11.36

Date: 2026-10-18. Owner design basis: private §E Precision Mesh & Reference-Driven Sculpting specification dated 2026-10-17.

**Status: FEATURE CANDIDATES PASS FOCUSED TESTS; FULL DESIGN INCOMPLETE; NO MERGE OR DEPLOY.** Read this alongside [the v11.29 acceptance ledger](PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md) and [the v11.30–v11.32 acceptance addendum](PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_32.md).

## Draft development lineage

The stacked feature branch is [PR #246](https://github.com/kaministrator999-ui/Swrlzkamico/pull/246), based on [PR #245](https://github.com/kaministrator999-ui/Swrlzkamico/pull/245) → [PR #243](https://github.com/kaministrator999-ui/Swrlzkamico/pull/243) → [PR #241](https://github.com/kaministrator999-ui/Swrlzkamico/pull/241) → [PR #240](https://github.com/kaministrator999-ui/Swrlzkamico/pull/240) and the earlier precision-editor drafts. These are **draft pull requests** stacked on one another, not engine production versions and not separately deployed artifacts.

### v11.33 — CI triggering efficiency

Historical source seal, head-authoring, pose-frame, grounded-anatomy and geometry-profiler workflows previously listened to `projects/swrlz-forge-moba/**`; a documentation-only or opt-in editor-preview change thus scheduled roughly five redundant validation workflows. One historical anatomical-head browser suite took approximately 3–3½ minutes.

- Changed PR path filters to include all **90 exact sealed manifest patch paths**, source-manifest, `build_space.py`, base payload, and the relevant tests/source for each old suite. Candidate-only editor preview patches and Markdown documentation no longer trigger all five old suites.
- Historical workflows remain available through `workflow_dispatch` for manual release gates. New editor modules continue to receive their own dedicated CPU and real-browser checks.
- Coverage guard [CI 39162547495 PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39162547495), checking every sealed patch dependency for all five workflows. The later v11.34/v11.35/v11.36 branch heads each ran their one matching feature workflow, without five redundant historical suite launches. **No measured guarantee about runtime of the remaining inherently expensive browser operation.**

### v11.34 — native named-region selection algebra

- Add / Subtract / Intersect a named independent lasso region against another named lasso. This is **evaluated selection algebra**, not destructive polygon cutting: each original 📌 region keeps its control pins and native source mesh unchanged.
- Reject unknown, self-referential, nested/cyclic, incompatible-resolution and reversed-orientation operands; prevent deleting referenced operands.
- True vertex morph **and** local conforming subdivision use the composed mask. The same mask evaluator powers topology Preview and Apply; original regions without optional `selectionOp` remain backward compatible.
- [CI 39162956068 PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39162956068): synthetic actual triangulation baseline **5,140**, Add **5,776**, Subtract **4,292**, Intersect **4,080**; desktop/Android original head generated and reloaded real correct topology and native JSON.

### v11.35 — corner/curve boundary interpolation

- Optional numeric 0–1 `boundaryCurve`, sampled using two bounded smooth interpolation rounds (up to 128 evaluated points from 32 saved 📌 pins).
- The source pin count, triangle attachments and base mesh remain intact. Morph, Boolean membership, refinement selection and displayed selection boundary use the rounded footprint, not a decorative-only line.
- Reject out-of-bounds values, crossing/degenerate rounded boundaries and invalid native edits with whole-model Undo support.
- Prevent deleting a region with existing saved refinement layers.
- [CI 39163499804 PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39163499804), original head local preview **50,454 → 50,180** triangles after smoothing, unchanged pin controls, desktop/Android Save/Undo/Reload. Earlier failed [39163395500](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39163395500) was a local-frame test assumption and remains part of the test record.

### v11.36 — independently adjustable selected lasso boundary segment

- Selecting an existing boundary pin defines the segment between that pin and the next, including final-to-first wraparound. Enter signed surface-plane growth/shrink amount (±0.15).
- Outward/inward is computed from polygon winding; both existing endpoints are shifted together and reprojected onto actual mesh triangles. Invalid or crossed proposals reject the entire change. Only the chosen two pins move, with one Undo checkpoint; source mesh topology is preserved.
- Works alongside optional curved region selection and Boolean masks.
- [CI 39163920434 PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39163920434). Synthetic region area grew 0.16→0.18 or shrank 0.16→0.14. Real desktop/Android original head density preview grew **50,454 → 50,594** triangles; original third pin, 283 part IDs, Save/Undo/Reload and earlier curve/Boolean tests remained valid.

## Remaining engineering and release blockers

1. **True camera-visible surface occlusion selection** (including concave/interior thickness) instead of projected nearest-shell approximation; brush-painted lasso and selection paint flow with explicit brush radius and stroke history.
2. **Arbitrary mesh topology operations:** vertex/edge/face insert/remove, robust retopology, actual geometric Boolean polygon clipping/bake and controlled normal-offset boundary attachments. Refined geometry currently remains a non-destructive evaluated layer; generalized permanent topology bake/rollback is not complete.
3. **Generalized density and production LOD:** target-vertex budget solver, reduction/decimation of arbitrary imported/generated meshes, true distance-based runtime LOD meshes/export, dense hardware performance profiling and crack-free transitions across all materials.
4. **Complete deformation stack:** meaningful continuous shape-layer blending and associated lock/visibility/ordering/rollback semantics; visual rotation/scale control handles for both pin families; dense-selection simplification/culling.
5. **Multi-view reference-driven face construction:** independent fully dockable synchronized image-reference panels, camera perspective/lens registration, drawn photographic cutout contour and landmarks, profile-based depth modeling, carefully closed skull/neck and model likeness verified by actual front/three-quarter/profile/rear reference comparison. UV face sheet starter alone is not a completed head.
6. **Integration and release gates:** exact source manifest and version marker updates only after all functionality is implemented; comprehensive cross-tool desktop/Android Save/Undo/Redo and native JSON/OBJ equivalence; owner visual approval; all independent source-seal and anatomical studio workflows at final release head; governed merge; dedicated `DEPLOY_REQUEST.json` **last mutation**; matching deployment Actions run plus independent exact served host marker/digest verification.

**The original v11.20 sealed 283-part anatomical starter was never replaced or deployed by these drafts. No claims of production readiness, automated facial reconstruction or actual Codex-operated character sculpt have been made.**
