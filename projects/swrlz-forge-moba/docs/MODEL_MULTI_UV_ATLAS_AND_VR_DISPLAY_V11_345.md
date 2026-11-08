# §E v11.345 · Whole-character source-UV atlas and VR model display modes

## What changed
The previous v11.336 UV Layout tool exported transparent UV wireframes for a *single selected mesh* and reimported PNGs onto that mesh’s original UVs. It could not export a character with multiple parts or identify which UV segment corresponds to which model part.

The existing inspector now contains a collapsible "Whole-model UV atlas · linked parts" section with:
- Select All, Clear and Select Group, plus checkboxes for individual loaded model parts.
- A strict source-UV atlas drawn from the same mesh geometry/UV attribute used by the native model editor, one numbered tile per editable mesh.
- 2048px/4096px transparent PNG guide export, JSON mapping export with native part IDs/names, tile pixel/normalized coordinates, UV bounds, vertex/face counts and a fingerprint that prevents applying the wrong source geometry.
- An atlas preview and a Focus button: clicking an atlas region selects its actual native source mesh in Model Studio.
- A painted atlas PNG importer that reads the source map, validates each existing part, crops tiles to the parts’ UV images, writes bounded `uvPaintPNG` values and performs one Undo checkpoint. No original UVs/topology are edited.
- Supported texture constraints: 18MB max atlas PNG, square 512–4096 resolution, per-mesh PNG limit 360000 data-URL characters; tiles are downsampled to 512/384/256/192px if needed.

**Important:** this is correct mesh-to-region segmentation. Complex meshes can have multiple overlapping source UV islands *within the same mesh*. The exporter does not invent a non-overlapping unwrap or alter existing per-part UV seams. For painting, an artist may need to repair those source UVs using the native UV tools. An AI artwork generated from the guide must preserve exact region placement, vertical orientation and image proportions.

## Model usage
Open the intended mage/Hooded Vanguard project in Model Studio. Open UV Layout → Whole-model UV atlas, then Select All (or the character group). Export `*-GUIDE.png` and `*-MAP.json`. Upload **both files** to ChatGPT with style instructions; the label/UV guide lines should not be included in the painted PNG. Reopen or keep the same model, load the mapping JSON if needed, and import the finished square painted atlas PNG.

## VR display correction
Model VR **Views** is now about the model's appearance: Textured (original), Solid neutral material, Wireframe mesh edges, X-ray translucent, and Normal-direction color visualization. The earlier camera angle presets remain under **Views → Angles**. All buttons reuse the existing twelve VR panel slots, with no new floating UI, and original source materials are restored before releasing the XR model when VR closes.

## Validation
Narrow [candidate run 42457148584](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42457148584) passed with real Three.js r169 on a 17-part character-like model. The test checks 17 disjoint atlas cells, stable source part IDs/fingerprints, invalid texture/missing UV rejection, detection of a stale map and temporary VR material restore. The generated HTML has SHA-256 `39a192fc72c4eac1435a6bdec4a53039578196e6bb97040716fe6b64b3452cc5`, 9162827 bytes, and 356 ordered source patches. The actual browser UI export/download workflow, painting results and physical Quest 2 shading modes remain owner testing.
