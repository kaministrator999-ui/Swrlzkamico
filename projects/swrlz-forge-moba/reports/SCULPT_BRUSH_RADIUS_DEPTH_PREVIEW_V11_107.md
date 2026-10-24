# §E v11.107 · Live picked surface radius and depth preview

## User feedback
The existing Pick center on mesh marker was a fixed-size ring and did not represent current sculpt radius. Owner requested a second-layer depth visualization prior to committing a brush edit.

## Bounded feature
- Preview reads **validated existing native sculpt form** values, including screen-pixel to local-unit radius conversion, action (negative intrusion/positive extrusion) and rotated brush axis. Invalid values retain a small marker but no falsely asserted depth.
- Amber ring draws a brush-radius footprint around the picked center in a tangent plane, following the object's local-to-world transformation.
- Violet inset secondary ring and tapered spokes indicate selected center displacement along the brush axis. Cyan indicates normal/direction; white crosshair identifies center.
- A numeric label displays picked XYZ, radius and depth with explicit **preview only** wording. It updates on actual form input/change, including mobile keypad Apply. Only the original Apply brush writes to sculptBrushes and Undo history.
- This is a planning guide, NOT a precise preview of vertex falloff or a Boolean drilled hole. Real topology, surface-targeting and density still govern the committed result.
- Editor-only helper resides outside native modelRoot; never serialized, exported or raycast as editable mesh. It is cleaned up on repick and deselection.

## Preserved behaviors
- No geometry engine, saved meshes, materials, transform tools or export changes.
- Maintains the v11.106 render-mode material check and redraw handling, as well as the v11.105 panel sizing, drag, menu spacing, scrolling gutters and hold-to-edit number pad.

## Source receipt and acceptance
- 139 ordered patches; 68 packaged assets; HTML 6545909 bytes.
- SHA-256 `9aa81dd84b445e3cb51e84279a4141acd9a83069305332720753fea42f8946d0`.
- Marker `SWYRL_ENGINE_DEPLOY_MARKER: V11_107_RADIUS_DEPTH_PREVIEW`.
- Production workflow must verify syntax and hosted source/assets. Actual phone test: pick sphere, change radius and depth, confirm preview resizes/moves before applying, rotate wireframe/X-Ray camera, confirm no saved stroke count change until Apply and render mode remains stable.
