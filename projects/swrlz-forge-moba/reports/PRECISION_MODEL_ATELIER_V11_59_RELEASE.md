# §E v11.59 governed production release — scoped acceptance and evidence

Date: 2026-10-19. User explicitly requested promotion from stale production v11.20 to the latest §E v11.59.

## Source contents

The source tree includes the entire cumulative *opt-in* native Model Atelier precision editor from v11.21 to v11.59. The single new governed terminal patch `patches/v11_59_precision_model_atelier.py` invokes the additive verified precision toolset from the sealed v11.20 anatomical base, changing its deployment marker and Maker title to **v11.59**. This is a release/promotion of accumulated tested editor changes, not a claim all proposed modeling research features are implemented.

Inventory: 91 ordered engine patches, 43 historical packaged native scenes/media (same bytes and paths), and the 283-part editable anatomical starter retained.

Included tooling: brush/vertex topology, actual camera-ray occlusion, screen-pixel radii, painted native lasso selection, editable falloff curves, bounded grouped transform gizmos, saved front/profile reference photos in independent floating windows, alpha feather UV face cutouts, manual photo landmarks, profile depth, face extrusion and geometry editing, topology/boundary/UV audit, controlled adaptive mesh and UV-island-safe LOD, plus camera-visible mesh-geodesic brush path targeting.

## Release source SHA

Authoritative `source-manifest.json`: **2,926,239** HTML bytes, SHA-256 **3a23b53ce48ba1b25aa19346a4d640aebee8a81ba0f2a161ca66621f31a5f0e1**.

Version and marker: `§wyrl§ Engine v11.59`, `SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER`. Actual production `SOURCE.json` must reproduce exactly 91 patches, 43 original assets, this byte length and this digest. Measurement was independently reconstructed on GitHub Actions with exact sealed v11.20 source before changing the manifest. Production `build_space.py` remains authoritative.

## Validation boundaries

- Preview [v11.59 cumulative regression](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39271247522): 8/8 SUCCESS across geometry/native-schema, six desktop/Android editor suites, isolated preview publication and hosted byte verification.
- Release candidate must separately reproduce the **production** v11.59 checksum and pass the complete previous engine/historical compat tests, plus six re-run editor browser regression shards against production HTML.
- Source integration to `main` is separate from the dedicated deployment button. No deployment is authorized from incidental patch, manifest, roadmap, workflow or documentation changes.
- Final `DEPLOY_REQUEST.json` change (on `main` only) follows all merged source/test work. Dedicated production Actions run must pass with matching trigger head SHA. Independent served-root HTML, `SOURCE.json`, all 43 assets and hosted desktop/phone native editor must be verified before declaring **LIVE**.

## Known scope limits / artistic signoff

This release does **not** implement automatic photo-to-complete-head reconstruction, calibrated lens photogrammetry, general QEM/UV-material-sensitive retopology, full independent XYZ manipulators for both mesh and lasso pin types or benchmarked GPU performance on physical Android devices. Owner visual likeness/signoff remains separate; production promotion of tools does not assert reconstructed photographic likeness or full original design-spec completion.

Preserve historical source and evidence; if any production gate fails do not claim a successful live version.
