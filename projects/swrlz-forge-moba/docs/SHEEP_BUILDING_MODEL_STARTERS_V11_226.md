# §E v11.226 — Sheep Tag faction houses, editable 3D model starters

**Scope:** User-requested native Model Atelier building pack based on the farm/sheep concept schematics. These are real 3D primitives/meshes, not pictures on planes or gameplay prefab replacements.

## Five independent starter projects

| Native template ID | Project card | Authored features |
| --- | --- | --- |
| `sheep-free-shelter` | Free Sheep Shelter | Open-sided lean-to, blue sloped roof, three-sided windbreak, lantern, hay bedding; 18 editable parts |
| `sheep-thatched-hut` | Thatched Starter Hut | Compact wooden hut, split thick thatch roof, crest, ram ornaments, wood doorway; 59 parts |
| `sheep-cottage` | Cozy Sheep Cottage | Warm cottage, straw roof, chimney, glowing paned window, flowers, sheeplike crest; 68 parts |
| `sheep-barn` | Flock Barn | Red timber, blue gable roof, open front, diagonal braces, loft window, hay bales; 37 parts |
| `sheep-ram-house` | Ram House | Sheep crest, cottage roof, open barn doorway, hay threshold and timber porch; 60 parts |

Every part is native editable mesh/sphere data in `currentProject.modelAtelier`, with unique part IDs, groups, UV-bearing indexed box topology, and ordinary `position` / `rotation` / `scale`. Each original template is cloned for use. Project cards participate in the existing per-browser default-starter and native project copy workflow. Existing Model Atelier front/side/top camera views can be used to inspect the same geometry.

### Open paths

From §E: **Projects → Starter Projects** and select one of the five cards. Direct routes in the existing Modeler page:

- `modeler.html?project=sheep-free-shelter`
- `modeler.html?project=sheep-thatched-hut`
- `modeler.html?project=sheep-cottage`
- `modeler.html?project=sheep-barn`
- `modeler.html?project=sheep-ram-house`

This integration uses the existing `createProjectFromTemplate` hook, `loadProject`, `ModelAtelier.syncProject`, and `ModelAtelier.open`. It does not invent a secondary editor/store or WebGL render loop.

### Source ownership and persistence

- Native builder: `runtime/sheep_building_model_starters_v11_226.js`
- Append-only HTML patch: `patches/v11_226_sheep_building_starters.py`
- Registered in `source-manifest.json`, 258 ordered patches.
- Model geometry safety tests: `tests/test_v11_226_sheep_buildings.cjs`.
- Strict build/source/packaging verification: `scripts/verify_v11_226_sheep_buildings_release.py`.
- Same 68 existing packaged media assets, unchanged.

### Provenance and staged acceptance

Verified candidate: **7,656,704 HTML bytes**, SHA-256 `7395e442f324b33cf67f49aa1eb1be9349f07c2e4d7f00aa5872d3312112129d`; 258 ordered patches. Focused Node checks validate the geometry, UV shape, indexes, groups, unique IDs and independent clone behavior for all five starters. Compilation and packaging are separate from owner-phone/Quest visual approval.

**Scope boundary:** Model starter assets do *not* automatically replace the host-authoritative Sheep Tag farm/house actors. Building-menu choices, collision and passable gaps, cost, construction timing, LAN game rules and wolf pathfinding are unchanged. An approved follow-up can transform selected native models into low-poly game prefabs in the existing Sheep Tag actor factory, with separate LOD/collision validation.

**Owner device acceptance pending:** Open each starter on Moto G Power and Quest Browser. Confirm front/side/top camera silhouettes, touch-selectable individual parts, valid Save/Load/export, frame rate, and whether the approved house dimensions work for Sheep Tag construction.
