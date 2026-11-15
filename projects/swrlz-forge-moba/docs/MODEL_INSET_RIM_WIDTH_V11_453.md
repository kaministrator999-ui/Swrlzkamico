# §E v11.453 · Inset rim visibility and direct width control

## Owner observation
On a cube face selected as a connected square of two triangles, selecting Inset appeared to operate at the perimeter without a recognizable, adjustable rim. The mobile screenshot showed Inset fraction 0.2, a disabled Apply action and the message "Bake validated vertex edits into topology first".

## Root cause and fix
The original topology algorithm creates an inner cap connected by a coplanar border ring. The previous transient `THREE.EdgesGeometry(geometry, 10)` preview omitted this flat inner border because its dihedral angle was zero. v11.453 renders a second, transient `THREE.LineLoop` made from the *actual preview candidate's validated selected inner-face boundary*. It is disposed on geometry replacement, Apply, Cancel and projection change.

A single gold touch handle is projected onto the preview's inner rim and derives a bounded Inset fraction from a drag along the original vertex-to-centroid direction. Its drag updates the *existing native amount input*, which rebuilds a source-safe disposable preview. A press does not edit persisted geometry or create Undo history. Drag inward = wider rim, outward = narrower. On strongly edge-on views it refuses an unstable resize. The numeric slider and exact amount stay available, and an Inset of 0.2 on a square gives a rim about 10% of the face width on each edge.

When the inspected source has unapplied, validated vertex edits or remains a plain primitive, the modifier shows **Make editable & preview rim** / **Bake edits & preview rim**, reusing the actual `se430ModelWorkshop.convert()` transaction and connected planar face reselection. Baked edits require explicit confirmation. Protected authored paint, rig, procedural source and invalid topology remain guarded.

## Source, tests and acceptance
Source is appended as the v11.453 patch; historical v11.452 Face flyouts and v11.451 preview controls are not replaced. Focused v11.453 test checks actual `THREE.LineLoop` creation, disposal, the absence of implicit Apply/history, direct native input routing, and preservation of the prior Face flyout behavior.

On phone: Select a cube face → Inset → adjust the gold diamond or slider until the yellow inner border shows the desired opening → Apply → Undo. Confirm dragging the handle doesn't orbit the camera, and that the same face can be prepared safely after existing vertex edits. On Quest: verify previous VR menus/tools unaffected; no headset-specific rim gesture is introduced in this release.
