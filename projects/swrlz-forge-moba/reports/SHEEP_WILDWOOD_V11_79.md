# Moonbell Wildwood · §E v11.79

The owner requested a bigger and improved Sheep Tag map. The native starter expands from ±40 m to ±64 m, giving 128 × 128 m of playable terrain and 2.56× the former area. The stable project query remains `?project=sheep-tag-meadow`.

## Layout and rendering

Pinewatch, Moonflower, Amberglade and Willowmere each have distinct tree/ground colors, an open building glade and an outer merchant plaza. Cardinal roads, four diagonal approaches and an octagonal loop provide alternative travel/rescue routes. Four ponds, 112 individually editable trees, eight sanctuary markers, four actual 1 m stone gaps, optional thorn hazards and eight dispersed sheep starts provide landmarks without walling off starts or roads. The native scene contains 176 actors in nine named layers. Sheep/wolf navigation radii remain unchanged; real route checks confirm sheep use each narrow passage while wolves take longer routes around its stones.

The original 4K JPEG ground is authored at 4096×4096 with multiscale mottling, full-resolution grass flecks, flowers, painted trails, market circles and a compass court. It is not a resized low-resolution image. The image is shared by the world floor and minimap; existing fog/units are drawn afterward, preserving fog behavior. Ground keeps the 80 m native prefab coordinate system and a saved 1.6× X/Z transform, so both native and portable creator imports (including missing-floor regeneration) yield exactly 128 m. The base is lowered enough to prevent depth fighting at full-map editor distance, with no forward depth bias that would hide shallow pond water.

The old map JSON, all previous runtime/patch files, previous artwork, and the independent 106-part Astra model remain byte-preserved. The new starter reuses eight sheep/three Astra hunters and keeps gameplay timing/rules unchanged. Previous 80 m saves reconstruct their original ground and roster. All objects can still be selected, transformed and saved using the existing editor/map creator.

## Validation and publication

`scripts/verify_v11_79_release.py` rebuilds the exact source seal, validates 111-patch lineage, freezes 253 older runtime/patch files and all 46 older assets, checks the new native scene/roster/layers and JPEG SOF 4096×4096 dimensions, and extracts the generated module for `node --check`. The package adds the Wildwood scene and ground image for 48 bundled assets.

`scripts/test_sheep_wildwood_v11_79.mjs` uses actual native Chromium desktop and 412px phone layouts with a controlled real RAF clock. Authored native project inputs and ordinary Play/move/build/Stop drive gameplay; live match state is not edited. Tests check all spawns valid, editor corner framing, every sheep clearing and all four outer roads connected to the center, four species-sized shortcuts, native scene reload, portable creator export/import, floor regeneration, movement and construction in the newly expanded pasture, retained Astra hunters, minimap terrain, Stop restoration and old 92-actor map compatibility. Physical-device acceptance belongs to the owner after publication.

The dedicated deploy request is a separate final commit after normal source publication. Require terminal exact-trigger production success and live HTML/SOURCE/all-asset agreement before calling this release live. No unrelated historical regression matrix or automatic hosted full-browser workflow is launched under current §§§ policy.

## §E v11.79 · Moonbell Wildwood — larger Sheep Tag map (2026-10-22)

The default Sheep Tag starter is now **Moonbell Wildwood**, **128 × 128 m** versus the previous 80 × 80 m (**2.56× the area**). Four color-separated woodland regions — Pinewatch, Moonflower, Amberglade and Willowmere — surround open building glades, an octagonal road loop, cardinal/diagonal roads, four merchant plazas, four ponds and a central sanctuary with stone markers. Four genuine narrow stone passages admit sheep while hunters detour. The terrain and fog-respecting minimap share original **4096 × 4096 ground artwork**. There are **176 individually editable native actors** in nine map layers, retaining eight sheep and three 4K Astra hunters. Match timing, movement/combat rules and optional archive settings remain intact; the previous 80 m map is preserved as a separate source and remains loadable.

Release **111 patches / 48 assets**, HTML **3,222,398 bytes**, SHA-256 `f2d2c22aa4620f76407494767e27a4227c3d178af3f8a52f7fc736c6eb28e9ec`, marker `V11_79_MOONBELL_WILDWOOD`. All 253 preceding runtime/patch sources and 46 earlier assets retain exact bytes. Targeted desktop/phone-layout checks cover start validity, full map framing, all spawn/outer-road connectivity, four species-sized passages, native/portable save/load, generated floor scale, movement/construction outside the old boundary, terrain minimap and previous-map compatibility. Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and its terminal production receipt. See [map design and evidence](reports/SHEEP_WILDWOOD_V11_79.md); delivery follows current [RELEASE_PROCESS.md](RELEASE_PROCESS.md).


Actual local results: `WILDWOOD_ROUTE_NETWORK_PASS` and `SHEEP_WILDWOOD_MAP_PASS` passed for desktop and phone, with no uncaught browser errors. Final clean overview/game screenshots were reviewed. Exact rebuild/source preservation, generated module syntax, deploy YAML and five embedded Python blocks, and the actual 111-patch/48-asset publishing guard passed. Detailed measured route lengths and browser checks are in `SHEEP_WILDWOOD_EVIDENCE_V11_79.json`.
