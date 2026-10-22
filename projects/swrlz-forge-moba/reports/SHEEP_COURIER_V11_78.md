# Astra in Sheep Tag · §E v11.78

The owner requested replacing the Sheep Tag wolf with the just-created Astra model. The canonical saved 106-part model and two 4K atlases are reused directly by the native `st-wolf` prefab. No derived low-detail character or substitute texture is introduced.

## Integration

A private Model Atelier factory uses the existing geometry/sculpt/material evaluators on the immutable Astra source. A shared template owns geometry/materials, while each hunter clones its own transform hierarchy. Named `stLeg0..3`, `stHead` and `stTail` pivots match the existing gameplay animator. Saved cheek/head and tail assemblies drive the head/tail; four sets of leg, paw, toe/claw and haunch parts drive a diagonal quadruped gait. A visual-only 0.58 scale fits the old hunter and places measured sole bounds at ground level without changing logical actor transforms or collision radii. The stable model name is inside the actor root because native markActor assigns the root's authored name and metadata.

The inspector exposes actual model mesh/triangle counts, loaded image dimensions and joint rotations, allowing integrations to inspect real render state without editing simulation state. The independent model workspace, all saved scenes and all historical runtime/patch files remain unchanged.

## Validation and delivery

`python scripts/verify_v11_78_release.py --output <candidate>` rebuilds the exact manifest-sealed package; checks 110-patch lineage, all 250 predecessor runtime/patch hashes, all 46 original asset hashes and the original heroine canonical JSON; extracts the module for `node --check`.

`node scripts/test_sheep_courier_v11_78.mjs` exercises the actual native game in Chromium desktop and 412px phone layouts. It uses authored input fixtures and a deterministic real RAF clock, never writes live match state: three default hunters, full-resolution images/shared image sources, native prefab spawn and project save/reload, forward movement, all four animated leg pivots with diagonal phase, real building damage and head animation, sheep tagging, Stop/restart, and returning between the independent model and Sheep Tag. Layout emulation is not physical-device acceptance. Extended unrelated historical game matrices are not launched under the current §§§ release policy.

The final separate deploy request records the exact source commit and artifact SHA. Production must reach terminal success and verify the exact live HTML/SOURCE/all 46 asset bytes before reporting the release as live. The owner performs device UX acceptance.

## §E v11.78 · Astra hunters in Sheep Tag (2026-10-22)

Sheep Tag's `st-wolf` prefab now renders the complete **Astra · Comet Courier** model, with all 106 native meshes and the original 4096 × 4096 color/normal atlases. The three canonical hunters, newly spawned hunters and wolves reconstructed from older native project saves all use the same visual. Independent head, tail and four leg pivots connect the saved model to the existing walk and attack animations; geometry/materials and texture images are reused across instances. Logical wolf roles, IDs, names, teams, navigation/collision radii, combat, economy and map data are preserved. The independent editable Astra project remains available.

Release **110 patches / 46 assets**, HTML **3,152,424 bytes**, SHA-256 `234ddf6065f89438a3cabbcd9e3521d82fb08245830525131e3976d4f86b9ad4`, marker `V11_78_SHEEP_TAG_COURIER`. All 250 preceding runtime/patch files and 46 bundled assets are byte-preserved. Targeted local desktop/phone-layout checks cover loaded 4K maps, native spawn/save/reload, movement/four-leg gait, building attacks/head animation, sheep tagging and Stop/restart restoration. Deployment status and source commit resolve through the final separate `DEPLOY_REQUEST.json` and its terminal production run; owner device acceptance follows publication. See [integration evidence](reports/SHEEP_COURIER_V11_78.md). Delivery follows current [RELEASE_PROCESS.md](RELEASE_PROCESS.md).


Actual local result: `SHEEP_COURIER_GAMEPLAY_PASS desktop` and `SHEEP_COURIER_GAMEPLAY_PASS phone`; no uncaught browser errors. Native render inspection measured 106 meshes / 274,980 triangles and two loaded 4096×4096 images per hunter with shared image sources. Source preservation/rebuild, generated module syntax, YAML/embedded Python and the actual 110-patch/46-asset publishing guard passed. See `SHEEP_COURIER_EVIDENCE_V11_78.json`.
