# §E v11.59 governed production release — scoped acceptance and evidence

Date: 2026-10-19. User explicitly requested promotion from stale production v11.20 to the latest §E v11.59.

## Source contents

The source tree includes the entire cumulative *opt-in* native Model Atelier precision editor from v11.21 to v11.59. The single new governed terminal patch `patches/v11_59_precision_model_atelier.py` invokes the additive verified precision toolset from the sealed v11.20 anatomical base, changing its deployment marker and Maker title to **v11.59**. This is a release/promotion of accumulated tested editor changes, not a claim all proposed modeling research features are implemented.

Inventory: 91 ordered engine patches, 43 historical packaged native scenes/media (same bytes and paths), and the 283-part editable anatomical starter retained.

Included tooling: brush/vertex topology, actual camera-ray occlusion, screen-pixel radii, painted native lasso selection, editable falloff curves, bounded grouped transform gizmos, saved front/profile reference photos in independent floating windows, alpha feather UV face cutouts, manual photo landmarks, profile depth, face extrusion and geometry editing, topology/boundary/UV audit, controlled adaptive mesh and UV-island-safe LOD, plus camera-visible mesh-geodesic brush path targeting.

## Release source SHA

Authoritative `source-manifest.json`: **2,927,005** HTML bytes, SHA-256 **f4d72c72a5fc4ee90c921198d7086b5898b89941de3efadd7f52c063d3dab0b3**.

Version and marker: `§wyrl§ Engine v11.59`, `SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER`. Actual production `SOURCE.json` must reproduce exactly 91 patches, 43 original assets, this byte length and this digest. Measurement was independently reconstructed on GitHub Actions with exact sealed v11.20 source before changing the manifest. Production `build_space.py` remains authoritative.

## Validation boundaries

- Preview [v11.59 cumulative regression](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39271247522): 8/8 SUCCESS across geometry/native-schema, six desktop/Android editor suites, isolated preview publication and hosted byte verification.
- Release candidate must separately reproduce the **production** v11.59 checksum and pass the complete previous engine/historical compat tests, plus six re-run editor browser regression shards against production HTML.
- Source integration to `main` is separate from the dedicated deployment button. No deployment is authorized from incidental patch, manifest, roadmap, workflow or documentation changes.
- Final `DEPLOY_REQUEST.json` change (on `main` only) follows all merged source/test work. Dedicated production Actions run must pass with matching trigger head SHA. Independent served-root HTML, `SOURCE.json`, all 43 assets and hosted desktop/phone native editor must be verified before declaring **LIVE**.

## Known scope limits / artistic signoff

This release does **not** implement automatic photo-to-complete-head reconstruction, calibrated lens photogrammetry, general QEM/UV-material-sensitive retopology, full independent XYZ manipulators for both mesh and lasso pin types or benchmarked GPU performance on physical Android devices. Owner visual likeness/signoff remains separate; production promotion of tools does not assert reconstructed photographic likeness or full original design-spec completion.

Preserve historical source and evidence; if any production gate fails do not claim a successful live version.

## Source integrity reconciliation (2026-10-19)

Code-review repairs for stale runtime LOD after mesh-shape/topology mutation and cross-pointer gizmo gesture ownership changed the generated source. GitHub Actions independent measurement `39282819839` on `1327077fb1089e950d483379e59682d58652b9e0` reproduced the canonical ordered 91-patch build as **2,926,762 bytes / SHA-256 `dd9df586ab032c0c100905a2b398569e66dc433aab4d4e470c8eebee0bf141bd`**. Updated this release seal and the strict verifier from the observed build, not by bypassing checksum assertions. Prior v11.59 seal is retained in Git history. The next release CI and hosted desktop/mobile checks remain mandatory; a changed source checksum is not a deployment receipt.

## Release continuity repair · verified build on 2026-10-19

A legacy mesh-density editor refresh was shadowed by the new per-object precision density refresh, leaving the original density controls hidden on desktop and Android. Distinct function names now preserve both editors. The viewport toolbar container now passes non-control pointer events through to inspector controls, retaining native button/select/input interaction. Native screenshot capture targets unoccupied canvas outside the mobile zoom toolbar. The Sheep Run regression expects the v11.59 release receipt (91 ordered patches and matching marker) while preserving the historical `SWYRL_ENGINE_BUILD` compatibility version. Earlier failures were retained in GitHub Actions lineage.

After these changes the governed 91-patch source was independently rebuilt on GitHub Actions run `39289210927`: **2,926,858 HTML bytes**, SHA-256 **`50d5d4325e35716ef95f7f6a0041c557f87e09e6f3199c791cd89b4a781651c0`**. The prior release seal and intermediate digest are retained in Git history and above reconciliation notes. Actual desktop/phone workflow gates, merge, deployment and hosted audit are distinct and cannot be inferred from source sealing alone.
