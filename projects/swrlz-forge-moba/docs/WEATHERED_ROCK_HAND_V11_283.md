# §E v11.283 · Weathered / smoothish Rocky Anime Hand

User requested a smoother rock appearance after the v11.282 solid-cliff rebuild. Scope: a **new** Rocky Anime Hand Starter Model only.

The v11.282 generator already creates completely solid, jagged rock anatomy rather than armor. v11.283 leaves the 89 existing separately editable parts, full palm, articulated 12 stone finger segments, three thumb sections, broad wrist, luminous cracks, all project controls and 17 bones intact. For the **solid rock pieces only**, the generator now welds repeated triangle vertices within each part, subdivides triangles once, and gently smooths the surface with two low-strength neighbor averages. Shared indexed vertices allow the native renderer to compute continuous vertex normals *within* individual rocks. Rocks retain irregular silhouette, individual seams and obvious stone materials; the polished geometry does **not** bring back any smooth flesh/glove core.

Emissive amber fault-line meshes and separate-rock boundaries remain sharp to preserve the organic-rock aesthetic and joint articulation. Existing saved projects are not migrated or overwritten; open the Starter Model again to see the new generated geometry. The prior Arcane Gloves, mirrored model, Mage Spell Lab, VR player hand inputs, Sheep Tag and §C remain unchanged.

Narrow receipt verifies actual source build, complete JS syntax, all 17 bones, no organic core, original 12+3 rock sections, valid indexed mesh topology, reused/smoothed vertices and bounds. Owner smartphone/Quest visual acceptance is still required.
