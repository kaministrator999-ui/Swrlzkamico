# §E v11.358 · WebXR left/right hand Starter Models

Projects → Starter Models contains two new, independent project templates:
- `webxr-hand-left`: **WebXR Left Hand**
- `webxr-hand-right`: **WebXR Right Hand**

The source `generic-hand/left.glb` and `generic-hand/right.glb` assets are distributed under the MIT terms in `assets/models/webxr-hands/LICENSE.md`. These derived projects ship as JSON-native `topologyMesh` surface assets instead of requiring an external GLB CDN. The conversion preserves the original mesh vertex/triangle topology and UV coordinates, and transforms the original down-oriented hand into §E's upright workspace coordinates (with mirrored triangle winding to preserve outward face normals). The source GLB blob SHAs are retained in the JSON metadata for provenance.

Each contains 1,360 vertices, 2,314 triangles, 25 named reference-joint positions, one selectable/editable mesh, native UVs, and a neutral anatomical material. The joint landmarks are metadata only; §E's separate hand rig uses another schema. Do not describe these as native WebXR tracking or as a poseable/animated 25-bone rig without implementing a compatible skinning bridge.

Integration: new cards are inserted before Plain Hand Base. The pre-existing explicit STARTER MODEL classifier moves them into the Models tab by reparenting DOM nodes; no new categories/dialogs, duplicates, or unrelated engine changes. The wrapped `createProjectFromTemplate` and direct `?project=webxr-hand-left|webxr-hand-right` route use the existing Model Atelier load, history, save, workspace activation and renderer. Public model data are loaded from the Space's bundled assets path. Unsaved project changes still require confirmation.

Source: https://github.com/immersive-web/webxr-input-profiles/tree/main/packages/assets/profiles/generic-hand

License: https://github.com/immersive-web/webxr-input-profiles/blob/main/packages/assets/LICENSE.md

Release: check exact-source build and source integrity, then trigger the separate deploy request. User performs phone/Quest visual verification.
