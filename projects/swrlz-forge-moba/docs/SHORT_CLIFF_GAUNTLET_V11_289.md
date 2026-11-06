# §E v11.289 — short Cliff Hand forearm (connected gauntlet)

## Owner request and visible problem

After v11.288 replaced rock chunks with a single smooth, texture-mapped hand, the owner's Android front/back screenshots showed too little arm below the palm. The desired appearance is a modest stone gauntlet, *not* a full long arm, extruded cuff accessory, or a return to 3D rock chunks.

## Minimal source change

The new runtime `runtime/cliff_gauntlet_forearm_v11_289.js` and append-only patch `patches/v11_289_short_cliff_gauntlet.py` intercept only the existing `plain-hand-base` / `se288SmoothCliffHandScene()` path.

- Keep `se212HandScene()` connected anatomical source topology, `model.parts=[stone]`, original hand proportions, native editor, and the 17-bone rig.
- Reshape **that same indexed topology vertex buffer** in a smooth, monotonic way below about `y=1.28`. The bottom extends approximately **0.74 engine units** and flares outward at most about **9% in X and 6.5% in Z** toward the gauntlet end, blending cleanly into the unchanged palm.
- Do not add any new meshes, crack lines, bracelets, cut seams, rock blocks, shaders, effects, draw loops or separate cuff pieces. Preserve original topology indices and counts. The gauntlet is the same hand surface, slightly longer.
- Regenerate the continuous planar UVs across the *new* vertical hand/forearm bounds. This prevents the old fixed map from clamping the material at the added forearm. Preserve the existing local 384px-per-tile owner rock PBR atlas, albedo with restrained moss, normal, AO and roughness, and the lack of modeled stone cracks.
- Preserve all starter routing, model JSON structure, open/fist animation functionality, and existing saved projects. Historic source patches and independent Rocky Anime Hand are not changed.

## Source verification vs live-device acceptance

`scripts/test_v11_289_gauntlet.cjs` exercises the geometry function without a browser: the extension is finite and monotonic, upper hand vertices remain exactly unchanged, the original vertex/triangle arrays and one mesh are preserved, and remapped UVs are valid. The full engine seal check verifies its exact assembled HTML, packed assets and JavaScript syntax. These are not a substitute for inspecting the silhouette and animated rig on Moto/Quest.

**Owner check:** Reload, open **Projects → Starter Projects → Starter Models → Plain Hand Base · Smooth Cliff Hand**, rotate front/side/back, confirm the tapered forearm looks gauntlet-length, stone texture continues into the new section, and open/fist poses do not deform awkwardly. Review any screenshots before another shape adjustment.
