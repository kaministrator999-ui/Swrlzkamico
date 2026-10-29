# §E Model Atelier — verified progress and outstanding owner-spec requirements (v11.43–v11.44)

**Scope:** §E / Model Atelier, 17 October 2026 owner-private design specification, sections 2–12. This report extends [v11.42](PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_42.md) and does not publish or quote the private specification itself.

**Release classification:** stacked **DRAFT candidates** on top of the byte-verified isolated [v11.42 review preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-42/index.html?project=model-atelier). Original v11.20 production, source seal, model and its 283 parts, existing references and `DEPLOY_REQUEST.json` remain untouched.

## New slice A — actual runtime LOD

[PR #253](https://github.com/kaministrator999-ui/Swrlzkamico/pull/253). [Targeted native CPU and desktop/Android browser run **PASS 39182893911**](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39182893911).

- Every opt-in **baked indexed topologyMesh** can save a strictly validated `runtimeLOD` object: `{enabled:boolean,switchDistance:number,low:{positions,uvs,indices}}`. The original `topologyMesh` remains the high-detail authority. Both are actual indexed triangle geometry, not merely chosen shader/viewport quality.
- Native model rendering switches between independently instantiated high and low `BufferGeometry` based on camera-to-mesh distance. Switch has 8% hysteresis; selecting a part always displays high topology for editing. Inactive geometry is disposed when the editor reconstructs/wipes an object, and the candidate's self-stopping editor RAF does not interfere with the separate world/animation renderer.
- User controls: Generate saved two-level LOD at chosen reduction fraction, numeric camera threshold, enable/disable, remove profile, measured triangle counts. Native Undo/Redo and portable JSON Save/Reload preserve both geometries and values. Invalid meshes, source geometry and out-of-bounds distances reject.
- Dedicated real original-head tests confirmed high→low→high actual displayed triangle counts and independent native history transitions on desktop/Android.
- **Limitations:** two levels, bounded single-material indexed mesh, no QEM silhouette/detail preservation, no seamless geomorph/crossfade, no edge seam preservation guarantee across material meshes, and no independently verifiable external game-engine runtime LOD package. In-editor native JSON has the saved LOD profile.

## New slice B — indexed topology inspection/limited repair

[PR #254](https://github.com/kaministrator999-ui/Swrlzkamico/pull/254). [Dedicated test **PASS 39183031850**](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39183031850).

- Counts explicit undirected indexed edge incidence, open/boundary edges, >2-face nonmanifold edges, degenerate/zero-area triangles, and pairs of adjacent faces with inconsistent shared-edge orientation.
- Only reorients faces if incidence is at most two, no zero-area faces exist, and a connected-component BFS can satisfy all orientation constraints. Changes **triangle index winding only**, never geometry positions/UVs; preserves open boundary count, checks deterministic native schema, and allows Undo/Redo/Save/Reload. If source `runtimeLOD` exists, repair drops its stale low profile explicitly rather than allowing inconsistent high/low orientation.
- Synthetic oriented/inverted square and adversarial nonmanifold/degenerate CPU cases plus imported real browser square editor controls tested; original 283 anatomical parts unchanged.
- **Limitations:** open boundaries do not always mean holes; no automatic patch filling, welded vertex remapping, global orientation of closed solids, full manifold remediation or robust arbitrary remeshing.

## Full cumulative acceptance

[Full v11.44 cumulative CI and gated isolated preview](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39183191247): real desktop+Android sculpt, surface, reference/face and topology shards plus all historical precision geometry tests, original 90 sealed source patches. Publish only after those complete and hosted HTML, SOURCE receipt and original v11.20 anatomy scene match byte-for-byte. **Do not claim hosted v11.44 success until terminal upload/digest logs confirm it.**

## Still-open items in the full owner specification

| Domain | Unfinished acceptance evidence |
|---|---|
| Surface brush and visibility (§2) | Camera-ray depth occlusion against true rendered triangles, backface/shell correctness on folded interior shells, screen-space brush sizing vs influence radius, configurable falloff curves/offset center and independent symmetry policies; dense-scene mobile GPU profiling |
| General mesh topology (§3/§5/§11) | Feature-preserving decimation with UV/material seams, adaptive topology subdivision, robust manifold repair/quad/edge-loop retopology, dedicated vertex/face extrusion/inset/bevel and permanent refined region bake; native explicit restore and crack-free seams |
| Runtime LOD (§3) | Beyond two levels with explicit game deployment format and robust no-pop transition/profile thresholds, tested multi-material high-dense scenes |
| Surface lasso (§5) | Direct brush-painted/editable topology-following outlines on concave/interior shells, normal offset for attached boundary pins, revision-safe local topology bake and continuous blend-weighted refinement layers |
| Consistent gizmos (§6) | Large visible 3D translate/rotate/scale handles with independent boundary-versus-mesh selection state and snap/context orientation; zoom-aware point culling |
| Multi-perspective references (§7) | More than one simultaneously independently docked panel, calibrated image camera/lens and silhouette overlays, full tablet/phone dock layout/performance |
| Face-image to complete head (§8) | Freehand cropped alpha/feathered photo silhouette (12 radial contour is only star-shaped), actual feature topology extrusion and nostrils/lips/ear placement, calibrated independent front/profile depth, intentional anatomically checked jaw/cranium/neck closure, UV repair and owner-verified full face likeness |
| Acceptance/release (§9/§12) | Demonstrate a coherent imported front+side reference→UV face→local densification→nose/eyes→profile→closed head→integrity repair→runtime game LOD→native save/export/reload on a real project, with dense mobile stress and final owner visual approval; then independent root source seal/version manifest, governed integration, last `DEPLOY_REQUEST.json` and exact served production marker |

**Governance:** Passing individual feature tests is not proof the whole design is finished. Never silently deploy incomplete features to stable production, replace the original head, or describe manually guided image references as automated reconstruction.
