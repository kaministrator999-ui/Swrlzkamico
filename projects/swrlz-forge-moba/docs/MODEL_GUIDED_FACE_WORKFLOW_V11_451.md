# §E v11.451 — guided Face tools and native live-preview modifiers

## Request and diagnosis
The November 14 Android screenshot showed a crowded Model Studio inspector: Shape/Face, Topology, manual workshop, selection, and a second stack of “Run” buttons all visible at once. Native Inset already supported planar regions and source-safe preview, but the editor required unnecessary navigation. The original amount handler canceled previews on edit, forcing users to repeat the operation.

## Implementation
- Keep the existing Face tools actions (Inset, Extrude, Solidify, All face tools) and their native `se448ShapeQuickActivate` entry point.
- Add one compact modifier section below them with a bounded slider, exact numeric entry, status, and Apply/Cancel, all delegating to `se430ModelWorkshop`.
- While the Topology → Manual mesh modeling tool is active, hide only the duplicate native proxy fields by default. **Advanced tools** exposes the complete original workshop without removing or replacing any functionality.
- Update amount changes to rebuild the same disposable native preview, coalesced to one candidate per animation frame in guided mode. No slider handler calls Apply or writes document data.
- Preserve planar square-face selection via its underlying triangle IDs, conversion/UV safety, preview validity checks, Undo, VR modeling menu, camera and touch controls.

## Validation and release
`scripts/prepare_v11_451_release.py` rebuilds from the ordered patches, seals the exact `finalBytes` and `finalSha256`, then runs `scripts/verify_v11_451_release.py` with the relevant existing and new focused tests. Owner Android and Quest acceptance occurs after verified HF deployment.

## Acceptance walkthrough
Open a blank Model Studio project, select a cube, choose Sculpt → Face tools → Inset. Tap the cube's top square face if none is selected. The selection should include both coplanar triangles, and one transient preview should appear. Drag the amount slider: the preview should change while keeping the camera pose, mesh and Undo history unchanged. Apply once to commit, Undo to restore. Repeat with Extrude and a negative amount. Confirm Cancel preserves the original, and Advanced tools opens the original native actions.
