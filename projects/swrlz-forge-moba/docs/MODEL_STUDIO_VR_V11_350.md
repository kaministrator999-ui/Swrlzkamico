# Model Studio VR v11.350 — two-hand modeling and native creation

The immersive editor now executes Controller Studio's validated Model/Sculpt profiles through the existing XR renderer and frame loop. It keeps the v11.344 calibrated rays/camera presets, v11.345 display modes, v11.346 UV sheets, and the subsequent owner UV image import correction.

## Default Quest / Touch controls

| Input | Behavior |
| --- | --- |
| Right trigger | Select; hold to sculpt, draw an outline or trace a lasso in that mode |
| Left trigger | Add/remove a part; sample a sculpt surface and hold for temporary Smooth |
| Right grip | Edit the selected group with Move/Rotate/Scale; pull a drawn face to extrude |
| Left grip | Reposition the presentation workbench |
| Both grips | In Inspect, resize/turn the presentation; in explicitly selected Two hands mode, edit the selected geometry |
| A tap / hold | Next tool or brush / ray-select tool or brush wheel |
| B | Cancel the preview before any release can commit; otherwise Inspect |
| X tap / hold | Toggle palette / studio category wheel |
| Y / X+Y | Undo / Redo; the chord suppresses both single-button actions |
| Left stick / click | Pan; in Sculpt, radius and strength / toggle Precision |
| Right stick / click | Orbit / focus |
| Left grip + right stick up/down | Smooth presentation zoom |

Face-button taps resolve on release so holds and chords do not accidentally fire taps. The default hold is 450 ms. Trigger/grip thresholds, deadzone, precision gain, snap angle and sensitivities come from the active profile. Custom mappings dispatch to real Model VR actions. Reserved headset buttons are not required. Unsupported action/binding combinations remain diagnostic rather than dispatching unintended edits.

## Native editing and visual feedback

Left-trigger selection toggles up to 32 native part IDs, with aggregate selection bounds. Group transforms preserve native assembly placement and attached-skin preview behavior. Two-hand geometry edits require the explicit Two hands tool; ordinary Inspect gestures affect only the workbench presentation. A completed gesture creates one native history checkpoint for the whole selection. Cancel, tracking loss, input profile changes, document replacement, native rebuild and session exit discard uncommitted work. Current-frame release poses are included before committing.

Sculpt supports Push, Smooth, Flatten, Inflate, Pinch and Translate using native sparse vertex edits. The brush footprint and live radius/strength show the active operation. Lasso traces save actual native surface regions with triangle/barycentric attached pins; the selected region feathers and limits subsequent sculpt strokes. A gold boundary and “Lasso mask” status show its scope. Whole surface clears the active mask without deleting saved regions.

Draw traces a planar closed outline at the pointer's initial depth. Release validates and triangulates a native topology mesh. Grip extrusion creates a closed solid along the face normal, including negative thickness; tangential motion does not add depth. Outlines, sculpt strokes, lasso regions and extrusion all support native Undo/Redo. Geometry previews do not alter serialized source data before commit.

The palette has Mesh, Sculpt, Draw, Display, Angles, Aim and Guide navigation, plus tool/brush/category wheels. Menu plates block selection behind them. Hover/selection/commit haptics are brief and throttled. The workbench stays in world space so physical leaning and side inspection remain possible.

## Deliberate limits

- Sculpt and extrusion support unrefined source meshes and skins verified at their bind pose. Posed skin edits are rejected with readable guidance rather than saving incorrect vertex correspondence.
- Native edit/topology limits still apply; sculpt previews are capped at 24,000 vertices, native sparse edits at the existing portable budget, lasso regions at eight per part and 32 attached pins, and outline traces at 128 samples.
- Group transformations that require nonrepresentable saved TRS shear are rejected atomically. This does not rewrite assembly or rig data.
- Draw creates planar outlines and whole-outline extrusion. This release does not add a general immersive edge-bevel/topology selection editor.
- Controller emulation verifies software behavior. Physical Quest 2 comfort, visual alignment, frame time and haptic feel remain owner acceptance testing.

## Verification and delivery

The new native/profile/workspace tests use actual Three.js r169 and the shipped native sculpt/topology validation code. They cover group transaction safety, attached skins, all six operators, lasso masking and pins, topology closure, signed extrusion, profile changes, chords, tracking and cancel priority. The browser check uses pinned official IWER 2.8.0 Quest 2 hardware emulation with the real `renderer.xr.setSession` and engine frame loop. No application editor methods are used to fabricate controller results; fixtures and custom profiles enter through normal file import.

Source seal: **358 ordered patches, 9249898 HTML bytes, SHA-256 `5729bbee128f39cb7a97b73effb1e9d22cc51621f4377d206b68373b8cc1f3bf`**, 71 bundled assets. `index.html` and `modeler.html` are identical and agree with `SOURCE.json` and `source-manifest.json`.

Local validation passed: 14 native group, 20 native surface, 12 input profile and 10 actual-workspace regression groups; the spatial UI ray-picking smoke; and 16 end-to-end IWER controller workflows with zero page errors. The browser-tested HTML SHA is identical to the source seal. Existing 811-part/nine-sheet UV export and five-mode display tests also passed. Hosted verification is complete. Deployment follows the separate `DEPLOY_REQUEST.json` commit required by [RELEASE_PROCESS.md](../RELEASE_PROCESS.md).


### Confirmed hosted receipt

- Coherent source commit: `9804253f1f080a491c853c9a3c775be4b6df554f`.
- Separate request-only commit: `e1004bdae050c2e2489289e8ddec7ee283e47bbd` (one commit, one changed request file).
- Deployment: [42461483101](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42461483101), **SUCCESS**.
- Hugging Face revision: `d5a67a835ff173b2658a1d9a7cc0e5a5aa224f25`, **RUNNING**.
- Official revision-pinned `SOURCE.json` matches the full patch lineage, source version, HTML size/hash and 71 assets. Independently streamed hosted `index.html` and `modeler.html` each match **9,249,898 bytes** and SHA-256 `5729bbee128f39cb7a97b73effb1e9d22cc51621f4377d206b68373b8cc1f3bf`.
- An additional read-only preview loaded the original 59-part mage with Quest browser profile: 59 native XR targets, no serialized data/history change, parent restored and no page errors. No account or cloud project mutations were needed.
- This closure changes documentation only; it does not bump runtime identity or initiate another deployment.
