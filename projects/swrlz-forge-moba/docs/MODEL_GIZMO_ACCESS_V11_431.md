# Transform handles on touch and VR — v11.431

The native transform picker required direct ray contact with small object/component handles. VR used 4 mm shaft/ring thickness and a 24 mm uniform-scale cube. Desktop/mobile rotation already allowed nearby ring picks, but biased the previously selected axis by 12 pixels, allowing a neighboring ring to lose despite being nearer the pointer.

This checkpoint extends the existing gizmos and native Move/Rotate/Scale transactions. It does not add an independent transform tool, replace controller profiles or change saved project data.

## Touch and mouse

Native object and vertex/edge/face component handles retain an apparent screen size across perspective/orthographic projection, zoom and viewport resizing. Touch endpoints provide a 44-pixel target; mouse targets remain tighter. The outer axis shafts also accept nearby presses without expanding targets over the entire model.

The calibrated object-rotation arcs retain their real angle/drag pipeline. Picking evaluates visible projected arc segments and chooses the nearest, removing the old 12-pixel selected-axis preference. Hover and captured-transform feedback brighten the applicable axis. UI controls retain priority, and hidden, off-canvas or behind-camera targets cannot swallow a mesh press.

On a narrow phone, use **Hide inspector → Frame selected** for more working room, then **Show inspector** to adjust fields. A direction viewed exactly along its axis can overlap another handle; orbit the model or use the existing X/Y/Z toolbar controls for an unambiguous axis.

## VR

Move tips and rotation rings are visibly thicker. Invisible, bounded pick shells add controller-ray tolerance without entering the saved model or drawing a large solid overlay. Uniform Scale has a larger central cube. Hover and immediate Grip queries share the same picker; exact visible contact wins over padding. The active axis brightens, other handles dim during a transform, and entering a handle gives one short haptic pulse rather than continuous vibration.

The gizmo retains native model-root orientation and selection pivot, with a bounded apparent-size adjustment for workbench distance. Existing independent world-space menus stay independent of the headset. Grip/release, cancel, tracking-loss recovery, snap/precision and native Undo remain the existing engine paths.

VR Scale remains a uniform scalar operation. This release does not display misleading per-axis scale handles that the native group bridge cannot execute.

## Verification and publication

All **408 ordered source patches** reconstruct **9,913,140 HTML bytes**, SHA-256 `06e08dd6620102862ed333fbf6fa51fcf29024c67903378db2a0d2e81ad10396`. The 23 new actual-Three.js groups pass: 11 native touch/mouse groups and 12 VR groups, including screen sizing, orthographic/perspective projection, every supported axis/mode, padded hits, real hover event shape, menu priority, visibility/tracking/range guards and owned-resource disposal. Final IWER checks passed **11/11**, with zero page errors on that exact source hash: padded Move X/Y/Z, Rotate X/Y/Z and uniform Scale rays identify and grip the intended axis, native commits create one Undo operation and restore the exact geometry, B and tracking loss cancel previews, spatial menus retain priority, and XR exit restores the desktop model. The packaged release verifier also passed all **90 focused native groups**, including the previous workshop, camera, component-selection, starter-clone and VR UI preservation checks; both HTML entry points and all 77 asset hashes agree with `SOURCE.json` across 81 package files. Final browser touch/mouse transformations are in progress. Source/request commits and hosted receipts will be recorded after verification. Physical Android/Quest ergonomics, comfort, haptics and sustained performance require owner acceptance; browser emulation does not establish those results.
