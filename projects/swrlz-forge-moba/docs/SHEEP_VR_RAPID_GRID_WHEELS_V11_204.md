# §E v11.204 — Sheep Tag PLAY rapid building and ability wheels

This is **Sheep Tag Play mode**, not the Game Editor or Model Editor. No gameplay house rotation control.

## Quest controller mapping
| Input | Gameplay action |
| --- | --- |
| Hold **right A** (~340 ms) | Open compact house radial; right stick highlights Farm/Income/Fort/CANCEL |
| Release right A after hold | Equip the highlighted house; selection persists |
| Tap **right A** | Place the equipped house at the ground ghost, stay equipped |
| Right trigger | Existing precise world action; while house is equipped, place it and stay equipped |
| Hold **left X** (~340 ms) | Open separate Mirror/Totem/NONE ability radial |
| Release left X after hold | Equip highlighted ability, keeping house selection independently |
| Tap **left X** | Cast/activate equipped native ability (or report why unavailable) |
| Right B | Open or close existing full wrist tools/camera/capture menu |
| Left Y | Recenter native camera on controlled sheep |
| Left thumbstick | Direct sheep movement as before |
| Right thumbstick | Tactical orbit/zoom normally; menu highlight while holding a wheel |

A/X event handling happens on button **release**, not press, avoiding unwanted house placements or skill activations on a long press. Mode checks scope all changes to an alive user-controlled sheep in immersive Play, not editor tools or wolf inputs.

## Real house matrix / walkable clearance
The normal house footprint is **2.4 × 2.4 units**. After the first live preview defines a lattice origin, each aim snaps to a **3.6-unit pitch** on native fine (`.15`) world coordinates, leaving **1.2 units of open corridor** between adjacent house footprints. The visual grid is drawn at these exact coordinates. On native coarse 3-unit snaps, the pitch becomes 6 so it stays legal. World axis-aligned houses **do not rotate**, even if the user changes the headset angle.

This is a usability grid, not an automatic building bot: native `stCanBuild` still checks existing obstacles, visible collisions, no-build zones, units, costs, house caps, trapped builders and lane geometry. A blocked cell stays red and does not place a house. Users can still construct an unwanted maze if they intentionally close passages with other structures; this mode does not alter game rules.

## Ability selection
Mirror is available only when the map rules enable Split and the native unlock/cooldown requirements are met. Totem requires enabled rules and a valid owned built house selected by the player; the native command provides any rejection reason. Abilities never bypass game authority.

## Performance / cleanup
Each wheel is built at most once per XR session, with cached `se195Text` label textures from v11.203. Hover changes material opacity/scale only; no new menu meshes per frame. Press-and-hold selection uses native Quest button state and the existing XR frame; no new animation loop. Optional haptic feedback is guarded against unsupported gamepads. Menus and GPU resources clean up on XR exit or restart.

## Tests
`node projects/swrlz-forge-moba/tests/test_v11_204_rapid_grid_wheels.cjs` verifies short versus long press, repeated placements, 3.6m lattice and coarse 6m mode, zero building rotation, independent persistent ability selection, modal input, cooldown-aware native skill calls, no editor input change, and menu disposal. Existing v11.203–v11.181 Quest/Sheep/editor/fog/ARPG regressions remain in release CI.

The terrain/map graphics and movable world panels are **future separate phases**; this patch deliberately addresses repeatable house-grid gameplay before a large art overhaul.
