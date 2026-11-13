---
title: §wyrl§ Engine v11.440
emoji: 🐉
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
fullWidth: true
header: mini
short_description: Maul, Sheep Tag, Model Atelier and Dragon Den
---

## §E v11.440 · Model Studio VR and mobile tool audit (2026-11-13)

The existing modeling workshop gains eight focused corrections: drawn VR outlines keep their native grip-thickness tool alongside the cube face-Extrude shortcut; VR Subdivide respects its valid 0.025 minimum; touch Vertex/Edge picks tolerate small silhouette misses; changing tools through the mobile lesson cancels the previous geometry preview; accessory shape/detail/fit cards explain their preview prerequisite; loaded assembly-motion choices refresh correctly; and VR picking uses current controller/menu transforms while excluding hidden cards. The v11.435 Grab handles, v11.436 connected satchel lesson, v11.437 Sheep Tag changes and existing projects remain in the ordered source.

See [the tool audit and official modeling-reference comparison](docs/MODEL_TOOLS_AUDIT_V11_440.md) for the actual VR/mobile capability matrix, native transactions, browser interactions, incomplete tools and physical-device limits. Verification and hosted publication results are recorded there as they complete; source discovery and menu navigation are distinguished from successful modeling operations.

## §E v11.439 · Smooth moving-sheep pursuit and capture tracing (2026-11-13)

SOLO VR wolves now use a direct approach when a moving sheep is visible in a clear lane instead of repeatedly probing up to nine A* routes; heavier decisions are paced across game ticks. A physical movement step that crosses the existing capture radius but is stopped by sheep-body collision can now capture once, respecting invulnerability. New diagnostics measure pursuit work, actual capture CPU, capture-frame and following-frame CPU separately. Rendering, WebXR tracking, LAN authority, previous worker/batching and Model Studio remain native. Physical Quest acceptance pending.

## §E v11.438 · Render continuity and solo-XR pathfinding Worker (2026-11-13)

Solo VR NPC primary A* pathfinding can now run in a bounded Worker using immutable numeric navigation data. Scene state, physics, headset rendering, LAN networking and controlled sheep movement stay native. Stale worker results are discarded on session, target or navigation changes, and unsupported workers fall back to existing paths. Engine diagnostics separate simulation CPU time, rendering submission CPU time, worker completions and XR callback gaps, but do not measure GPU/compositor time or guarantee zero frame stalls. Existing game, editor, VR controls and v11.437 capture pooling remain intact. Physical Quest acceptance still required.

## §E v11.437 · Sheep Tag independent AI bases and smoother captures (2026-11-12)

Solo sheep teammates no longer select home-building plots by following the human player's houses. Their Quest and desktop AI planners now choose staggered candidates based on each sheep's authored home, with spacing around player construction and other assigned sheep territories. The existing v11.411 path-planning quota and v11.419 congestion safeguards are unchanged.

Captures already coalesced building navigation invalidations and deferred material disposal; those protections remain. The Quest game now gradually prepares up to four unattached spirit visuals for reuse when wolves tag sheep, reducing synchronous work during capture. The new diagnosis reports spirit-cache hits/misses and JavaScript capture cost, not GPU or headset compositor frame time.

The 414-patch v11.437 candidate source was assembled and checked for inline JavaScript syntax, with focused territory/spirit tests. Exact 9,947,658-byte HTML receipt: `b1bfaf78a0c16c87ed96f826e574e857c904a85746f6707dccf1505d148be309`. Physical Quest acceptance is pending. See `docs/SHEEP_TERRITORY_CAPTURE_V11_437.md`.



## §E v11.436 · Cube face Extrude and one-mesh Satchel (2026-11-12)

The VR Extrude tool now recognizes selected cubes and editable topology and routes them through the existing native Manual mesh workshop. A plain cube converts to welded editable geometry; Trigger selects a face, then Preview and Apply commit a real extrusion. The previous drawn-outline extrusion remains available. For hollow shapes, Inset the top face first, then Extrude inward using a negative amount.

The Apprentice Satchel lesson now teaches a single connected bag body (Cube → editable topology → Inset rim → inward Extrude cavity), with the same tool references in phone and VR. Its ghost uses one noneditable 28-triangle cavity instead of five wall cubes, and its checker verifies a recessed interior floor and connected walls. Existing tutorial saves, quest progress, native Undo and account sync are preserved. All 413 source patches built to 9,942,103 bytes, SHA-256 `21ed3557c3bf5edabdeff55fee7fbb35b346c07d02ccd0c13b11af6e5291fee5`. Six focused native Three.js r169 groups passed. Physical Quest acceptance remains open. See [the release report](docs/MODEL_CUBE_EXTRUDE_SATCHEL_V11_436.md).

## §E v11.435 · VR Grab transformation handles (2026-11-12)

Selected meshes in Model Studio VR now display the same concept of a pivot-anchored transformation gizmo as mobile, even in the automatic **Grab** mode. Existing colored XYZ Move arrows remain independently ray-selectable: gripping an arrow starts the native axis-constrained Move preview, while gripping elsewhere keeps free-form Grab (translation, wrist rotation and stick scaling). Dedicated Move, Rotate and uniform Scale modes keep their existing handles. The VR tools menu, selected-mesh project, Undo and mobile gizmos are unchanged.

The real Three.js r169 regression passed five groups covering Grab visibility, selection-pivot axis rays, constrained movement, free-form fallback, menu pointer priority, explicit modes and no-selection hiding. The complete 412-patch source was reconstructed and its inline JavaScript syntax checked at **9,933,817 bytes**, SHA-256 `19d7464f80b572d6ace882ccac4a93cd8f9d96a370b13661d1b3c4ae9c7cdc84`. Physical Quest 2 selection and long-session performance still require owner testing. See [the v11.435 model gizmo checkpoint](docs/MODEL_VR_GRAB_GIZMO_V11_435.md) for verification and release history.

## §E v11.434 · Crowded Sheep Tag VR recovery and rendering (2026-11-13)

Crowded Sheep Tag no longer interprets a bounded slow frame as a Quest menu interruption while the native XR session remains visibly active. Real menu pauses and controller-release protection remain in place. Compatible scenery and authored building meshes share draw submissions while retaining their original triangles, normals, UVs and materials; the game editor also reuses unchanged shadows during camera movement. Busy VR prioritizes controlled/selected sheep occlusion outlines on Auto/Low/Medium, and High retains all teammate outlines. Occlusion checks now use the native XR camera.

The sealed build passed 34 new focused native test groups, existing AI/frame-budget checks, and preservation checks for v11.433 camera preferences and larger mobile gizmo targets. An emulated stereo stress match kept eight sheep alive while seven AI teammates built 76 houses, then passed head movement and menu-return checks. The matching editor fixture dropped from 4,414 to 2,416 draw calls with the same 515,659 triangles (45.3% fewer calls). These software-rendered checks establish application behavior, not physical Quest FPS or compositor acceptance. See [the crowded VR report](docs/SHEEP_CROWDED_VR_V11_434.md) for evidence, limits and publication status.

Live publication verified: [source 638bffb](https://github.com/kaministrator999-ui/Swrlzkamico/commit/638bffbd009119f4838cc3d41043ddcf96c4d1d0), [separate request 20453bf](https://github.com/kaministrator999-ui/Swrlzkamico/commit/20453bf770f988a79e3e792de556b33e66d9bf70), and [successful deployment](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43352719088). The Space is RUNNING at HF revision `2c4fc0698772efd1663444a0c54a7f55ed15e1e5`; both hosted HTML entry points and all 77 asset receipts match the sealed build. The owner's approximately 20-second onset, delayed Meta OS menu and temporary improvement with the overlay remain physical Quest acceptance cases; this release does not claim that complete symptom is confirmed resolved.


## §E v11.433 · Camera settings and easier mobile gizmos (2026-11-12)

Model Studio now offers **Camera settings ▾ → Invert touch orbit**, switching immediately between follow-finger camera drags and the original reversed direction. The choice is saved in this browser's local settings without touching project data. Mobile Move/Rotate/Scale gizmos also have slightly larger visible grips and 56px touch picking zones, including an easier shaft corridor. Desktop mouse, VR controller picking, model transforms, Undo, gesture priority, pinch/pan, and the shared workspace remain unchanged. The packaged mobile direction and persistence logic is regression-tested before release.

## §E v11.432 · Mobile Model Studio orbit direction (2026-11-12)

One-finger touch dragging in the native 3D modeling viewport now orbits with the finger: horizontal and vertical drags move the camera correspondingly. The change is applied in the final ordered build patch so earlier Model Studio source anchors, exact orthographic/perspective camera behavior, desktop mouse navigation, two-finger pinch/pan, VR controllers, selection, saved geometry and Undo stay intact. A focused assembled-HTML regression check covers touch orbit, desktop behavior, tap/drag separation and pitch bounds.

## §E v11.431 · Easier touch and VR transform handles (2026-11-12)

Move, Rotate and Scale gain easier targets using the existing native transformation transactions. Mobile handles retain useful screen size across zoom and projection changes, with padded touch picking and nearest-handle selection. VR uses larger visible handles and bounded invisible pick shells, consistent hover/grip contact and clearer axis feedback. Menus retain pointer priority; hidden handles remain unavailable.

See [the transform-handle report](docs/MODEL_GIZMO_ACCESS_V11_431.md) for controls, limits and verification. Live publication is confirmed: [source 7a21152](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7a21152f6bd159c51ebf85b593ed4381735b9b8b), [separate request 07c4b89](https://github.com/kaministrator999-ui/Swrlzkamico/commit/07c4b893be7260ebc03809ebd63afd6cca23b5b5) and [successful deployment](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43319424881). The exact source package, all 90 focused native groups and 11 IWER checks passed. Browser checks cover 20 distinct transform cases per mouse/touch profile, with exact authored-geometry Undo, Android cancellation and desktop hover feedback. Both hosted HTML entry points and the 77-asset source receipt match the tested build. The detailed report records the unchanged desktop pointer-lock Escape limitation. Physical Quest comfort remains owner acceptance testing.

## §E v11.430 · Visual teaching and manual mesh workshop (2026-11-12)

Model Studio keeps its existing editor and adds optional shared tool lessons with meaningful icons, Before/During/After diagrams, selection requirements and practical examples. The existing inspector exposes component modes, direct primitive choice, persistent assembly controls and contextual operation availability. A UV-seam vertex-selection mapping defect is fixed.

A manual **Cube → editable mesh → flat face region → Inset → inward Extrude** workflow creates connected native geometry with real previews and one Undo step per Apply. Bounded planar Solidify and the existing split/refine/fill/winding tools share the workflow. Native views gain true orthographic/perspective projection, six exact directions, group/component/all framing and a compact orientation control; VR retains its perspective camera and independent world-space console.

See [the visual workshop checkpoint](docs/MODEL_STUDIO_VISUAL_WORKSHOP_V11_430.md) and [the source audit](docs/MODEL_STUDIO_AUDIT_V11_430.md) for controls and limits. General bevel, merge/weld, bridge/loop tools, unrestricted mirror and several advanced construction/constraint tools remain incomplete. Live publication is confirmed: [source d995a3c](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d995a3c1b0b0ccf450398a8bcd9c9a2088b6befb), [separate request 04d1f2e](https://github.com/kaministrator999-ui/Swrlzkamico/commit/04d1f2ec01055c5b46c770b651a98fccaed82509) and [successful deployment](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43258217243). The sealed source and 67 focused native groups passed, with 12 desktop, 12 Android touch-profile, nine IWER controller and five startup/Projects checks and no page errors. Both hosted HTML entry points and the 77-asset source receipt match the tested artifact; the Space is RUNNING. The v11.425 updates are preserved. Physical Quest acceptance remains owner testing.


## §E v11.425 · Responsive editor startup and stable level controls (2026-11-12)

A full mobile-sized Chromium run confirmed that the restored 170-part Embervault Dragon Den, Project Levels selector, all three native Projects tabs, vertical project-window scrolling, Tutorials and My Projects switching work after a targeted startup repair. The cause was a v11.423 level-toolbar observer feedback loop that reacted to harmless control reordering, moved DOM controls and rebuilt selectors repeatedly. The v11.425 correction leaves attached controls in the editor's chosen position and reattaches them only after actual detachment, preserving project/account data and level packs. Real Moto and Quest acceptance remains to be checked.

## §E v11.424 · Fix full editor startup (2026-11-11)

A real Chromium mobile-screen reproduction of the live v11.423 page exposed a synchronous JavaScript error: `ReferenceError: se416Show is not defined`. The Sheep Tag VR setup patch was running outside the lexical scope containing its original setup function, aborting all subsequent startup logic. v11.424 relocates the same v11.420 radial bridge into its owning closure. This restores execution of normal Starter Projects / My Projects / Tutorials tab registration, authored Project Levels loading and the default scene. The Sheep Tag AI count controls and original user saves are preserved. Real-browser regression and owner acceptance are required before declaring the issue resolved.

## §E v11.423 · Projects menu, scrolling and editor levels (2026-11-11)

The native Projects dialog repairs missing Starter Projects, My Projects and Tutorials tabs without replacing the owner's starter cards or account project records. The dialog restores touch scrolling and keeps the three tab headings visible on narrow phone/Quest screens. The game editor reattaches its existing Project Levels selector and next-level controls after toolbar reconstruction, and preserves all authored level snapshots. Existing saved project and tutorial data are untouched. Physical device verification remains the owner's final acceptance check.

## §E v11.422 · Projects Tutorials tab recovery (2026-11-11)

The native Projects dialog now reliably exposes **Starter Projects / My Projects / Tutorials** together in a compact, responsive tab row on phone and Quest screens. Apprentice Satchel no longer depends on one lucky mount order: when the native se170 project hub appears late, the tutorial installer invokes it and adds the tutorial entry; a scoped observer recovers missing panes or tabs after dialog reconstruction. All three choices use the original native project tab selection, so inactive panels are hidden correctly instead of overlapping. The tutorial Start/Resume actions still operate on the existing independent model project, local progress and explicit Save Project/Save to Account flows. Starter cards and saved account projects are not rebuilt, deleted, or replaced. A read-only diagnostic inspection hook is available to verify tab registration. Browser/device acceptance remains pending.

## §E v11.421 · Reliable Model VR tutorial interaction (2026-11-11)

Apprentice Satchel's VR quest now stays hidden until the native headset viewer pose is calibrated, then appears once to the side of the normal tools console as an independently placed **world-space menu**, not a child of the model or the camera. Aim a controller and press Trigger to select the lesson's actual buttons. Real ray intersections take precedence over the old default 1.2m empty-space target; genuinely nearer model and tool controls still receive their native input. The native controller ray/reticle and highlighted hover/press borders show interactive targets. Hold Grip against the tutorial window to **move and rotate the entire window**, then release to leave it there; ordinary camera orbit and recenter do not overwrite that position. Both the regular VR tool menu and lesson window are physically larger with stronger angled-texture filtering for improved Quest 2 legibility. Existing §E modeling, VR object index, Sheep Tag setup and save controls are preserved. Automated source and controller tests are distinct from physical Quest 2 acceptance.

## §E v11.420 · Sheep Tag VR teammate setup with stable menu controls (2026-11-11)

The Quest in-world **Choose AI Sheep** menu now uses the exact same original controller-ray/trigger selection flow and stable button targets as the game main menu. Updating the team size no longer destroys/recreates the radial button meshes. The selected count is visible in the radial heading, all five wedges have meaningful actions (minus, plus, No AI Sheep, Start Match, Cancel), and min/max actions show clear feedback. Existing phone/desktop dialog behavior is unchanged. Preserves v11.419 AI collision-recovery frame budget, v11.418 solo team size, v11.417 VR Object Index and v11.416 Satchel Academy. Source and UI interaction regression tests pass; real Quest physical acceptance remains pending.

## §E v11.419 · Bounded Sheep Tag AI collision recovery (2026-11-11)

An owner-observed Quest freeze occurs when several AI sheep converge on recently built farm lanes and try to pass between houses. The existing v11.411 optimizer budgeted AI building-site selection, but collision back-out could still launch many complete A* route searches in one update. This release caps **solo Quest NPC sheep traffic/path recalculations at one per game tick across the flock**, rotates at most one back-out trail candidate per recovery attempt, and staggers blocked-lane retry timeouts. No extra render loop, no actor or building removal, no saved-scene changes. The human-controlled sheep, LAN multiplayer, non-VR logic, and sheep construction rules remain unchanged. Includes read-only traffic diagnostics. Source and syntax checks do not establish Quest hardware FPS; physical headset acceptance is pending.

## §E v11.418 · Sheep Tag AI flock selector (2026-11-11)

**Main Menu → Start Game** now asks how many AI sheep teammates should join your solo match. Select **0–5** on the starter map (up to 8 when authored sheep spawns allow) using +/−, the range control or the Quest VR radial menu; **Start Match** launches the existing game with that roster. The player-controlled sheep is not counted as an AI teammate. These are session-only changes: saved maps, wolf AI and multiplayer match authority remain unchanged. Retains v11.417 Model VR Object Index, highlighting and v11.416 Satchel Academy. Physical Quest acceptance remains pending.

## §E v11.417 · Model VR Object Index and mesh silhouette (2026-11-11)

The world-space VR console now lists named model parts with a nine-per-page Object Index, supports single and additive/toggle multi-selection, and outlines selected meshes individually. The v11.416 Satchel Academy remains integrated, with physical Quest testing pending.



## §E v11.416 · Interactive Apprentice Satchel Academy (2026-11-11)

The Apprentice Satchel tutorial now offers **Show Me** highlighting of real Model Studio tool controls, toggleable scene-owned **transparent ghost geometry** for each construction stage, and geometry-based **Verify** feedback about the floor, four surrounding walls, flap, strap segments, smaller details and leather/metal materials. Its illustrated controls are guidance, not duplicate editing tools, and the ghost cannot be selected or saved as model geometry. Verification is deliberately conservative: complex geometry and final save still require manual confirmation.

Each independent tutorial project may store **up to seven bounded, device-local recovery checkpoints**. Restoring requires confirmation and uses the native model editor's history so Undo remains available. Completed lesson objectives are serialized with the existing native project/account-save data and synchronize only after the user explicitly saves the project to their account; checkpoint geometry itself is not cloud-synced. In VR, the independent world-space quest adds Show, Ghost, Checkpoint, Restore and a selectable-part Leather/Metal/Shade control row, with the native tool menu retained and grip-repositioning only of the quest window. Physical Quest and phone acceptance is pending.

## §E v11.415 · Clear tool pictograms throughout Model Studio VR (2026-11-11)

The independent world-space VR tool console now shows distinct pictograms for selection, swipe/front/through lasso, Save Project, Save to Account, Clone, Projects, menu controls, controller aim, display modes and labeled viewpoints. Move/Rotate/Scale/Grab retain their original actions; Rotate is visually different from Undo. Increment/decrement cards show +/- marks. Existing hover/selected/disabled feedback, controller mappings, save schema, XR loop and the v11.414 satchel tutorial's native button references remain intact. Physical headset readability remains owner acceptance testing.

## §E v11.414 · Recognizable tool buttons beside tutorial instructions (2026-11-11)

The Apprentice Satchel quest now displays **visual miniatures of the real native Model Studio buttons next to the corresponding tool names** and within relevant instructions, including Scale, Move, Rotate, Add, Shape, Duplicate, Material, Color, Views, and Save Project. Miniatures read the current labels and CSS presentation of native buttons and are read-only; the actual buttons still perform edits. The matching VR quest uses the existing WebXR console's actual icon renderer beside Cube, Scale, Move, Rotate, Duplicate, Views and Save project, rather than creating an inconsistent icon set. The tutorial explicitly distinguishes the flat editor's **Add sphere → Shape: box** process from VR **Create → Cube**; Material/Color remain inspector fields instead of falsely implying a general VR material control. All lesson progress, cloned models and the existing world-space VR windows remain unchanged. Actual device acceptance remains pending.

## §E v11.413 · Apprentice Satchel on Quest (2026-11-11)

The standard Model Studio tutorial now uses a supported beginner hollow-bag workflow: turn the practice box into a bottom slab, then add four thin wall boxes, rather than suggesting a one-click inset on a solid primitive. The quest offers compact front/side/top concept diagrams and a native-tool shortcut. On Meta Quest Browser, start or resume the independent satchel project first, enter Model VR, and use the separate fixed world-space quest window with controller rays: Prev, Verify, Done/Reopen and Next. The panel is **not head-following** and follows only an explicit recenter; the original world-space VR tool menu and native geometry tools remain unchanged. Lesson progress is shared with the regular Model Studio through the same project ID and device-local checklist. The model still uses Save Project / Save to Account. Complex geometry steps remain owner-confirmed; headset comfort and final UX are pending physical testing.

## §E v11.412 · Apprentice Satchel guided Model Studio quest (2026-11-11)

Projects gains a dedicated **Tutorials** tab and the first beginner quest, **Apprentice Satchel**. Starting the quest creates an editable, independent native Model Studio project with one practice cube. Seven objectives teach sizing the pouch, constructing a real hollow opening, making a flap and shoulder strap, adding a buckle, assigning leather/metal materials, and inspecting/saving the result. The movable, collapsible quest dialog explains tool choices and provides hints, checkoffs and step navigation. Two basic checks inspect the actual model proportions and material assignments; advanced shape objectives use explicit human visual confirmation instead of claiming automatic geometry recognition. Progress is local to the independent saved project; existing Save Project and Save to Account are authoritative. No canonical starter or saved mage is overwritten. This first pass targets standard Model Studio; the separate immersive VR control panel is preserved.

## §E v11.411 · Solo Quest Sheep Tag AI frame-budget optimization (2026-11-11)

Quest 3S owner reports smooth menus but repeating freezes in active Sheep Tag gameplay that improve as living AI sheep disappear. The current NPC planner can evaluate multiple full-map route/build candidates synchronously. This patch distributes sheep base-selection and 12-site building-route checks at **one expensive planning candidate per game tick across the NPC flock**, only in solo immersive VR. NPC movement, controlled-sheep joystick movement, collision and original maze/sanctuary/wide-world path validation remain authoritative each frame; non-VR and multiplayer fallback remain unchanged. Identical same-update visibility queries reuse validated results. All v11.410 VR accessory workshop features and original v11.391 FOLLOW/FREE camera behavior are preserved. Physical Quest acceptance remains pending; elimination of all stutters is not yet established.

## §E v11.410 · VR accessory workshop (2026-11-11)

Model Studio VR adds **Create → Accessories → Hip pouch**: a rounded leather bag with a curved flap, belt loops, closure strap, clasp, edge stitching and a leaf/star emblem. Separate **Body**, **Details** and **Fit** pages adjust a live preview with coordinated leather colors, readable dimensions and clear selected states. The starting body is approximately **14 cm high** in the immersive workspace; it scales with the placement controls.

Aim freely or choose Surface fit against a character's hip. The preview holds its pose while the pointer operates the menu; the right stick turns/resizes it. After releasing the menu click, a fresh primary Trigger places the default eight editable native components as one selected group and one Undo step, ready for Grab. B or the first Y cancels an uncommitted preview. After placement, native mesh tools edit the components; the recipe controls do not persist as a parametric object. No saved cloud mage is modified by this checkpoint.

See [the accessory workshop checkpoint](docs/MODEL_VR_ACCESSORY_WORKSHOP_V11_410.md) for the workflow, geometry and transaction boundaries. The source package, 17 native test groups, nine spatial UI checks, 12 controller workflows and five disposable mage-reference checks passed. [Deployment 42961445702](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42961445702) succeeded; the RUNNING hosted editor and Modeler match the exact tested source seal. Physical Quest comfort remains owner acceptance.

## §E rollback · v11.392 FOLLOW throttle withdrawn (2026-11-10)

Owner Quest 3S retest: v11.392 slowed tracking of the controlled sheep, while full gameplay stalls continued (roughly 3s movement / 1s frozen) and scene glitches appeared even in FREE. The game menu remained smooth; lag decreased markedly after other sheep were captured. Therefore the v11.392 follow-camera throttle is **not active**. Production returns to the exact sealed v11.391 build (390 ordered source patches, SHA-256 6c002024054723ed9352d86b4703fd22748f311b7abb86607f735ff2ec5b2809). v11.392 source files remain in Git history for diagnosis but are intentionally excluded from the release manifest. Next investigation: per-sheep gameplay simulation, AI/pathfinding, fog, and render work while the match is active; no new hypothesis is called confirmed.

## §E v11.392 · Quest Sheep Tag stable FOLLOW camera (2026-11-10)

Headset A/B established that FREE avoids the severe geometry repaint/distortion while occasional full XR frame stalls remain. This scoped candidate reduces FOLLOW reference-space changes (at least 140ms apart and 12cm of target movement, with a 62cm maximum per change), preserving native head tracking, FREE camera, all game/guest controls and authored content. Use Y → FOLLOW or FREE to compare on the headset. It does **not** claim to resolve the distinct remaining frame freezes. Device acceptance pending.

## §E v11.391 · Left Y opens Sheep Tag VR tools (2026-11-10)

Meta Quest Browser reserves the physical left Menu button. In immersive Sheep Tag, press the available left **Y** face button once to toggle the existing tools radial. The main radial gives immediate **FOLLOW** / **FREE** camera actions; X skill selection, A building, right B camera free and L3 Nerd Stats are unchanged. This is not a binding for the system Menu button. Hardware Quest verification pending.

## §E v11.390 · Fluent controller selection, Grab and creation (2026-11-10)

Selecting from Inspect now arms Grab: grip moves and turns the existing selection, the stick sizes it, and the off-hand trigger provides smooth fine motion. A taps cycle Move/Rotate/Scale; hold A for broader tools. X+A opens Create with native Cube/Sphere/Cylinder/Cone placement previews; X+Trigger duplicates a group in one Undo step. Confirmed creations and copies become the selection and hand directly to Grab. Cancel and tracking/source changes discard uncommitted previews.

See [the v11.390 controller checkpoint](docs/MODEL_VR_FLUENT_HOTKEYS_V11_390.md) for controls, transaction boundaries and validation. Current Selector, menu drag, camera, image/UV, graphics and Quest guest synchronization work remains included. Deployment [run 42925139497](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42925139497) succeeded. The RUNNING hosted editor and Modeler match the tested source seal and asset receipts.



## v11.381 · Meta Quest as guest in phone-hosted Sheep Tag

Fixed the mismatch between browser-only multiplayer guest animation and immersive WebXR guest rendering: sheep/wolf replicas now advance on existing headset frames, while the Quest left-stick sends input through the existing authoritative host command transport. Host-built farms and bot sheep should remain spatially synchronized. The browser-only guest/touch path, Quest-hosted game, match authority, game saves, graphics controls and all other studios are unchanged. Device A/B verification pending.

## v11.380 · Graphics, Performance, VR tabs

The original Graphics & Performance panel now has responsive Graphics, Performance and VR tabs. Existing settings are retained; additional controls provide optional browser-only FXAA, hardware-bounded anisotropic filtering, authored LOD distances, shadow camera coverage, Quest/WebXR foveation where supported, and Sheep Tag VR stereo resolution on next session entry. Diagnostics identify browser native AA and reported XR capabilities rather than inventing GPU metrics. Controls persist locally and do not alter game saves, joystick input or headset tracking. Physical Quest 2 testing is pending.

## v11.379 · Visible Sheep Tag headset-frame recovery

A bounded XR callback gap during explicitly visible gameplay no longer triggers the Quest OS-overlay camera/input suppression. Genuine OS focus loss, hidden/blurred XR states and longer callback gaps retain recovery. VR graphics presets now choose the Sheep Tag eye framebuffer scale at VR entry rather than always forcing 72%. Real 25-FPS comfort and movement still require physical Quest testing.

## v11.378 · Improved experimental 3D blockout from edited 2D contours

The existing **editable 2D outlines** remain the default and support re-trace, selection, correction and SVG export. The optional **Experimental old rough 3D blockout** now reads the corrected main front silhouette, keeps a stable centerline rather than combining arbitrary full-width row samples, uses bounded side-view depth, and produces three independently editable loft sections (upper, middle, lower). The separate narrow accessory/prop option remains available. Use a separate Blank 3D Model project to compare both; existing model parts and starter projects stay protected. This is still approximate geometry, **not** semantic anatomy detection or automatic UV reconstruction. Device acceptance pending.


## v11.377 · Reference images now trace editable 2D outlines first

In the existing integrated §C image panel, import a five-view mage reference and review local color-connected outlines over each selected view. Select and rename regions, adjust/add/remove contour vertices with touch or mouse, toggle visibility, re-trace after changing view guides, and export visible vector shapes as SVG. This is local image segmentation, **not** semantic model recognition; outline labels require review and correction. The previous rough 3D loft generator remains tucked under an explicitly experimental disclosure and no longer represents the default next step. Reference pixels remain client-local. No automatic model-part creation or 3D mesh conversion occurs in this phase; saved model data, VR tools and chat transport remain unchanged. Physical phone/Quest acceptance pending.


## v11.376 · Selector menu with Grip-drawn lasso

A new **Select** tab in Model Studio VR offers the established reversible **Swipe · trigger** selection plus **Lasso · front** and **Lasso · through**. In an active lasso choice, hold Left Grip and trace a closed visual loop with the controller pointer; release Grip to add all model parts projected into the region, with front-layer filtering or full through-depth coverage. Existing single tap and swipe remain available. The original menu Grip still moves the floating window when targeted; otherwise Left Grip returns to workspace control outside Lasso. Existing source meshes, UV and project/cloud saves, controller models and §C image-to-model blockout are preserved. Owner headset acceptance remains required.

## v11.375 · Image → 3D blockout in integrated §C

Open an independent Blank 3D model, expand the image blockout section in § Chat, upload a five-view character sheet and review adjustable view guides. A local silhouette algorithm builds four editable loft sections, with optional detached side prop, using the existing native model/Undo/Save tools. This is an approximate untextured 3D starting shape, not a model-generated full likeness. The uploaded image is not sent to a model backend or stored as an account image. See `docs/IMAGE_TURNAROUND_BLOCKOUT_V11_375.md`. Owner image/VR acceptance remains outstanding.

## v11.374 · VR Model Studio Quest 2 usability feedback

The immersive VR tool console now supports pointer-anchored Grip window dragging instead of short hand-translation motion, without following head movement. A distinct expanding multi-selection Box3 helper encloses all selected parts; single selection keeps its original outline. Visible Move/Rotate/Scale gizmo handles now supply raycast hover hits to the controller pointer reticle. A top-level **Projects** tab makes **Save to Account**, local Save Project, and detached Clone Project discoverable. Existing Quest Touch models, dynamic labels, Undo/Redo, native mesh and UV content, starter immutability and authenticated account revision checks remain the same. Actual controller feel and cross-device account acceptance require owner Quest 2 testing.

## v11.373 · Reliable reversible mesh sweep in Model Studio VR

Corrects the held-left-trigger sweep start after native selection invalidated cached hover contact. Capture the original trigger hit once, carry it into the sweep session, retain preexisting selections, and remove only new meshes when retracing the same path. This narrowly scoped source repair preserves account-linked Save to Account, project identity/revision safeguards, Move/Rotate/Scale feedback, spatial menu grips, and Quest Touch controller models/labels. Owner Quest 2 acceptance remains pending.

## v11.372 · Quest 2 model manipulation and in-VR project save

In immersive Model Studio, the left trigger now supports press/tap selection and a reversible drag sweep over individual meshes, preserving preexisting selections when reversing. Selected Move/Rotate/Scale tools show a model-space gizmo and Grip displays a temporary controller-side transform feedback guide. The right thumbstick uses corrected lateral orbit with analog sensitivity. The side tool palette is independent of the loaded model and head movement, follows virtual orbit changes, may be Grip-dragged, hidden with its toolbar action or controller shortcut, and restores its stored placement. The native VR Studio menu and §E desktop toolbar expose account saving through the existing authenticated Chat connection without opening its chat UI. Save/Clone retain local project copies and account revision safeguards. Physical Quest 2 behavior and cross-device saves await owner acceptance.

## v11.371 · Safe Save Project and Clone Project

The Game, Model and Particle studios and the Projects library now offer project-native Save and Clone actions. Starter templates are never overwritten. Saving a starter produces a separate editable copy in My Projects; saving an existing copy updates its unique ID. Cloning always creates another unique ID, preserving native UV, rig, material, scene and particle data. Google-account saving reuses verified § Chat authentication and revision checks, while a complete on-device save remains available offline. Model, material and WebXR editing remain unchanged. Physical phone and headset acceptance is owner-tested.

## §E v11.370 · Anatomical stone texture polish on the WebXR Cliff Hand (2026-11-09)

The **approved real WebXR hand geometry and its UV islands remain unchanged**. The existing Plain Hand Base / Cliff Hand starter now performs a one-time material bake when first opened: copy the original owner-provided clean sandstone, tangent-space normals, roughness, AO and moss/fracture mask tiles from the 1536×768 PBR atlas into aligned 384×384 CanvasTextures. Project the actual 1,360-vertex hand triangles into UV space, so stone moss concentrates on wrist, thumb web and subdued dorsal creases **based on 3D anatomy, not arbitrary atlas rows**; clean up fingertips and large palm surfaces. Gradually vary mineral fracture width/intensity, interrupt some continuous equal-dark tile seams, introduce subtle sandstone grain, slightly lower exaggerated normal relief, and add a visually weathered wrist-edge material band. No polygon or rig changes, no new cuffs or arbitrary crystals. The improved 89-rock Rock Hand, original WebXR reference hand projects, Quest 2 controllers, existing user saved projects and UV Editor are not touched. If the new baked material cannot load, original cliff PBR remains the fallback. Phone and Quest 2 visual acceptance remains with the owner.

## §E v11.369 · Cliff Hand uses real WebXR hand geometry and existing sandstone textures (2026-11-09)

**Only** the Plain Hand Base / Cliff Hand project is replaced. It now asynchronously clones the locally bundled MIT-licensed WebXR right hand with its real 1,360 vertices, 2,314 triangles, all original UV islands and 25 joint reference landmarks; transforms axes and scale to match §E's native 17-bone rig; and maps the original owner-supplied 4-channel cliff sandstone color, tangent-space normals, roughness and AO from the same PBR atlas. Unlike v11.365/367, **there is no procedural SDF remeshing of the Cliff Hand**. The previous UV-specific dorsal crystal overlay is intentionally excluded because its texture coordinates belong to the old mesh. The native project card and save/UV/rig controls are retained. The independent WebXR hand starters remain untouched; **the improved 89-part Rocky Anime Hand remains unchanged**. The actual mesh is loaded using the native model project loader and named *Smooth Cliff Hand · WebXR Anatomy + Stone* so users can distinguish old saved projects. Phone/Quest inspection remains the user acceptance gate.

## §E v11.368 · Rotated UV auto-center and reusable Slide alignment

Model Studio's optional UV alignment marker can automatically center and turn its artwork guide toward the visible 3D mesh surface using true triangle UVs, the world-transformed mesh and current camera-up direction. This also works when a sphere or hand is rotated; a camera-facing side is not necessarily an anatomical front. **Capture corrected UV Slide position** converts a completed manual correction such as +0.2494 U into a reusable centered marker near U=0.2506, without changing the original mesh or ordinary image import. Source v11.368 preserves all v11.367 stone-hand geometry fixes and VR/editor tools; physical phone/Quest acceptance remains the owner test.


## §E v11.367 · Visible Cliff Hand anatomy and full multi-rock silhouette (2026-11-08)

Owner review identified two failures in v11.365: the connected Cliff Hand looked unchanged, and deleting decorative rocks made the multi-rock hand less true to its purpose. This release directly reshapes the connected Cliff signed-distance-field before generating the single UV-painted sculptable mesh: stronger palm narrowing, wrist/heel taper, separate finger barrel contours, natural thumb and nearly straight ulnar side. The second existing starter, *Rocky Anime Hand*, again starts from all **89 original stone meshes** (not the filtered 61), including 20 layered palm stones, 10 side stones, 12 finger chips, 12 solid finger shafts and the full angled rocky thumb, now drawn toward a credible hand silhouette rather than randomly overflowing the palm and fingers. The original PBR stone/moss/crystal artwork, 17-bone rigs, source UV attributes, editable rock groups, exported meshes, reference hands, saved projects and Quest controllers are preserved. Fresh starter names include *Anatomy* or *Anatomical Rock Formation* to distinguish updated geometry from older saved copies. Physical user visual acceptance remains separate from automated geometry tests.

## §E v11.366 · Paint alignment marker and rotated UV guide (2026-11-08)


Auto alignment is available inside the marker section: **Auto center + upright from view** raycasts the selected visible mesh and uses world-transformed UV tangents plus the current camera-up direction to orient artwork even when the object is rotated. **Capture corrected UV Slide position** extracts the proven manual U/V correction (a centered image with U offset +0.2494 maps to mesh U≈0.2506). Neither button silently changes mesh geometry, ordinary import behavior, or existing painted textures. A camera-relative visible side is not necessarily a semantic palm/front for arbitrary topology.
Inside the existing Model Studio UV popup, expand **UV alignment marker**. Select a mesh, choose **Pick center on model** or **Pick center on UV preview**, then tap its desired front/palm/face center. Adjust **Rotate guide** and **Artwork scale**, export the **marked UV guide** plus **marker JSON**, and design a normal clean artwork image against the centered orientation. **Import marker-aligned artwork** performs the inverse pixel transform against the original mesh UVs, clears the old UV Slide offset in the same Undo operation, and keeps original UV geometry unchanged. Marker settings persist per mesh in project JSON; the original direct paint import and UV Slide workflows remain unchanged. Owner-device validation follows the sealed source release.


## §E v11.365 · WebXR anatomy fit for Cliff Hand and multi-rock starter (2026-11-08)

**Projects → Starter Models** keeps the two existing separate stone-hand projects: *Plain Hand Base · Smooth Cliff Hand* (one smooth connected stone-PBR shell) and *Rocky Anime Hand · Emberstone* (rigged multi-rock anatomy). Both receive restrained proportion corrections grounded in the bundled WebXR right-hand 25-joint reference: index/middle/ring/pinky tip-to-proximal ratios **0.943 / 1.000 / 0.920 / 0.746**. The connected Cliff Hand now has a less swollen palm, more natural index and pinky tip reach, a narrower distal wrist and refined finger taper, retaining its original stone cracks, UV paint, geodes and 17-bone rig. The multi-rock hand keeps its closed stone geometry and animated digits, but removes 28 redundant decorative overhangs/slabs (never the core structure), narrows oversized fingers/outer palm, and gently corrects the index/pinky reach. The two WebXR hand references, Quest controllers, older saved projects and other editor tools are untouched. Device visual acceptance is pending.

## §E v11.364 · Export corrected UV image and calibration (2026-11-08)

After positioning an imported texture directly on a selected model with UV Slide, open the existing UV Editor and expand **After UV Slide · save corrected reference**. Export the corrected **aligned PNG** for texture use at U/V offset 0,0 and the matching **correction JSON** recording exact mesh references and offsets. These are non-destructive downloads; the current project, original texture, Undo/Redo and geometry UV coordinates remain unchanged. Save Project continues storing the live offset. Physical device acceptance remains with the owner.



## §E v11.363 · WebXR reference hand/controller starter load fix (2026-11-08)

The four Projects → Starter Models WebXR reference projects (left/right hands, Quest 2 Touch left/right controllers) now explicitly discard the outdated *Prism Jester* named socket/attachment graph before native project loading. Real mobile-browser validation identified `Invalid named socket` as the reason the first hand card did not open, despite valid bundled geometry; this is the same issue previously addressed for Hooded Vanguard in §E v11.294. The controller's independent seven-part native `meshGroups` assembly is preserved, as are original source UVs/textures, the entire existing Model Studio, and v11.362 tool-aware VR controller labels. Physical phone and Quest 2 confirmation remains owner acceptance.

## §E v11.362 · Live Quest 2 controller models and adaptive labels (2026-11-08)

In immersive **Model Studio VR**, tracked Quest 2 Touch controllers now show their bundled MIT-licensed WebXR reference models as the controller bodies, with small floating labels beside triggers, grips, thumbsticks and face buttons. Labels follow the tracked controller and switch automatically with the active Inspect/Move/Rotate/Scale/Sculpt/Draw/Lasso/Extrude tool, selected sculpt brush and Controller Studio profile. Pressed buttons highlight in place. No hand tracking is required; the Meta system button is never remapped. Controller meshes and label GPU textures are cleaned up when leaving VR; the existing synthetic body remains a fallback if an asset fails. VR-native controls, UV painting and model save/schema are unchanged. Physical Quest 2 fit and legibility remain owner-acceptance checks. See `docs/MODEL_VR_CONTROLLER_LABELS_V11_362.md` for mappings, scope and validation.

## §E v11.361 · Reliable WebXR starter opening + Quest 2 Touch models (2026-11-08)

**Projects → Starter Models** now includes the original WebXR Left/Right Hands and new **Quest 2 Touch · Left Controller** and **Quest 2 Touch · Right Controller**. The shared starter loader explicitly validates the native project, switches into the existing Model Studio and confirms the modeling viewport opened before reporting success; it also handles deep links and shows actionable errors. Each controller has seven editable native mesh sections for housing, trigger, grip, thumbstick and buttons, preserving real source triangles, UVs and the original 512px color texture. The models derive from the MIT-licensed public `oculus-touch-v3` WebXR GLBs; attribution and independent model assets are bundled. No special headset input implementation was added, and all existing model starters, UV workflows and current VR menus remain intact.

## §E v11.360 · Spatial VR menus, tactile buttons and smoother feedback (2026-11-09)

Model Studio VR gains a larger, clearer spatial console with persistent studio navigation, icon tool cards, stronger button states and polished controller wheels. Hover/press feedback and page/panel transitions run in the existing XR loop, respect reduced motion and pause when hidden. Menu ray feedback updates at headset frame cadence while native model-surface hover remains bounded. Current camera orbit, selected-only grip controls, native modeling history, wireframe-first UV painting and the new reference-hand starters stay intact.

See [the v11.360 menu checkpoint](docs/MODEL_STUDIO_VR_MENUS_V11_360.md) for behavior, source integrity and verification. Physical Quest acceptance remains owner testing. Deployment [run 42553034002](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42553034002) succeeded. The RUNNING hosted index and Modeler pages match the tested source seal exactly.



## §E v11.358 · WebXR anatomy reference hands (2026-11-08)

Projects → Starter Models now contains two separate **WebXR Left Hand** and **WebXR Right Hand** starter projects. Both use native editable mesh geometry converted directly from the public WebXR Input Profiles `generic-hand` GLBs, retaining 1,360 vertices, 2,314 triangles and UVs per hand. Each project also stores 25 named joint reference landmarks for anatomy study, but is not a live XR-tracked skin rig. Meshes and the MIT license are bundled locally, rather than fetched from an external host. Existing Plain Hand, Rock Hand, Arcane Glove and other starters remain unchanged. Model Studio editing, UV image painting and hand pose/animation of other models are unaffected. Physical phone/Quest acceptance pending.

## §E v11.357 · Simple UV wireframe painting (2026-11-08)

The selected-mesh UV Editor again opens on the exact exported UV wireframe by default. Export UV wireframe → paint an illustration → import painted image → align directly on the model with UV Slide. Colored surface-direction and JSON reference exports are tucked under an optional advanced disclosure, not required for normal texture painting. Original authored UVs, large-image acceptance, guide-line cleanup, model saves, Undo/Redo, whole-model atlas, and latest VR camera/selection fixes remain intact. Physical device acceptance follows hosted release.

## §E v11.356 · Accurate UV preview and stationary-model camera orbit (2026-11-08)

The standalone UV Editor now stays below the real viewport toolbar bounds, without covering the mesh hierarchy, and offers image/UV surface preview with interactive 2D-to-3D linking. Wireframe, colored surface-direction map and applied texture previews use the model's actual UV triangles. Tap on a UV region to highlight its 3D location, or enable **Pick on model → UV** for the reverse mapping; UV overlaps are reported. In Quest Model VR, the right thumbstick orbits the tracked camera horizontally/vertically around a stationary model, and right grip transforms only the existing selection instead of ray-picking a different mesh. Verify on phone/headset after publishing.

## §E v11.355 · Dedicated UV Editor window (2026-11-08)

Open **🎨 UV Editor** in the Model Studio top header to access single-mesh UV guide/image import, true surface directions, mesh-linked JSON and whole-model UV atlas in one movable, scrollable popup. Texture UV Slide and U/V nudges live there as well, while viewport Move/Rotate/Scale and Undo/Redo remain in the transform bar. The inspector no longer contains duplicate UV controls. UV surfaces, eye meshes and project assets are not rewritten by this UI move. Hands-on phone/Quest acceptance is a separate step.

## §E v11.354 · UV Slide and in-viewport Undo / Redo (2026-11-08)

The model viewport transform toolbar now provides Undo and Redo using native model history. Painted meshes also offer UV Slide: drag across the selected 3D surface to shift texture alignment without moving the model itself, use fine U/V buttons or Reset UV, and save the offset in the project. One completed drag is a single undoable edit. Existing UVs and project geometry are retained. Final source-integrity verification and hands-on phone/Quest acceptance are tracked separately.

## §E v11.353 · Viewport transform bar on mesh selection (2026-11-08)

The existing Move, Rotate, Scale and X/Y/Z ± native transform controls now appear in a compact row at the top of the actual Model Studio viewport **only when a mesh is selected**. The bar remains visible with the inspector collapsed. The previous sidebar duplicate transform rows are hidden while their backing handlers remain active, preserving real gizmos, Undo, bounds checks and grouping. UI spacing avoids the top camera overlay and the bottom zoom controls. UVs, 3D eye geometry, VR and Game Engine behavior remain untouched. Physical phone/Quest acceptance remains with the owner.


## §E v11.352 · Model Studio transforms back in Tool settings (2026-11-08)

The existing native Move, Rotate and Scale tools are now directly accessible in Model Studio's Tool settings inspector, even while a category mode is active. X/Y/Z axis selection and ± nudge buttons reuse the original mesh transform, gizmo, grouping and Undo handlers. The selection and components disclosure remains organized below the transform row; no additional floating tool sheet or duplicate transform engine is introduced. VR, UV coordinates and existing project data are unchanged. Phone and headset acceptance remains owner testing.


## §E v11.351 · Game Engine quick actions restored (2026-11-08)

Projects, Play, Stop, Enter VR, and More options have an accessible Game Engine header row on phone, desktop and Quest Browser. Reuses native controls and the existing More options popover; avoids a second Quest Controls drawer. File → Projects remains a secondary path. Source-sealed package and owner phone/Quest acceptance are separate from this source change.

## §E v11.350 · Two-hand VR modeling, live profiles and native surface tools (2026-11-08)

Model VR now uses the active Controller Studio profile to drive real editing. Right-hand tools and left-hand view controls add multi-part selection, explicit two-hand geometry transforms, A/X hold wheels, focus/precision shortcuts and safe Undo/Redo. Native sculpt strokes, saved lasso masks, planar outline creation and signed closed extrusion stay inside the same immersive editor. Cancel and tracking loss discard previews; each completed operation commits one native history step. Camera/aim/display tools, UV sheets and the owner UV image import correction remain included.

See [the v11.350 checkpoint](docs/MODEL_STUDIO_VR_V11_350.md) for controls, source integrity, targeted verification and deliberate geometry limits. Physical Quest feel and performance remain owner acceptance testing. Deployment [run 42461483101](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42461483101) succeeded. The RUNNING hosted index and Modeler pages match the tested seal exactly; physical headset acceptance remains owner testing.



## §E v11.346 · Whole-character UV export across readable numbered sheets (2026-11-08)

v11.345 introduced multi-object native UV guide export and Model VR display modes (Textured, Solid, Wireframe, X-ray, Normals), but a single guide was capped at 96 parts. A complex §E character may contain hundreds of native meshes. **Select All now includes the entire character** without shrinking every UV segment into an unreadable tile: the existing UV inspector shows Previous/Next sheet controls and exports up to 96 parts per numbered sheet, each with a matching **GUIDE.png + MAP.json**. Source model names, part IDs, UV rectangles and fingerprints remain linked to each sheet; importing a painted sheet changes only those exact source parts in one Undo step. The existing 3D mesh and source-authored UV coordinates remain unchanged. Overlapping islands within a single part are explicitly retained, not falsely described as auto-unwrapped.

The sheet navigation reuses the existing UV inspector without introducing a new global toolbar. Selecting all/groups refreshes checkboxes in place instead of rebuilding hundreds of UI rows. A bundled-source test [succeeded](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42458051449): an **811-part character produced nine sheets**, each with no more than 96 native parts and the last with 43. The rebuilt §E source contains **357 ordered patches**, **9,165,566 bytes**, SHA-256 `77228e757f77977a35f0b9b74bf0f5efc9c82659d70178256b4b9c8f2919ed23`. Real-device export behavior and the user's privately saved mage UVs require owner verification in Model Studio.


## §E v11.345 · Linked multi-object UV atlas and true VR display modes (2026-11-08)

The owner clarified that **VR Views** should control how the model is rendered (Wireframe, X-ray and other material/geometry modes), not primarily the camera perspective. The existing 12-button VR palette now presents **Views → Textured, Solid, Wireframe, X-ray, Normals**; **Angles** retains Front, Back, Left, Right, Top, Bottom, and Isometric model orientations. Every temporary display material is restored to its exact native reference on mode exit or VR closure, with no changes to stored part colors or textures.

The previous UV Layout inspector only exported the current single mesh. Its new, collapsible **Whole-model UV atlas · linked parts** section supports Select All, per-group selection and individual checkboxes for every loaded editable mesh—including whole-character Hooded Vanguard/mage models. It exports a transparent **GUIDE.png** with source-authored UV triangles in separate, numbered 2048/4096px part cells, plus a matching **MAP.json** with exact cell pixel coordinates, original part IDs/names, UV bounds and stable mesh fingerprints. Tap an atlas cell or **Focus** in the list to select the corresponding 3D part. Send both files to ChatGPT when requesting aligned painting; the resulting artwork should preserve the cell placements and omit the guide labels/lines.

A painted atlas PNG can later be imported and automatically cropped to the original UV space for every linked mesh in **one native Undo checkpoint**. Import checks part IDs and UV fingerprints first, rejects wrong model versions, and observes existing per-part texture size constraints. This is **mesh-part segmentation**, not automatic topological re-unwrapping: UV islands overlapping *inside* one part are still authored overlaps and must be manually corrected for fully unique painting. Original geometry, UV coordinates, rig and existing materials are preserved.

The [focused real-Three.js candidate test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42457148584) passed for a 17-part source model, independent non-overlapping atlas cells, exact part linkage validation, stale-manifest rejection, all five VR model render modes, and restoration of native materials. Verified source: **356 patches, 9,162,827 bytes**, SHA-256 `39a192fc72c4eac1435a6bdec4a53039578196e6bb97040716fe6b64b3452cc5`. Owner browser/Quest 2 export/import UX remains unmeasured and must be tested on real hardware.


## §E v11.344 · Quest pointer calibration, modeling perspectives and faster click response (2026-11-08)

Quest 2 owner testing of v11.343 identified a substantial discrepancy between the WebXR Model Studio pointer direction and the Meta system-menu pointer, plus a synchronous stall each time a trigger selected the hand. This release adds an **Aim** panel for independently adjustable left/right controller yaw and pitch (2° increments, ±25°, with per-hand and all-hands reset), persisted locally in the headset browser. The visible ray mesh and its selection ray now use **the same correction quaternion**. WebXR cannot access Meta's OS ray, so offsets must be visually calibrated; no exact native alignment is claimed without owner testing.

The existing Model Studio VR palette now has organized **Tools**, **Views**, and **Aim** pages reusing the same twelve spatial buttons, rather than growing overlapping controls. Views offers **Front, Back, Left, Right, Top, Bottom, Isometric** and Focus positions; these change the model presentation relative to the user while retaining genuine immersive stereo-perspective projection and free right-stick orbit.

Trigger and grip selection now use the cached simplified glove-surface picker (rather than full-resolution skinned-triangle raycasting). Repeated clicks on an already-selected native part avoid redundant native selection/rebuilds. The native model remains authoritative for Move/Rotate/Scale commits, Undo and Redo; no saved mesh geometry is changed. Read-only `lastTriggerMs` and `maxTriggerMs` counters enable focused performance feedback.

The [isolated candidate build](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42455530224) passed native Three.js r169 aim/view/trigger source checks, producing 355 ordered patches, **9,135,955 HTML bytes**, SHA-256 `7adec1e91ee56f5eeda364c3d733de3d95d8fb5824753d943ef6382f27bc3d4f`. The software check does **not** measure physical Quest 2 frame timing, UI ray accuracy against Meta OS or actual trigger stall duration. Owner hardware testing is the acceptance gate.


## §E v11.343 · Surface-following VR selector and camera-oriented sticks (2026-11-08)

Owner Quest 2 feedback on v11.342 confirmed much better frame rate but identified two usability defects: the ray reticle slid across the glove's rectangular *bounding box*, not its visible fingers, and the left/right joystick view directions felt inverted. This release keeps the fast bounds-only broadphase, then places the hover reticle at the nearest intersection with a **cached, connected, reduced-polygon model surface** rather than the box. On skinned hand models, the pick surface shares the real skeleton and follows bone movement. True Trigger and Grip selection still raycast the original native mesh; temporary hover geometry is not saved to the model.

The left stick's horizontal/vertical pan and right stick's horizontal/vertical orbit signs are reversed for camera-relative navigation; right-stick press plus vertical still zooms in/out. The reduced pick surfaces are built at session entry for the first few visible parts and reused across hover samples; model edits/rebuilds and VR exit invalidate or dispose them. No unrelated game, engine or AI chat editor behavior is changed.

A real Three.js r169 surface test [passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42450424824): five curved-surface ray contacts differed from the full geometry by 0.00027–0.00349 **Three scene units**; the center hole was correctly unselectable; and a skinned model was correctly hit after a bone translation. The full source candidate rebuilt to **9,128,756 HTML bytes**, SHA-256 `7f34d4884d8491515789052b4c36a5564cdd298c5901debb9824cfe0b2dee2f6`, on 354 ordered patches. Physical Quest 2 FPS, controller comfort and final alignment acceptance remain owner testing.


## §E v11.342 · Smooth dual-controller hover on skinned models (2026-11-08)

A real Quest 2 Model Studio test of v11.341 exposed lingering frame-rate loss when aiming one controller at the native hand model, increasing with both controllers. The root issue was a skinned-mesh exception in the earlier broadphase: **hover still performed full skinned-triangle raycasts**, alongside repeated CPU skin bounds and native projection refreshes.

**v11.342 removes those operations from idle pointing.** A tracked ray hits cached world-space part boxes (approximate hover guides) rather than model triangles; trigger selection and grip still perform immediate, exact mesh intersections, including individual finger gaps and overlapping parts. Both controllers share a native projection cache until the model revision changes, and unnecessary per-hover UI scene traversals are removed. Per-session read-only picking diagnostics report hover and precise counts with hover duration. Existing left-stick pan, right-stick X/Y orbit and press-to-zoom controls remain unchanged.

The isolated candidate GitHub Actions [run 42448714716](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42448714716) passed its two-controller no-triangle hover test and sealed the rebuilt 353-patch HTML at **9,122,053 bytes** and SHA-256 `ab1f1309ac860c540583db730c4ff1866be5fc074f73ca220181a6cf5029a4ad`. Physical Quest 2 frame-time, reticle alignment and click-accuracy acceptance is owner testing.


## §E v11.341 · Optimized Model VR picking and analog model orbit (2026-11-08)

In the immersive Model Studio, idle controller hover now samples at a bounded rate instead of launching full mesh raycasts on every headset frame. A shared per-frame model projection and cached world-space part boxes avoid repeated full-model traversals; ordinary meshes use bounds to reject misses before face tests. Trigger selection and grip-initiated editing remain immediate and precise, with native Undo/Redo and model ownership intact.

Joysticks are now oriented around modelling: **left stick pans horizontally and vertically**, **right stick continuously orbits around the model's centre on both axes**, and **hold right-stick click plus vertical movement to zoom**. Orbit pitch is clamped, Precision reduces navigation sensitivity, and Recenter restores the neutral view. The physical Quest 2 performance and comfort check remains the owner's acceptance test. This fixes only Model Studio VR; Sheep Tag and other editor workspaces are unchanged.


## §E v11.340 · Immersive Model Studio and controller authoring (deployed)

Model Studio has its own Enter model VR action, a comfortable model presentation stage, native controller rays and selection feedback, and a readable world-space tool palette. Trigger selects model parts; choose Move, Rotate or Scale before gripping. Release applies one native history edit; cancel, tracking loss and session exit discard an uncommitted preview. Inspect mode and view framing preserve saved geometry.

The actual native model root, geometry, materials and rigs are reused in an isolated Model VR scene through the existing main XR loop. Exit restores the browser Model Studio. Game/Arcane XR, the Materials workspace and owner hand/UV releases through v11.337 remain preserved. Deployment [run 42442450957](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42442450957) succeeded; the RUNNING hosted index and Modeler artifacts match the exact tested build. Controller emulation, source verification and physical headset acceptance are separate gates; current receipts and supported controls are recorded in [the checkpoint](https://github.com/kaministrator999-ui/Swrlzkamico/blob/main/projects/swrlz-forge-moba/docs/MODEL_STUDIO_VR_V11_340.md).

## §E v11.337 · Organic finger smoothing, natural wrist blend, inlaid aquamarine knuckles (2026-11-07)

Owner-provided close-up palm and finger photographs alongside real Moto screenshots identified three remaining modeling issues in **Plain Hand Base · Smooth Cliff Hand**: a sharp-looking hypothenar heel before the wrist, stacked/ridged middle-finger joints and angular tips, and simplistic repeated cyan spikes on the dorsal knuckles. This release corrects them **only for that starter**, extending v11.335's narrowed ulnar edge without changing the global base-hand generator or other projects. A feathered SDF sample offset gently rolls the bottom of the outer palm into the wrist. A starter-specific organic finger field smooth-blends PIP, DIP and distal fingertip pads, and the single connected gauntlet mesh receives a modest sampling improvement (.047→.044) while keeping all 17 native bones, poses and sculpting support.

Four new **inlaid aquamarine geode textures** replace the flat repeated spike stencil: individually varied faceted gemstone cuts, recessed slate sockets, stony rims, internal color planes, polished roughness and restrained emissive reflections. These remain **dorsal-only**, composited via the native MeshStandardMaterial, without separate crystal meshes or palm bleed. Original fractured sandstone/albedo, normal/AO/roughness, wrist moss and the v11.336 **UV layout export/reimport** remain unchanged. Actual source-field checks measured the lower ulnar edge moving from x=0.51149 to x=0.40390 at y=1.36 while leaving the thumb and upper knuckle area unchanged. Both desktop and Android-sized WebGL shaders/viewport checks passed, including loading with the original atlas URL deliberately blocked. **350 patches, 71 packaged assets; 9,055,350 HTML bytes; SHA-256 `649c09b82d7ff0fee600c5b941be28da2bd77f54ee709d7bc635248857451ea6`.** Final physical Moto/Quest visual acceptance remains owner-controlled; the reference photos are not stored in the repository.


## §E v11.336 · Native mesh UV guide and painted texture round-trip (2026-11-07)

Model Atelier's selected-mesh inspector now offers **UV Layout**: export the actual indexed triangle UV wireframe to a transparent 1024×1024 PNG, paint the artwork on a separate layer using that template, and import a PNG/JPEG onto the exact same mesh via its original UV coordinates. The image is converted to a bounded 512×512 PNG embedded in the model part, retained by project save, JSON export and Undo/Redo; it previews as a color texture on the model itself. No generated geometry or new renderer. Meshes with absent or out-of-0–1 UV coordinates are rejected rather than silently projected. The exported cyan guide is a **reference overlay**, not artwork to be baked into the import. Existing Material Studio actor workflow, UV diagnostics, and Sheep Tag/Quest logic stay unchanged. An overlapping UV atlas still requires proper UV unwrapping; this tool accurately extracts existing coordinates and does not promise automatic seam correction. Phone/Quest acceptance remains owner-tested.



## §E v11.335 · Straighter pinky-side palm contour (2026-11-07)

Following actual Moto screenshots, the owner noted the **ulnar/hypothenar edge under the pinky bows out too far** compared with the provided palm reference. Append-only patch `v11_335_cliff_ulnar_contour.py` applies `se335NarrowUlnarField` **only to the Smooth Cliff Hand SDF**, shifting positive-X samples inward smoothly up to 0.105 model units in the mid-palm (fade y=1.24–2.19), without a flat clip or hard edge. It restores a nearly straight outer-palm profile while retaining natural taper into the existing wrist and pinky MCP. The photo-guided thumb/thenar and finger shapes, single connected mesh, all 17 bones, dark rock fractures, wrist moss and four teal dorsal crystal knuckles remain untouched. The real source-backed field test measured mid-palm outer edge x=0.6064→0.5014 at y=1.74,z=0.06; thumb, wrist and finger-root samples were exactly unchanged. **348 patches**, **71 assets**, sealed HTML **9,034,925 bytes**, SHA-256 `f90898624ca109fd4ab2b09c6ab23562112d9b4864a1aedc185829b7d65c3637`. The owner retains physical Moto/Quest visual acceptance; no reference photo is shipped in the repository.


## §E v11.334 · Photo-guided Smooth Cliff Hand and dorsal-only crystal knuckles (2026-11-07)

Owner's latest physical Android screenshots verified the sandstone and dark cracks now render, but reported that the old stone knuckle accents appeared through the **palmar** side. Owner also supplied a real left-palm photo for proportional study and requested tasteful crystals on the knuckles. The single connected starter now receives a **small, model-only** reference-guided refinement to finger length hierarchy, finger splay, metacarpal width and thenar pad volume, retaining the original 17-bone rig and all sculpt/animation features. No personal photograph is embedded or stored in the engine.

**Material fix:** Shared front/back planar UVs made the previous albedo/normal/AO knuckle relief visible on both sides. Those shared knuckle stamps are removed from the original source atlas composition; rock cracks, normal/AO/roughness and wrist-only moss remain. A new transparent 384px **teal faceted crystal CanvasTexture** is composited into the existing native Three.js MeshStandardMaterial **only on dorsal-facing surface normals**; the photographed palm therefore remains uninterrupted stone instead of seeing imaginary dorsal rocks. No crystal or rock geometry is added. Both real-browser palm and rotated dorsal captures showed intended behavior; desktop and Android-sized WebGL loaded with no errors or external rock atlas requests. The 347-patch build is **9,033,432 HTML bytes**, SHA-256 **`332911f48c24b60555197597bcdf626919e2affad49fd35743d7e7401907105d`**, 71 assets. Final physical Moto/Quest approval belongs to owner testing.


## §E v11.333 · Original Cliff Hand atlas guaranteed inside the page (2026-11-07)

Owner phone screenshot showed the **Plain Hand Base · Smooth Cliff Hand** as a uniformly tan, undetailed surface despite source-level v11.332 fixes. A corrected end-to-end browser capture actually renders the intended mineral cracks on desktop and Android-sized Chromium, with the original 17-bone single connected hand. Hosted Hugging Face `SOURCE.json` and the separate 404,577-byte rock JPEG both returned HTTP 200 and exact SHA-256 matches. This narrowed the remaining fault to the mobile session/cache or a failed client image load, not the original UV or atlas artwork.

The v11.333 patch verifies the **original owner-provided 404,577-byte JPEG** against SHA-256 `fc56730c8019d8079794c7b7379c75c8c07381794104eb56a439a94588647cbe`, then embeds it byte-for-byte as a data URI inside the sealed HTML for **this starter's PBR compositing loader**. Once the new page loads, the hand no longer needs a second HTTP request for rock textures. The exact color/normal/AO/roughness tiles, dark fault mask, wrist-only moss, four knuckle ridges, geometry, rig, and unrelated models remain unchanged. The 346-patch package is **9,027,112 bytes**, SHA-256 **`e3e46cfd23dc4cddaf9ecb5316de58e5f099277b848ab7f884968335c59cd5ce`**, 71 original assets. Source pixel, inline byte, no-network, and browser checks are scoped to the affected starter; final Moto/Quest visual acceptance remains the owner's test.


## §E v11.332 · Smooth Cliff Hand original fracture mask repair (2026-11-07)

The connected **Plain Hand Base · Smooth Cliff Hand** used clean sandstone albedo, normal, roughness and AO tiles, but did not composite the supplied atlas's separate bottom-right *fracture outline mask*. Thin base-color cracks were therefore easy to lose at phone/Quest display size. The new material step reads that existing fracture mask, adds clearly visible dark mineral seams with a narrow one-pixel shoulder, then preserves the four painted stone knuckles and wrist-only moss. This uses the same original asset and mapped UVs; **zero additional geometry**, no floating crack tubes, one connected gauntlet mesh, and the original 17-joint rig/animations. The 345-patch package measures **8,487,373 bytes**, SHA-256 `0d84c3c8d7243db25a8f7406146eac54b7c23da8ab4771686d2bd96d656fc308`. Focused pixel/atlas/source checks passed; phone/Quest visual acceptance remains owner-controlled.


## §E v11.331 · Smooth Cliff Hand sandstone PBR repair (2026-11-07)

The **Plain Hand Base · Smooth Cliff Hand** starter now uses neutral-white material tint over its supplied clean sandstone atlas, normalized ambient-occlusion strength, and explicit secondary texture-channel selection for compatible Three.js renderers. The existing rigged-mesh renderer already supplied `uv2`; this release preserves that working attribute and exposes the same UV coordinates as `uv1` for newer renderer conventions. Four mapped knuckle reliefs, wrist-only moss, normal/roughness maps, one connected tapered hand/gauntlet topology, and its 17-bone animated rig remain unchanged. Other starter models, saved scenes, Quest controls, and Material Studio are unaffected. Native/packaging checks precede release; final phone/Quest visual acceptance remains with the owner.


## §E v11.330 · Dedicated Material & Texture Studio (deployed)

Materials opens a dedicated library, preview/painting workspace and property inspector. Desktop uses reserved columns; phones and wider portrait frames use Library, Preview & paint and Properties tabs. An empty library hides unavailable fields and offers a clear first-material action. The default texture view covers the underlying game editor; an explicit native 3D scene preview remains available. Covered 3D drawing pauses while editing textures, then resumes for the visible scene preview; native updates and history continue.

The existing material definitions, PBR controls, direct texture painting, brush undo, scene assignments, project saves and PNG/JSON import/export handlers remain authoritative. Opening Materials does not create a material or replace the current project. Model, Game and Particle studios retain the v11.320 navigation changes and the owner's v11.321 sightline/Quest work. Source and browser verification plus publication receipts are recorded in [the checkpoint](https://github.com/kaministrator999-ui/Swrlzkamico/blob/main/projects/swrlz-forge-moba/docs/MATERIAL_STUDIO_LAYOUT_V11_330.md); physical-device appearance remains owner acceptance. Deployment [run 42365572126](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42365572126) succeeded; the RUNNING hosted index and Modeler files independently match the browser-tested source seal.

## §E v11.321 · Sheep Tag house sightlines and crowded Quest diagnostics (2026-11-07)

The owner's Quest testing found the v11.306 last-sheep chase much smoother, but severe slowdown remains while turning the headset with living teammate sheep and many houses under construction. Gameplay source confirmed enemy sight used distance-only checks, not building obstruction. In fog-enabled matches, visible wolf/sheep pairs now test house line-of-sight, while true last-observed enemy memory, scent clues, allied shared sight and fog-off behavior remain intact. Sight results are reused within the same simulation update. Crowded Quest gameplay (2+ living sheep, 8+ houses) keeps the existing escape-search scoring but spreads its candidate checks across more frames. Nerd Stats adds pages **9/10 and 10/10** to compare head-turn versus still frame gaps and draw-call counts while busy, and show sight checks and AI budget. The v11.306 wolf-radius A* counter now uses the actual configured radius. Other studios, controllers, assets and saved projects are unchanged. **342 patches, 71 assets, 8,451,859 bytes**, SHA-256 `47e8cc9f9f54fb1592715961ecd4faab13fc94f56e0f8208c250efc3306b2079`. [Release checkpoint](docs/SHEEP_SIGHT_XR_CROWD_V11_321.md). Quest performance improvement and visibility fairness require owner-device confirmation.



## §E v11.320 · Organized studios and automatic project navigation (deployed)

Game Engine, Modeling and Particle Studio now use distinct navigation and action rows, clearer labels and deliberate tool docks. The model category rail occupies its own column immediately left of the inspector, remains usable when that inspector collapses, and becomes a separate scrollable row in Compact mode. Selection, component and group controls live in the inspector. A dedicated Projects action is available from Modeling; Particle menus stay reachable on phones and their layout selectors live under Tools.

Project Library reserves separate header, Starter Projects / My Projects tabs and a scrolling content pane, eliminating the fixed-offset overlap. Completed native model, game and saved particle-workspace loads select the corresponding studio. New exports retain an editor workspace hint; a valid emitter-library import opens Particle Studio. Explicitly loaded documents suppress the deferred first-game bootstrap so navigation preserves the loaded data.

The complete 59-part Little Crystal Mage is now the only account project with that name: the older 41-part checkpoint was removed after both cloud documents and revisions were verified. The 59-part save remains unchanged at revision 2. Existing Vanguard mesh/UV, Sheep pursuit cache and Arcane VR glove releases through v11.309 are preserved. See [the checkpoint](https://github.com/kaministrator999-ui/Swrlzkamico/blob/main/projects/swrlz-forge-moba/docs/STUDIO_NAVIGATION_LAYOUT_V11_320.md) for browser checks and exact source receipts. Exact packaging, desktop/phone browser checks and the authenticated Game → Model Studio cloud-load flow passed. Deployment [run 42345232697](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42345232697) succeeded. The RUNNING Hugging Face release and both hosted HTML pages match the exact v11.320 source seal. Owner-device visual acceptance remains separate.

## §E v11.309 · Native Arcane targeting, no stray VR beams (2026-11-06)

The owner observed cyan/yellow §E beams pointing left and slightly above the native Meta Quest pointers even after v11.308 claimed the rays were hidden. Source investigation found **two independent visual emitters**: the legacy `se181` Line and the `se192` tapered ray plus reticle, which can inherit a saved controller yaw trim. v11.308 hid only the first. This release hides **both visual beams and the reticle** in **Blank VR · Arcane Hands** and uses the untrimmed native WebXR target-ray controller pose for Arcane hit tests, without changing the controller transform or analog glove finger animation. Other VR editors restore their beam presentation and saved trims. Native spell aiming, grip-space glove mounting and Sheep Tag controls are preserved. Focused two-controller tests and inline JS integrity checks are included; exact comparison with Meta OS pointers still requires Quest testing. Sealed source: **340 patches / 71 assets / 8,402,089 bytes**, SHA-256 `f52a2e9838735d4bf0026d560a4bdf24e943b54d01c933bce9e05dfb6af90ec5`. [Source checkpoint](docs/ARCANE_NATIVE_RAY_V11_309.md).

## §E v11.308 · Arcane grip-space alignment and ray-free spellcasting (2026-11-06)

Owner Quest screenshot: the native two-glove rig and pink/violet material detail now render upright, but glove/controller alignment is slightly off and the cyan/yellow target-ray lines cross the hands. In **Blank VR · Arcane Hands** only, gloves now follow WebXR Touch **gripSpace** when available (target-ray fallback), with a modest wrist offset and approximately 7% visual size reduction. The visible controller ray lines are hidden only in this starter; their target-ray transforms, hit-testing and independent spell firing continue operating. Other XR projects restore their own rays. Equipped spell labels follow the glove pose; original editable glove models, analog finger animation and Sheep Tag are untouched. A focused smoke test covers grip mounting, fallback and beam visibility, with real Quest 2 alignment acceptance still pending. Source sealed: **339 patches / 71 assets / 8,399,073 bytes**, SHA-256 `a0148e2a9d406ef806bc580eee692e66011dc0922a0573ae07820d4f9f242511`. [Checkpoint](docs/ARCANE_GRIP_FIT_RAY_VISIBILITY_V11_308.md).

## §E v11.307 · Arcane Quest VR glove orientation (2026-11-06)

Fixed the **Blank VR · Arcane Hands** starter's upside-down glove mounts: fingertips still follow the controller target ray, but the armored backhand now faces up and the palm faces down. The 180° roll also inverts the thumb X-axis; the tracked controller uses the opposite authored mirrored glove instance to keep each thumb inward without changing the independently editable model starters or skeletons. Trigger/grip gestures, Spell Lab casting, Sheep Tag and other controls remain unchanged. Source checked with a focused 338-patch/71-asset build; exact generated HTML **8,397,373 bytes**, SHA-256 `6c3591a2e2261366de0f96f09517e5f933a770440a8d1b8a782bc8cd1b8f278a`. Physical Quest 2 orientation/fit acceptance remains the owner's test. [Focused checkpoint](docs/VR_GLOVE_ORIENTATION_V11_307.md).

## §E v11.306 · Sheep Tag wolf pursuit cache and simulation diagnostics (2026-11-06)

The owner isolated two distinct stress cases: occasional stutter when **all sheep and all wolves** move, and sustained game-wide slowdown when three wolves switch from attacking maximum houses to pursuing the last surviving sheep. Review of the *effective* `sheep_lanes.js` route resolver identified an overstrict 0.2-unit moving-target cache that could repeat up to nine A* approach tests almost every frame during pursuit. The new shared 0.40–0.56-second cache reuses reachable and blocked approach decisions across both wolf AI and target resolution, with movement and navigation invalidation. Preserves existing v11.256 frame-budgeted sheep evasions, all building/capture rules and WebXR controls. Nerd Stats pages 7/8 and 8/8 report path CPU, cache reuse and the simulation/wall-clock ratio; GPU timing and live Quest acceptance are not claimed. Source sealed at 337 patches / 71 assets / 8,397,357 bytes (SHA-256 `a47415627055cda09f2152e9c6adc311347ed709971e6c0bea1be6bc7195910c`). [Focused checkpoint](docs/SHEEP_PURSUIT_CACHE_V11_306.md).


## §E v11.305 · Whole Hooded Vanguard mesh + UV reconstruction (2026-11-06)

The owner requested a **whole-model sculpt and UV mapping fix together**, not just another face/texture patch. The new character factory replaces the old planar body projection with true front/back radial seam UVs for the torso, tapered arms/legs and swept forearms; builds a soft open hood, cowl and overlapping scarf, two-sided teal cloth, rounded boots, a buckled waist belt, shaped cartilage ears and naturally aligned five-digit hands. The existing successful chest and shoulder surfaces keep their original contour and UVs, gaining closed metal thickness. Retains the improved v11.303 768px face portrait and hair, all eleven dedicated painted color/normal/roughness material families, all **17 native editable part IDs** and previous v11.304 document synchronization. Other Modeler starters, Chat, VR, Sheep Tag and saved projects are unaffected. The owner will determine actual visual quality on Android/Quest. [Full checkpoint](docs/VANGUARD_COMPLETE_MESH_UV_V11_305.md).

## §E v11.304 · Loaded models refresh the open Modeler (deployed)

Loading a saved native model into an already-open Model Atelier now rebuilds its derived mesh scene, mesh list and inspector in place. Previously, the document and JSON could contain every saved part while the old empty viewport and GLB export still contained no meshes. The synchronization follows the effective native/scratch model that was actually rendered, so valid empty scratch documents also clear the previous view correctly.

The existing renderer, canvas, camera, render loop, native document and Undo/Redo history are retained. Stale document-specific selection, component and drag targets are cleared; repeated synchronization of the same rendered document preserves selection and global view preferences. It does not close/reopen Model Atelier or initialize Game. All owner Vanguard releases through v11.303 (image/UV, mesh, mapped PBR and anatomical portrait) and outward Chat-loft lighting are preserved. Focused real-Three scene/list/GLB tests and the exact package seal are recorded in [the checkpoint](docs/MODELER_DOCUMENT_VIEW_SYNC_V11_304.md); the fresh v11.304 browser automatically displayed all 59 parts and exported 59 exact named GLB meshes through the native buttons. Deployment [run 42333988830](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42333988830) succeeded. Hugging Face revision `97345e21b5c240d61e44fda90d806afacc42978a` is RUNNING; both official index and Modeler HTML independently match the verified 8,377,905-byte SHA-256 `c2f005b86f9c6e925272c052d429d8b01139d30cb121af7553d38a61788eac5b` seal (335 patches, 71 assets). Owner-device visual acceptance remains separate.

The complete **Little Crystal Mage** has **59 editable parts**, all authored through embedded §c across66 receipt-backed native model operations. Its newest account save is a durable revision 2, independently cloud-reloaded at 59 parts under the earlier sync candidate. The final v11.304 check used the unchanged native-project file through the ordinary file picker because account resume returned 401 after a later Chat release. It automatically populated59 mesh rows and exported a 232,076-byte editable JSON plus 1,092,072-byte GLB with 59 exact mesh names. No geometry was injected during reload verification.

## §E v11.303 · Anatomical face sculpt + aligned 768px portrait (2026-11-06)

Owner's latest real-device review found the face was still a flat oval with primitive, childlike facial markings. The new Hooded Vanguard starter uses one **continuous 80×144 facial topology** with recessed eye sockets, eyelid/brow ridges, cheekbones, a shaped nose bridge/tip/alar wings, philtrum, lips and chin, together with a purpose-painted **768px UV portrait** featuring detailed blue-gray irises, realistic eyelids, nuanced skin tones, subtle nostrils, brows and lips. The scalp silhouette, hairline and front locks are refitted to reveal the facial work. The **other fourteen mesh geometries stay unchanged**, including improved chest and pauldrons, forearm-aligned hands, scarf and teal coat. All 17 editable IDs, eleven mapped material families, existing saves and unrelated §E studios are preserved. Source/UV/JavaScript tests precede live release; visual quality remains subject to device inspection. See [face sculpt checkpoint](docs/VANGUARD_ANATOMICAL_PORTRAIT_V11_303.md).

## §E v11.302 · Hooded Vanguard UV-consistent material depth (2026-11-06)

Continuing the v11.301 hand/face overhaul, this focused pass leaves **17 editable native meshes and their painted albedo UVs intact**. It adds mobile-friendly **256px tangent-space normal and grayscale roughness maps** for the eleven existing surface families, with shallow height relief drawn where hood/scarf folds, metal embossing, coat borders, hair strands and leather seams logically lie on the UVs. Skin remains nearly smooth; cloth and steel reflect light differently; no photographic concept-art collage is reintroduced. Preserve v11.301 corrected wrists, face, all other model/game starters, §C/VR/Sheep Tag, saved projects and append-only source lineage. Source/geometry integrity and real device visual inspection are separate gates. See [the v11.302 checkpoint](docs/VANGUARD_UV_PBR_RELIEF_V11_302.md).

## §E v11.301 · Stylized face, surface artwork and neutral wrists (2026-11-06)

Owner's Android screenshot of v11.300 showed a distorted face, armour/clothing that looked like pasted magazine photographs, and five-digit hands hanging vertically despite diagonally outstretched forearms. This append-only patch changes **fresh Hooded Vanguard Starter Model construction only**: broadens and smooths the jaw/nose on the continuous head mesh, authors face UV painting at measured forehead/eye/nose/lip coordinates (plain skin around rear longitude), and paints **11 distinct native game-art material maps** for ivory hood/scarf, dark suit, engraved steel, teal coat, leather, gloves, hair and boots. The generated concept art remains the style/palette reference, not a cutout texture pasted onto geometry. The tapered breastplate gains a pointed lower silhouette; both existing five-digit glove meshes rotate **±0.64 rad about their wrists** to follow the forearms in a relaxed A-pose. All 17 editable part identities, historical patches, saved scenes and other §E tools stay unchanged. A focused JS/model/UV/material test and source seal verify engineering correctness; Android/Quest appearance remains owner acceptance. See [v11.301 notes](docs/VANGUARD_STYLIZED_FACE_WRISTS_V11_301.md).

## §E v11.300 · Hooded Vanguard joint mesh + UV rebuild (2026-11-06)

After the owner's front/back Android screenshots exposed mismatched Boba Fett-like hood, rectangular chest armor, extreme coat-tail shapes and still-misaligned image textures, v11.300 redesigns **the underlying mesh contours and their UVs together**. The new starter has a continuous rounded head, layered tapered hair, an arched hood opening with full canopy/back mantle, anatomically fitted neck/chest scarf, contoured tapered breastplate, curved shoulder armor and two-sided draped teal cloth panels. Five-fingered native hands, boots, belt and the other model projects remain intact. All 17 editable parts have explicit UV coordinates matched to the new surface shape and material; textures sample actual pixels from the previously imported generated artwork only in appropriate surface regions, while the rest uses matching dyed fabric/metal/skin. No more arbitrary whole-illustration torso/back wrapping. This remains a **static character** without bird, weapon or complete rig. Owner-device front/side/back visual acceptance still pending. See [v11.300 checkpoint](docs/VANGUARD_MODEL_UV_REBUILD_V11_300.md).

## §E v11.299 · Corrected artwork UV alignment (2026-11-06)

Owner screenshots revealed v11.298 did embed genuine painted image pixels, but used each entire **illustrated concept-sheet cutout** as a full-square material texture. The front face, chest and back therefore showed stretched, mismatched art and white page fragments. The v11.299 successor keeps the same original source image bytes and **17 editable native meshes** but extracts tighter painted surface samples from the existing atlas, recovers the exact pre-v11.298 local UVs, tiles real material pixels per family with mirrored repetition, and reserves frontal face art for the front of the head only (neutral skin on the back). One CanvasTexture per surface material family; no extra decorative geometry, no changes to saved projects. This is a focused image-mapping correction, **not** a perfect high-resolution artist-authored UV bake, and owner Android/Quest visual acceptance remains pending. Details in [the correction checkpoint](docs/VANGUARD_IMAGE_UV_ALIGNMENT_V11_299.md).

## §E v11.298 · Actual generated image pixels mapped to Hooded Vanguard (candidate)

The fresh **Starter Models → Hooded Vanguard · Real Artwork UV** now uses **actual image pixels from the previously generated Hooded Vanguard texture illustration**, not a hand-drawn JavaScript imitation. The artwork was manually cropped into 11 surface regions, resampled into a 512×384 JPEG sheet (4×3 cells of 128×128), SHA-256 verified, and embedded directly into the engine. Each of the 17 native editable meshes gets a UV tile assignment to its corresponding painted face/hair/hood/scarf/uniform/armor/pauldron/teal/leather/glove/boot region. Shared source-color texture replaces v11.297's procedural look; conservative material roughness/metalness remains per part. The exact image checksum, 17-part mapping and unrelated-material fallthrough are verified by a focused native test. Historical saved models, the other starters, §C, VR and Sheep Tag are unchanged. This is still a static character; the image atlas is a **mobile-resolution image sample**, not an artist-retopologized full-resolution UV bake, so device visual acceptance and finer art alignment remain separate.



## §E v11.297 · Hooded Vanguard painted-UV remaster (candidate)

The owner clarified that the generated UV concept sheet should become **a better native character in §E**, not another render. The reference board is not an actual matching UV bake, so the updated **Starter Models → Hooded Vanguard · Painted Remaster** maps hand-composed surface artwork to the *real UV coordinates* of each current mesh: face shading and placed eyes/mouth, brown layered hair, ivory/gold hood, draped white scarf, engraved dark armor, shoulder metal, gray fitted clothing, teal embroidered coat panels, leather, gloves and boots. Eleven cached 384px base-color maps are accompanied by conservative derived tangent-normal and roughness maps. Geometry changes in the same 17 native parts round the face/jaw, create a head-covering hood crown and lower wrap, reshape the paper-bib scarf, soften hair locks, and turn leaf-like coat tails into flowing fabric. No new decorative mesh confetti; existing five-finger gloves remain.

**Boundaries:** This is a new-starter reconstruction, not rewriting saved projects. No actual reference-sheet pixels are claimed as directly UV-baked, and the image itself is not the material file. This remains a static unrigged character without weapon/bird. Source integrity, native loading and owner Android visual acceptance are separate gates. See [the checkpoint](docs/VANGUARD_PAINTED_UV_V11_297.md).


## §E v11.296 · Hooded Vanguard reconstructed from reference (candidate, 2026-11-06)

After owner Android visual inspection exposed an oversized chin/mouth, rounded ear lumps, flat hood, crude hair and absent fingers, the fresh **Starter Models → Hooded Vanguard · Rebuilt Character** factory now constructs a continuous fitted face with subtly sculpted nose, layered hair locks, a wrapping hood plus curved forehead brim, gathered/draped scarf, fitted breastplate, formed shoulder pauldrons, flowing teal coats, narrow belt/boots, and **two separate five-digit glove meshes**. Geometry, proportions and fabric silhouettes are deliberately simplified, while detail is carried by **384px UV-aligned color, normal and roughness maps** per material (skin, hair, hood, scarf, uniform, armor, pauldrons, teal cloth, leather, gloves, boots). Decorative filigree is painted, not assembled from hundreds of meshes. The older v11.291 model generator remains in append-only source history; previously saved models are not rewritten.

This is still a **static character** without a full-body rig, bird or weapon. Source integrity, loaded model and actual owner phone/Quest appearance are separate verification gates. See [the v11.296 reconstruction checkpoint](docs/VANGUARD_REBUILD_V11_296.md).

## §E v11.295 · Correct lighting on Chat-created curved meshes (deployed)

Plain loft meshes authored through §c now present outward-facing triangles and recomputed surface normals to the existing renderer. This corrects the inverted shading that made saved ivory hair and other curved parts catch the cyan backlight from the wrong side. The saved part colors, paths, radii, UVs and transforms remain unchanged.

The repair is limited to plain Chat-authored lofts. Existing textured and styled surfaces keep their established rendering path; Hooded Vanguard's v11.294 loader repair, all model provenance, native editing/history, Chat progress and account saves are preserved. Focused real-Three geometry checks, the existing native character-tool checks and the exact source package seal are recorded in [the checkpoint](docs/CHAT_LOFT_SURFACE_NORMALS_V11_295.md). [Deployment run 42247315758](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42247315758) succeeded. The RUNNING hosted v11.295 HTML and SOURCE receipt match the verified 8,263,130-byte, 326-patch, 71-asset seal. The final 59-part mage was subsequently viewed with corrected surfaces and passed fresh v11.304 import/display/native-export checks; owner-device visual acceptance remains pending.

## §E v11.294 · Hooded Vanguard Starter Models loader correction (2026-11-06)

Targeted hosted mobile Chromium check on v11.293 reproduced the owner's report: Hooded Vanguard generated **14 meshes / 61,476 triangles** correctly, then `loadProject()` threw **`Invalid named socket.`** Native Prism Jester assemblies/sockets had been inherited from the canonical project while all original part IDs and groups had been replaced. New `patches/v11_294_vanguard_socket_loader_fix.py` clears only this starter's obsolete `model.assemblies` graph before loading; its own native geometry, texture maps, and existing model editing path remain intact. Other model starters, the v11.292 Cliff Hand material work, Chat character tools, saved projects, and game/VR flows are unchanged.

Verification gates: exact assembled source SHA/bytes, targeted JS syntax and native hosted load, then owner Android/Quest appearance acceptance. The release is static until a dedicated full-body skeleton is authored.



## §E v11.293 — §c character geometry and visible editor work (candidate)

Negotiated Chat mesh tools add curved lofts, open lathe surfaces and native framing. Reviewed plans support 64 operations, painted between edits with named native progress; snapshots retain the backward-compatible 48-row cap and truthful full totals. Closing Chat, Stop and intervening edits halt subsequent work. Native persistence, scratch authority and history remain in place.

Preserves the latest Cliff Hand, Hooded Vanguard, project picker, XR and particle changes. The paired Chat source also repairs interrupted-stream delivery, grounded no-edit inspection, bounded error reporting and heartbeat CAS retries. Source seal, verification and deployment evidence are recorded in [the checkpoint](docs/CHAT_CHARACTER_TOOLS_V11_293.md). Actual mage construction and owner device acceptance are separate evidence.

## §E v11.292 · Cliff Hand: wrist-only moss and PBR knuckles (2026-11-06)

The owner's real-device gauntlet screenshot showed too much green moss on the palm and fingers, and insufficient knuckle definition. Only the existing **Starter Models → Plain Hand Base · Smooth Cliff Hand** material changes: clean sandstone covers the palm, thumb and fingers; original mossy stone is composited through a feathered mask over the **lowest ~23% of the wrist/gauntlet**. Four knuckle-shaped mineral ridges are drawn into matching albedo, OpenGL normal and AO map regions to suggest raised chiseled rock under light, **not as new 3D objects**. The original local 384px-per-tile source atlas remains unchanged; four lightweight CanvasTextures are derived once when the owner starts this hand. Original textured crack geometry, the single connected gauntlet surface, rig, saved projects and separate **Hooded Vanguard v11.291** remain intact.

A focused test validates the exact mask, four UV knuckle targets and matching PBR channels, plus assembled engine syntax/source seal. Owner phone/Quest visual inspection remains the acceptance test. See `docs/CLIFF_WRIST_MOSS_KNUCKLES_V11_292.md`.


## §E v11.291 · Hooded Vanguard native material-first starter (2026-11-06)

New **Starter Models → Hooded Vanguard · Material Study** recreates the owner's hooded-armored character concept as an original editable male model **without the weapon or bird**. Rather than assembling hundreds of trim objects, the generator produces one continuous male silhouette and dedicated shaped face, hood, hair, scarf, chest armor, pauldrons, coat tails, belt, boots and gloves: **14 editable native mesh entries**. Decorative chest filigree, clothing grain, gold trim, leather and scarf details are drawn onto aligned per-part 256px base-color / normal / roughness UV maps. Coat tails and shoulder armor stay independent for potential future animation.

The first release is **a static visual/modeling study, not a full-body skinned rig**. The engine source and JavaScript are checked through a targeted build; real Android/Quest appearance, export/material persistence, and detailed visual fidelity require owner's acceptance. The previous 121-piece rock hand, updated connected cliff hand, Scorchette and all existing projects remain unchanged.


## §E v11.290 · Smooth Cliff Hand gauntlet load repair and richer rock PBR (2026-11-06)

Owner Android screenshot: **Starter Models → Plain Hand Base · Smooth Cliff Hand** failed before opening after the v11.289 forearm update. The cause was a hardcoded lower-bound assumption: the current v11.217 organic hand closes near **y≈0.85**, but the earlier synthetic test started near y≈0.60. The v11.289 post-process therefore rejected the valid hand under its minimum extension assertion. **v11.290 removes the failing stretch path.** The short, subtly flared stone gauntlet is now included in the same native signed-distance hand surface *before* meshing, producing **one connected rigged topology** with a clean lower rim, smooth wrist transition, original fingers/thumb/palm and no separately modeled crack or rock chunks.

The original owner-provided **384px-per-tile cliff PBR atlas** remains. The material uses stronger tangent-space normal relief (1.12), darker AO crevices (1.28), non-metallic rough sandstone (0.88), subtly warm stone toning and continuous forearm UVs. A focused regression exercises the actual v11.217 anatomy field and the new connected gauntlet field, the mesh/UV contract and material selection, alongside the complete engine's syntax and source-integrity build. It does **not** replace the owner's real phone/Quest visual and rig acceptance. Other starters, saved user projects, Sheep Tag and VR controls remain unchanged. See `docs/CLIFF_GAUNTLET_LOAD_FIX_V11_290.md`.


## §E v11.289 · Short gauntlet forearm on the smooth Cliff Hand (2026-11-05)

Based on the owner's front/back Android screenshots, **Plain Hand Base → Smooth Cliff Hand** now extends the existing connected stone hand into a **short, tapered forearm**, enough to read as a gauntlet without becoming an entire arm. A smooth monotonic geometry remap lengthens only the lower wrist/carpal vertices by approximately **0.74 model units**, with a restrained **9% flare** near the end. Upper palm, thumb and fingers retain their shape. There is still exactly **one rigged native topology mesh**—no new cuffs, chunky stones, cracks, overlays or separate mesh objects. The existing 384px/tile owner rock PBR texture now remaps continuously over the longer forearm. The **17-bone rig** and unrelated model/game starters are preserved. Phone/Quest visual and animation checks remain owner-tested. See `docs/SHORT_CLIFF_GAUNTLET_V11_289.md`.


## §E v11.288 · Smooth Cliff Hand, texture-built stone illusion (2026-11-05)

Following the owner's real-phone screenshots and reference analysis, **Plain Hand Base → Smooth Cliff Hand** now uses **one connected 3D hand topology**, not the v11.287 assembly of 121 separate stone blocks, palm plates, chips and dark 3D crack objects. The original high-quality organic finger/thumb/palm/wrist silhouette and **17-bone rig** are kept. There are no new floating rocks, geometry seams or discrete modeled cracks. All stone faces and separations are drawn directly in the material's color map, OpenGL normal map, roughness and ambient occlusion; sparse moss is baked into the albedo. The original supplied ZIP was used to prepare a **384px-per-map** PBR atlas `assets/cliff-hand/cliff_pbr_atlas_384.jpg` so details stay clearer on phone than in the prior 128px atlas. One continuous X/Y projection maps the texture across the whole connected hand, instead of repeating it separately on 121 shapes.

The `plain-hand-base` template, save behavior and actual rig are preserved; unrelated Rocky Anime Hand, Arcane Gloves, Sheep Tag and user projects are not modified. Targeted assembled source and JavaScript checks are used; owner Moto/Quest real-device visual acceptance remains pending. See `docs/SMOOTH_CLIFF_HAND_V11_288.md`.


## §E v11.287 · Cliff Hand sculpt with owner PBR materials (2026-11-05)

**Plain Hand Base** now opens a native, 17-bone **Cliff Hand** instead of the neutral clay anatomy. The editable hand has complete faceted stone fingers, thumb, wrist, rounded rock volumes and 32 additional small, layered palm/back sandstone slabs. Amber glows are replaced with recessed dark cracks. It preserves the original open/fist animation timeline and starter ID; existing saved scenes and the separate Rocky Anime Hand remain unchanged.

The supplied texture ZIP was used to produce a packed **128px-per-map mobile PBR atlas** at `assets/cliff-hand/cliff_pbr_atlas_128.jpg`: sandstone, moss composite, packed dirt, OpenGL normals, roughness, ambient occlusion, height bump and crack mask. Native `MeshStandardMaterial` now applies those maps to the skinned cliff geometry with per-piece UVs, uv2, rough nonmetallic stone and selective moss. No game spell-growth implementation is implied. See `docs/CLIFF_HAND_SCULPT_PBR_V11_287.md`. Owner phone/Quest visual and rig acceptance pending.

## §E v11.285 · Compact Projects picker and reliable Starter Models (2026-11-05)

The native **Projects → Starter Projects** picker now keeps playable starters under **Starter Games** and editable hand, wolf, sheep-building and other model-only starters under **Starter Models**. This repairs a v11.284 category helper that accidentally depended on the private Chat-host scope, and also covers the picker before Chat mounts. Existing native cards and default selections are moved in place—not cloned or reset.

On phones and touch/desktop-mode browsers, the project picker is now a **compact, scrollable dialog** with smaller cards and persistent category navigation. Its active window is promoted above right-side editor/inspector panels instead of disappearing behind them. No scene, model geometry, Sheep Tag, particle, WebXR, AI Chat or saved-project data migration. Candidate assembly and inline JavaScript syntax verified; real Moto/Quest visual acceptance is still owner-tested.

## §E v11.284 · Plain Hand Base and corrected Starter Models tab (2026-11-05)

Added a separate **Plain Hand Base** Model Atelier starter using one clean, connected five-finger hand mesh with a neutral matte finish and the original **17-bone** open/fist animation. It contains **no armor, glove details, rocks, runes, cuffs or effects**. All previous models—including the weathered Rocky Anime Hand and both Arcane Gloves—remain unchanged. Direct route: `?project=plain-hand-base`.

Repaired the original Starter Games / Starter Models card classifier: legacy category rules missed some later-model IDs. The gallery now moves original model card nodes (including Rocky Anime Hand, Arcane Glove Left, original glove, plain hand and other model-only starters) into **Starter Models**, while true playable games remain in **Starter Games**. Existing card events, scene IDs, project saves and Starter Particles are preserved. See `docs/PLAIN_HAND_STARTER_V11_284.md`. Owner phone/VR acceptance pending.


## §E v11.283 · Weathered Rocky Anime Hand (2026-11-05)

The owner requested a **slightly smoother rock hand** following the fully covered cliff-rock rebuild. On the independent Rocky Anime Hand · Emberstone Starter Model, each solid rock is now gently rounded: the generator shares matching mesh vertices, subdivides faces once, and softens their sharp corners through two restrained surface-smoothing passes. The original 360° rock anatomy, 12 stone finger sections, three thumb sections, closed angular palm, fractured wrist, 25 crisp emissive fault-line parts and editable 17-bone rig are preserved; **no organic glove is exposed**. The 89-part native scene remains individually editable and saveable. Original Arcane Gloves, Quest VR game, Sheep Tag, Mage Spell Lab, other projects and §C remain unchanged. Model test confirmed 64 weathered solids (8,708 vertices and 17,160 triangles); build checksum and visual acceptance are separate. Details: `docs/WEATHERED_ROCK_HAND_V11_283.md`.


## §E v11.282 · Rock Cliff Hand — solid stone anatomy (2026-11-05)

The user's real-phone screenshot showed a smooth glove with separated rock armor rather than a cliff-rock hand. In response the independent Rocky Anime Hand · Emberstone Starter Model has been fully rebuilt: **no visible organic core**, a closed angular palm volume with complete front/back/side rock coverage, thick overlapping stone strata, 12 solid finger stone sections, a fully rock-covered articulated thumb, chipped side silhouette and a broad rooted basalt wrist. Short glowing amber fault lines mark joints and rock cracks. Each element is editable native 3D geometry with existing 17-bone rig and animation. Original Arcane Gloves, VR glove game, Mage Spell Lab, Sheep Tag and saved projects are preserved. Source: `runtime/rock_cliff_hand_v11_282.js`, `patches/v11_282_rock_cliff_hand.py`; evidence and testing: `docs/ROCK_CLIFF_HAND_V11_282.md`. On-device visual acceptance pending.


## §E v11.281 — Rocky Anime Hand · Emberstone (2026-11-05)

Added an **independent Starter Model** in Projects → Starter Models. Based on the generated rocky anime hand reference, it has actual native chiseled low-poly gray-violet rock plates on front/back palm, individual three-section finger stones, a segmented thumb, layered wrist blocks, and glowing amber fracture-line meshes. All parts remain editable in Model Atelier. The verified native 17-bone wrist/palm/finger/thumb rig provides open → fist → open animation. New route: `?project=rocky-anime-hand`. The prior Arcane Gloves, VR casting, Sheep Tag, saved levels and §C are unchanged. See `docs/ROCKY_ANIME_HAND_V11_281.md`. Owner 3D visual acceptance pending.


## §E v11.280 — Mage Spell Lab particle library and VR glove casting (2026-11-05)

**Native catalog:** Starter Particles and Particle Studio now expose all 14 existing engine-native presets plus 18 new editable Mage spell emitters (32 in total). There is a searchable library, individual Add Emitter actions and a one-click 8-spell testing pack; every emission remains under the native 12-emitter validation/undo/save/export path. Fire, ice, electricity, spiral, ring, healing, void and other categories have different emitter behavior.

**Quest VR sandbox:** The v11.279 blank Arcane Gloves starter casts from either tracked Touch controller using that hand's trigger. Both hands have independent equipped spell choices and small readable tracked labels. L3/R3 clicks cycle the spell on that hand only, grip-driven finger poses remain. Cast effects are bounded temporary native point clouds sharing the existing VR render callback; no combat/authority, no extra scene actors and no change to Sheep Tag bindings.

**Scope:** Existing original glove, mirrored glove, saved scenes, original Vortex and its 4-emitter loader, native curve editor and other studios stay intact. This is a visual spellcasting foundation; Quest 2 physical acceptance is pending. See `docs/MAGE_SPELL_LAB_V11_280.md`.


## §E v11.279 — Blank VR starter with dual Arcane Glove hands (2026-11-05)

**Game:** New **Blank VR · Arcane Hands** Starter Game (`?project=blank-vr-hands`) creates a ground-only editable level with no enemies, scenery, or pawn. In Quest immersive VR, the existing rigged glove model attaches to the tracked right controller and a true mirrored copy to the left. Each independently responds to grip (grasp/fist) and trigger (pinch); no hand-tracking claim.

**Model:** **Floating Hand · Arcane Glove (Left)** (`?project=arcane-glove-left`) appears in Starter Models with physically mirrored geometry, thumb alignment, 17 bone pivots, saved animation poses and all gesture presets. Original right glove and saved models remain unchanged.

**Release integrity:** 310 patches, 69 assets, 8,125,233 assembled bytes, SHA-256 `678667a1360fc495366cda34d0e7873042c6763baf92e1a6f766ae2de194f0ed`; targeted source/JS syntax passed. Meta Quest 2 physical rendering, controller offsets and latency require owner acceptance. See `docs/BLANK_VR_ARCANE_HANDS_V11_279.md`.


## §E v11.267 — Continuous galaxy wisps, not stamped smoke (2026-11-04)

**Owner screenshot:** The v11.266 portal now mixes magenta and cyan properly but the textured smoke still reads as clusters of separate stamped leaves, and the long curved filaments are overwhelmed.

**Focused update:** Keep the six purple-rooted half-S energy arms, cyan transitions with purple patches, short inner violet tendrils and magenta center glow. Reduce the sampled smoke count from 72 to 60 per native arm record, shrink random phase/lateral/height/depth offsets, and orient slightly elongated sprites along the projected filament tangent. Blend the owner-derived atlas into a softer feathered low-contrast haze inside the existing fragment shader; strengthen the continuous filament width/opacity slightly for visual hierarchy. Preserve editable Smoke density/arm spread and original slow rotation.

**Performance and protection:** No new emitters, GPU batches, renderers or callbacks. Keep v11.266 JavaScript startup repair, source syntax gate, v11.258 per-emitter containment, v11.265 Sheep Tag house batching/Nerd Stats, saved project data and Quest controls. Reconstruction and Node parse plus full package verification passed; real-device mobile appearance/performance acceptance remains pending.

## §E v11.264 — Purple-origin spectral galaxy and mixed-color tendrils (2026-11-04)

**Reference interpretation:** On the owner-supplied galaxy screenshot, the white-hot center is enveloped by purple/magenta energy. Major arms originate purple and diverge: most long cyan segments grow from purple roots, a main arm stays violet, and other blue-dominant strands (especially the leftward one) retain intermittent purple blotches. Short violet roots fill space between longer arms.

**Implementation:** Branch-specific `se264Profile` transitions now color all six live spiral filaments, their associated atlas-textured smoke puffs, and the separate stars. Add three short, all-purple inner filaments per vortex arm emitter in one batched geometry each, and one purple halo behind the existing core. Purple splotches break up cyan outer lengths rather than dividing the galaxy into monochrome arms. The shared mist buffer uses 72 rather than 54 overlapping, softer smoke samples per color (same number of draw calls), with dynamic projected-tangent orientation.

**Preserved:** Reference-derived 128px atlas, six half-S paths, slow swirl, editable Smoke density/arm spread, native emitter count, renderer/tick, cleanup, editor zoom/timeline, v11.257 TDZ fix, v11.258 faulty-emitter isolation and Sheep Tag/Quest controls. Focused source/package verification passed; owner real-device visual and FPS acceptance remains pending.

## §E v11.263 — Owner-supplied nebula layer texture integrated into live 3D particles (2026-11-04)

**Reference ZIP evidence:** `galaxy_transparent_layers.zip` includes a composite and five alpha-masked passes: `01_Nebula_Smoke.png`, violet/magenta streams, cyan streams, stars/sparks and core glow. RGB channels are essentially identical across PNG passes; transparency masks isolate visual components. They are art/mask sources, not independent volumetric objects or a ready-made 3D game effect.

**Focused implementation:** Four feathered smoke fragments are cropped from the owner-supplied nebula pass and packed into a ~2.5 KB 128×128 grayscale alpha atlas. The atlas is embedded in the v11.263 shader source (no external network asset) and decoded only once. Existing batched camera-facing mist points (54 per native violet/cyan arm emitter) choose tiles across the six short spiral paths. The smoke fragment shader samples the user-derived plume opacity in place of costly procedural per-pixel noise; a soft analytical fallback is used until the image is ready. Puff size is increased but capped to control mobile GPU overdraw.

**Continuity:** The signed core, 3 violet/3 cyan filaments, stars, slow spiral motion, editor timeline and orbit control stay as before. No new native emitters, render loops, 3D scenes, GPU batches or UI panels. Existing Smoke density and Smoke arm spread still work, with emitter-failure isolation, TDZ repair and GPU cleanup preserved. Final visual and performance acceptance requires real mobile/Quest testing.

## §E v11.262 — Galaxy smoke rendered as textured mist, not planar strips (2026-11-04)

**Owner feedback:** Three Moto screenshots at 2:33 PM show that v11.261 has working short half-S violet/cyan filaments, bright central core and animated stars at multiple camera angles and zoom levels, but virtually no visible curling nebula. Flat surface smoke alternated between invisible noise and large colored fan panels in previous attempts.

**Source-level correction:** The six line filaments and native star emitters are preserved. Hide the two planar smoke ribbons per branch and instead add **one** dynamic `THREE.Points` batch (54 soft, irregular, camera-facing clouds per native violet/cyan emitter) with procedurally noise-shaped sprite alpha, slow internal curl, transparent edges, and a wider radius near each arm's outer end. The cloud batch follows the same branch-aware `location` and existing `se223Step` timing; there is no new render loop or native particle-emitter record.

**Performance/cleanup:** One extra GPU draw call per native vortex emitter, no external image/texture requests, static sprite size/seed/color buffers, only dynamic positions. Dispose the new points' geometry and shader material when the emitter is removed. The existing editable, persisted Smoke density and Smoke arm spread values control the mist. Retain first-frame TDZ fix, particle-failure isolation/toast, editor navigation, Sheep Tag and VR controls.

**Acceptance:** Source integrity and generated package must pass before publishing. Real-device graphics quality, GPU performance and camera-angle behavior remain for user verification.

## §E v11.261 — Visible galaxy smoke without flat sheets (2026-11-04)

**Owner device evidence:** At 2:12 PM on Moto, v11.260 displays six stable half-S cyan/violet filaments, bright core, normal stars and progressing timeline, but the nebula smoke is nearly invisible after the overly restrictive masking pass.

**Cause and focused repair:** The noise-cut alpha mask removed too much cloud coverage and the remaining smoke was normal blended against near-black. Keep the same existing two smoke ribbons per galaxy branch, slow motion, project data and camera. Loosen the fractal smoke threshold, retain noise gaps and feathered outer edges, restore additive emissive smoke, slightly widen its outer trailing edge and cap fragment alpha to avoid reintroducing v11.259's translucent fan panels.

**Preservation:** Reuse one WebGL renderer and existing GPU resources. Keep v11.257 TDZ correction, v11.258 emitter-fault containment, native saved/undoable Smoke density, fast viewport controls, Sheep Tag, network code and VR inputs unchanged. The source verifier validates the code; mobile visual acceptance remains with the owner.

## §E v11.260 — Galaxy fan geometry corrected to feathered wisps (2026-11-04)

**Owner visual evidence:** At 2:02 PM on the Moto, v11.259 shows six intact short violet/cyan arms and stars, but widened smoke strips turn into large smooth translucent fan/paddle silhouettes. Editor timeline and viewport are visibly active.

**Root cause and fix:** The previous smoke pass made each planar ribbon too wide and left a nonzero body-opacity floor across most of it. Retain the proven six-arm path and slow spin, but reduce outer strip width, carve broad gaps via layered animated noise, add a faint slender wispy vein and feathered edges, and cap maximum fragment alpha so crossing layers do not form colored solid sheets. No new particles, renderer, shader program, UI panels, or update loops.

**Continuity:** Preserve native saved smoke-density control, v11.257 TDZ repair, v11.258 per-emitter fault isolation, v11.259 static UV uploads and project history; no changes to Sheep Tag, other studios, multiplayer or Quest controls. Build/source verification is separate from real-device visual acceptance.

## §E v11.259 — Galaxy smoke thickness and wispy material (2026-11-04)

**Owner screenshot:** The v11.258 Galaxy Portal now has six clear half-S cyan/violet paths and an active editor preview, but the wispy nebula clouds in the reference are barely visible. Most of the shape still reads as smooth, thin neon paths and isolated glowing points.

**Visual repair:** Retain the short half-S geometry and slow rotation. Enlarge the two existing smoke layers per arm as they travel outward, use a soft fractal-noise alpha field with ragged edges/negative space, and switch the smoke to translucent pigment blending while keeping the fine energy filament additive and rendered above it. The glow retains a fading tip and the luminous star/core emitters remain independent.

**Native control and performance:** Add schema-validated `Smoke density` (0.1–2.0) alongside `Smoke arm spread` and `Starfield density`, with original undo/redo and VFX JSON persistence. Upload static ribbon UV coordinates just once instead of every frame. No added emitters, frame callbacks, renderers, or external GPU assets.

**Preservation:** Keep the v11.257 first-frame TDZ repair, v11.258 per-emitter error toasts, saved projects, Sheep Tag, Quest input, and other workstations. User hands-on mobile comparison is the visual acceptance gate.

## §E v11.258 — Short, slow galaxy wisps and particle fault containment (2026-11-04)

**Reference-matching visual:** The original Astral Vortex drew two long looping rings. This release creates six shorter, half-S curved filaments across alternating violet and cyan arms, with widening irregular smoke layers, embedded small/large stars, softer fading tips and a luminous core.

**Motion:** Remove duplicated spin-curve multiplication, slow global rotation and star trajectories, retain slow internal smoke motion. Avoid recalculating invisible legacy ribbon meshes and reuse the same WebGL renderer; owner device confirmation still required.

**Error containment:** Per-emitter preview guards stop only the particle responsible for a runtime error, display a one-time toast with the emitter and reason, and keep the other emitters and engine tick operating. A final guard prevents particle-frame errors from aborting camera/timeline updates. Invalid saved particle data now produces a visible warning without mutating the saved project.

**Boundaries:** v11.257's first-frame TDZ repair is preserved. Native actor/game data, 12-emitter limit, Sheep Tag, §C and Quest control bindings are unchanged. Deployment and owner real-device acceptance are distinct from source verification.

## §E v11.257 — Confirmed Astral Vortex first-frame freeze repair (2026-11-04)

**Owner reproduction:** Particle Studio camera and timeline animate normally until the Astral Vortex starter is loaded. On adding the violet and cyan arms, native rendering and the timeline playhead stop together while independent DOM modifier controls remain responsive.

**Confirmed root cause:** The v11.251 nebula ribbon function `writeMesh` defines `normalAt` with outer band parameter `b`. Inside `normalAt`, a local declaration `const b=location(...,b.index)` shadows the outer band and tries to read the new binding before initialization. JavaScript throws `ReferenceError: Cannot access 'b' before initialization` on the first violet/cyan emitter frame, aborting the shared animation callback. This is a code exception, not evidence of particle count or GPU overload.

**Minimal repair:** A new append-only patch changes only that inner sample name to `nextPoint`, retaining the correct outer band's `b.index`. No modifications to saved emitters, galaxy geometry design, shader effects, the viewport's input mapping, Sheep Tag, Quest controls, or the one renderer.

**Verified:** Focused regression executed the sealed native particle core plus the real v11.248/249/251 effect modules against the Three.js library. The historical original failed for both vortex arms on the first frame; the corrected generated source passed first-step tests for violet, cyan, core and sparks, then completed 90 particle frames with four live emitter records and two nebula arms. Full release packaging and owner phone acceptance are separate gates.


## §E v11.256 — Galaxy preview continuity, AI sheep route smoothing and Quest building rays (2026-11-04)

**Owner symptoms:** Adding a galaxy particle can leave Particle Studio's rendered preview empty and its camera nonresponsive. Living AI sheep correlate with intermittent gameplay frame spikes; once all AI sheep are captured the spikes stop. In Quest Play, equipping a building produces a sheep-centered extra beam and limits ghost movement to near the sheep; VR menu cursor is visually behind its labels/options.

**Particle correction:** The authoring chamber's previous frame invalidation checked `currentProject !== state.project`. Authoring transactions can replace the project object without changing the actual Three.js scene, closing the layer-25 chamber and restoring the game camera. Rebind the chamber to the edited project and dispose stale live emitter GPU resources without closing its camera; reopen on a legitimate scene/camera swap. Recovery is in the existing engine tick.

**Sheep AI:** The danger-escape bot previously called A* for each progressively better candidate, sometimes repeatedly per living sheep. Keep the newer AI's full sheep/wolf path scoring and escape candidates. Evaluate at most two candidate routes across all living sheep per frame, continuing each bot's pending plan over subsequent ticks. This distributes expensive A* searches instead of concentrating many on a single XR frame. No behavior changes to controlled sheep, wolves, authoritative host, collisions, or nav rules.

**XR controller ray:** Disable the virtual short-range forward projection and secondary synthetic building beam. Use the physical right controller orientation to intersect actual terrain out to the playable map bounds, with no arbitrary radius around the sheep. A ghost appears only on actual ground, never in sky or in front of a menu; the normal world ray stays free. Modal A/X wheel and VR radial rays/reticles use foreground render ordering above menus with existing hit testing.

**Validation:** Append-only extension of the existing one-renderer source. Full source reconstruction, syntax, package integrity and on-device acceptance recorded separately. Do not turn on broad browser/VR test suites by default.


## §E v11.255 — Particle viewport input and dedicated camera ownership (2026-11-04)

**Owner regression:** After v11.254, the Particle Studio scene still did not respond to touch/drag/zoom, and native particles were not visible despite the Astral Vortex emitter tree loading. Earlier panel-only fixes did not address the actual render-camera conflict.

**Verified source causes:** The actual visible `#se249Root .se249-stage` was `pointer-events:none`, while an independent invisible, shell-wide shield handled drag/wheel input elsewhere. The base engine also ran Game OrbitControls **after** the Particle Chamber frame set the existing camera position/orientation, potentially overriding the chamber view every frame.

**Focused fix:** In Particle Studio only, make the visible viewport the direct pointer/touch target, use the existing stage camera API for one-pointer orbit/pan/vertical zoom, two-pointer pinch zoom and wheel zoom, and stop Game OrbitControls overwriting the native camera while the chamber is active. The existing Perspective, Focus, +/− zoom and tool buttons keep their native actions; the old shell-wide shield is not hit-testable in the Particle workspace. Preview can open the native chamber on demand if lazy mounting delayed it. A live viewport status line reports chamber readiness, preview state, active particle count and zoom distance to diagnose further reports.

**Preservation:** Append-only 286-patch extension. Keep one existing Three.js scene/renderer/engine tick, original emitter project data and limits, source lineage, §C integration, model+particle stress sliders, Sheep Tag Play, game camera outside Particle Studio, Quest XR controllers and game physics. Focused source reconstruction succeeded; owner Moto and Quest real-device acceptance remains outstanding.


## §E v11.254 — Particle Studio docks, VFX preview and camera zoom (2026-11-04)

**Owner device screenshot:** Particle Studio displays extraneous purple vertical handles *inside* the Project pane and central viewport, side panes do not expand/collapse or drag-resize, Astral Vortex is absent, and viewport zoom appears unresponsive. Mobile data speed had recovered after a connection reset; these layout problems are independently grounded in the editor source.

**Dock fix:** The extra handles are the Materials studio's `se251-split-materials-*` elements, incorrectly visible while the shared `se225Shell` is showing Particle Studio. Hide and disable pointer events on these only in the particles workspace. When the v11.249 Particle Studio root mounts asynchronously, explicitly invoke v11.250's existing native dock initializer so its own side and bottom splitters, collapse buttons, persisted layout state and drag handlers are actually installed.

**VFX/camera fix:** Keep Game Editor preview teardown from stopping an active standalone Particle Chamber preview. Allow edit-mode chamber particles to run even if the global game simulation was paused; dedicated Particle Preview/Stop still work normally. After opening the chamber, refresh its controls, apply zoom +/- immediately to its original camera, and expose camera distance for focused diagnostics.

**Boundaries:** Native editor-only fix, 285 source patches, one unchanged WebGL renderer. Preserve the native validated 12-emitter library, §E model/particle stress sliders, saved scenes, Sheep Tag runtime, multiplayer, physics, Quest controller mappings, and source history. Focused source integrity passed; physical phone/VR acceptance pending. The editor thumbnail is not the live effect; the actual preview is in the 3D chamber.


## §E v11.253 — Release dialog startup responsiveness hotfix (2026-11-04)

**Owner report:** The engine appears to load, opens the new-updates dialog, then becomes unresponsive; Continue and other page controls cannot be activated. This is a startup regression, not a measured particle-performance problem.

**Fix:** The v11.251 shared-editor MutationObserver previously re-initialized workstation layouts on any page childList change, including the textContent mutations produced by its own sync method. It now initializes only on relevant Model Atelier/Materials/Particle Studio workspace mounts. The v11.252 diagnostic panel observer is similarly mount-scoped; its animation-frame measurement loop stays idle during the release notes dialog and when no supported editor is open.

**Preservation:** This is an append-only v11.253 patch. The native release-notes Continue button, default game/VR workspace, saved projects, native particles, §E Model Atelier, Sheep Tag gameplay, physics and controller mappings remain unchanged. User Moto / Quest on-device responsiveness acceptance pending.

**Release integrity:** 284 ordered patches; the authoritative generated HTML byte count and SHA-256 are in `source-manifest.json`. Focused source reconstruction and startup observer checks passed; real-device acceptance pending.


## §E v11.252 — Model + Particle Stress Test Modifiers (2026-11-04)

**Owner request:** Add sliders and numeric modifiers inside the actual Model Atelier and Particle Studio to measure how far real geometry and active particle counts can be pushed. No automatic or hidden stress load.

**Model:** Collapsible Model Geometry Stress Test in the native right inspector. Slider and exact numeric entry request 100–1,000,000 triangles. **Apply load** generates a temporary indexed high-poly sphere inside the already-running Model Atelier renderer, reports actual produced triangles and viewport render calls. It does not add an authored part, change model topology, or enter model save/Undo history.

**Particles:** Collapsible Particle Stress Test in Particle Studio's right inspector, with 100–1,000,000 selectable live particles. **Apply load** creates a disposable, animated THREE.Points / BufferGeometry test cloud in the existing isolated Particle Chamber layer 25; the typed position buffer is updated each frame. This is distinct from saved native emitters, whose validated normal 96-per-emitter / 576-total runtime limits remain unchanged.

**Control and instrumentation:** Explicit Apply and Stop, resource disposal on stop/workspace exit/visibility loss, current actual count, approximate requestAnimationFrame FPS and frame time. These are whole-page animation-frame readings, not GPU timing metrics. Extremely high loads are *intentionally* capable of stalling a weak device; movement of the slider itself never allocates giant geometry. Tests do not change Sheep Tag Play, radial menus, VR controls, scene files, network authority or physics.

**Source receipt:** v11.252 has 283 ordered patches; generated HTML **8,003,675 bytes**, SHA-256 `f0368006687eb8d588cce4e999e4bd1728701b45760b236d6b8797c9d6628c8b`. Focused JavaScript syntax and full patched-source integrity succeeded; real Moto G Power / Quest 2 acceptance remains with the owner.


## §E v11.251 · Upright Galaxy Nebula + native editable curves + unified studios (2026-11-04)

Owner reference comparison: previous Astral Vortex looked like horizontal rings. This release changes its 3D orientation to a lifted upright spiral and includes **one thin tapering luminous filament, two outward-widening jagged noise-based smoke bands, and 44 large/small independently animated stars on each of the two colored arms**, using existing Three.js renderer and native engine tick. Saved emitter locations are untouched; the new stage camera targets the lifted visible effect. New validated `nebulaSpread` and `starDensity` controls live under the native Forces inspector.

The bottom **Timeline** has five actual clickable lanes: Emission, Size, Opacity, Color and Rotation. **Curves** now has a five-point direct-manipulation editor with keyboard and numeric input. Edits persist to the native `swyrl-particle-studio-v1` JSON through the normal `se223Update` mutation/Undo/Redo path; old emitters receive backward-compatible curve defaults. The old every-frame emitter-row redraw no longer overrides the new animation tracks. This is a five-point curve editor, not arbitrary keyframe insertion or audio-synchronized FX.

All four studios now share a consistent dark-violet visual language. Modeling and Materials gain native-data left-side asset hierarchies, central previews, right native inspectors, mouse/Quest-pointer panel resizing, independent collapse/restore controls, and Desktop/VR/Compact selection. Game Engine retains its existing native panel architecture and gains matching color/tool styling; no duplicated game renderer or control loop. Source is append-only (282 patches), sealed HTML **7,990,559 bytes**, SHA256 `aa0e0d0e0bb827c2d28d2cf2ab476ca4ebc18582e11e2557b65b837dfca97337`. Owner real phone/Quest acceptance is pending.

## §E v11.250 — True desktop/VR Particle Studio docks and soft vortex (2026-11-04)

**Owner test feedback:** The previous 1080px/coarse-pointer CSS treated Chrome "Desktop site" and Quest browser as mobile, stacking Project and modifiers into huge bottom panels. This release uses automatic Compact only below 700 CSS pixels plus a visible **Auto / Desktop-Quest / Compact** override. Desktop mode shows the Project/Assets tree at left, live VFX viewport in the center and native Properties/Emission/Forces/Material modifiers at right. Left and right separators drag horizontally, bottom Timeline separator drags vertically, each dock has a collapse/restore button, and modifier/tree sections keep native individual accordion controls with expand-all/collapse-all. Preferences persist locally when browser storage permits.

The selected Astral Vortex now uses feathered GPU shader ribbons with consistent segment normals instead of segmented neon rings; selected four-emitter starter groups are preview-isolated even after repeated loads. The lower Timeline has selected-emitter-derived Emission, Size, Opacity, Color and Rotation profiles that open real modifiers; **no keyframe editor or arbitrary extra renderer is implied**. Native project data and Quest gameplay are preserved. Sealed release source: 281 patches, 7,923,641 HTML bytes, SHA256 `f8d4f6df5a2e64fe8ef200c631557b960f5d4ab197fdfb47b39e58b23cf58954`. Owner real-device acceptance is pending.

## §E v11.249 — Native Particle Editor workstation

Full purple/cyan editor workspace inspired by the owner-approved concept: Project/Assets tree, interactive camera rail, native preview, tabbed editable modifiers and a live Timeline/Curves/Output dock. Astral Vortex adds paired dynamic 3D ribbon meshes, editable vortex spin/pull/glow/tilt parameters and existing four native emitter layers. Responsive one-at-a-time mobile docks keep the 3D preview accessible; original renderer, project save, Sheep Tag, modeler and VR controls are retained. Source: 280 ordered patches; owner Moto G Power/Quest 2 acceptance pending.

## §E v11.247 — Optional scene-editor live previews

Game Engine's compact ✦ Preview panel lets creators enable/disable authored particle effects independently of Play mode. The authored cinematic Storyboard episode also has a reversible looping preview that restores the editor camera when stopped. Preview does not change saved scene data or add a second WebGL loop. Current source: 278 patches, 7,810,723 bytes, SHA-256 `0069237edcb5f32d53a349caeb7505cc9fd6466f389def849ed442e8b30cfbb4`; owner phone/Quest acceptance pending.



## §E v11.244 — Sheep Tag menu/grass and removal performance (2026-11-03)

**Owner observations:** Large blurred rectangle behind the game menu, flat meadow grass, frame hitches on sheep capture and house removal.

**Correction:** Constrain menu backdrop to title card, bake sparse natural meadow sprigs without more VR geometry, hide removed runtime houses instantly and dispose their resources across idle slices, coalesce capture navigation invalidation and stagger non-player path recalculation. Preserve roads, VR controls, multiplayer authority, Project Studio, Particle Studio, save data and older release lineage. Owner phone and Quest 2 visual/lag acceptance pending.


## §E v11.242 — Natural Sheep Tag grass instead of square tiled camouflage (2026-11-03)

**Owner screenshot:** On Moto G Power, the newly published v11.241 grass showed obvious bright/dark square patches, even where authored meadow terrain should be smooth. The small 128×128 generated swatch was repeated 16×16 and its saturated colors replaced 75% of the original vegetation — visually unacceptable.

**Targeted correction:** The append-only `patches/v11_242_natural_grass_blend.py` preserves the authored meadow/Wildwood colors and their roads, while applying only a low-contrast, luminance-centered grass detail variation to green vegetation. Reduce swatch repeats from 16 to 8 and lower normal strength from 0.24 to 0.07. Preserve original roughness/normal material channels, renderer, Sheep Tag collisions, build rules, controls, fog, Quest headturn repairs and the independent Particle Studio.

**Owner acceptance:** New grass must be reviewed on phone and Quest 2; this source fix does not claim pixel-perfect seam removal or real-world ground photogrammetry.


## §E v11.241 — Sheep Tag grass PBR (2026-11-03)

**Owner asset:** The grass generated in chat is a packaged, verified green WebP source. Sheep Tag's `stMeadowGround` and `MoonbellWildwoodGround` use a native standard material with composed grass color, matching calculated tangent normal and matte roughness maps. Compose only onto vegetation areas, retaining roads, sanctuary and the existing biomes.

**Quest performance:** One-time map preparation, 16 tile repeats, subtle normal strength, mipmaps, Quest texture budget 1024px, desktop Wildwood 2048px. Approximate normal/roughness maps are computed from color luminance (not independent photogrammetry). No VR controller mapping, collision, sheep/house/wolf movement, fog-of-war, previous head-turn fix or Particle Studio changes.

**Lineage:** Append-only `patches/v11_241_sheep_grass_pbr.py` after v11.240 Particle Authoring Chamber; source-manifest/source receipt carries exact artifact hash. Quest 2 real-device visual acceptance pending.




## §E v11.239 — Quest Sheep Tag fast-head-turn frame budget (2026-11-03)

**Owner Quest 2 finding:** After v11.238, rapid head turns still reveal a hard black edge in the right side of the captured immersive view, with sporadic background stutter. The image alone cannot distinguish compositor reprojection, one-eye mirror clipping or missed application frames.

**Measured source hotspot:** The original v11.181 native VR entrypoint kept recursively ray-intersecting every authored actor's mesh for *both controllers every XR frame* even during Sheep Tag, where v11.192+ already owns native gamepad and build targeting. v11.239 skips only this redundant gameplay actor-triangle raycast while preserving the EXIT VR target and editor actor selection outside gameplay. The existing rendering, input, collision, camera and tracking systems remain unchanged.

**Diagnostics and source receipt:** `SWYRL_ENGINE_QUEST_HEADTURN_239.diagnose()` reports frame callback gaps and the number of redundant game raycasts avoided, separately counting gaps when §E's circular radial is open. **270 ordered patches, 68 unchanged assets, 7,763,865 generated HTML bytes, SHA-256 `684bb107e5f88a011d6ad71f0f86479a6138de5b315a78b1fe13e764be55d57c`.** Native Quest hardware performance acceptance is still required. v11.238 layout and menu stabilization stay intact; experimental stereo/camera PRs #362/#363 remain excluded. Source: `docs/QUEST_FAST_HEADTURN_RAYCAST_V11_239.md`.

## §E v11.238 — Quest radial-menu stability and browser studio controls (2026-11-03)

**Quest 2 owner evidence:** Immersive Sheep Tag is responsive with natural head turning until its **VIEW / BACK / FORWARD / TACTICAL** circular menu opens; the menu then triggers a lag spiral and sometimes disappears. Quest Browser's floating 2D Game Engine and Model Atelier windows overlap menu/tool controls.

**Runtime correction:** A slow application-owned XR callback (170–650 ms) while its radial remains open and the XR session is still visible no longer gets mistaken for a lost Meta OS overlay event. Genuine native Meta blur/hidden and longer interruptions retain existing focus protection. The native radial reuses same-frame ray hits and label textures between pages, disposing the cached textures on XR exit. No camera reference-space, physical HMD tracking, gameplay movement, fog/visibility, or model geometry changes.

**Quest Browser workspace:** The four native studio tabs remain in a compact scroll lane. Existing Game Engine toolbar controls move into a **Controls** drawer. Model Atelier preserves the original **Close**, with the other existing header controls under **Model actions** and its previous side tool rail under **Edit tools** to avoid covering the Wolf Motion inspector. Existing DOM controls and handlers are reused; opting out of Quest UI restores their original arrangement. Meta OS browser windows themselves are unaffected.

**Verified source:** 269 ordered patches, 68 packaged assets, **7,759,927 bytes** HTML, SHA-256 `b732a8868cd74ead21e085365d6c3004f5e71e63a9cfd473ae676b955179e13c`. Owner headset UX and long-run FPS confirmation pending. Relevant files: `patches/v11_238_quest_radial_workspace_comfort.py`, `docs/QUEST_RADIAL_WORKSPACE_V11_238.md`. Other experimental Quest PRs #362 and #363 are not included.

## §E v11.236 — Complete sheep houses, steadier Wolf animations and organized starters

**Sheep house models:** Closed front and rear triangular attic walls and an editable interior floor now complete the Thatched Hut, Cottage, Barn and Ram House starter models. The Free Shelter intentionally stays open.

**Astra Wolf modeling:** Nose, cheek ruff and smile details follow the skull during head animation. Two new preview checkboxes in Wolf Motion—**In place (lock root height)** and **Steady torso**—reduce walking/running body bob and rocking without overwriting animation clips or changing gameplay.

**Projects:** Starter Projects now has separate **Starter Games** and **Starter Models** tabs; My Projects and all default-selection checkboxes remain intact.

Focused 390px mobile browser acceptance passed; physical Moto/Quest testing is pending. Verified source: 268 patches, 68 existing media assets, 7,735,923 HTML bytes, SHA-256 `02056c0d0ff3722b503a03d6fe31ebfc4a99adbdeb2ba132b58d1ba447d105ae`. Existing saved custom model files are not rewritten.

## §E v11.235 — Astra Wolf motion and animation tools

The native Wolf Rig & Motion controls now appear when tapping **Motion** in Model Atelier: clip selector, Play/Stop, playhead, bone pose controls, and **Set keyframe** beside Play on mobile. Wolf bone changes invalidate the existing HD render loop, so animations become visible during playback without moving the camera. The anatomical rig also uses more appropriate head, elbow, hock, limb and fur weights to reduce overstretching. The focused Android-width browser regression passed and reproduced a changing render without camera input. Other saved models, studios, Sheep Tag gameplay and the §C host remain intact. Source: 267 ordered patches, 68 media assets, 7,729,335 HTML bytes, SHA-256 `446edd4f0d7ff1fc8d59216035eef315159437bc70952457203e9a266ce728a5`. Physical Moto/Quest animation quality acceptance remains pending.

## §E v11.233 — §C native Material, Particle and Rig Studio commands (source candidate)

**New native host bridge:** The existing paired Chat side panel now advertises versioned, live-context Studio Commands v1 only in the correct studio tab. Supported operations are material create/edit/assign-to-scene-actor, particle emitter create/edit, existing hand/wolf bone pose, and animation keyframe save. Each is a bounded **single operation**, validated by both Chat server and native host against exact IDs, current project/studio/edit mode, and approved through the existing immutable design-preview/consent/receipt flow. The native material/particle transaction owners, Model Atelier rig storage, Sheep Tag gameplay and one WebGL renderer remain authoritative. No arbitrary JS, file imports, material-to-modeler-parts application, new hand-tracking capture, or code-based auto-rig generation is added.

**Measured and sealed candidate:** v11.233, 265 ordered patches, 68 unchanged assets, **7,725,488 bytes** HTML, SHA-256 `936e49ec155d091a8e0e651a6043713554e6ac5c776a7b6fec45884c2967b34c`. Candidate source reconstruction passed in GitHub Actions; full release-package/source verification, Chat-server promotion, HF deployment and owner Moto/Quest physical acceptance are separate pending gates. The prior v11.232 workspace-start fix is preserved.


## §E v11.232 — Model starters now switch to Modeling

The five Sheep Tag houses, Astra wolf and other native model starter cards now open the Modeling workspace and show their 3D meshes instead of leaving Game Engine selected with an empty World Ground scene. Model Atelier is opened once after data/rig loading; the native editor and tools are visible. Game Engine still boots first on the main page. Focused mobile browser checks passed: Ram House (60 parts), Astra Wolf (108 parts and 10 clips) and Blank Model (1 part). Verified source: 264 patches, 7,714,177 bytes, SHA-256 `a5f840685f618872d69b3e1dc1e197e496e68d2500bfb46008883bfb5c6df9d9`. Owner phone and Quest acceptance pending.

## §E v11.231 — Sheep house models now auto-fit the camera

The five editable Sheep Tag house starters now use the Model Atelier's real mesh-bounds camera for full-building front, side, top and three-quarter viewing. This fixes scenes that loaded correctly but looked invisible or massively zoomed-in on mobile. Focused 390px browser checks proved each complete house fits in the viewport; all old models, saved projects, Wolf rig and Sheep Tag match rules are preserved. Verified release: **263 ordered patches**, **7,713,229 bytes**, SHA-256 `0e960a32760f081f20bfb8e8ed1cd61cf3a0eec8d1f5e583b865311d2bd6e4d0`. Owner Moto G Power and Quest acceptance remains pending.

## §E v11.230 — Wolf Model first-load rig repair (2026-11-02)

Fixed the active Astra Wolf Model starter loader, which had bypassed the rig initialization and relied on a second costly editor close/reopen. Wolf Model now receives the same 14-joint rig, ten motion clips and editable face details *before its first modeler render*, with the Wolf Rig & Motion controls available immediately. The sheep-game wolf, other starters and existing saved projects are untouched. Verified source: **262 ordered patches**, **7,712,134 HTML bytes**, SHA-256 `f22f0ab28b072d6a60498ea82111e62212f2ffd71ba05a175a80a3750e689ac5`. Android/Quest acceptance pending. See `docs/WOLF_MODEL_SINGLE_PASS_LOAD_V11_230.md`.

## §E v11.229 — Sheep house native model loading repaired

All five sheep house starters now load into Model Atelier as editable 3D geometry. A focused mobile-browser regression confirmed the Free Shelter (18 parts), Thatched Hut (59), Cozy Cottage (68), Flock Barn (37) and Ram House (60), using the real modeler project loader. The repair corrects invalid rotation/material fields, window trim colors and inherited character sockets. Sheep Tag gameplay, other editor studios and previously saved models remain unchanged. Android/Quest device visual approval is owner-tested.

## §E v11.228 — Game Engine GUI / Menu Setup sub-tab (2026-11-02)

Inside **Game Engine**, compact **Scene | GUI / Menus** child tabs and a **Show/Hide UI** editor-preview switch organize existing menus without adding another top-level studio. The new inspector reuses Sheep Tag's editable Main Menu UI (title, subtitle, Start button, color, cinematic orbit) and adds up to 24 validated project-native label/button/panel layers with editable content, colors, viewport-percent layout, and safe Play actions (Start, Next, Stop, display only). Per-layer eye visibility and Show all/Hide all are editor-only; each layer has an independent saved Show in Play flag. GUI definitions participate in project save/export, authored level capture and native Undo/Redo; no new renderer or Quest input loop.

**Verified source:** v11.228, **260 ordered patches**, **68 packaged assets**, **7,712,043 generated HTML bytes**, SHA-256 `16b6e24f471b79a1a9c6ec7ce7df2565dfeb5de8a0c527196e7b9008a907ca2d`. One-shot actual source build, JavaScript syntax, and focused GUI save/restore/visibility tests passed. Device UI acceptance on Moto/Quest is pending. Code: `runtime/game_gui_menu_subtab_v11_228.js`, `.css`, append-only `patches/v11_228_game_gui_menu_subtab.py`.

## §E v11.226 — Five editable Sheep Tag house model starters

Projects now includes separate native 3D Model Atelier starters for the **Free Sheep Shelter**, **Thatched Starter Hut**, **Cozy Sheep Cottage**, **Flock Barn** and **Ram House**, based on the cozy farm/sheep visual concept. These projects expose independent editable mesh groups and can be viewed from front, side and top. Sheep Tag's current in-match building rules remain unchanged; owner mobile and VR visual approval is pending. Full details: `docs/SHEEP_BUILDING_MODEL_STARTERS_V11_226.md` in the GitHub source.

## §E v11.225 — Material & Texture Studio + Four Workspace Tabs (2026-11-02)

**Native top workspaces:** Game Engine | Modeling | Particle Studio | Materials & Textures. The existing two editor tabs remain intact, Particle Studio now has its own native tab and full-screen preview workspace, and the new Material & Texture Studio has its own tab with the same live §E Three.js scene (no second rendering loop). The game viewport toolbar's ✨ Particles shortcut enters the Particle Studio tab. Tab switching preserves unsaved scene/model data and native controls.

**Material authoring:** Create/duplicate/delete up to 12 project-native PBR materials using ten starters (steel, gold, wood, stone, brick, fabric, leather, arcane glow, glass and ceramic). Edit roughness, metalness, opacity, emissive color/glow, base/accent colors, seeded procedural detail, UV tiling and texture pattern. Generate eight 256×256 procedural/paintable patterns, draw bounded brush strokes (including Undo/Clear), import PNG/JPEG under strict limits, and export PNG textures or validated JSON material libraries. Apply authored materials to specific scene actors, preview with a native rotating 3D sample sphere, and restore the exact original actor material. Scene assignments and material definitions persist in project snapshots, native Undo/Redo and level records. GPU resources are temporary and disposed on changes. User projects, §C, Sheep Tag authority, native glove rigs and previous Particle Studio VFX data are preserved.

**Exact source receipt:** §wyrl§ Engine **v11.225**, **257 ordered patches**, **68 unchanged packaged assets**, **7,642,539 generated HTML bytes**, SHA-256 `7407ca6b520912437c280035c1f4258f5b1e7a8ab577f3701b855db26f7bf3a7`. Focused generated-JS syntax, procedural texture, material validation, painting, actor assignment/restore, JSON import and project-switch tests passed. Physical Android/Quest 2 layout and rendering remain owner acceptance pending; material-to-Model Atelier part assignment is not yet exposed (PNG/JSON asset export is available).

Read `docs/MATERIAL_TEXTURE_STUDIO_V11_225.md` for workflow, source contracts and limits.

## §E v11.224 — Native Particle Studio · Creator, Editor & reusable 3D VFX (2026-11-02)

Following the independently preserved v11.223 Arcane Glove fist/wrist-wave work, §E adds **Particle Studio** to the main Game Editor via **✨ Particles**. Ten reusable effects (Arcane Motes, Flame, Smoke, Sparks, Snow, Rain, Healing Wisps, Building Magic, Portal and Confetti) support creation, duplication, deletion, live preview, burst tests, camera placement and attachment to selected native actors. Edit continuous/one-shot modes, four spawn shapes, rate, burst count, lifetime, motion direction/speed/spread, gravity, drag, 3D position, radius, particle size, both colors and blend mode. Native `currentProject.particleStudio` metadata participates in Save, Undo/Redo, project level snapshots, and validated JSON import/export. Visual motes render on the existing flat/XR frame and never enter authored scene actors, collision or LAN authority; max 12 emitters, 96 motes per emitter and 576 global. Imported project VFX is validated before use. **v11.224 exact source:** 256 ordered patches, 68 preserved assets, **7,590,193 HTML bytes**, SHA-256 `29583040d840e7bd328d7417d0abb8a0d0c8cebf5a6db2db8014b602bdfb6a54`. Focused source build, generated JavaScript syntax, imported-data guard and emitter lifecycle mock test PASS. Dedicated publish and owner's phone/Quest 2 visual approval remain separate gates. Details: `docs/PARTICLE_STUDIO_V11_224.md`.

## §E v11.223 — Tighter Fist & Wrist-Twist Wave (2026-11-02)

Owner phone testing requested deeper finger closure, a tighter thumb tuck, and an animated wave that twists and swings the wrist rather than showing one fixed rotated palm. v11.223 tightens MCP/PIP/DIP curls in all four fingers, tucks the opposable thumb across them, and authors an eight-key 2.2-second wrist-driven wave with alternating yaw/roll, palm follow-through and finger flutter. All previously saved clips, native glove geometry, thumb helix, Clover, Sheep Tag, other starters and Quest input remain intact. Focused source/17-bone motion math passed; owner phone acceptance is pending. **v11.223:** 255 ordered patches, 68 packaged assets, 7,551,989 HTML bytes, SHA-256 `db352ebd9c49735b4ec5df884ce2f855d412a995138e7bb987bdeb808c296b4e`. Details: `docs/FIST_CLENCH_WRIST_WAVE_V11_223.md`.

## §E v11.222 — Clover sheep animations and Sheep Tag construction sparkles (2026-11-02)

Six common Clover joint animation clips — Idle, Graze, Walk, Trot, Build and Celebrate — now come from one pure joint-pose library. The standalone **Projects → Clover · Meadow Sheep** starter includes timed, exportable model JSON joint keys and a non-destructive, touch-friendly preview selector; the **Sheep Tag** starter reuses the same six poses on the existing head/tail/four-leg hierarchy. On entering Sheep Tag Play, sheep get short aqua spawning sparkles. A house under genuine construction sheds warm amber motes and completes with a teal flourish, with a short owner-sheep celebration. Effects only read the host/guest's displayed construction progress and do not change game authority, collisions, placement, resources or LAN state. All particles use a shared 96-mote point cloud and are disposed at Stop; no additional animation/render loop.

**Exact source:** §wyrl§ Engine **v11.222**, **254 ordered patches**, **68 existing assets**, **7,550,334 generated HTML bytes**, SHA-256 `27876c460d3c824f23d6628d3207693eb0d2194db9091a72c743122a95e17a35`. Changed-only source checks and assembled HTML JavaScript syntax passed on the dedicated branch. See `docs/CLOVER_ANIMATION_VFX_V11_222.md`. Physical Android/Quest 2 animation, effects and performance remain **owner acceptance pending**; source build alone is not live evidence.

## §E v11.221 — Opposable Thumb and 14 Hand Gestures (2026-11-02)

Owner phone screenshots confirmed v11.220 finger skinning and keyframes worked, but the thumb needed proper opposition, a better bend and more gestures. v11.221 keeps the same 17-bone glove and native geometry, improves thumb CMC/MCP/IP movement and capsule skin weights around the violet helix, adds 14 distinct gestures (Open, Relaxed, Fist, Point, Pinch, OK, Thumbs Up, Peace, Horns, ILY, Shaka, Wave, Grasp and Finger Gun), introduces touch-friendly Opposition/Flex sliders and one-tap 3-key gesture clips. Existing saves and other starters remain intact. Candidate syntax and 14-gesture/near-contact math build checks passed. **v11.221**: 253 ordered patches, 68 assets, 7,535,801 HTML bytes, SHA-256 `1f7f32229504110c2d6d758bf3cadf3c0f048630ad8a79ffdbffc4bac8431f90`. Read `docs/THUMB_GESTURES_V11_221.md`.

## §E v11.220 — Native Hand Rigging, Posing & Animation Studio (2026-11-02)

The Floating Hand · Arcane Glove now creates a real 17-joint parented hand skeleton (wrist, palm, four × MCP/PIP/DIP, thumb CMC/MCP/IP), with four-influence per-vertex skinning across the continuous glove and separate hardware using native THREE.SkinnedMesh. A collapsible touch-friendly Rig · Pose · Animate studio adds per-bone X/Y/Z rotation, skeleton view, Open/Fist/Point/Pinch presets, editable timeline keys, play/stop, loop and clip duration. Rig metadata, active pose and timeline are saved/exported in native model JSON. Existing unrigged saved hands and other projects remain untouched; an arbitrary-model auto-rigger and IK are not claimed. Focused hand math/syntax and sealed source candidate checks pass; real-device visual acceptance remains owner-controlled. **v11.220:** 252 ordered patches, 68 assets, 7,526,101 HTML bytes, SHA-256 `5551fb674e6a33eae5329880e6195fe404bb22af7a4f10ec7fe42629fdb89b89`. Details: `docs/HAND_SKELETAL_STUDIO_V11_220.md`.

## §E v11.219 — Finger rails mounted under the last finger links (2026-11-02)

Owner review of live v11.218 phone screenshots requested the four purple non-thumb finger rails to follow the finger backs and sit beneath the top metallic links, as in the approved concept. Each finger now has a six-point native dorsal conduit path fitted to its own length/splay. Both metallic retention links sample the same path (45% and 77% height) and wrap around finger sides; the rail runs to the fingertip setting. Thumb helix, anatomy, armor, other starter projects, saved copies, §C and Quest controls are preserved. Focused source/syntax candidate passed; manual phone acceptance pending. **v11.219**: 251 ordered patches, 68 assets, 7,504,085 HTML bytes, SHA-256 `f2c7177cd479e001b823f2684f3ceae1fcd5235e6333bd97d006a631661ef3c0`. See `docs/FINGER_RAIL_CONTACT_V11_219.md`.

## §E v11.218 — Arcane Glove fidelity, attached conduits and thumb helix (2026-11-02)

Native Floating Hand starter now uses the approved blue-black/silver/lilac aesthetic: slightly longer proportional fingers, a connected two-turn purple helix wrapping the full 3D thumb to its back-of-tip setting, four separately socketed backhand conduits, finger rail clamps, a geometric dorsal shield frame and illuminated cuff hardware. All new details are editable Model Atelier parts. Existing saves, §C, Sheep Tag and Quest input are untouched. Narrow candidate source build/syntax checks passed; owner phone/Quest acceptance remains pending. **v11.218:** 250 ordered patches / 68 assets / 7,503,389 HTML bytes / SHA-256 `fd4f16810ce066eb9b905748461ce8717a2b0f0eee633491364b5f8bb56aab41`. See `docs/ARCANE_GLOVE_FIDELITY_V11_218.md`.

## §E v11.217 — Proportional Floating Hand refinement (2026-11-02)

Owner's second phone screenshots exposed oversized cylindrical fingers/knuckle studs and a swollen palm edge opposite the thumb. Added a scoped native signed-distance model refinement: varied index/middle/ring/pinky lengths and roots, tapered smaller distal digits, smaller armor studs/medallions, a narrower pinky-side hypothenar/ulnar contour, and smoother thumb web/thenar connection. New starter loads only; saved hand copies and Quest/Sheep controls are unchanged.

**Focused browser proof:** 53 editable meshes, 10 groups, 13,070 connected hand vertices, natural tip-length hierarchy, palm depth 0.629 and ulnar X boundary +0.611 (previous +0.755); no browser errors in [Actions #41472504506](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41472504506). Version v11.217 retains v11.216 Sheep wheel movement. Sealed 249 patches / 68 assets / 7,497,822 HTML bytes / SHA-256 `4d7b2d0aa3fa8183956b3f751411ad1a5e20662d41c2f7f7123093262a55c5d8`. Full details: `docs/FLOATING_HAND_PROPORTIONS_V11_217.md`. Phone/Quest visual approval remains owner-controlled.


## §E v11.215 — Floating Hand anatomical sculpt (2026-11-02)

Owner's four-angle phone review exposed a flat palm and weak thumb/opposite-thumb side silhouettes. Updated **only** the Floating Hand starter's native organic signed-distance field with a thicker convex palm, rounded hypothenar (pinky-side) bulge, curved ulnar edge, forward-angled blended thumb saddle/mound and four tapered, gently splayed fingers with anatomical knuckle contours. Repositioned front/back magic symbols over the new volume and added editable thumb, palm, ulnar and finger seams. The original other game/editor starters, v11.214 Quest quick-wheel fix, saved user projects and Model Atelier validation are preserved.

**Focused browser proof:** 53 native editable meshes, 10 groups, 16,938 connected glove vertices; measured central palm front/back range 0.718 units and ulnar-side maximum x +0.755; Chromium mobile-size deep link loaded with no page/console errors (GitHub Actions #41468763144). Strict source: 247 patches, 68 assets, 7,490,431 HTML bytes, SHA-256 `90095eecc2a4e2af538d9332966108c7bede67d6cb041c329219ad475f3cdf1d`. Full scope and physical-device acceptance: `docs/FLOATING_HAND_ANATOMY_V11_215.md`. Initial model is not yet weight-painted, skeletal-rigged or linked to Quest hand tracking.

## §E v11.213 — Floating Hand loading repair (2026-11-02)

Fixes the v11.212 Floating Hand starter's actual browser loading failure: an unsupported cylinder mesh-density field and inherited Festival named-socket assemblies caused native Model Atelier validation errors and left zero meshes. The append-only repair keeps all 39 hand parts, corrects the sleeve data, and removes old character socket metadata only from the new hand scene. Focused Chromium deep-link reproduction now passes with **39 meshes loaded and no reported JavaScript errors** (Actions run #41399909619). Source: 245 patches, 68 assets, 7,478,295-byte HTML, SHA-256 92785aeafddf55ec02535858b89b2b9e9a6c6f10cfcc149fcd8395ec2b01d8a4. See docs/FLOATING_HAND_LOADER_FIX_V11_213.md. Hosted/owner acceptance is separate from this candidate browser check.

## §E v11.212 — Floating Hand · Arcane Glove starter (2026-11-02)

Owner-supplied multi-view glove reference is now an **independent native Model Atelier starter**. Open Projects → Floating Hand · Arcane Glove, or navigate to modeler.html?project=floating-hand-glove. The original indexed organic palm/finger/thumb shell, metal knuckle/dorsal armor, glowing front/back crests, rune seams, cuff and suspended violet rings are separate editable model parts. Saving/exporting uses the existing Model Atelier project/mesh workflow; other starters, user projects, XR bindings, chat and Sheep Tag are unchanged.

**Sealed source receipt:** 244 ordered patches, 68 assets, 7,478,674 HTML bytes, SHA-256 add8a1718f8d06a1ef178bf4adaa55e12ae38f9d33be1404396637c32ebfa92f. See docs/FLOATING_HAND_MODEL_STARTER_V11_212.md. The open-hand model is not yet bone-rigged, skinned, pose-animated, or linked to Quest hand tracking. Owner phone/Quest visual acceptance remains pending.


## §E v11.198 — Quest editor free flight, controller-driven 3D grabs, selectable gizmos and control legend (2026-11-01)

**Owner controls:** The immersive native editor now provides smoother adjustable free-flight (1.5/3.2/6.4/12.8 world units/s), accelerated/braked velocity, left-stick-click speed boost, left grip + right-stick Y ascent/descent, and optional 15–45° snap-turn increments. The existing stable XR reference-space movement is reused to avoid stacking transforms over time.

**Real scene editing:** Right-grip dragging now follows the controller's full world displacement, including pulling objects closer toward the headset, with one native undo transaction per completed move. Red/green/blue world-axis gizmo arrows are actually selectable with the trigger and restrict movement to X/Y/Z until release. The compact wrist radial gains FLIGHT, GIZMOS and a readable LEGEND page; prefab and capture controls remain accessible. Controller shells, aura and particles are visually smaller, editor-only helpers are kept out of capture, and menu selection remains modal.

**Safety / source receipt:** 230 patches, 68 assets, 7,320,589 generated HTML bytes, SHA-256 `c5e42de3a9c6dca98d72843b70c4cb2eb549c22589aae4a7fb0d4f7e8ba00f0f`. See `docs/QUEST_SPATIAL_EDITOR_FLIGHT_GIZMO_V11_198.md`. Previously working Sheep Tag gameplay, Chat sign-in, Model Atelier, authored scenes and desktop/mobile controls remain outside this change. Real Quest 2 comfort, grip alignment, ray hit sensitivity and frame-rate acceptance require headset testing.

## §E v11.197 — Sheep Tag meadow aliasing, LAN fog and efficient flat camera (2026-10-31)

**Screenshot follow-up:** the 1-pixel periodic grid baked into the original 1024px meadow texture could shimmer and form moiré at shallow camera angles even after the separate fog plane depth fix. v11.197 removes that grid without changing authored ground/paths, configures mipmap filtering for both the old meadow and current 4K Moonbell Wildwood, prefiltering Wildwood to 2K for Quest Browser, blocks the solo fog painter from overwriting LAN team fog, and replaces the flat-screen camera's unnecessary per-frame full `stStatus()` snapshot with native controlled/selected actor position tracking. Existing Quest camera/radial, capture tools, LAN authority, starter projects and saves remain unchanged.

**Authoritative source:** 229 ordered patches, 68 assets, 7,300,640-byte HTML SHA-256 `315e2acb7f54118fce4e428e534cceac14a0ecbaac596291df29ba6dbd7cc54d`. Details and device acceptance limits: `docs/SHEEP_MEADOW_VISUAL_STABILITY_V11_197.md`. Actual Quest 2 long-session GPU/stereo verification remains pending.

## §E v11.196 — Sheep Tag browser fog and Quest VR menu/camera recovery (2026-10-31)

Two independent screenshot-reported problems fixed. On the **2D floating browser**, transparent fog sat almost coplanar with the meadow and could produce flickering stripes: this patch raises the translucent plane above the ground, adds polygon depth offset and coalesces texture redraws without changing logical fog sight rules. In **immersive Quest VR**, the wrist radial was inverted and repositioned during aiming, and headset movement clashed with Sheep Tag's authored cinematic. The menu now faces the player and remains stationary while open; entry gets a single sheep-centered reposition, gameplay follow snaps once rather than flying toward the sheep, and editor locomotion/grabs cannot compete with cinematic control. The menu retains an explicit REFOCUS action and the existing screen capture tools.

Source: 228 ordered patches, 68 assets, 7,295,859-byte HTML, SHA-256 `679d14774b8abb97254f1adf072b98f0db51bbad152a2567142105155b944ca1`. See `docs/SHEEP_VR_FOG_CAMERA_RECOVERY_V11_196.md`. Source/browser checks cannot establish actual Quest 2 stereo visuals, frame rate or comfort; owner headset acceptance required. Original saved scenes, Sheep Tag network rules, §C, Dragon Den, Emberfall and Model Atelier preserved.

## §E v11.195 — Quest 2 Sheep Tag camera, fog, menus and capture repairs (2026-10-31)

**Owner-reported issues addressed in source:** left-offset VR follow camera, severe lag after game begins, fluttering ground/fog texture, controller rays selecting through menus, duplicate Exit VR sign/arrival overlay, static Main Menu positioned by houses and cumbersome tall floating dialog stacks.

**Native XR repair:** keep one stable XR reference-space base while moving the headset to a centered, elevated strategic sheep-follow viewpoint. Skip repeated game-status snapshots and hidden 2D camera/HUD work during headset play, route frequent hover rays to cheap terrain hit tests, and run full scene actor selection only on trigger. The Quest Sheep session uses 72% pre-session framebuffer scale, no extra stereo shadow pass, and a visual fog layer lifted off the meadow with polygon offset and roughly 3 Hz cosmetic repaints. Existing game visibility and fog-of-war logic remain authoritative.

**UI overhaul:** automatic authored-actor Sheep Tag menu cinematic with a slow comfort-aware sheep-centered headset view, compact right-controller-tethered radial palettes (X to open/close, trigger to select), modal menu input interception, minimal low-poly controller grip bodies and glowing calibrated beams with particles. Dismiss duplicate in-world exit signs while retaining Meta system menu and browser toolbar exit. Photo mode freezes play for framing, captures on trigger and restores pause with X; clean/debug JSON/stereo exports use the original screenshot writer with after-XR download fallback. Debug screenshots include FPS/draw-call and fog diagnostics.

**Release source:** 227 patches, 68 assets, 7,288,202 exact HTML bytes, SHA-256 `7fa6242cfeeb6f9b44e8887cf86b905ed5e6ee9c55e7e12696a64fc77a0a31ad`. See `docs/QUEST_SHEEP_VR_STABILITY_V11_195.md`. Browser and unit acceptance cannot replace physical Quest 2 frame/comfort/stereo acceptance; other engines, projects, storage, §C authentication and Model Atelier stay unchanged.

## §E v11.194 — Emberfall: Shattered Vale, original hack-and-slash starter (2026-10-31)

**New project template:** Projects → **Emberfall · Shattered Vale** creates an independently editable native §E map, with Wayfarer hero, Blightwoods, cliff formations, camp portal, corrupted crystals, shrine ruins, 11 enemies and a Cinder Warden boss. Explicit deep link: `?project=emberfall-arpg`. Original startup project preference and existing saved projects are untouched.

**Playable first slice:** Play starts a top-down action RPG session. Tap/click terrain to move or tap an enemy to pursue and slash; keyboard WASD/arrows are optional. Slash (Space), arcane Bolt (Q), area Nova (E), and healing Potions (R) all have usable touch buttons and proper mana/cooldown rules. Enemies pursue and damage the player; a friendly lantern follows and occasionally attacks. Kills grant gold/experience, levels grant skill points, randomized common/magic/rare loot drops and auto-upgrades simple attack/armor ratings. Defeat the Cinder Warden for a starter objective.

**Native integration and boundaries:** The editor owns authored objects and project serialization; combat AI, temporary drops, VFX, hero health and XP reset with Play/Stop, preserving the exact editable level. No second WebGL renderer or animation loop; no licensed ARPG assets, names or map designs copied. Full persistent RPG character/inventory, procedural dungeon generation, co-op and dedicated VR ARPG input remain future phases. Physical mobile/Quest tests are required to accept the new gameplay.

**Release receipt:** Source v11.194, **226 ordered patches**, **68 assets**, **7,259,828 HTML bytes**, SHA-256 `740bfa088414731cd6b397aaf85290ef550461d8708ade833f9f3742a27aa2f4`. GitHub candidate run [#41267781381](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41267781381) built the exact package and passed targeted ARPG and existing Quest regression checks. Final production deployment and owner hardware acceptance remain separately evidenced.

## §E v11.193 — Quest Sheep Tag immersive menu, wide follow camera, and VR Capture Studio (2026-10-31)

**In-world Sheep Tag:** Use a native ray-selectable title menu in Quest VR, backed by the existing authored Sheep Tag Main Menu and canonical level transition. The strategic headset rig follows the sheep from an elevated, zoomable distance, with detach, pan, orbit, recenter and natural independent head-look.

**Quest controls:** Controller rays select and move sheep, attack/rescue and place validated farm structures through Sheep Tag's existing gameplay authority; newly built farm meshes are targetable. Compact in-world pages expose building choices, pause/restart/stop and screenshots. The existing native map editor retains its own creation palette, with a link to Capture Studio.

**Captures:** Generate an in-engine clean PNG, debug PNG plus JSON, or side-by-side stereo PNG via a temporary offscreen render target, with a browser download control after exiting VR. This does not capture the Quest compositor's Facebook-style photo depth effect.

**Safety:** Reuse the original XR session, renderer, scene, project storage, and 2D editor. Preserve Quest system exit. VR menus do not allow accidental authoring/grab actions through their surfaces. Physical Quest 2 comfort, exact UI aiming, performance and downloads require owner acceptance.

## §E v11.192 — Quest 2 spatial Game Editor, native tools, locomotion and target rays (2026-10-31)

**Physical Quest report:** Dragon Den immersive rendering and EXIT VR now work. Owner reports thin disconnected beams floating in air, pointer mismatch with Quest target, zero locomotion, camera-facing scene labels shifting as the head moves, and lack of spatial map-editing tools.

**One live XR editor layer:** Extend the *existing* immersive renderer and tracked `getController(index)` target-ray poses, rather than starting a second game or rendering loop. Draw tapered world-space beams with two target rings per controller, using the same ray origin/direction as selectable editor actor collisions, the EXIT sign and in-world palette. Add a device-local, opt-in yaw-trim action (+/-0.012 radians per click) to align our visual aiming with the Quest UI pointer where browser/device offsets differ.

**VR navigation:** Left thumbstick glides through the game scene (no gravity); left grip + stick enables vertical flight; right thumbstick snap-turns by 20 degrees. Position/heading changes use WebXR reference-space offsets, preserving headset 6DoF and the project's authored Arrival Court spawn rather than moving scene geometry.

**Native authoring:** A fixed-in-world headset palette provides Select, Grab/Move, Place Wall, Place Rock, Undo, aim trim and EXIT VR. Quest trigger selects game editor actors by the calibrated ray; right grip drags a selected actor using its original parent transform and a native single undo transaction. Input capture is from actual connected Quest gamepads, not the Studio's fake diagnostic input; left X toggles the palette and right A toggles the interaction mode. Object placement uses existing native `createPrefab`, `selectActor`, scene hierarchy and transaction functions. Do not change saved objects or enable edits while a game is in Play/Simulate.

**Stable world text:** Native `WorkspaceStationLabel` billboard sprites become fixed planar 3D labels when entering Quest VR and are restored on exit. No texture deletion, no change to authored sign JSON, no edit to world-space actor coordinates.

**Boundaries:** This is a usable first VR **game-map editing** layer, not full Model Atelier VR sculpt, two-hand skeletal rigging, advanced node edits, or cloud controller-profile binding. An immersive palette isn't a replacement for the complete desktop UI. Device FPS and aiming/locomotion calibration require physical Quest acceptance. Keep original mobile/desktop editor, 2D Modeler, scene/project state and Quest menu exit unchanged.

**Testing:** Fast mocked native WebXR ray/controller, undo/transaction, billboard and reference-space tests plus exact HTML/asset hash verification; never install Chromium automatically.

## §E v11.191 — immersive Quest 2 black-view repair and Arrival Court spawn (2026-10-31)

**Owner report:** Pressing Enter VR in the game editor on Meta Quest 2 entered an immersive black display. The original WebXR gateway initiated local-floor but did not offset tracking coordinates to the saved project arrival zone; the authored Dragon Den Arrival Court is at [0, 0.02, 14.1]. A black headset view may also indicate a renderer or headset-frame failure; the source alone cannot establish which.

**Repair:** Place the headset via WebXR's native `getOffsetReferenceSpace()` and Three.js `setReferenceSpace()`, using the project-owned arrival zone (and Dragon Den fallback only for that project type). Preserve the scene JSON, 2D orbit and camera state. Show a head-relative, brightly emissive/unlit startup panel that ignores occlusion, plus the existing EXIT VR surface; both appear in the XR scene even if the world is dark or the headset starts inside a wall. The welcome panel hides after 9 seconds. If zero XR frames arrive in 9 seconds, exit the session and return to the editor rather than leaving the user in a black compositor. Quest menu remains available for immediate exit.

**Performance:** Allow 80% framebuffer scale before requesting the session on supported devices. Bound per-frame controller-ray hit tests to once per ~95ms per hand, preserving immediate native `selectstart` ray hits. Keep exactly one Three renderer, one XR animation loop, authored parent selection and existing controller studio. This is not immersive Model Atelier or controller-based sculpting.

**Diagnostics:** `window.SWYRL_ENGINE_XR_RECOVERY.diagnose()` exposes XR frame count, offset success, arrival source, exit sign visibility and last error to distinguish a missing game view from total XR output failure. No real-headset acceptance can be inferred from mocked or source tests. Physical Quest 2 testing remains required.

**Verification:** Fast Node mocked API and source/rebuild integrity checks only; no automatic Chromium install or browser marathon.

## §E v11.190 — honest rendered FPS and built-in vault batching (2026-10-31)

**Measured evidence:** User Android screenshots had reported ~18 FPS on Medium, 53–60 on Low, and 24–30 on Mobile Boost, but screenshots showed different scene views and times. Source inspection identified a telemetry flaw: the displayed FPS counted animation-loop invocations, even when `shouldRenderFrame()` skipped WebGL frames according to the preset cap (Low=45, Mobile Boost=60). These were not apples-to-apples measurements.

**Correctness fix:** The overlay now displays *actual submitted renderer frames per second* and corresponding inter-render interval. Internal update FPS remains separately inspectable, rather than being mislabeled as rendered FPS. Synthetic browser frame rates are not used as a proxy for Android/Quest hardware performance.

**A/B comparison:** In View → Graphics & Performance, use **Compare Low / Boost** to run two consecutive measurements against the same loaded scene/camera under the same temporary 60 FPS cap. The original graphics preference and cap are restored afterward. Keep the camera stationary while the comparison runs. A lightweight on-demand scene audit identifies actor groups with many visible child meshes; its results are *estimates of submesh count*, not precise per-actor GPU timing.

**Safe draw-call batching:** Only existing built-in, non-skeletal vault decoration is modified at rendering-time: opaque vault canopy panels and chamber wall triangles are combined into one mesh per actor; repeated brass and glowing vault rib cylinders and star oculus points become instanced meshes within their original actor groups. The Embervault project JSON, actor IDs, positions, material colors, collisions and editable parent actors remain unchanged. Estimated maximum reduction across visible canonical decorations is around 100 draw calls; actual viewport reduction and device performance must be measured.

**Other:** Switching Low/Boost no longer unnecessarily disposes same-size shadow textures or resets the WebGL pixel ratio when unchanged. Existing modeling, project persistence, game simulation, VR, dynamic actors and 11.189 graphics choices are preserved. Package and syntax checks run automatically; Chromium suites remain opt-in/manual.

## §E v11.189 — mobile graphics performance controls and diagnostics (2026-10-31)

**Owner issue:** The main §E Game Engine screenshot on Android showed about 18 FPS / 56.7 ms per frame, at 82% rendering scale with a complex Dragon Den scene. The 82% figure is resolution scale, not CPU utilization. This release avoids inventing a claimed FPS gain before physical-device measurement.

**Graphics:** The existing View → Graphics & Performance controls now include an explicit **Mobile Boost** setting (62% render scale, no dynamic shadows, 512 shadow tier, 60 FPS cap). Preserve the user's existing Auto/Low/Medium/High/Custom preference unless they deliberately choose the boost. Model geometry and authored project data are unchanged.

**Viewport work:** Avoid running the main WebGL viewport's DOM-size measurement on every animation frame. ResizeObserver, browser viewport resize and orientation events invalidate the cached sizing, with a fallback check every 250 ms. This does not throttle physics or requestAnimationFrame / XR render updates.

**Evidence:** The Graphics & Performance panel includes CPU-side editor update time and WebGL render-submission time, draw calls and triangle counts. GPU completion times are *not* measured; browser frames may be limited by GPU, JavaScript, thermals, or display refresh. The native FPS overlay remains available independently.

**Scope:** Keep the v11.188 Game Engine/Modeling tab routes, saved projects, native modeling, Sheep Tag gameplay, multiplayer, VR session ownership and editor authoring intact. Dedicated two-size browser smoke verifies graphics choice, preference retention, viewport invalidation and tab switching. Owner Android/Quest comparison still needed.

## §E v11.188 — Game Engine first, Modeling second (2026-10-31)

**Owner-requested startup:** Opening the normal §E site or `index.html` lands on the Game Engine, not Modeler. The topmost two native workspace tabs are now **Game Engine** (selected first) and **Modeling** (second); selecting Modeling is the explicit way to move into the separate Modeler page.

**Root fix:** Legacy default-project restore code still called the Model Atelier overlay's `open()` method automatically. The model editor now respects the active workspace route instead of overriding the Game tab. A remembered model starter or saved-model preference is preserved but will not hijack the Game Engine landing page; the regular game scene opens instead. Explicit Modeling tab clicks, the dedicated `modeler.html` URL and native editing remain supported.

**Scope and safety:** Saved project bytes, local/account model defaults, untitled model drafts, VR, Sheep Tag, chat and independent tab state remain untouched. The native Edit Model shortcut enters the Modeling tab rather than bypassing the navigation boundary.

**Validation:** Focused Android-size and Quest-size browser checks cover ordinary startup, user-selected Modeling, back navigation, model-starter default, locally saved model default, and the existing direct-Modeler/draft regression. Physical device acceptance remains with the owner.

## §E v11.187 — Game Engine and Modeler as separate tabbable workspaces (2026-10-31)

**New architecture:** The existing Game Engine remains at `index.html`; the native Modeler now also has its own public `modeler.html` page. A compact Game Engine / Modeler tab strip switches routes in place, without reloading the page or discarding the active game scene. Both URLs work when opened directly.

**Project-optional modeling:** The model editor opens with a blank, untitled in-browser model when no model project is loaded. Mesh editing, sculpt tools, Add, Import and Export use the existing native Model Atelier. Scratch meshes are stored separately from `currentProject`, preventing edits in Modeler from dirtying or replacing the game workspace. A Blank model button starts a fresh untitled draft after confirmation.

**Draft safety:** An untitled model draft is bounded, validated and retained in the same browser through refresh when local storage permits. Export JSON is available even if local storage fails; user-named model projects still follow native project-save workflows. Neither editor requires a preexisting user-saved file to begin working.

**Packaging:** Both pages share one verified native runtime; the static upload includes a second `modeler.html` entrypoint with the exact sealed bytes. Version-pinned source SHA and 68 packaged asset receipts are unchanged in meaning. Dedicated mobile and desktop browser tests cover direct open, tab switching, draft edits, game state preservation and reload.

**Validation:** Browser acceptance and owner testing on physical Android/Quest remain required before considering UX final.

## §E v11.186 — first-paint glitch-wisp boot repair (2026-10-31)

**Owner screenshot:** Hosted mobile launch displayed only “✦ §E · Initializing workspace” on a dark background instead of animated wisps. Root cause: v11.185 created the decorative overlay from a late engine-module initializer, so the page's earlier pseudo-element fallback could paint alone while the engine script was pending.

**Repair:** Build a static startup overlay directly after the original opening `<body>` tag, before the large engine module. The CSS creates a glowing §E sigil with two rotating rings, three wisps, 32 animated fragments, and a loading shimmer; an independent tiny early script updates human-readable initialization states. Existing v11.127 editor-readiness signal governs exit. The emergency fallback pseudo-element no longer masks the animation.

**Recovery:** If readiness never arrives, reveal a manual Reload §E button after 18 seconds—no fake progress, forced reload or automatic project overwrite. Respect reduced motion.

**Scope:** Leave v11.185 collapsible Model Atelier toolbar, save/export/close controls, native editor, scene geometry, project-default restoration, LAN, VR and Chat integrations unchanged. Test initial paint without evaluating the engine module; check native browser and owner Android/Quest next.

## §E v11.185 — Glitch-wisp initialization and collapsible Model Atelier settings (2026-10-31)

**Startup:** The existing readiness-gated startup screen now animates lightweight teal/violet glitch fragments, wisp trails, concentric rings and the §E sigil. The status wording reflects real initialization states without invented percentages. The underlying stable boot gate, its fallback, and saved-project restoration stay authoritative. Reduced-motion devices see a calm static presentation.

**Model Atelier:** A Settings toggle in the main modeling header expands/collapses native render mode, target, camera view, reference and display options while leaving model Save, Export, Close and the working viewport accessible. It remembers its state per browser; coarse-pointer and narrow layouts begin compact. No modeling controls, handlers, undo history or saved meshes are replaced.

**Verification:** The focused v11.185 package/build integrity check is required before a separate deployment request; owner Android/Quest acceptance follows the hosted release.

## §E v11.184 — My Projects preview gallery and one saved startup default (2026-10-31)

**Owner request:** Render visual preview cards for user-owned projects directly in the native Projects menu, and let a single checkbox determine which saved project §E opens by default.

**My Projects gallery:** The existing My Projects tab now contains responsive cards for browser-local IndexedDB projects and signed-in § Chat account projects, alongside their native Open actions. Local saves now include a lightweight, bounded top-down scene overview derived from real saved actor coordinates; older local projects lazily generate those overviews only when their cards enter view, with at most two simultaneous reads. Account cards display an immediate illustrative tile, and an explicit Preview scene action can download and inspect one saved account scene without importing it or replacing the active editor. These are actor overviews, **not claimed 3D camera screenshots**. Existing local list controls remain available in expandable advanced controls.

**Exclusive default:** Saved-project cards and original starter cards use the same same-browser `swyrl.engine.defaultStarter.v1` preference. Exactly one optional checkbox can be selected. A selected device-local project loads from the existing IndexedDB store during normal startup; an account default initializes the existing authenticated Chat iframe and attempts loading only when signed in, falling back to Dragon Den with a message if unavailable. Explicit `?project=` deep links still take precedence. This preference is per browser/device, not synced to the Google account or saved project bytes.

**Safety and performance:** No second project store or renderer, no eager cloud downloads, no raw saved scenes in localStorage, no cross-account scene import, no silent project overwrite after the default account timeout. Native file/Cloud loading, rollback, Model Atelier, Sheep Tag, WebXR, editors, and starter behavior are preserved.

**Verification:** Isolated default-pref, cloud-boot callback and JS syntax tests passed; locally seeded browser preview/default/reload acceptance passed on Android-sized and Quest-sized Chromium viewports. Real account sign-in, physical Quest 2 and owner Android visual acceptance are separate checks.

**Receipt:** 216 ordered patches; 68 assets; 7134586 generated HTML bytes; SHA-256 `35ba507edf2eedd98a85a49e8ae5e55e5b43f0b78c61139e1b2e6b50e8b95c5b`.

## §E v11.183 — Project controls, HUD clearance and visible loading (2026-10-31)

**Owner screenshots:** The right-side actor-count pill covered toolbar actions in desktop-mode phone view; Sheep Tag menu allowed editor-only top/bottom hints to intrude; the Project Levels controls were compressed into the narrow scene column; opening saved and starter projects felt delayed without meaningful feedback.

**UI remediation:** Hide the redundant floating actor-count pill (native status bar still reports actors and selection). While a Sheep Tag cinematic/runtime menu is open, hide editor-only viewport badges, shortcut hints, level-edit overlay and other stray chrome without affecting Start, LAN, Exit or Chat. Project Levels now starts as a compact 44px button, expanding on demand into the original functional selectors/buttons, with outside-click and Escape dismissal. No project IDs, scene controls, input handlers or user data are replaced.

**Real performance work:** v11.141's bundled-level loader previously invoked the native scene rebuild twice: once for the outer scene and once for the selected saved level. v11.183 chooses the active saved level first, then invokes the same native build **once** while hydrating the original level pack for future saves/links. Cloud lists reuse a same-account in-memory result for up to 12 seconds, with explicit Refresh bypass and cache invalidation on account changes. Starter, IndexedDB and account project opening now display stage/elapsed-time status and yield UI frames before synchronous import. Account/local loads recheck workspace state before replacement, preserving native rollback guarantees.

**Evidence:** Focused code and single-native-rebuild VM tests passed. Controlled Chromium UI checks passed at 390×844, 430×932, 844×390, 980×680, and 1280×800; starter flow was exercised in portrait, landscape and Quest-sized desktop window. Actual Quest 2/Android acceptance and device-specific load time remain owner checks.

**Release receipt:** 215 ordered patches; 68 preserved assets; 7,110,847 HTML bytes; SHA-256 `070aad1b47dcf1a05bdfee3e82f48e81991bc4826e9d128bb904d3bc8f1b3145`. Separate final deploy request and upload receipts must confirm this build.

## §E v11.182 — Professional interface and overlap audit (2026-10-31)

**Owner request:** Review overlapping editor controls and polish the whole §E interface to professional consistency while preserving the working Game Editor, Model Atelier, VR Controls, Chat, projects and gameplay.

**Implemented:** Unified restrained dark-slate/teal colors, consistent borders, radii, typography, focus states and scrollbars across the native main toolbar, outliner, Details dock, prefab cards, Projects window, Canvas level controls, responsive drawers, Chat panel, VR Controller Studio and compatible Model Atelier control styling. No editor objects are remounted and no listeners, game input, 3D scenes, WebXR render loop or model tools are replaced.

**Layering:** The already-portaled Projects dialog stays above Chat and editor docks; native modal dialogs remain above Projects; the in-world runtime menus remain confined to the viewport. Projects window is viewport-bounded and scrollable, with sticky header and consistently sized close target. Mobile tabs retain the v11.174 measured level-bar offset. First-party topbar remains a horizontal rail rather than floating over the canvas.

**Found/fixed:** A true 8-pixel canvas/toolbar collision in compact 844×390 landscape was caused by a too-tall new header; use the native 48-pixel toolbar grid height instead. A 1-pixel portrait adjacency is ignored by the 3-pixel geometric tolerance, not hidden by a scene override. A transient startup release-notes modal also correctly sits above Projects until dismissed; it must not be "fixed" by weakening dialog priority.

**Verified:** Browser-layout run checked 390×844 portrait, 430×932 portrait, 844×390 landscape, 980×680 Quest-sized browser viewport and 1280×800 desktop. All five passed: no identified unintended baseline chrome collisions, Projects window inside viewport, Projects close button clickable, horizontal toolbar scroll available, no unexpected JS errors. Focused layout audit API is `window.SWYRL_ENGINE_UI_AUDIT.audit()`. These are controlled Chromium results, not physical Quest 2 or Android acceptance.

**Exact source:** 214 ordered patches, 68 bundled assets, 7,094,717 final HTML bytes, SHA-256 `0b4af9562ac14811d597938d75e716a39110ce1849929bb3a8599b78370b4f25`. Build verifier `scripts/verify_v11_182_release.py`; new layout patch `patches/v11_182_professional_ui.py`; focused tests `tests/test_v11_182_ui.cjs` and `tests/ui_layout_v11_182_browser.mjs`. Only the designated deployment workflow should trigger for a final DEPLOY_REQUEST-only commit.


## §E v11.181 — Enter immersive WebXR from the live §E browser (2026-10-31)

**Owner request:** Open §E normally on Meta Quest 2, then press Enter VR to step *inside* the same 3D project instead of using Quest's controller rays only on a flat floating browser window.

**Actual native renderer:** The editor's existing main THREE.WebGLRenderer (Three.js 0.169.0) and existing scene/simulation/editor tick remain authoritative. The old main manual requestAnimationFrame chain is replaced with exactly one renderer.setAnimationLoop(tick) bootstrap, so the same renderer serves desktop 2D and WebXR headset stereo views without a competing renderer. The main resize handler never sets the 2D framebuffer size while XR owns the frame buffer, and immersive frames bypass the 2D max-FPS skip. Native actor/play/Sheep Tag/maul physics and animation updates continue from the original tick.

**XR doorway:** A topbar 🥽 Enter VR button probes runtime feature support and only requests an immersive-vr/local-floor session from a direct click on HTTPS. WebXR asks for headset permissions; nothing enters VR automatically on page load. Exiting via a small in-world EXIT VR sign (aim + select trigger) or the Quest system's exit mechanism restores the previous camera, orbit mode, transform gizmo visibility and ordinary 2D renderer, keeping the current scene and project. The WebXR session lifecycle is also attached read-only to the existing Controller Studio for device diagnostics.

**Native interaction milestone:** Real WebXR controller target-ray spaces produce 3D visible rays; ray hits only accepted native actor geometry and change ray color/length. Trigger-select in edit mode calls native selectActor through existing selection rules. No click synthesizing, no mutation operation, no remote/editor/Play trigger forwarding and no new undo transactions. Selection is deliberately non-destructive. Ray/controller geometry and event listeners are removed when XR ends.

**Boundaries:** Model Atelier owns a separate renderer: if its panel is open, Enter VR is blocked rather than showing the wrong game editor. Model Atelier sculpt VR, tracked grab/move transforms, two-handed gestures, locomotion, room alignment customization, floating Chat panels and full Controller Studio action dispatch are not yet implemented. Quest 2 physical acceptance and real tracked input behavior remain pending; browser stereo rendering requires actual supported XR hardware.

**Test/receipt:** Dedicated JS static and mocked headset-session tests cover deferred user-gesture entry, distinct Model Atelier block, existing renderer binding, controller rays, restoring prior camera/orbit/transform after app/Quest exit, XR cleanup, no fake scene mutation and re-entry. Exact 213-patch/68-asset build measured 7,079,620 bytes, SHA-256 fb0732cc05fb4a4e5c5a8e114ffba9518c88be42a220c5d8908090262c20fd77. The sealed source verifier must pass independently from the deployment upload. A physical Quest is still the final acceptance check.


## §E v11.180 — Chat automatically slides away after an outside tap (2026-10-31)

**Owner request:** When the user selects outside the embedded §wyrlz Chat in §E, the Chat should slide away without closing the editor or losing the current conversation.

**Implemented:** A document-capture primary pointerdown handler closes Chat only when the tap/click target lies outside both the Chat side panel and its toggle. A click fallback also handles keyboard-activated controls outside Chat. Pointer events are never canceled or replayed, so selecting a scene/mesh/editor control still works. Right mouse button and secondary touch pointers are ignored to prevent accidental dismissal.

**UX:** The existing Chat aside slides right over 210 ms, supports prefers-reduced-motion, and is hidden/inert after exit. The original iframe stays mounted across opening/closing, so the embedded conversation and draft DOM are not destroyed. The existing close button, toggle and Escape work. On outside selection the focus stays with the chosen editor control instead of jumping back to Chat's toggle.

**Security:** Closing uses the existing revoke() path, withdrawing the short-lived native edit lease; reopening reconnects normally. It does not copy Chat credentials, mutate a project or touch model/gameplay/VR control state.

**Verification:** Focused VM tests cover inside/outside targets, toggle exclusion, right-click, non-stolen focus, transition timing, preserved iframe, stale timer cancellation and explicit close focus. A source build verifies the HTML patch, version, 212 ordered patches and 68 assets.

**Exact source:** v11.180, 212 ordered patches, 68 assets, 7,066,690 HTML bytes, SHA-256 befd3604d7614483eff73ef958c9652204ba3aeed4533f01a4b6204b9212ea60. Implemented with runtime/chat_outside_dismiss_v11_180.js and .css, patches/v11_180_chat_outside_dismiss.py, tests/test_v11_180_chat_outside_dismiss.cjs, scripts/verify_v11_180_release.py.

**Remaining acceptance:** Physical phone/Quest Browser outside-tap behavior and live-hosted hash must be separately checked after the final explicit release request. §E's chat/project/model/game and VR Controller Studio are unchanged otherwise.


## §E v11.179 — VR Controller Studio configuration release (2026-10-31)

**Owner source:** Kami Precision VR Controller Studio archive (25-part specification, original JSON). This release implements the 2D configuration foundation; it does NOT claim full immersive Quest controller support.

**Features:** 🎮 VR Controls toolbar panel; Kami Precision (default), Standard, Left-Handed and Precision Sculpt immutable preset profiles; independent Global/Game Editor/Model Editor/Sculpt/Play mappings; editable custom copies; mapping and threshold validation; conflicting/reserved shortcut rejection; 2D simulated capture and resolver for X+A, Y+B and Play isolation; local Save/Revert; versioned JSON import/export including migration from owner-provided Kami Precision format; navigator.xr capability diagnostics and externally attached XR input-source inspection.

**Limitations:** Actual immersive WebXR scene/controller handling, physical Meta Quest 2 input, native scene/model actions, continuous strokes, two-hand gestures, live recording, per-account sync and headset acceptance are NOT implemented. No new renderer loop or unsafe native mutation dispatch. Profiles are device-local rather than account-isolated.

**Exact artifact:** §wyrl§ Engine v11.179, 211 append-only patches, 68 assets, 7,063,978 HTML bytes, SHA-256 2b9119cb587ca262be0948c3d5a04d35cfa3ebf0a1a5169dea116c1619d365fd. Patch: patches/v11_179_vr_controller_studio.py. Runtime: runtime/vr_controller_studio_v11_179.js and .css. Validator: scripts/verify_v11_179_release.py. Read reports/VR_CONTROLLER_STUDIO_V11_179.md for the remaining work and acceptance boundaries.

**Release boundary:** CI/source seal, guarded final DEPLOY_REQUEST-only commit, HF upload/live serving and physical headset verification are separate evidence levels. Preserve v11.178 history and original native editing/Chat.


## §E v11.178 — grounded analysis of the active project and workspace (2026-10-30)

**Owner request:** Now that the Google account, Chat side panel, and active project selector work together, make §wyrlz Chat understand and analyze what is actually open in §E. The target is the **current native editor**, including Sheep Tag's active level and scene workspace, not GitHub source files or generic project advice.

**Implemented read-only workflow:** The new **Analyze workspace** button in §E's Chat panel uses the existing verified Chat-origin session. Chat submits a fixed inspection prompt through the ordinary authenticated message transport. Before each request the bridge takes a **fresh editor snapshot** and obtains a short-lived server-side presence lease bound to the active project, thread and browser host. There is no silent editing, direct model execution, repository mutation or new credential handoff.

**What Chat can inspect:** Real project name and kind, starter when known, active level, edit/play state, unsaved state, selected object, bounded actor/mesh names and transforms, count, type distribution and basic organizational hints. The §E host computes a capped `workspaceAudit` from actual sampled metadata: duplicate names and objects sharing a position are flagged only as **possible concerns to inspect**, never assumed defects. Up to 48 native object records are included; large projects remain summarized and incomplete. It cannot visually inspect rendered geometry, physics or behavior solely from this metadata, and must not claim those as verified.

**Safety:** The host never places actor names into executable commands or arbitrary prompts. Chat's server recognizes analyze/review/audit as read-only, returns literal bounded findings and cannot invoke native mutation batches on this path. Existing explicit editing grants, undo/redo, project creation, local/cloud save, profile avatar, authentication and Sheep Tag gameplay are preserved. If a user has an unsent Chat draft, the Analyze action does not overwrite it.

**Exact source:** §wyrl§ Engine **v11.178**, **210 ordered patches**, **68 bundled assets**, **7,034,587 HTML bytes**, SHA-256 `925c1761e8bc89e22a1ba807320d4ff74f8ed53a6410c4f6e29ed16477773386`. Source is append-only `patches/v11_178_workspace_analysis.py` and `runtime/chat_workspace_analysis_v11_178.js`. [Sealed source verification #41129255647](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41129255647) SUCCESS, including 13 workspace/audit UI checks. Chat source `869ffbb65cb803bb548e0c36061f9ca4c7ff8e9a`, [Chat offline CI #41128929702](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41128929702) SUCCESS with read-only request and inspection-contract checks. Chat publication and §E final deployment use **separate gated releases**; live owner Android/Quest inspection acceptance remains distinct from CI and upload receipts.


## §E v11.177 — real Google avatar and single-tab sign-in code preflight (2026-10-30)

**Owner Android screenshot and correction:** The § Chat panel was successfully connected to the Google account but still showed a generic **G**, not the user's Google profile picture. Opening Google sign-in from an embedded or single-tab browser also obscured the original Chat iframe, so the recovery code could not be copied while the Google page was in front.

**Targeted fix:** An append-only **209th** patch (`patches/v11_177_google_avatar_single_tab.py`) displays the **verified account's actual Google profile picture** next to the account name when the Chat-origin broker supplies an allowed HTTPS `googleusercontent.com` image URL. Invalid, unavailable or failed images retain the accessible G fallback. The previous v11.176 connected state, native open-project picker, local/cloud project guards, Sheep Tag and VR editing remain unchanged.

**Single-tab recovery:** `Sign in with Google` now prepares the pairing *without opening a new page*. The original Chat iframe renders a selectable, copyable **12-character five-minute recovery proof** at its top, with an explicit **Copy code** action. Once copied, the user taps **Continue to Google**, a separate browser gesture that opens the existing first-party login page. The proof never crosses into the §E parent, appears in a URL or persists to disk. This preserves the canonical Chat-side verification, first-party Google login, PKCE binding, single-use exchange, and account isolation. If a browser destroys the original editor tab altogether, in-memory pairing may still fail; use a full browser such as Chrome when that occurs.

**Exact generated engine package:** §wyrl§ Engine **v11.177**, **209 ordered patches**, **68 assets**, **7,031,135 HTML bytes**, SHA-256 `329ebe66d3b1e4b75e3777d4cdabff2dc52d16850d9a445601b7d532b9dec5d6`. Focused node regression checks enforce the two-stage sign-in, trusted avatar source and no recovery proof in the parent URL. The new `scripts/verify_v11_177_release.py` verifies the source manifest, all 68 assets and final-only `DEPLOY_REQUEST.json` commit before the engine Hugging Face upload. Chat-origin code is delivered separately through its guarded Chat Space release. Physical Android/Quest behavior and exact served live hash remain separate acceptance boundaries.


## §E v11.176 — connected Google badge and real project selector (2026-10-30)

**Owner Android screenshot:** § Chat showed the verified Google account as connected but still displayed **Sign in with Google**. Its dropdown showed only Google-saved projects (and could be cleared on account change), although Sheep Tag was open locally. The native editor project was not missing; the host's account presentation and project picker were out of sync.

**Fix:** Append-only patch **208** (`patches/v11_176_chat_account_project_picker.py`) hides the redundant sign-in button while connected and displays a Google badge beside the verified account name. The selector always displays the **active native project** and groups available **on-device copies** and **Google account saves** separately. My projects refreshes both lists. Native local loads use the existing v11.175 recovery path; Google-saved loads retain the v11.170 authentication and dirty-state checks. Logout clears cloud names and returns the sign-in button; stale list responses cannot restore another account's projects. No Google credentials or email are shared with §E. Opening the selector never changes the scene.

**Browser boundary:** ChatGPT's in-app browser and an external Chrome tab may not share the original popup/opener context. Open §E directly in Chrome for same-browser Google pairing; mobile recovery codes must remain private to the original Chat iframe. Chrome login succeeded in the owner report; a new v11.176 device test is still pending.

**Source/CI:** §wyrl§ Engine **v11.176**, **208 ordered patches**, **68 packaged assets**, **7,028,937 HTML bytes**, SHA-256 `861e9eba85cda6feacc7f4ed0e360024ea54a10be30c4b1dd20e08a4339bfbde`. [Exact sealed candidate verification](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41113497738) PASS, including 16 controlled login/logout/local/cloud-picker assertions and generated-artifact verification. `scripts/verify_v11_176_release.py` and the existing request-only deployment process govern production publication. Actual Android/Quest visual acceptance is distinct from source CI.


## §E v11.175 — Chat creates a project from a reusable starter (2026-10-30)

Embedded **§ Chat** can create a named blank project or a new project from an advertised starter, then open it in §E. The new project is an independent editable copy; the original starter remains available for the next project. Chat receives the actual open project's name, starter, current level, workspace and selection before its next request, so work can continue on the project visible in the editor.

Before opening the copy, §E saves the preceding workspace **on this device**. The new copy is saved locally too; a storage failure stops creation or reports the recovery result. **Projects → My Projects → On this device** lists local copies, and identified projects autosave native edits in this browser. Use **Save to account** separately to sync a complete project through the connected Google account. Local copies can be lost when browser data is cleared; creating a project does not publish it to Google, GitHub or a live site. Copy-specific workspace drafts and exports use the new project identity, and listing reads at most 1,000 project names without loading all saved scene bodies.

For the first reliable command path, supply an exact advertised starter and a quoted project name, for example: `Create a new project from the Blank scene starter named exactly "My Starter §§".` A bounded command resolver uses that current catalog and the same native validation/receipt flow. Two actual pinned Qwen7B planner probes redundantly asked for clarification despite the supplied name; those failed probes remain **REPAIR_REQUIRED**. The command path improves orchestration and does not establish improved model weights or general project-building competence. Ambiguous or compound requests retain the typed planner/clarification path.

Current source seal: **207 ordered patches**, **68 packaged assets**, **7,022,679 HTML bytes**, SHA-256 **`0510e556b49cd94a3d1f89b264c194542476bc26c96169f3c6b8177301d482ff`**. Creation is one native action with an actual completion receipt. Further changes use fresh context and the active editor connection for the newly opened project; standalone Chat has no editor access. The update preserves v11.174 phone layout and earlier project/dialog/header features. Exact sealed desktop and phone native-browser checks and Chat source CI pass. The separate Chat/§E publication results and remaining owner acceptance are recorded individually in the [project workflow checkpoint](https://github.com/kaministrator999-ui/Swrlzkamico/blob/main/docs/engineering/entries/2026-10-30_CHAT_FORGE_PROJECT_WORKFLOW.md). The checkpoint distinguishes source verification, publication and owner-device acceptance.

## §E v11.174 — full-height phone editor and usable mobile controls (2026-10-29)

Normal phone mode now stretches the existing editor canvas to its workspace instead of collapsing it into a short strip. Mobile Outliner/Inspector buttons sit below the measured Project Levels toolbar, and their drawer opens below the buttons. Narrow screens hide desktop keyboard hints, the stale build stamp and duplicate actor statistics; the native selection badge remains at the bottom. The Chat panel starts 48px below the top edge to leave room for the observed Hugging Face provider badge. This does not guarantee every provider wrapper layout or repair the separately observed unstyled outer Hugging Face page.

The repair uses the original scene, renderer and resize handling, with no new render loop. It preserves v11.170 My Projects and Starter Projects tabs, v11.171/173 dialog layering, v11.172's clean embedded Chat header, desktop layout, native Play fullscreen and existing Chat/account assistance. Focused Chromium checks cover canvas/workspace geometry, real Inspector clicks and taps, project changes, resize and adjacent Chat controls. Their actual results, deployment evidence and owner-device disposition are recorded in the [mobile repair checkpoint](https://github.com/kaministrator999-ui/Swrlzkamico/blob/main/docs/engineering/entries/2026-10-29_FORGE_MOBILE_VIEWPORT.md); source publication alone does not establish physical Android or Google-account acceptance.

Current source seal: **206 ordered patches**, **68 packaged assets**, **7,008,228 HTML bytes**, SHA-256 **`1254e78c5bfd0d55a940f0e7d7c5fd590c325f89d4a45dc893b54f0f76fb9ce4`**. Use `scripts/verify_v11_174_release.py` and the existing separate final request-only deployment lane. Earlier release sections remain historical records; their normal-phone canvas layout is superseded by this repair.

## §E v11.173 — Projects dialog above editor docks and Chat (2026-10-29)

**Owner Android screenshot:** the right Details panel covers the active Projects modal. The v11.171 z-index fix was inside an editor stacking context; numeric priority alone cannot escape its ancestor.

**Correction:** Ordered append-only patch **205** (patches/v11_173_dialog_stack.py) and runtime/editor_layer_priority_v11_173.{js,css} reparent the original #projectHub node into document.body. Identity, listeners, Starter/My Projects tabs, default checkboxes, cloud/local Save and Load are retained. Layer order: viewport < Outliner and Details docks < Chat < modal Projects dialog and native modal dialogs. No gameplay, LAN, Quest, model, authentication or Chat backend changes.

**Verification:** [Focused tests and measured complete rebuild](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40967053619) SUCCESS, including dialog portal identity, idempotence and layer ordering. The 205-patch generated HTML is **7,005,338 bytes**, SHA-256 `7f02848d00e954a5358db4a62e3c1a72b454866e54585d436e962f156ff3797a`, with the original **68 assets**. Separate sealed verification and final deployment are pending at this source checkpoint. Owner Android/Quest UI acceptance remains DEVICE_TEST_PENDING.


## §E v11.172 — clean embedded Chat side-panel header (2026-10-29)

**Owner screenshot/request:** the redundant external **Open Chat** link sits immediately beside the **§wyrlz Chat** title inside §E's already-working Chat panel. Remove that link only; keep the X/Close, launcher, Google Sign In and existing account project controls.

**Implementation:** append-only engine patch **204** (`patches/v11_172_clean_chat_header.py`) removes the unique external-link anchor from the canonical embedded `runtime/chat_account_panel_v1.js` host as the source is assembled. No redesign, new account storage, authentication changes, Chat deployment, model updates, Sheep Tag mechanics, Project Hub/tabs, Quest interface or existing actions modified.

**Verification:** focused [CI 40962520717](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40962520717) succeeded: reconstructed full 204-patch HTML has no redundant link and retains side-panel Close, Google authentication, project Load/Save, and My Projects. Rebuilt engine measured **7,003,719 bytes**, SHA-256 `6037f52db537508b3c338b72bee4ac915498adf55589b8386c76394459ac9e2b`; **68 assets** retained. Sealed release CI and Hugging Face deployment are distinct subsequent gates. Real owner-phone acceptance is separate.

## §E v11.171 — Projects dialog foreground priority on Sheep Tag (2026-10-29)

**Owner screenshot:** in portrait Android, Sheep Tag's main/start menu overlaps the native Projects dialog and its **My Projects** tab. Root source: native `.project-hub` uses z-index 30; v11.143's canvas-hosted Sheep Tag runtime overlay uses z-index 3900 (some historical menu rules up to 4200). Projects should be in the foreground when open.

**Correction:** append-only patch 203 introduces `runtime/project_hub_layer_v11_171.css`, scoped to `#projectHub.project-hub.show`: `position:fixed`, full inset, isolation, and z-index 20000. The modal outranks viewport menus/HUD, but stays below the separate Chat panel. Closing the modal removes the selector and reveals Sheep Tag unchanged. No menu rerouting, controller change, gameplay mutation, game camera, LAN, save file, Google account, or Chat backend changes. Existing starter-project checkboxes and My Projects account transport remain the same.

**Source evidence:** [focused stacking test and full build measurement](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40960856304) SUCCESS. 203 historic patches rebuild to **7,003,771 bytes** / SHA-256 `c20a884ef7b690b03c98b28e74b896c9ac9cceeadb105561abd65ea7730d657e`; the original 68 assets remain. Dedicated sealed release CI and deployment receipts are separate. Physical Android/Quest visual and touch acceptance remains pending and cannot be inferred solely from the source test.

## §E v11.170 — Starter Projects + My Projects tabs (2026-10-29)

The existing native **Projects** dialog now includes two tabs: **Starter Projects** (original starter cards, default-project checkboxes and local Save/Load unchanged) and **My Projects** (the current Google/Chat account's saved project library). A connected user can refresh the library, inspect a project's stored revision and choose **Load**. If Chat has not connected, My Projects initializes the existing Chat-origin bridge and offers **Open § Chat / Sign in** rather than pretending to have an account.

My Projects uses the canonical v11.169 `cloud.list` and `cloud.load` authenticated RPCs and the **same native loadCloud importer**, preserving the unsaved-local-changes confirmation, full native scene import, recovery snapshot, Model Atelier reopen and server-enforced account ownership. The list clears on account status changes/logout; names are inserted with `textContent` and are never interpreted as HTML. No new credential store, project database, AI mutation privilege, external server, or automatic cloud deletion is introduced. The feature works in the native picker, independent of whether the Chat side panel is visible once its transport is connected.

**Exact source:** ordered patch **202**, original **68 assets**, generated HTML **7,003,123 bytes**, SHA-256 **`3c54fd230c18967d975fab314d37a23d8b2b0e462ab3143226a733b802ff07a6`**. Focused Node/jsdom UI test passed: starter node identity and checkbox retention, My Projects list, literal project title safety, Load handoff, tab changes and account-clear behavior. The first candidate measured an incorrect CSS insertion count because the historical HTML includes two `</head>` text occurrences; a bounded correction inserts before the first actual document head. Final complete build, SHA/assets verification and production release have their own gate. Real-account Save/Load on owner Android/Quest remains **DEVICE_TEST_PENDING**; no user account data was accessed during synthetic tests. The Chat Space and runtime/LALM versions are unchanged in this §E-only feature.

## §E v11.169 — shared Chat account and native editor assistance (2026-10-29)

The **§ Chat** button opens the full existing Chat in a responsive side panel. **Sign in with Google** opens the Chat account window; connect the same account to load its Chat history and explicitly saved preferences. **Save to account**, **My projects** and **Load** preserve complete native project snapshots through separate encrypted storage (96MiB raw maximum). Local editing and native downloads remain available without sign-in. After a reload or expired connection, reconnect the account in the popup; credentials stay in Chat-origin memory.

Chat can inspect the active workspace and request supported native Model Atelier mesh add/set/select/duplicate/remove or scene prefab add/transform/select/rename, plus native Undo/Redo. The server requires a fresh account/thread/project-bound editor lease; the host executes fixed native handlers and returns actual results. Closing/hiding the panel, changing project/thread or expiration revokes access. Standalone Chat has no editor mutation grant. No model JavaScript, general method execution, cloud deletion or deployment is exposed. Unsupported/stale/partial edits do not become success. Literal object names stay text, including in the mobile inspector.

Preserves v11.168 Quest controls and all preceding gameplay/LAN/project source. Ordered patch201; generated HTML **6,995,807 bytes**, SHA256 **1c484cf4f627a87c95d720d11fabfe1fb9005f114c2a7712b67f7474222a3d84**;68 packaged assets. The minimal deployment verifier checks the exact package and separate final request identity; no broad game/browser suite is added to production deployment. Source tests and controlled desktop/mobile native and canonical Chat browsers pass. Exact CI, deployment/runtime observations and remaining real Google/deployed-storage/owner-device acceptance are tracked in the [release checkpoint](https://github.com/kaministrator999-ui/Swrlzkamico/blob/main/docs/engineering/entries/2026-10-29_CHAT_FORGE_INTEGRATION.md). Existing Chat and §E release lanes remain separate.



## §E v11.168 — Quest 2 Meta Browser adaptive 2D editor (2026-10-28)

Owner requested controller-friendly operation of §E in Meta Quest 2 Browser without regressing phone/PC. Meta Browser supports a resizable 2D Chromium window (desktop/mobile modes); that panel's mouse/pointer/select events are NOT WebXR XRInputSource 3D rays. Full immersive WebXR would require explicit session and renderer/scene/controller integration and is **not** represented as implemented by this patch. Meta's browser guidance recommends controls at least 48×48 CSS px, focus feedback, and feature-checking `navigator.xr.isSessionSupported('immersive-vr')` rather than relying on a user agent for capability.

**v11.168 implementation:** Ordered patch 200 adds `runtime/engine_quest_panel_v11_168.{js,css}`. For 2D presentation only, an OculusBrowser+Quest UA hint opts into `se-quest-panel`; other screens get a coarse-pointer/viewport profile without changing their existing UI. A native top-bar **🥽 Quest UI on/off** toggle locally saves on/off/auto, and works on other browsers for testing. Larger 48px controls and visible focus cues are scoped to editor toolbar/Model Atelier; actual Sheep Tag joystick/HUD and Three.js world raycasting are untouched. Dynamic viewport resize updates the profile. `SWYRL_ENGINE_DEVICE.read()` exposes detected profile, last browser pointer type, viewport and separately feature-tested immersive-VR support; does not request XR or fabricate controller tracking. No new renderer, animation loop, gameplay/network state, Space or deployment workflow.

**Validation:** Focused Node VM device-profile test PASS (Quest desktop/mobile UA, saved toggle, phone/PC, pointer diagnostics, resized Quest panel). Local Node syntax and Python patch smoke check PASS. Physical Meta Quest 2 visual selection, precision 3D drags and the fully immersive WebXR path **not yet accepted**. Full package build occurs via existing guarded engine deployment. Preserve v11.167 authoritative Sheep Tag movement, restricted construction preview, 199 preceding ordered patches, all shipped assets and dedicated engine-only HF target. Do not infer active headset behavior from desktop mock tests.


## §E v11.167 — Guest joystick updates host movement; central no-build previews stay invalid (2026-10-28)

Owner's actual Android LAN guest screenshot (after concurrent v11.165 frame batching and v11.166 visual input prediction) shows `joystick idle · TX 129 · host ACK 66 · host moves 0`, a green House preview within the protected central arena region, and a sheep that only appears to move in a small circle when pushing the joystick. v11.166 intentionally predicted up to 0.8 terrain units **visually only**; when host movement is absent, this can look like a brief local wiggle with no actual translation. Real game movement and collision must still be applied by the host.

**Root source defects and fix:**

- v11.162 guest `stCanBuild` fallback converted many failed native placement validations into `ok:true`. It was not limited to stale guest data, and could turn the Spirit Pen, no-build zones, static obstacles or existing house footprints green. v11.167 uses the native `se162OriginalCanBuild` on the guest for the preview and preserves full host validation on command execution. Restricted ground stays red; no speculative local houses.
- v11.155 host applied network guest movement only once at the ~130ms world snapshot, distinct from native frame simulation. v11.167 moves only registered guest-owned sheep on every native host `stUpdate` step, including v11.164 background-host fallback steps. It bypasses v11.155's extra snapshot movement step to avoid double movement. Movement uses host `stBlocked` plus constrained tangent slides and preserves accepted construction approach orders.
- On mobile, after the original joystick pointer handler updates direction, guest sends seq-numbered `guest-stick-v2` intents on pointer changes (roughly 65ms throttle) and immediate release, through the existing verified PeerJS connection. The 115ms game heartbeat is retained as a fallback. No invented local authority, extra game server, or new render loop.
- Actual host movement reason, joystick strength, input age and blocked counts piggyback in the existing host world packet; the guest badge and `SWYRL_ENGINE_LAN.guestControlV167()` distinguish movement from idle/stale/collision/invalid-seat cases. Stale visual wiggle without corresponding host movement can thus be diagnosed precisely.
- Existing v11.165 fog/house frame optimizations and v11.166 local visual prediction are **preserved**, without symbol collision (new module uses `se167`). Other LAN discovery, building, wolf countdown, fog and HUD systems unchanged.

**Focused deterministic JS check:** native host move produced movement; old snapshot tick did not move again; blocked central placement remained invalid; guest joystick press and immediate release were transmitted as real sequenced inputs. PASS. Physical two-browser acceptance pending. Source manifest adds patch 199, all existing engine assets retained. Dedicated GitHub Actions remains **package + Hugging Face upload only**, with no Chromium, browser testing or remote audit.



## §E v11.166 — More responsive guest-controlled sheep (2026-10-28)

Owner reported that guest Sheep Tag felt somewhat laggy even after multiplayer discovery, house construction and movement fixes. v11.165 had already reduced CPU/GPU work through coalesced fog draws and caching unchanged house replicas and was successfully uploaded. This next change addresses **input-to-visual-motion latency**, especially when the host background browser sends snapshots infrequently.

`runtime/sheep_guest_input_visual_v11_166.js` only biases the already-running v11.161 guest visual interpolation target toward the player's held mobile joystick. The on-screen sheep may anticipate up to **0.8 terrain units**, never moving the authoritative host actor or generating local building/physics commands. The per-frame host anchor is restored immediately; prediction is disabled on collision, capture, pause, end of round, pre-release wolf and invalid input. Normal packets correct the displayed sheep back to the host position, and releasing the joystick smoothly converges without persistent drift. No additional timers, packet traffic or render loop. The v11.165 batched fog and cached house work remain intact.

**Focused V8 test:** Held joystick moved the local visual sheep ~0.75 world units with no host positional updates, original authoritative track remained exactly unchanged, releasing returned it to zero with smooth convergence, a blocked prediction had zero movement, and host role was untouched. PASS. This is a *visual latency improvement*, not a guarantee of actual network latency or that a fully background-suspended browser can continue hosting. On-device acceptance pending. `SWYRL_ENGINE_LAN.inputResponse()` exposes assisted frames, maximum lead and suppressed collisions. Prior shared game state and all 68 assets unchanged, cumulative patches 198. Production deployment remains build/package and Hugging Face upload ONLY, without Chromium or extra audit jobs.



## §E v11.165 — Batch guest fog updates and cache unchanged houses (2026-10-28)

Owner's real two-browser v11.164 test now confirms genuine guest building completion, both displays show 36/36 authoritative houses, and host background catch-up works, but the guest game looks laggy. At the previous code level, three separate guest synchronization layers requested full team fog painting during every 130-ms host snapshot, each walking the entire flock and up to 36 houses, drawing radial gradients, rebuilding team exploration masks and uploading a fog texture. The canonical host building reconciler also wrote all house properties/transforms/mesh heights on every packet even when no host state had changed. Those main-thread tasks compete with the existing guest requestAnimationFrame.

**Optimization:** Add `runtime/sheep_guest_frame_performance_v11_165.js` as an append-only patch. On guest only, coalesce multiple fog paint requests into one paint on the *existing* guest animation frame and limit routine paints to approximately once per 235ms; paint immediately after changes to live team unit count, current role/fog mode or active building count. Preserve native fog/exploration implementation, wolf release visibility and team vision. Cache authoritative building state signatures per host ID, and short-circuit unchanged live models that are still mounted in the game scene; changed HP, progress, ownership, building kind, location/rotation and other fields still use the verified canonical reconciler and v11.163 host-driven growth. Prune cache when host removes structures and clear all on game-stop or session restart. Avoid creating new renderer, timers or a network service. Diagnostic `SWYRL_ENGINE_LAN.performance()` reports measured frame FPS, network packet update cost, fog paints/coalescing and unchanged house cache hits. Guest LAN badge adds compact FPS and snapshot processing milliseconds.

**Focused 36-building stress test:** 60 host world snapshots, 480 guest render frames: 2,160 possible state writes became **37 actual changed state applications**, while 180 full fog requests became **32 paints**. All 60 packets and 480 frames processed, no mock errors. These are simulated JavaScript counters, not measured real-device latency or proof of higher user FPS. Physical acceptance pending. No changes to v11.161 movement algorithm, v11.162 guest building commands, v11.163 real house construction progress, v11.164 background host clock, live LAN game search, fog logic or wolf rules. 197 historical source patches with all assets preserved. Production GitHub Action remains **package → Hugging Face upload only** and does not run Chromium or extra remote tests.



## §E v11.164 — Host background gameplay keeps construction progressing (2026-10-28)

**Actual device evidence:** Owner's two-browser screenshot shows LAN guest received host world frames and all **12/12 houses**, but an active house reads **building 9% host / 9% shown · progress stalled**. This disproves the earlier idea that the guest lacks a building replica: authoritative **host simulation** is not progressing. The game's render loop ordinarily calls native `stUpdate(dt,t)` and advances sheep movement, pathing and house progress. When one Android browser is foregrounded as guest, the other browser running the host may have its `requestAnimationFrame` paused or heavily throttled. The separate 130ms host snapshot interval can remain active and keep sending the same stalled construction data.

**Fix:** `runtime/sheep_host_background_sim_v11_164.js` wraps the *existing* host `se152Snapshot` timer. Before the host constructs the next network world packet, compare monotonic session time that the native animation already advanced with wall-clock passage since the last snapshot. Only when native simulation falls behind, execute the **same native `stUpdate`** in capped 50ms steps, at most three seconds/60 steps per timer callback. This progresses actual accepted build routes, actual sheep physics and house construction rather than painting fake completed houses on the guest. Normal host rendering does not double-advance; paused, stopped or completed games do not accrue catch-up debt. Native match rules and existing camera animation are unchanged. A small `hostSimClock` diagnostic piggybacks on real world snapshots; guest HUD may show "host background catch-up", and `SWYRL_ENGINE_LAN.hostSimulationClock()` exposes counters and mode.

**Testing:** Focused deterministic JavaScript test without host animation frames: 9% native house reached 100%, all snapshots reflected actual host progress, no foreground double ticks, no pause catch-up debt — PASS. This is not a physical two-browser acceptance. **Limit:** If Android fully suspends all JavaScript in the host tab, browser code cannot keep the match running until it is resumed; a separate always-on network game authority is required for that level of reliability. No guarantee of fully persistent hosting is made.

Continues v11.161 smoother guest movement, LAN automatic host discovery, canonical guest houses, fog, wolf countdown and original game mechanics, retaining all assets. 196 cumulative append-only patches. Only the established GitHub build/package → Hugging Face upload workflow; no Chromium, remote audits or new server.



## §E v11.163 — Guest buildings grow visibly with authoritative construction (2026-10-28)

Owner's newest Android screenshot shows two real houses in the multiplayer world but one stuck as a flat roof/foundation after several attempts. The guest correctly mirrors buildings (HUD houses 11/11), so the problem to investigate is visual **progress/height**, distinct from model existence. Native Sheep Tag farms use approximately 1.4 seconds of host time to construct; a newly built house initially stands at 15% scale, then grows to its full original mesh height. The prior guest mirror set static progress on snapshots but didn't animate the growing model on each actual guest render frame.

`runtime/sheep_authoritative_growth_v11_163.js` reads authoritative **host-supplied** progress for each real host building ID after world replication, updates the guest model's original base height and uses the **existing v11.161 guest requestAnimationFrame** to animate intermediate growth. Prediction is capped to one snapshot interval and never declares completion when host progress is stagnant. It immediately enforces full model height when the host reports progress=1. Adds a compact LAN badge construction readout `building HOST% / SHOWN%` and `SWYRL_ENGINE_LAN.constructionProgress()` to distinguish stalled host simulation from stuck guest mesh. On an authoritative **rejected** building placement, restore the user's House placement mode and show the host's reason to avoid repeated skill re-selection; no automatic host retries or client-generated fake buildings.

Focused, deterministic V8 test passed: model height .15 at 0% host progress, .4475 at 35%, intermediate .4779 visual scale during interpolation, and exactly 1 at 100%; rejected-site restored House with actual rejection text. This is **not** physical multiplayer acceptance. Preserves automatic live game discovery, v11.161 continuous smooth guest motion, native host gameplay, authoritative building ownership, team fog, wolf timing and all 68 assets. Patch 195 appended; deployment remains GitHub build/package + HF upload **only**, no Chromium or remote verification.



## §E v11.162 — Reliable LAN guest house orders and real host receipts (2026-10-28)

Owner confirms v11.161 restored smoother multiplayer guest sheep movement but guest house construction still fails. The actual host code at v11.152 applies a 36-ms `peer.lastInput` throttle to *every* packet, including a discrete `world-command: build`, so build taps arriving immediately after joystick data are silently dropped. Client-side construction preview also validates against potentially stale/smoothed guest positions, which can reject sites before ever asking the authoritative host.

**Fix:** Introduce a narrow room/match/registered-peer-bound host-side build command handler in `runtime/sheep_reliable_guest_build_v11_162.js` that bypasses the joystick throttle for builds only, calls the unchanged native `se152BaseCommand('build', payload)` with the actual guest sheep bound, and returns explicit accepted/rejected results with validated request IDs. Once the native sheep reaches the building site and `stNewBuilding` creates an actual house, send a **completed** result with that real host ID. Preserve v11.160's immediate real-building model broadcast and v11.157's canonical authoritative snapshot reconciliation. A guest's preview is only advisory if its local world is stale; the host still enforces all actual structure rules, resources, geometry, paths and bounds. On acceptance, clear prior stale joystick intent so it cannot cancel the active construction order. `SWYRL_ENGINE_LAN.houseOrders()` surfaces guest send/accept/reject/complete and host pending/accepted/completed telemetry, including reasons. Never treat a local click as a built house.

**Focused JS test:** Host accepted a build even with a fresh `peer.lastInput` (throttle collision), sent real completion only when the native building was created, rejected an invalid path with reason, cleared stale joystick, and let an otherwise stale local preview reach host validation. PASS. No physical dual-browser acceptance yet. This adds patch 194, with prior v11.161 continuous guest motion, live discovery, player seat ownership, fog and wolf countdown unchanged. HF GitHub Action remains **package + upload only**, no Chromium or remote verification.



## §E v11.161 — Continuous LAN guest movement regression correction (2026-10-27)

Owner confirmed v11.159 live lobby discovery and one-tap join work, but guest sheep motion returned to a step-stop-step-stop pattern in v11.160. Root code issue: v11.156's renderer restarts a smoothstep `ease-in/ease-out` transition at each incoming ~130ms authoritative position snapshot. That imposes zero velocity at every transition boundary, especially visible under network jitter. The guest also runs visual updates through both a native `stUpdate` wrapper and an independent requestAnimationFrame callback.

**Fix:** `runtime/sheep_continuous_guest_motion_v11_161.js` replaces the per-packet restarts with continuously tracked host position and velocity, a short capped extrapolation across jitter, and exponential position/heading correction on the existing guest requestAnimationFrame loop. The redundant native guest visual update is suppressed; host remains the sole gameplay authority and no new loop or server is created. Discontinuous jumps are safely snapped back to host positions. Captured actors remain handled by the existing wisp system. Existing lobby discovery, guest control, construction mirroring, team vision, and wolf countdown are unchanged.

**Focused test:** 85 frames with 11 authoritative snapshots, 62/62 consecutive positive-motion frames after startup, no backwards steps, no duplicate native guest updates — PASS. This is a deterministic JS simulation, not a two-device acceptance result. Release adds append-only patch 193, maintains the 68 asset files. GitHub Action stays build/package and HF upload only; no Chromium or remote asset verification.



## §E v11.160 — Guest building visibility and timed wolf release (2026-10-27)

Owner live-multiplayer report: guest sheep orders a structure and it appears only in the host's game; wolves already stand in the arena as soon as LAN Gameplay starts even though the release/head-start countdown has not finished. This patch retains real host-authoritative simulation, guest movement smoothing and canonical building snapshot reconciliation.

**Construction delivery:** On actual host `stNewBuilding` creation (not on a local preview or speculative tap), broadcast a room/match-scoped `world-building-created-v2` event through the established WebRTC guest channel. The guest renders the authoritative model and host ID, maps the owning sheep and reattaches/shows its real mesh if fog or legacy scene handling hid it. The regular full world snapshot remains the source of truth and continues resolving missed events. Guest ghost clears only after host construction is confirmed. Guard against the older v11.153 joystick handler overriding an active guest sheep `build` approach order; native building validation and navigation remain on the host. Diagnostic `SWYRL_ENGINE_LAN.constructionRelease()` tracks building created/sent/received/rendered counts and current head-start wolves.

**Wolf release:** The native start still creates the wolf gameplay units and keeps the existing collision/AI/head-start rules, but wolf models are hidden on both host and guest until the authoritative `elapsed >= headstart` release moment, even when fog/vision passes repaint visibility. At release they become eligible for visibility according to team fog. No pre-release wolf controls or attacks.

**Verification boundary:** Focused JS source and event test passed: wolf model hidden before timer, shown on release, host building message emitted, guest received and rendered a real house. Physical dual-browser acceptance pending. 192 append-only engine patches, all 68 historic assets retained. Production GitHub Action remains checkout/package/upload to the dedicated HF Space only—no Chromium or remote verification workflow.



## §E v11.159 — Automatically discover live hosted Sheep Tag lobbies (2026-10-27)

**Owner request:** Local LAN game search should automatically list currently hosted live games and allow joining from a single entry in the game browser, eliminating the need to exchange an invitation code when discovery works.

**Runtime:** `runtime/sheep_live_lan_directory_v11_159.js` hooks the existing `Local LAN` browser. On the hosted HTTPS Space, it starts a real expiring live-directory subscription. Hosts advertise an open PeerJS room every ~5.5 seconds, respond to new viewers' probes, include actual lobby seat occupancy, and withdraw listings when the host closes the room or starts the match. Viewers see genuine waiting rooms and use **Join**, which delegates to the already working `se151JoinGame()` PeerJS handshake; an advertisement never marks a player connected. Stale rooms expire after 18 seconds. Full rooms do not allow joining. The existing one-code manual invite path stays available.

**Important network truth/privacy:** Browser HTTPS cannot scan arbitrary local IPs or read Wi-Fi SSIDs, and free PeerJS Cloud peer enumeration isn't available without permission. For public HTTPS only, discovery uses an unauthenticated public MQTT test broker `broker.emqx.io` over WSS and a topic based on the hash of clients' public IPv4 egress fetched through `api.ipify.org`. This groups devices sharing an internet exit (often the same Wi-Fi), **not a cryptographic privacy boundary or proof of local LAN membership**. The public broker learns participants' connections and can carry visible room IDs/counts; it is a prototype/testing dependency, not a production directory. Users on mobile cellular and shelter Wi-Fi will likely be in different groups, and can still exchange an invite. If third-party endpoints are blocked, manual one-code join continues functioning. Never claim the browser scanned a private subnet. The old `scripts/lan_bridge.py` separately provides actual UDP/subnet discovery when the engine is served from the local HTTP bridge.

**Focused code test:** JS syntax PASS, host open announcement emitted, another browser's valid room parsed, invalid IDs excluded, closed rooms removed, and match-start advertisement withdrawn. Real cross-device directory visibility remains **pending owner acceptance**. The feature does not alter v11.155 player movement, v11.157 structures, v11.158 death/seat state, or any native game simulation. 191 historical engine patches, 68 artwork assets unchanged. GitHub deployment remains strictly **package + HF upload**; no Chromium or remote audit.



## §E v11.158 — Guest retains their sheep when captured (2026-10-27)

Owner confirmed that the guest can complete buildings but, when tagged, seems to take over another sheep; after the last free sheep is gone they wind up watching a wolf. Root cause in v11.152: the host's `se152Roster()` discarded captured animals from its eligible player list and repeatedly reassigned live peers to other animals. In v11.158 a connected guest owns one reserved character ID throughout the match, regardless of capture. That sheep becomes their wisp until rescued and is the same sheep they resume controlling after rescue. It must not switch to another sheep or wolf without explicit role-changing behavior. Initial joining and disconnect allocation remain intact. Captured guest joystick commands are paused while the shared game continues; camera follow and capture feedback are retained.

Focused JS test: guest seat stable after capture, last sheep captured, and rescue — PASS. Source adds 190th append-only patch; confirmed guest movement smoothing, building replication, all assets and minimal build+upload-only HF workflow untouched. Physical guest-capture acceptance pending.



## §E v11.157 — Authoritative host buildings mirrored reliably (2026-10-27)

Owner's physical browser test confirmed smoother multiplayer sheep movement in v11.156, but structures ordered/constructed on the host still did not appear on the guest. Root code risk: original v11.152 three-kind mirror and v11.156 expanded mirror both mutate the same guest building list during each world packet. v11.157 leaves the existing host snapshot/gameplay simulation intact, suppresses both legacy creation/removal passes only while applying a packet, and then performs one canonical reconcile keyed by the host's building IDs. It renders actual houses, walls, ramps and other supported game structures, including owners, rotations, health and construction progress, and removes only structures absent from the host snapshot. No guest-side independent game simulation.

Guest HUD now distinguishes **houses guest/host** (visible list count against the host's authoritative snapshot), and programmatic `SWYRL_ENGINE_LAN.buildSync()` reports replica creates/updates/destroys/errors and guest build requests versus host-confirmed orders. This is network-source telemetry, not proof the house appears through camera/fog on user devices. Focused script passed creation, repeated update without duplicate, and removal. Owner two-device acceptance pending. Existing v11.156 movement smoothing and team fog remain; deployment workflow strictly package+upload to Hugging Face, no Chromium or remote audits. 189 cumulative patches and all assets retained.



## §E v11.156 · Smooth guest movement, complete building replication and team fog (2026-10-27)

Owner real two-phone test demonstrated shared authoritative movement but the guest visually stepped/stopped, guest build attempts showed only a ghost while the house built on host, and fog of war did not reveal the team's actual sheep-and-house sight. This focused patch reuses the existing native host world without any new gameplay simulation or server.

- Guest character positions are interpolated visually between 130-ms host snapshots, with bounded predictive lookahead and a guest-only visual animation callback; game AI and physics remain host-authoritative.
- Replicate all configured Sheep Tag structures (including castle walls, ramps and totems), their rotation, owner, construction progress and HP. Honor host-confirmed guest build orders and clear preview. Preserve native validation/build travel.
- Multiplayer sheep-team sight is the union of living sheep vision circles plus allied owned structures; wolf vision remains separate. Repaint the actual fog texture and exploration mask on guests even though the guest does not run native game simulation.
- Source adds the 188th ordered patch; all prior engine assets and the dedicated build-and-upload-only HF deployment workflow remain unchanged. Physical dual-phone acceptance is pending; focus test for remote wall replication and team-house vision passed.



## §E v11.155 — Host snapshot-tick guest movement fix (2026-10-27)

Field screenshot: guest TX 68, host ACK 34, host moves 0. The WebRTC receive/ack path works; host movement does not advance. v11.155 moves the registered guest's sheep on the already-running host snapshot tick, before broadcasting authoritative state, with collision checks, stale-intent timeout and no new simulation loop. The prior per-frame input movement path is bypassed to avoid duplicate movement. Focused JavaScript mock confirmed a guest sheep position change appears in the very next host snapshot. Physical two-browser verification pending. GitHub Actions remains build/package + HF upload only, per owner instruction.



## §E v11.154 — Guest movement transport diagnostics

Host now acknowledges the real guest joystick packets over the established WebRTC connection and moves the registered guest sheep in the authoritative simulation. Guest displays attempted TX separately from confirmed host ACK and applied movement frames. This avoids treating a send attempt as successful delivery. Shared host world and existing 68 assets remain. Minimal HF package/upload deployment only; physical acceptance pending.



## §E v11.153 — Guest joystick movement

Guest-held mobile joystick sends bounded direction over the same existing WebRTC connection and the host advances the assigned guest animal in its authoritative gameplay frame. Live diagnostic counters distinguish send/receive from movement. Physical-device verification still pending. HF deployment stays build + upload only.



## §E v11.152 — Shared host-authoritative Sheep Tag world

The host now runs one native authoritative Sheep Tag simulation. WebRTC guests receive 130-ms snapshots of units, captured wisps, buildings, construction, resources and timer, with input commands and mobile movement sent back to host and validated there. Guests are assigned distinct playable animals and must not run their own separate AI or economy. Public PeerJS Cloud is used only to introduce WebRTC peers, not to host the game simulation; each peer needs connectivity to the host. Untrusted Wi-Fi may block connections. Source includes 184 cumulative patches. Deployment remains package + upload only; physical two-device acceptance is pending.


## §E v11.151 — One-code lobby (2026-10-27)

Host creates one invitation; guest enters it once. PeerJS Cloud performs the WebRTC signaling, and the guest appears in an occupied seat when the direct channel opens. No manual answer code. Cloud signaling requires internet access; client-isolated Wi-Fi or blocked peer traffic may prevent connections. Start Match launches local Gameplay on connected clients, but movement, houses and combat are not network synchronized. Production GitHub Action now only packages and uploads §E; it does not run Chromium, inspect remote assets or poll the live site.

## §E v11.150 · Host-authorized Sheep Tag match launch (2026-10-27)

**Owner request:** After a laptop/phone join the same Wi-Fi WebRTC waiting room, the host may press **Start Match** to transition the host and connected guest browsers out of the menu and into each device's native Sheep Tag Gameplay level.

**Implemented:** `runtime/sheep_lan_match_start_v11_150.{js,css}` with `patches/v11_150_host_start_native_match.py` enables Start Match only once a verified WebRTC guest is connected. The existing host-controlled data channel delivers a room-matched, unique match-start command. Menu teardown preserves the peer connection; native Stop cleans up and host announces match-end. No new renderer or custom game mode. Original independent editable Main Menu and Gameplay, all existing animal/gameplay logic, and all 68 packaged assets are preserved.

**Truthful gameplay limitation:** This is **coordinated game launch**, NOT synchronized multiplayer. Each client runs its own local gameplay simulation; sheep positions, wolf positions, house placements, abilities, attacks, and physics are not yet replicated. Browser-peer invite exchange remains manual, Wi-Fi may restrict direct WebRTC traffic, and optional Python LAN Bridge players do **not** gain this match-start feature through their distinct protocol. Physical Android/laptop acceptance remains pending.

**Exact candidate seal:** 182 ordered patches; 6,833,482 generated HTML bytes; SHA-256 `2eb170d15eca9046d7116d76baeea7620246f41e1f46d2dc17b1dab66ce1fc54`; 68 verified assets. [Real Chrome and host/guest tests](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40540706814) **SUCCESS**, including actual menu Gameplay transition, direct channel guest-start receipt, editor Stop, and source rebuild. The first simulated Play tap failed in the automated test while a direct DOM click passed: treat this as a test-click limitation, not proof that all real touch hits work.

**CI efficiency correction:** Branch pushes now run focused start-module tests; the expensive exact-source build and Chromium session require an explicit `[verify-release]` commit. The guarded production deploy performs its own full build and hosted-source audit. Do not launch full compilation and browser runs on each debugging edit.

## §E v11.148 · Host-owned Local LAN waiting lobby (2026-10-27)

**Owner order of work:** Before synchronized Sheep Tag multiplayer, Host Game opens a waiting room with joinable slots and the hosting player in charge. The editor's static Main Menu and Play's 3D cinematic remain separate presentations; visual parity is deferred, not silently altered.

**Implementation:** The optional LAN Bridge maintains an eight-seat roster: host in seat 1 and up to seven real guest seats, with names, stable seating, admission cap, 45-second heartbeat expiry, leave and host-close actions. GET /api/lan/lobby provides the authoritative roster; /api/lan/join, /api/lan/pulse and /api/lan/leave operate on real LAN registrations including discovered same-subnet host proxying. The browser opens a dedicated responsive waiting room after Host Game or Join Lobby and displays occupied/open seats, headcount and host/guest authority. Only the actual bridge host may close its lobby.

**Truthful boundary:** No synchronized game-state, physics or match-authority transport exists yet; Start Match stays disabled instead of launching a misleading local-only match. The public HTTPS Space cannot host private LAN sockets; a trusted device running the existing local bridge is required. No extra engine/physics loop or replacement mode. Main Menu and Gameplay maps and the original 68 historical assets are unchanged.

**Measured source:** §wyrl§ Engine v11.148, 180 ordered patches, 6,814,236 HTML bytes, SHA-256 94bbd9594a9d76b0c9b83140877414d21800fb75e93d364d6ee99426c2da14ea. Dedicated candidate validation https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40522003917 SUCCESS, including older LAN tests, new HTTP/slot tests, exact source/68-asset build and real 412×915 mobile Chromium Host → Guest joins/leaves → Close → restored editor. Owner Android and two-real-device LAN acceptance are independent gates.

**Deployment gate:** Branch validation does not prove production. A final guarded DEPLOY_REQUEST.json release commit and exact hosted-source audit are required.

## §E v11.147 · Android Sheep Tag menu collapsed-to-top repair (2026-10-27)

**Owner visual evidence:** The actual Android hosted v11.146 screenshot shows the entire Start Game menu, 3D scene and Exit to editor squeezed into a short top strip over an otherwise empty black viewport; File/Edit/Outliner/Details/status chrome remains visible. This regressed after v11.145 introduced runtime `.viewport-wrap{flex:1;min-height:0}` in a layout where the WebGL canvas and menu overlay are coupled to the same editor workspace bounds.

**Change:** During native Sheep Tag Main Menu and Gameplay **Play only**, use the original `main.viewport-wrap` and `canvas#viewport` as a fixed full-viewport renderer host (CSS gated on `body.se145-runtime`) rather than relying on inherited editor flex sizing. On entering/leaving Play or switching to game, synchronously call the existing v11.143 menu-to-canvas fitting helper, trigger the original native window-resize handling, and refit once on next animation frame. Preserve original scene/camera and authored level data; do not add a second scene, renderer or game tick. Keep Start Game and Local LAN as scrolling centered menu content and place **Exit to editor** at the actual bottom edge. **Stop** restores editing because runtime styles are wholly scoped to a transient body class.

**Scope and acceptance:** Original 68 historical game assets, LAN bridge and browser logic, sheep/wolf actors, building validation, capture and animations unchanged. Include a targeted layout/resize/state regression plus prior menu/LAN/game tests. Source hash/hosted audit separate from real-device visual approval.



## §E v11.146 · Local LAN browser and actual discoverable lobby bridge (2026-10-27)

**Owner request:** Add Local LAN to Sheep Tag's cinematic Main Menu; entering it reveals Host Game above a browsing list of genuinely discovered LAN hosts, Refresh, and Back. Retain the original editable project/main-menu/game maps and Start Game.

**Implementation:** `runtime/sheep_local_lan_browser_v11_146.{js,css}` creates its own menu screen in the actual runtime overlay, with Host / Stop Hosting, browsed name/IP/player count, Join Lobby, Refresh and Back. It has no fake IPs or network scanners in the remote browser. A public HTTPS tab honestly reports that browsers lack direct subnet scanning/UDP/server privileges. `scripts/lan_bridge.py` is a standalone Python-standard-library **optional LAN host** serving the packaged engine on a private Wi-Fi HTTP address, with UDP 8766 discovery, bounded /24 HTTP probes to fixed local TCP port 8765, same-origin LAN APIs, host start/stop, lobby registration and peer listing. `LAN_BRIDGE.md` describes setup. The bridge serves the generated §e editor and assets, not an alternative game engine.

**Gameplay boundary:** Host/join/list are authentic LAN **lobby discovery and presence** only. **Networked synchronized gameplay is not implemented**; joining does not synchronize sheep, wolves, building orders, matches or physics. No remote API or paid service. That separate transport/state-authority step is required before multiplayer can be called playable.

**Source:** 178 ordered patches including `patches/v11_146_local_lan_browser.py`; preserve 68 historical packaged assets. Exact source HTML seal and build/deploy receipt are determined by `scripts/measure_v11_146_source.py`. Functional checks cover menu/back/HTTPS unavailable and local bridge HTTP hosting/security.



## §E v11.145 · Immersive Sheep Tag Play, stable house holograms, safer Rapid snap (2026-10-27)

**Android owner observations from v11.144:** Play shows editor toolbar over the live Main Menu and gameplay; the build preview rapidly blinks away/reappears while being moved; nearby red houses are rejected for narrow diagonal cracks even when a closely aligned, valid alternate footprint is available.

**Scope and behavior:** Play now suppresses editor-only topbar/menus/status bars while keeping native game HUD and a small visible **Exit to editor** control that invokes the original Stop flow. The independent authored Main Menu and Gameplay levels remain editable when Play ends. An invalid transient phone drag ray no longer destroys the live house hologram: it stays visibly **red**, never commits during invalid input, and resumes normal color after new native validation. The old periodic HUD reevaluation no longer overwrites the active placement pointer. With Rapid ON, near a narrow opening rejection, the candidate picker evaluates flush-corner and truly aligned neighbor alternatives within 1.65m, accepting only independently successful calls to the existing complete pre-v11.139 `stCanBuild` validation. Rapid OFF, occupied locations, build limits, resource checks, obstacles, safe 1.20m lanes, and the native building order remain authoritative. No additional render/game clock or custom game mode.

**Source and test evidence:** [candidate targeted CI](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40454261079) **SUCCESS**. Exact measured **177 patches**, **68 source assets**, **6,791,082 bytes**, SHA-256 `6448c1b8b004db9556b6760ed6987c4600c4ba0d19b1d38f35ddc29ae04ad206`. Package/JS parse, retained camera/menu/Stop/level/save tests and validator/Rapid/ghost state tests passed. Target is only `kamiloki/swrlz-forge-moba`; this source is not considered live or Android-approved until its own guarded deployment and verified hosted audit.



## §E v11.144 · Single menu launch control and cinematic rotating sheep portraits (2026-10-26)

**Owner Android feedback:** The newly visible Sheep Tag menu still presented redundant launch buttons in the editor header, and its orbiting camera did not visit the individual sheep.

**Implemented:** Keep the engine's native **Play/Stop** authoring controls and the interactive menu's large **Start Game** button. Retire the redundant **▶ Play Game** control from the Project Levels strip; the level selector, + New Map, Menu UI, linked Gameplay transition, and all save/load/export operations remain. During native menu playback only, the existing camera continues to orbit but now pauses over each of the three authored sheep in turn, eases between subjects on a seven-second schedule and follows their movement. Menu actors retain their existing chase, build, gait and wolf animation. The editor preview remains still, without gameplay state or a second simulation loop.

**Release candidate source seal:** **176 ordered patches**, **68 preserved assets**, **6,784,186 HTML bytes**, SHA-256 `f54aea74cafa0c024981390063eb6ec1da1d0301dbd90e4a13e31078b95d0a5a`, computed by reconstructing all patches on a GitHub runner rather than altering the source checksum by assertion. Patch `patches/v11_144_menu_sheep_camera.py`, runtime `runtime/engine_menu_sheep_camera_v11_144.js`, targeted independent test `tests/sheep_menu_portrait_camera_v11_144.mjs`. Deploy status is separate from source testing; hands-on Android visual acceptance remains with the owner.



## §E v11.143 · Visible main menu and editable level UI on mobile (2026-10-26)

The Start Game UI and Project Levels had been placed inside the actual 3D WebGL **canvas** element, where browsers hide HTML descendants as canvas fallback content. The menu simulation could be running, but its Start Game control was invisible and untappable. The level selector and editable title preview were similarly invisible.

**Fix:** Parent those existing controls to the real `main.viewport-wrap` element surrounding the canvas, with correct layering and touch targets. Press Play from Sheep Tag's editable Main Menu level to view the actual Start Game button on top of the animated authored 3D scene; tap it to enter independent Gameplay. Project Levels is visibly accessible during editing, while Stop and the native game/editor workflows remain intact.

Source target: 175 patches, 68 preserved assets, 6,781,776 HTML bytes; source SHA256 `97e662c9ec70e3e382a5130ff56b17e0a49f534bea5a53b3409dda9f03c05856`. Release gate tests actual Android-size Chromium touch and nonzero overlay geometry in addition to full source and Sheep Tag regression tests. Real-device acceptance remains with the owner.

## §E v11.142 · Stop button, visible Start Game and articulated actors (2026-10-26)

The project level selector no longer consumes the narrow top Play/Pause/Stop toolbar. It is placed in its own editor viewport strip. **Stop** stays beside Pause and can end a playing menu cinematic or the native gameplay match; when nothing is playing, Stop remains visible but inactive.

Opening the Sheep Tag starter keeps the separately editable Main Menu and Gameplay levels. **Play** on Main Menu now reliably opens its runtime title with the large **Start Game** button. **Play Game** in the level browser explicitly launches through Main Menu from elsewhere. Menu sheep and wolf characters animate their own authored leg/head/tail joints instead of only sliding at the root. Stop and Start Game restore all authored joint poses before editing or transitioning. No changes to gameplay physics, sheep building, wolf mechanics or the original assets.

Source seal: **174 ordered patches, 68 original assets, 6,774,378 bytes**, SHA-256 `c9c19fd57653f3d3e0a0ac6201c3bad90db56f3acac867d469275ff5de212696`. Synthetic CI and Android visual acceptance are separate.

## §E v11.141 · Independent editable levels and connected maps (2026-10-26)

**Architecture correction:** Opening the Sheep Tag starter now shows its authored **Main Menu Level in edit mode**—the cinematic does not play while editing. Its sheep, wolf, houses, trees and meadow are real selectable, movable and separately saveable scene actors. The menu's title, subtitle, button text/color and orbit speed can also be changed in **Menu UI**. Press Play to run the attract cinematic; tap Start Game to transition to the separately editable Grand Moonbell Wildwood Gameplay level and start native Play.

**All projects:** A project-wide **Project Levels** toolbar lists independent levels, offers **+ New Map**, level renaming, a **Next** connection and **Export Level**. Selecting a level loads its own editable scene without starting simulation. Save Project exports the full level collection as `project.levelPack` (schema `se-levels-v1`), with every level's data and connection; opening that saved project restores them. A connected runtime level exposes a Next Level control. Existing project types retain their native Play behavior.

All earlier Sheep Tag mechanics, map rules and 68 packaged assets remain intact. Source target: 173 ordered patches; the artifact byte count and SHA-256 are recorded in `source-manifest.json`. Tests validate level edits, creating/linking maps, save/reload, static editor state and native Start Game transition. Actual Android usability remains subject to owner acceptance.

## §E v11.140 · Sheep Tag starter 3D main menu (2026-10-26)

Open **Sheep Tag · Moonbell Meadow** to see a dedicated title screen with one large **Start Game** button over a genuine 3D cinematic: orbiting meadow camera, sheep running and constructing houses, and a scripted wolf chase/tag loop. The visual-only demo uses the existing engine frame; it never creates a real match or modifies authored map actors. Pressing Start Game cleans up the overlay/demo, restores the original camera, then uses the native Play workflow, including the correct actual seven-minute game with real bots, resources, and rules. Leaving the starter cleans up the temporary menu scene. All other editor projects remain unaffected.

**Sealed release:** 172 ordered patches, 68 original assets, 6,729,010 HTML bytes, SHA-256 `639cca010358ccf8a1c1c129ab1cfc99b45e32854ecd4802ff3d3610a32d39f7`. Source tests are separate from real Android visual acceptance.

## §E v11.139 · Safer, easier Rapid house corner placement (2026-10-26)

When a house hologram turns red beside the existing maze because of **"A diagonal crack is not a sheep passage"**, Rapid mode now tries a small automatic flush-corner adjustment. The ghost and actual order share the fully validated snapped site. The existing native collision and sheep-passage rules still reject blocked or unavailable positions; this does not make unsafe diagonal gaps passable. A correction more than the current safe lane width is not attempted, and Rapid OFF behaves as before.

Source target: 171 patches, 68 unchanged assets, 6,719,389 bytes, SHA-256 `f605af72628643e87d8fca5d97a08fcba438c43f2d9ffa693e4f6014032ce6fb`. Actual Android acceptance is a separate check.

## §E v11.138 · Rapid follows the last successful building's SCREEN position (2026-10-26)

With Rapid ON, the next house/ramp/walkway hologram now begins at the same relative position on the phone DISPLAY as the last completed order, not on the same old patch of ground. When the sheep or camera moves, the idle hologram is reprojected into the current world to keep its screen position, without silently placing a building. Dragging from anywhere in the meadow offsets that last screen position by finger movement. First Rapid build, regular builds and canceled placements retain existing behavior; disabling Rapid clears the memory. Native snap, costs, reachability, collisions, bots and multiplayer plans are unchanged.

Sealed target: 170 patches, 68 assets, 6,717,316 bytes, SHA-256 `384558ce7af5993f36ef002824455d850fdfebf635a881eea1fe4878931f7385`. Source audit and actual Android acceptance are distinct.

## §E v11.137 · Touch a house, then drag from anywhere on the meadow (2026-10-26)

On phones, dragging a hologram from its sheep-origin position while the finger begins on a bottom-right building button leaves too little travel room. **Touch/pen controls now use two intentional gestures:** (1) tap a house, ramp or walkway skill to select and show the ghost at the sheep; (2) touch anywhere on open meadow and drag the ghost from that new finger anchor, then release to build. A single meadow tap still places at the tapped validated site. The button gesture alone never builds. Desktop mouse direct drag is retained, and native placement and resource validation is unchanged.

Rapid Build continues selecting the same building after successful meadow placement, so players can repeatedly drag from different meadow starting locations without reselecting the button. No wolf changes. Verified source target: 169 ordered patches, 68 assets, 6,711,840 HTML bytes, SHA-256 `674354d6d9f0a0a324000161a002f31b47e56e8a1734f0b260b7adf8c48fa3ce`. Real Android touch acceptance is separate.

## §E v11.136 · smoother Sheep Tag build drag and capture cleanup (2026-10-26)

The sheep construction preview now computes its anchor and current finger ray against the same current follow-camera position, so the ghost no longer drifts solely because the camera follows the moving sheep. The previous sheep-origin placement and all snap, collision and resource checks remain authoritative; unchanged snapped grid footprints reuse GPU meshes.

When a sheep is tagged, their owned buildings are immediately removed from collision and the scene, exactly as before. Navigation invalidation is coalesced across the destroyed buildings and GPU resource release is spread across subsequent game frames, then flushed on Stop. Sheep/Wolf combat rules, the seven-minute match, Mirror/Totem, Rapid and all 68 assets are unchanged.

Verified source target: **168 patches, 68 assets, 6,711,684 HTML bytes**, SHA-256 `b6114ad2b3f8e6c3352869336845df015fdf18da40e580e5cb4ef819fc5476af`. Actual Android smoothness and ghost feel still need owner acceptance.

## §E v11.135 · Sheep-origin hologram and visible Mirror (2026-10-26)

The owner reported on real Android that choosing a house still showed its construction ghost beside the skill ring. The v11.135 phone fix prevents active skill-button camera rays from repositioning the ghost, places it at the controlled sheep, and moves the preview from that origin by deliberate meadow drag. The previous automatic placement grid stays hidden until a target is aimed, and the committed order uses the same validated site visible in the preview. Mouse and keyboard placement, sheep passages, collision, cost and Rapid placement logic remain intact.

The enlarged Free House button and Fortified House switch physical positions; Income House remains bottom-right. Mirror (decoy) and Totem remain separate visible mobile buttons, while custom rule restrictions still disable the relevant ability. Wolves and wolf AI are unchanged. Source seal: **167 patches**, **68 assets**, **6,708,052 bytes**, SHA-256 `40cf34d1322b071812e0061d25a3be5353a4ad81820714d32eb06608161a09b5`. Source packaging and real Android owner acceptance are distinct release checks.

## §E v11.134 · Rapid OFF cancels ghost, exact sheep-origin marker, restored ability slots, Free/Income HUD swap (2026-10-26)

The owner's Android acceptance exposed three post-v11.133 problems and one missing skill slot. **Rapid Build OFF** now immediately exits the active build mode and removes any unplaced ghost, touch gesture/placement marker and selected tool; it never removes already constructed houses or interferes with issued build orders. Turning Rapid ON leaves selected tools alone. **Selecting any build skill** immediately displays its hologram at the controlled sheep's *actual* X/Z (not a snapped construction site), on touchscreen, mouse and keyboard; after selection a meadow drag still drives native ghost placement with original collision, snap and resource checks.

**Mobile ability HUD:** both original sheep skills—Mirror and Totem—remain present. If a user-created map disables one in Sheep Tag rules, the icon stays visible but disabled with an accessible explanation; this release intentionally does not override owner's custom rules. The canonical starter's existing enabled ability settings and cooldowns remain unchanged.

**Bottom-right skill circles:** swapped the *physical screen positions* of Income House (now bottom-right) and Free House (now the previous Income slot), updating the circle and SVG sizes. Real game building types, free/paid costs, permissions, keyboard shortcuts, IDs, joystick, decoy, rapid position, and all 165 older patches are unchanged.

**[Full build + UI regression #40385878910](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40385878910) SUCCESS:** exact prior v11.133 seal independently verified, then **166 patches** assembled and JS syntax validated. DOM regression tested Rapid OFF with/without in-flight pointers, automatic exact sheep-centered preview after selecting Free/Income, visible-but-disabled custom-rule ability slots, intact wolf HUD hiding, and positional CSS swaps. Official output: **6,700,691 HTML bytes**, SHA-256 **`71a6056da0404f81f09337a2dddb45c87b81450ce49b327f8525fccd5d4efdbe`**; all **68 original assets** preserved. Protected live deployment and owner's Android real-device test remain separate verification gates.

## §E v11.133 · Rapid next to Income, touchable, and sheep-origin build ghost persists (2026-10-26)

**Owner's actual Android screenshot and test:** §E v11.132 rendered the circular Rapid toggle around mid-screen as an unexpectedly **small square**; owner could not turn it on or off. The house skill also frequently failed to leave a working holographic preview after tapping/dragging, although the **cyan sheep occlusion wireframe already worked**. Owner specified Rapid's intended location **immediately left of the Income house icon in the bottom-right build cluster**.

**Root causes and fix:** The native Sheep Tag HUD root has `pointer-events:none` and only certain child controls explicitly re-enable pointer input; v11.132's free-floating Rapid button inherited the no-pointer policy. The generic HUD button's higher selector specificity also overrode Rapid's circular border. v11.133 mounts Rapid/Rotate inside the actual `.st-builds` skill cluster and positions the circular Rapid ON/OFF icon to the left of Income, with `pointer-events:auto!important`, accessible pressed state, and strong circle styling. Rotation remains context-sensitive.

A second, independent defect: touching the House skill caused native `pointerup` to select the tool and seed its preview at the sheep, **then Chrome dispatched a synthesized click** to the skill button, running `stUiChooseBuild(kind)` again. That function **toggles the already-selected build tool OFF**, removing the hologram. The fix suppresses just the one matching touch-derived click after a handled skill pointer release, not keyboard, mouse or subsequent intentional taps. The ghost is also seeded while the button is held without triggering the old invalid-touch hide path. A continuous drag from icon onto clear meadow now moves the preview when the finger reaches valid ground; a normal tap followed by meadow drag also remains supported. If a skill drag ends above HUD/blocked ground, the selected tool and sheep-origin preview are retained.

**[Full source + Android click/ghost regression #40381957434](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40381957434) PASS:** exact prior v11.132 seal reconstructed; 165 patches compiled and JavaScript syntax checked, `jsdom` reproduced synthetic touch click and verified selection persistence, keyboard/mouse input, clickable Rapid, parent-location near Income, circle/ON/OFF CSS, meadow child canvas hits and all previous §E gameplay integrations. Exact build **6,696,326 bytes**, SHA-256 **`2c2b40a507bc91950479ac9983eb365c6c5d9319a5e85c9fe3b7ac18f27860b8`**, 165 ordered patches and original 68 assets. Owner's live Android acceptance is still needed after deployment; automated DOM events do not prove real Chrome behavior.

## §E v11.132 · Dragging sheep-centered hologram, Rapid Build, rotated raised crossings and occlusion wireframes (2026-10-26)

**Owner gameplay report:** tapping House correctly placed the preview ghost at the sheep after v11.131, but dragging on the meadow **did not move the hologram**. The native v11.84 pointerdown callback was discarding the selected tool and calling `stUiChooseBuild(kind)` again; that API **toggles the same selection off**. The final patch differentiates the selected skill-button event from a subsequent meadow drag, preserves the selected active tool on meadow pointerdown, recognizes viewport descendant targets, follows actual pointermove with native preview/snapping, and commits only upon valid pointerup/resource/collision checks. Finger drag on the skill icon is still separate from moving the hologram.

New **circular, accessible RAPID ON/OFF button near the middle of the mobile screen** keeps the selected house/structure after a successful native building order and reseeds the next hologram at the sheep. Off mode restores one-and-done placement. A companion **⟳ rotate control** exposes the existing 90° rotation for player-built ramps and walkways. On actually constructing any new owned building, the sheep pauses automatically for **0.28 s**; a movement order or joystick direction cancels that recovery immediately, while the game clock, captures, effects and AI remain updated.

All nine indestructible authored prebuilt ramp/deck pieces in **three Moonbell crossings** remain: Pinewatch at 0°, Moonflower at 90°, Amberglade at -90°. Opposing ramp high ends still join their real 6 m deck endpoints exactly. **Completed elevated walkways** now admit sheep/wolves travelling at ground level beneath the 3.3 m platform, without changing upper path surfaces; ramps and incomplete platforms remain blocking until complete. Occluded living sheep receive a **cyan see-through wireframe clone of their own actual animated sheep mesh** only when physically under a walkway or when a house/deck blocks the camera's sightline; it hides once clear and never changes unit physics, controls or original materials.

**[Complete 164-patch gameplay CI #40378516848](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40378516848) PASS**. The run rebuilt the exact preceding v11.131 release, assembled all **164 ordered patches** into **6,691,218 bytes**, SHA-256 **`6d678e0886907007de501b5f9d68916f09246eb25f6fa865a36e56481fa64920`**, checked compiled JavaScript syntax, and exercised actual Three.js wireframe materials, underpass blocking, three rotated crossing groups, responsive rapid toggle and rotation UI, interruptible construction recovery, and required assembled native pointer handler changes. Original 68 bundled assets and all earlier behaviors remain intact. Production deploy and real owner's Android touch acceptance remain separate gates.

## §E v11.131 · Drag-directed sheep Mirror decoy and ready-to-use mobile fixes (2026-10-26)

Following §E v11.130's successful **sealed-source** check, the owner additionally requested a **visible cooldown counter on the Mirror/decoy skill**, reliable casting while the sheep is moving, **drag-to-direct** the decoy and **short-lived disappearance**. The real archive gameplay `stArchiveSplit` now creates only a **separate decoy**, routes it toward the direction dragged from its skill button using the existing safe ground/upper path planner, boosts only the decoy's speed, and leaves the real sheep's movement/order/joystick completely untouched. A simple tap aims along the sheep's current velocity or facing direction. A blocked destination rejects without using cooldown, and existing unit validity and Classic-off rules remain enforced.

The Mirror skill icon gains a **live numeric cooldown badge** (not merely an info row) and accessible status label. The existing starter's **12-second Mirror cooldown** still comes from the game rules; successful casting sets the normal `archiveSplitAt`. Decoys expire after **at most four seconds**, or any shorter authored lifetime; they fade their own cloned materials in the final 0.7 seconds and can still dissolve earlier on wolf contact. The new touch ability owns only its own pointer; it does not cancel a second finger holding the sheep's mobile joystick, alter the camera, or spend gold.

Also includes the **v11.130 source fixes verified earlier but not independently deployed**: Android browser zoom is suppressed at the second single-finger starter-selection `touchstart` without blocking a true two-finger pinch; skill-button pointer movement and release no longer overwrite sheep-origin building previews. All original v11.129 and prior editor/Sheep Tag features remain intact, including the Clover model, startup gate, starter defaults, non-destructible walkways, player-build clearance, and all 68 bundled assets.

**[v11.130 sealed main preflight #40371349066](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40371349066) SUCCESS.** **[v11.131 full 163-patch CI #40372653251](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40372653251) SUCCESS**: rebuilt exact prior v11.130 seal, assembled 163 ordered patches, passed JavaScript syntax and automated Mirror ability tests for joystick-independent movement, drag direction, cooldown badge, short expiry, decoy-only material fade, tap use, no duplicate cast and original rule restrictions. Official new HTML: **6,679,918 bytes**, SHA-256 **`ae889b96eaeddf58d290a6214809463cf84930f88a02b5070cda83ae47080218`**, **163 patches, 68 assets**. Guarded production upload, live HTML/SOURCE audit and actual Android thumbstick/gesture acceptance are separate gates.

## §E v11.130 · Second-touch Android page zoom protection + true sheep-origin house preview (2026-10-26)

**Owner Android acceptance feedback:** §E v11.129 reduced browser magnification during rapid starter-project taps but **small browser PAGE zoom still reproduced**. This is not the 3D camera. The new `passive:false`, capture-phase `touchstart` guard observes a short stationary single-finger starter-card touch and prevents default on the **second** rapid single-finger touchstart within 670 ms, before mobile Chrome can decide to smart-zoom. Previous native `touch-action:manipulation` and post-click 420 ms handoff shield are retained as layered protection. Two-finger pinch, editable input interactions, long press, mouse/keyboard, viewport camera controls and general scrolling remain unaffected. This is a targeted browser-page control; no global viewport zoom restrictions are imposed.

**Owner also reproduced a construction regression:** tapping a Sheep Tag build skill still sometimes caused the house preview to spawn **at the skill icon**, despite v11.126 sheep-centered seeding. Root cause: the older v11.84 `stBuildInputAim(event)` unconditionally re-aimed the preview during **skill-button pointermove and pointerup**, overwriting the later sheep seed with the button's screen ray. v11.130 preserves native meadow pointer-down/aim/release but stops handling the skill-button finger as an aiming pointer. A skill tap simply selects the house tool and **re-seeds the preview at the controlled sheep** on release; only touching the meadow can aim or order a house. Native `stCanBuild`, collisions, unit relocation on valid build, resource costs, original joystick and safe lanes remain unchanged.

**[Full 162-patch source and DOM/native handler preflight #40370882999](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40370882999) PASS:** reconstructed exact v11.129 release; measured **6,672,532 bytes**, SHA-256 **`6156d4261621b38b570792f24acff2f126baaf2384b2f4f79acd5975a13b5a26`**; checked compiled module syntax. DOM tests confirmed rapid second `touchstart` cancellation, true pinch and editable-field exceptions, movement threshold, and actual extracted native skill-button `pointerup` handler re-seeding without ever aiming toward the button. Original **68 assets** and 161 earlier patches are preserved. Protected production deployment and owner real-device acceptance are separate checks.

## §E v11.129 · Android project-switch page zoom protection (2026-10-26)

**Owner's reproduced bug:** repeatedly, immediately after selecting a starter project, the **entire browser page** enlarged—not the 3D camera—cutting off editor controls until manually zoomed back out. This occurred despite the pre-existing v11.122 root-page `touch-action:manipulation` rule.

The targeted fix applies `touch-action:manipulation` on **actual project cards, their default-project checkbox siblings, project picker, and editor workflow chrome** (preserving native scrolling and browser pinch accessibility). During a **touchscreen** starter-card selection only, a 420 ms transparent, non-focusable hit shield intercepts rapid second taps **after** the native Open click finishes, preventing a subsequent tap from landing on a newly exposed unrelated editor control or triggering double-tap page magnification across replaced DOM hit targets. Keyboard/mouse selection, checkbox-only changes, text editing/paste, the 3D viewport's original touch rules, game camera, model sculpt brushes, saved projects, and all prior engine behavior remain unchanged.

**[Feature full source and touch-DOM preflight #40368154931](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40368154931) PASS:** reconstructed the exact preceding v11.128 seal, verified full 161-patch source syntax and measured **6,669,441 HTML bytes**, SHA-256 **`34caf41b05e3c404e12d0da122a79db61c8187aaea1692b2cd07c380a69a4f7f`**. The jsdom harness verified keyboard/mouse taps unaffected, native starter click still fires, default checkbox not intercepted, touch selection adds the shield, double-click prevention, 420 ms cleanup, and no `#viewport`/viewport-scale restrictions. The engine still carries **68 original assets**. This does **not** prove Android browser acceptance; user real-device retest remains necessary.

## §E v11.128 · Persistent default starter checkbox (2026-10-26)

The owner requested an individual checkbox beside **every starter project** in the §E Projects picker so users can nominate one project to open by default on future visits. The real native template picker has **10 starter-card buttons**. Each card now has a sibling accessible, touch-sized **Load this project by default** checkbox (not nested inside its Open button). Selecting a checkbox records that template ID as the one default in browser-local storage `swyrl.engine.defaultStarter.v1`, clears other checkboxes and **does not open a project**. Unchecking the currently selected option removes the default and restores normal Dragon Den startup. Choosing a new starter remains a separate click on the existing card button.

At regular launch without an explicit URL project, the already-native startup router now uses the saved starter. Explicit `?project=` URLs take precedence without changing the saved choice. Specialist model links keep their existing project query handlers, and async default-project loading keeps the v11.127 boot overlay active until completion or its existing bounded fallback. Importantly, the preference is **independent of project data and autosaves**: setting/clearing a default does not delete, mutate or overwrite custom project JSON, the in-progress editor project, or the existing `swrlz-forge-v5-autosave` key. Browser storage being unavailable fails safely with UI feedback.

**[Full 160-patch source + real DOM interactions #40350416722](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40350416722) PASS**: prior 159-patch §E v11.127 verified unchanged, 160-patch HTML built and syntax checked; `jsdom` verified **10 card checkboxes**, native Open click remains usable, one-choice exclusivity, selection/clearing persistence, avoiding accidental project openings, old autosave preservation, normal and explicit-link launch precedence. Complete HTML: **6,666,214 bytes**, SHA-256 **`9bf9658db0592f6dccc4c9b57a6eec700c76de04461f542403e50cb6c2a49a2a`**. Earlier organic Clover Sheep Tag model and cute swurv gait, stable boot cover, permanent routes and earlier engine features remain as-is. This source test is not the protected live deployment or Android visual acceptance.

## §E v11.127 · Native Clover organic sheep + smoother editor startup (2026-10-26)

The owner requested that Sheep Tag reuse **Clover · Meadow Sheep**, the existing native Model Atelier organic sheep generator, and give the sheep a more lifelike gait with occasional small, cute pouncing swurvs. The runtime now builds that genuine authored organic geometry *once* at mobile-adjusted tessellation, preserving sculpted fleece, muzzle, face, ears and split hooves. Mesh resources are shared across Sheep Tag sheep; native actor ownership, collision radii, joystick/pathfinding, saves, capture/rescue, and distance-based leg gait remain unchanged. The visual-only pounce triggers occasionally **while moving**, applies small body hop, head tilt and slight sideways *appearance* then returns to walk. Disabled for captured, upper-route, falling and building sheep. Failure to build the organic model retains the existing fallback sheep.

The owner also documented a visible editor startup handoff: temporarily showing an old/default empty editor shell before the current project and toolbars finish restoring. v11.127 inserts the boot style into the document head, covering only the *intermediate visible shell* with a minimal loading surface while project and toolbar signals settle. It reveals the fully restored current editor (or uses an 11 s safety fallback) rather than showing stale controls and then snapping. Rendering/initialization continues unobstructed beneath the overlay; existing persisted projects/data are **not reset or overwritten**. Reduced-motion preference is honored.

**[Full source + real Three.js sheep regression #40348104741](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40348104741) PASS.** Exact previous v11.126 seal rebuilt; all 159 patches independently assembled; compiled HTML syntax passed. Genuine organic sheep generator created **28 parts / 29,332 triangles**, with shared geometry for two animals. Automated tests covered ears/fleece/hooves, four walk pivots, rare cosmetic pounce and no physics drift, old animation callback preservation, editor boot gate and no serialized Object3D metadata. Full build: **6,660,681 bytes**, SHA-256 **`a6dc826751d28b0385971cd32fbb41df47131ea2d2b1d2aeeee1f1aac45e584a`**, 159 patches, original 68 assets. Production deployment and owner's actual Android appearance/startup test remain separate gates.

## §E v11.126 · Sheep-centered building, permanent raised routes, faster sheep abilities (2026-10-26)

Owner-requested improvements extend the verified v11.125 safe house placement and local collision-gap indicators. On tapping a building skill, its **live green/red build preview starts exactly at the controlled sheep's position** instead of requiring a skill-button drag. Move it by dragging on the meadow, releasing to commit through the native build/placement pipeline. Dragging from the skill ring remains optional. Merely previewing never builds.

The authored **Grand Moonbell Wildwood Sheep Tag starter** gains three completed elevated crossings: Pinewatch (-52.5, -45), Moonflower (60, -52.5), and Amberglade (-52.5, 60). Each group has two functional 6 m ramps attached to a 6 m walkway: **nine baked pieces**, native upper navigation for sheep/wolves. These specifically identified *world routes* cannot be damaged or sold during gameplay. Player-built ramps, walkways and houses remain normally destructible; this does not overwrite custom/user-saved maps.

With the Archive sheep skills enabled, **Mirror / Illusive Split** unlocks at level 1, ready at match start, and repeats after **12 s** (was 30 s). **Totem** is reusable after **25 s** (was 120 s) as soon as an owned house is completed, rather than demanding nine houses. Totem still needs an actual completed house to convert. Explicitly disabled Classic abilities remain disabled.

**[Full 158-patch candidate and prior-source validation](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40343082708) PASS**: compiled original 157 patches without alteration, measured complete 158-patch source, verified JS syntax and regression tests for preview/no-auto-build, physical raised route joints, collision distance from spawns and obstacles, permanent-route protection, and both cooldowns. Final complete HTML: **6,651,868 bytes**, SHA-256 **`dbbc8d1ac954e3e93ec9f8feb74ed0371575c6378a9b27ef77c021c20dabcec5`**, existing **68 bundled assets**. Production deployment and owner's Android gameplay acceptance remain separate gates.

## §E v11.125 · Honest house clearances and safe builder relocation (2026-10-26)

The owner's actual Android v11.124 playthrough confirmed accurate house placement, but a measured **1.20 m gap** incorrectly appeared **BLOCKED** while the sheep could traverse it. The old label checked a lengthy approach beyond both facing walls; unrelated nearby houses could make a locally walkable corridor red. The v11.125 additive patch uses native swept collision **inside the facing walls** with the current sheep/wolf radii and nearby obstacles when a gap meets the safe snapping width. Cyan/Gold mean **local physically clear space**, not a guarantee of a connected whole-map route. Truly obstructed and historically unsafe 0.90 m gaps remain blocked.

Owner also requested placing houses under the standing sheep and moving the builder to the **closest safe outside position**. The assembled v11.124 native validator already exempts its builder but protects other units. The v11.90 opt-out disabled the existing nearest-safe-side ejection path. v11.125 restores only that previously implemented collision-tested path: if every side is blocked, reject the build without changing gold or structures. Original snapping, joystick movement, collision, structures, other-unit protection, HUD and 68 assets remain unchanged.

[Candidate CI #40278508544](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40278508544) **SUCCESS**: exact sealed v11.124 reconstruction, new patch, JavaScript syntax, earlier passage regression, blocked-gap and nearest-side exit CPU cases. **157 patches**, **68 assets**, **6,645,687 HTML bytes**, SHA-256 29a27f8a683abfbaf31ee0a3b02fc0dabb49168f302602f99c1361998621c1d8. This preflight is not the guarded production deployment or owner Android acceptance.

**Official full-chain v11.125 seal:** [GitHub Actions diagnostic #40279350924](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40279350924) reconstructed the complete 157-patch release and compared it with the candidate. The canonical build includes the newly preserved v11.124 release-notes history and sets the new release-notes version. Its **6,645,795 bytes**, SHA-256 `4b4e0a69a388083817b72e6600c7c7a8e3b6c08247d4714430aebf0717f416ac` supersede the candidate-only seal for production. No gameplay/source behavior was changed by this history reconciliation. Guarded production deployment and owner Android acceptance remain separate.

## §E v11.124 · Sheep Tag flush-or-passable house placement (2026-10-25)

Android owner test of v11.123 showed an existing **0.90 m “SHEEP ONLY” gap** that still trapped the sheep. The correction is **in building placement itself, not sheep movement**. Near existing structures, new houses now snap either visually flush (a 2 mm collision-safe epsilon) or one additional navigation grid interval farther out: **1.20 m at the default sheep radius**, dynamically enlarged for larger sheep. The authoritative placement validator rejects intermediate horizontal, vertical, and near-corner slits. For a new snapped passage, it also checks an actual swept sheep-collision segment through the opening against existing obstacles and the proposed house; if obstructed it rejects the placement rather than showing a passable preview. Old houses remain where the user placed them, but the clearance overlay marks their 0.90 m unsafe gap **BLOCKED** instead of SHEEP ONLY, and explains the new minimum safe spacing. Main menu, thumbstick, skills, collisions, movement speed and existing camera/nav paths remain unchanged.

Preflight [run 40270681386](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40270681386) verified official **156 ordered patches and 68 assets**, **6,643,360 bytes** source SHA-256 `8a45b889b2d48edc1101e423b05c97ebf68de55eaf6b158cd4c6fbc7914fa08c`, plus exact snap placement, third-party blockers, honest labels and earlier v11.123–v11.114 editor regressions. Real device passage acceptance remains for the owner to validate.



## §E v11.120 · Unobscured top menus, centered category buttons, and editor-only browser double-tap control (2026-10-25)

User Android v11.119 screenshot demonstrated toolbar collisions at the top of Model Atelier, a viewport mesh quickstrip partly hidden behind the header and reference toolbar, and bottom category buttons kept near a rail edge. Fast double-taps within the editor could also trigger Chrome's page zoom instead of a second tool tap. The user requested all three presentation fixes, retaining model operations and camera gestures.

**Implemented:** Explicit stacking order places the original Export and Views dropdown menus above surrounding header/viewport/display/reference controls, keeping their anchored buttons intact. The existing mesh quickstrip's calculated location receives a minimum vertical clearance measured against the *actual* complete top toolbar (including dynamic rows), while preserving its earlier native positioning and user dragging. The bottom tool rail uses safe centering when its content fits, retains touch-scroll and right-to-left thumb preferences when overflowing, and scrolls the currently selected category toward the visible center. The web-platform `touch-action: manipulation` is scoped to `#modelAtelierPanel` and its non-canvas chrome to prevent browser double-tap page zoom; editor-specific canvas orbit/pinch logic, one-finger mode selection, horizontal scrolling, text field selection and deliberate browser pinch-zoom remain available. No document-wide touch interception or viewport maximum-scale lockout is introduced. This cannot disable Android/Chrome gestures outside the §E page.

**Validation and release gates:** [targeted tests v11.120](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40227843968) PASSED new menu layer / safe-top / RTL-aware centering / double-tap policy assertions and previous v11.119 unified inspector, v11.118 taxonomy, v11.116 camera pinch, precision gizmos, preview selection and v11.117 context-menu regressions. Official final-source artifact: **152 ordered patches, 68 packaged assets, 6,626,204 HTML bytes**, SHA-256 `17d0920293dbc1ab80d34d6576d1ff91c627115db810785214839d360d862aaa`. Official sealed-source verification, separate guarded Hugging Face deployment and real Android touch/menu acceptance are distinct checks; simulated behavior is not owner-device acceptance.

## §E v11.119 · One draggable inspector, contextual mode rail, cleaner top chrome (2026-10-25)

Owner's screenshots of Android v11.118 demonstrated the conflict: clicking Sculpt launched a second full-width compact bottom workbench, while the correct native mesh inspector remained as a separate movable panel. The requested model-editor workflow is now one main category rail along the bottom, **one horizontal submode rail immediately above it** for categories with multiple operations, and **one mode-specific native inspector** in the existing draggable right-side tool dock.

**Architecture / exact changes:** The v11.61 context workbench and its real native-control proxies are embedded inside the original `#modelAtelierInspectorDock`, rather than creating a second bottom-sheet overlay. The v11.62 mobile takeover no longer hides the original inspector. Existing category buttons (Meshes, Sculpt, Lasso, Topology, Face, Appearance, Motion, References) select available submodes; for Sculpt these include Brush & falloff, Precision circle cut, Brush placement, Brush shape, Vertex editing and Sculpt resolution. Selecting a submode displays its registered settings and actions in the same draggable inspector. **More** returns to the original full native inspector. Mode-specific settings do not create new parallel geometry implementations. The bottom mode rail scrolls horizontally and is hidden when unnecessary. Resizing, dragging, hiding, preserving Undo/model data and the non-destructive cut preview remain native.

**Top controls:** Save model and Close remain available. Existing GLB, OBJ and PNG controls move to an anchored **Export** menu; existing view-direction presets and Center Pan move to an anchored **Views** menu; Render Mode, Target, display/wire/interior toggles and References remain available. Original DOM buttons are moved rather than cloned, retaining event listeners. Existing touch callout suppression remains in place. The Chrome bootstrap regression discovered v11.117's scope mismatch between the installed long-press helper and its bootstrap call; this forward-only patch exposes that existing helper through `window` without changing its behavior.

**Release evidence:** 151 ordered source patches, 68 bundled assets, **6,621,308 HTML bytes**, SHA-256 `62dfb014d58287c78281e9579565732ecd7366bcd26d178110cc6d6abadca510`. Targeted compiled UI and previous radius/camera/preview/long-hold regressions passed (see workflow logs). A separate experimental headless-Chrome test established that the engine module initializes but its isolated starter-scene path could not open a model; it **did not pass full live touchscreen UX acceptance** and is not used as positive acceptance evidence. Final source package verification, hosted integrity and **owner Android usability** remain distinct release gates.

## §E v11.118 · Modeling-editor-informed semantic tool organization (2026-10-25)

Owner request: audit the existing §E Model Atelier tool grouping and move relevant tools into relevant places. Compare the architecture with the published Blender workspaces manual (https://docs.blender.org/manual/en/latest/interface/window_system/workspaces.html), Autodesk Fusion toolbar/workspace documentation (https://help.autodesk.com/view/fusion360/ENU/?guid=GS-THE-FUSION-INTERFACE), and the Nomad Sculpt tool and topology manuals (https://nomadsculpt.com/manual/tools , https://nomadsculpt.com/manual/topology). The borrowed design *principle* is domain separation with context-appropriate operations; §E retains its own implementation and visual identity.

**Tool audit / implemented destinations:** Default thumb rail now follows **Meshes → Sculpt → Lasso → Topology → Face → Appearance → Motion → References → More**; original DOM buttons and event listeners are moved in-place, not cloned or replaced. **Meshes** owns object selection, transforms, shape identity and model export. **Sculpt** owns sculpting brushes, falloff, local vertex refinement and the complete precision circle cut (radius, depth, flat/rounded cap, radius/depth gizmos, Preview and Apply). **Lasso** owns masking, boundaries, region painting and deformations. **Topology** owns face/edge/vertex topology operations, UV mapping, LOD and mesh audits. **Face** owns portrait/anatomy, facial landmarks, profile and photographic cutout. **Appearance** now owns material, color and surface finish, not unrelated facial tools or precision cuts. **Motion** owns poses and animation; **References** holds photographs/comparison; **More** retains the original inspector and advanced native settings.

Contextual discovery now routes individual control IDs, including previously untracked nested fieldsets, rather than sending all unknown sections into Appearance. The existing source controls remain the only editor authority: contextual proxies only operate the real nodes; favorites, recent actions, presets, selection, saved scene formats, Undo, pinch/orbit, inspector drag/scroll and browser-long-press protection are preserved. Previously hidden/restricted features are not promoted as functioning commands. Tools are not cloned, removed or replaced, and no geometry transformations are changed.

**Evidence:** [targeted category and legacy gesture tests](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40218133774) PASSED on the exact v11.117 base plus v11.118 patch. The final source is 150 ordered patches, **6,608,292 HTML bytes**, SHA-256 `1c2e048831bcc21ebf2b19149e9ab44263cf66e096f4fae4470fb0978d4efa12`, preserving 68 packaged assets. Targeted unit results, official sealed source verification, live hosted file integrity and owner Android usability are separate gates.

## §E v11.117 · Suppress Android/Chrome long-press menus inside Model Atelier (2026-10-25)

The owner requested that holding a finger anywhere inside the editor should not trigger the browser's native popup/dropdown context menu. Add a **Model Atelier-scoped** forward-only gesture guard. While `#modelAtelierPanel` is open, capture `contextmenu` on the editor viewport, floating tool panels and other editor controls, including its detached `#seMobileNumberPad` modal. Suppress incidental text selection on **non-editable** editor chrome, while preserving text-input caret, selection and paste, plus the existing touch-action CSS, scrollable inspector, single-finger orbit, two-finger pan/pinch, sculpt and radius/depth gizmo interactions. Closing Model Atelier restores the browser's ordinary context-menu behavior outside the editor; unrelated project/app surfaces are not affected. Scoped `-webkit-touch-callout:none` CSS and the minimal `contextmenu`/`selectstart` handlers never intercept `pointerdown`, `pointermove`, `touchstart` or `touchmove`. This does not claim control over browser/OS chrome outside the page.

**Evidence and gates:** [targeted source preflight #40203921640](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40203921640) passed suppression/selection scoping, previous camera-touch and radius/depth regression, and JavaScript syntax on the 149-patch candidate. Official v11.117 final assembled source is **6,605,187 HTML bytes**, SHA-256 `0a7af4ccc8515cc0f12a827427b2fba71e0362e878d3c6f45f16bb74bfecaa84`, retaining all 68 bundled assets and prior history. Sealed-release CI, guarded Hugging Face deployment, hosted integrity and owner's Android long-hold acceptance remain independent gates.

## §E v11.116 · Precision radius touch and reliable camera gestures (2026-10-24)

The owner's Android screenshot showed an oversized/clipped white sphere during a radius-handle drag, simultaneously visible XYZ mesh arrows, and incorrect finger-camera behavior. Source inspection found that v11.76 allows the exterior camera to zoom to 0.16 units (inside a selected ball), and the v11.115 preview ghost tap stops propagation of pointerup before the camera's touch map is cleaned, leaving a phantom finger. The wide v11.114 ring touch hit target additionally competed with ordinary orbit movement.

This forward-only fix protects the existing native precision cutter instead of adding a bowling-ball-specific preset. In precision mode, pinch, wheel and zoom buttons respect a camera distance derived from the selected mesh's world-space bounding sphere; opt-in interior inspection retains close camera access. Tapping a ghost preview releases the corresponding camera pointer. Two fingers interrupt an active radius/depth drag safely, restore its uncommitted value, and transfer both pointers to camera pan/pinch; the remaining finger resumes orbit once its partner lifts. Touch grabs use a narrower ring with a separate larger grip target, and XYZ whole-mesh gizmos stay hidden while precision editing is active. Cancellation never saves a half-cut; explicit Apply/Undo remains the sole geometry commit path.

**Validation:** [v11.116 sealed source verification #40159277934](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40159277934) PASSED 148 sequential patches, 6,603,142 HTML bytes, SHA-256 `a779619854cc8fc0639ac5c3e4ca8555c37b09a7993be3db3ec11591ef06868c`, JavaScript syntax, v11.114 radius/depth and v11.115 preview/mesh-transform regressions, and new camera pointer handoff / ghost tap / safe zoom tests. All 68 bundled assets and prior projects are preserved. Official source packaging, gated Hugging Face deployment and owner Android UI acceptance remain separate evidence levels; green automated tests do **not** establish that the owner has visually accepted the gesture feel.

## §E v11.115 · Prevent detached precision-cut preview and accidental mesh moves (2026-10-24)

The owner photographed one Model Atelier sphere plus a separate apparently unselectable second ball with a carved hole while native Mesh tools were set to **Move Z**. The editor showed **1 individually editable meshes**: the holed sphere was actually an unsaved **precision-cut preview ghost** (rendered in `world`, not the selectable `modelRoot`), while the real source sphere moved independently beneath it. This version guards the lifecycle of that temporary render, not the geometry of the underlying cut. During an active ghost preview, block native Mesh Move/Rotate/Scale hit-handle starts and quick-strip +/- whole-mesh nudges, with an explanatory warning directing the user to amber Radius and violet Depth controls. A tap on the ghost proxy now reselects the corresponding editable source mesh safely, and native `renderParts()` selection/Undo/transform rebuilds clean up stale ghost geometry. Clearly mark the cut as **PREVIEW ONLY** until Apply; no preview change invokes `checkpoint()`, changes native mesh source or silently commits a cut. The original user-made precision cut remains fully editable once explicitly Applied. Targeted [preview-safety preflight #40153683396](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40153683396) tested ghost raycast proxy selection, direct transform hit blocking, nudge blocking, render invalidation and zero model checkpoints, alongside the prior sealed artifact + JavaScript syntax. All 68 assets, previous tools, meshes, and viewport radius/depth handles are preserved. [Full-source seal #40153853279](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40153853279) passed **147 ordered patches**, **6,600,621 HTML bytes** and SHA-256 `5cf410b40661f9c4a0a11089eceaca9a57a6ff1f6664d7a9a1e8cea8ed879f37`, preserving all **68 bundled assets**. Official release packaging, live host checks, and owner Android acceptance remain independent gates.

## §E v11.114 · Direct viewport radius/depth editing for Precision Circle Cut (2026-10-24)

Owner-requested phone-friendly modeling UX: numeric radius and depth should each have a **toggle** that exposes touch-draggable gizmos directly on the part in Model Atelier. v11.114 adds independent **yellow Radius handle** and **purple Depth handle** toggles inside existing Precision circle cut controls. The radius handle outlines the exact circular footprint on the curved sphere or flat source face; the depth guide reaches from selected surface down the bore's cut axis. The user can drag the colored ring or bead to resize width, or drag the purple grip to increase/decrease depth; the numeric fields stay synchronized. Front-on cameras switch automatically to vertical downward/upward depth adjustment when axial screen projection is too small. Touch interactions are captured only when a handle is hit; tapping elsewhere continues native selection/orbit. During drag only temporary helper geometry/fields change; on release the engine regenerates its validated non-destructive preview once, and only explicit Apply saves/calls Undo checkpoint. Gizmo overlays are editor-only and omitted from model JSON/export; turn both toggles off to restore an uncluttered viewport. Previous manual individually editable cut layout, flat-to-rounded bottoms, prior sculpt modes, Wireframe/X-Ray, histories, 68 assets and unrelated apps are preserved. **Targeted test #40137169712** passed simulated Android pointer drag (radius, straight-on depth, synchronous fields, preview on release with no checkpoint) and complete last-version patch integration. Sealed source [preflight #40137347856](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40137347856) passed 146 ordered patches and JavaScript syntax: **6,594,602 HTML bytes**, SHA-256 `7cd989c5973bb978725f0495ad9b20cf17328cbeaacc0954e0ebdf1b5717c22b`, with 68 preserved assets. Official release packaging, live hosted verification and owner Android UX acceptance are separate gates.

## §E v11.113 · General precision circle cut (2026-10-24)

Owner correctly rejected the bowling-ball-only feature framing. This additive release extends user-placed **Precision circle cut** into a reusable modeling tool, rather than automating preset hole arrangements. Pick each surface position manually, set cut radius and depth, choose a **flat (0) through rounded (1) bottom**, preview exact candidate geometry, and Apply with Undo. Reopen a prior cut's recipe to adjust its dimensions without inadvertently relocating it; relocation requires an explicit checkbox. Real closed indexed cavities now work on **native spheres**, **planar native box faces** and **flat native cylinder end caps**. Limits: initial surface orientation shared by cuts on a part; up to **3 on spheres**, **6 on one box face/cylinder cap** under native 9k-vertex/16k-triangle budget. Not a general Boolean solver for imported arbitrary meshes or curved cylinder sidewalls. Existing native project metadata, rendered previews, ordinary sculpt brush, JSON and geometry export, and 68 assets remain preserved. Targeted geometry [preflight #40135278226](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40135278226) passed seven live-indexed-mesh scenarios, including flat-bottom box cut and six box sockets, with zero open/nonmanifold/inverted/degenerate faces and valid replay. Full 145-patch source [seal #40135439020](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40135439020) passed: **6,579,505 HTML bytes**, SHA-256 `445a93e9a1b077aebba942524c54877bb709f8e73687d9b600432232a40194c8`, 68 preserved assets. Official package, hosted verification and owner Android UX acceptance remain separate.

## §E v11.112 · Manually place and edit every circle carve (2026-10-24)

Owner correction superseded the v11.111 automatic bowling-ball preset: **the user wants the fundamental precision tools to make each hole themselves**, not a three-hole generator. Replace the UI preset with a manual one-hole-at-a-time workflow in Sculpt: use existing **Pick center on mesh**, tap anywhere on the visible ball hemisphere, choose independent local circle radius, exact depth, and rounded-bottom cap profile (0.5–1.0), preview the changed indexed geometry, and deliberately Apply. `roundHolePlan` is validated native part metadata saved alongside each topology mesh; after a cut, pick another location or choose an earlier hole to modify and rebuild the same ball without losing earlier holes. First cut reconstructs the original procedural sphere, preserving Undo recovery; each subsequent cut remains editable, Undo and JSON saving remain supported. All bores share the first hole's drill axis (the initial lightweight/parallel-cavity limitation). Supports up to three user-positioned holes within the existing portable 9k vertex / 16k triangle cap; this does not claim general-purpose Boolean cutting of arbitrary meshes. A second spherical midpoint refinement pass corrects the crumpled, faceted exterior in the user's v11.111 Android screenshot. Owner selection of each hole is the crucial design requirement; no automatic placement remains in the UI. Targeted [preflight #40133868935](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40133868935) passed manual geometry replay (1/2/3 holes: 4674/6050/7426 verts, 9344/12096/14848 faces), manifold checks, persisted plan schema, curvature improvement, patch application and JavaScript syntax. Full versioned [seal #40134031269](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40134031269) passed with **144 ordered patches / 68 preserved assets / 6,576,477 generated HTML bytes**, SHA-256 `77d8da050f64d09ab611d33bf7b97685a99b24eb7ce81e5fa0d9df21be46d52c`. Hosted integrity and owner Android UX acceptance are independent gates.

## §E v11.111 · Actual drilled bowling-ball holes (2026-10-24)

Code audit confirmed that v11.110 sculpt Intrude pushes native vertices and cannot drill precise circular openings; face intrude is per-triangle, while Boolean lasso is only a selection mask. Instead of implementing broad CSG, a bounded `Round hole maker · bowling ball` is added inside Model Atelier Sculpt. On a selected procedural sphere it generates a **new native indexed topology mesh** with 1 or 3 circular openings, stitched cylindrical interior wall loops and hemispherical ends. Use picked mesh center to orient the group or default front, set finger radius/depth, Preview to temporarily display true edited geometry, then Apply to replace the original sphere; Undo restores the original. The original part's existing sculpt strokes will be replaced by a new clean round-hole mesh (explained beside the controls). The builder reuses the native `topologyMesh` schema, triangle budget, validation and audit; no new core mesh format, external CSG library or portable-format exception. The phone menu, existing sculpt brush, rendering modes, save/export and all 68 bundled assets remain intact. Targeted geometry regression [#40129504189](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40129504189) passed: 1-hole 2,114 vertices/4,224 faces; 3-hole 3,322 vertices/6,640 faces; no open edges, nonmanifold edges, winding conflicts or degenerate triangles. Targeted geometry regression [#40129504189](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40129504189) and full-source reconstruction [#40129688184](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40129688184) passed. **143 ordered patches, 68 preserved assets, 6,571,928 output bytes**, SHA-256 `eac0886d3fcfbf922979851044344794c9670ccc8feba358e06671d931f3845e`. Live-host verification and owner visual testing are distinct final gates.

## §E v11.110 · Displacement-accurate before-Apply sculpt preview (2026-10-24)

After owner Android acceptance of v11.109's rounded surface-following brush, a bounded audit found one misleading visual edge case: the translucent teal shader could still paint untouched source triangles, including when the submitted stroke would move zero vertices because of depth, snapping or selection. The v11.110 follow-up only improves temporary preview presentation: sample exact native stroke displacements on the already disposable preview geometry, multiply fragment alpha by interpolated movement, trim wireframe edges to moving regions, and explicitly report when no vertices will move. It preserves the existing yellow radius ring, green/cyan gizmo, lavender depth indicator, the stroke/apply operation, Wireframe/X-Ray, mobile menus, Undo, native exports, saved scenes and all 68 bundled assets. The owner remains the final mobile UX acceptance gate. Targeted source preflight [#40124895300](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40124895300) passed: **142 ordered patches, 68 retained assets, 6,559,449 HTML bytes**, SHA-256 `85570c8d83a2eb1e15ea4c0854d0571b590f6e9858925996c4458aa1ea187d41`. Release sealing, hosted integrity verification and owner acceptance remain separate.

## §E v11.109 · Round surface-following sculpt preview (2026-10-24)

Owner Android acceptance of v11.108 showed the teal before-Apply ghost had squared/polygonal outer edges even though the yellow radius ring was correct. Root cause: the old preview included entire displaced-vertex triangles and rendered their complete face edges. This forward-only patch retains the original native brush stroke and yellow ring, but masks the actual proposed temporary mesh with a radial alpha fade in unmodified object-local space and clips its teal wireframe edges to the brush radius. Unaffected surface faces near the footprint remain available for a smooth transition. Only the non-destructive ghost visualization changes: Undo, Apply, exported/saved meshes, mobile inspector, wireframe/X-Ray, source and 68 bundled assets stay intact. GitHub targeted full-source [preflight #40119683427](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40119683427) passed deterministic reconstruction, preview guards and JavaScript syntax: **141 ordered patches / 68 preserved assets / 6,558,232 generated HTML bytes**, SHA-256 `54f1a4f994a14db376868240a14c56442ed7dfd38c5ac84a3aee2cf1545a1aa4`. Dedicated deployment and hosted verification remain separate gates before claiming live status.

## §E v11.108 · Native sculpt ghost preview with classic amber radius ring (2026-10-24)

The owner's side-by-side Android screenshots establish the intended pre-Apply brush UX: keep the familiar yellow/amber radius ring and visible wireframe, then show a teal temporary deformation preview on the existing mesh. §E v11.108 uses the real native sculpt stroke evaluator on a disposable geometry clone for meshes up to 48,000 vertices, rendering affected wireframe faces, raised/recessed vertex positions and motion vectors before committing. Dense models use a bounded, explicitly labeled sampled push preview where supported; other high-density modes retain the radius/depth guide without misleading precision. The new "Show mesh preview before Apply" toggle starts enabled and reacts to changed brush controls. Preview overlays are editor-only, disposable, non-pickable by the model selector, and never stored in source geometry, Undo history, JSON or GLB. Existing v11.107 amber footprint/violet depth, v11.106 Wireframe/X-Ray safeguards, mobile menus, saved scenes and all 68 assets remain preserved. Targeted GitHub preflight [run 40116649201](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40116649201) passed source reconstruction, exact patch anchors, JavaScript syntax and read-only preview checks; **140 ordered patches / 68 preserved assets / 6,555,286 generated HTML bytes**, SHA-256 `176ff6ec6baba39bffe123985ec1fecdd725b3002cf706f1a0c06950ebcf815b`. Code sealing and GitHub deployment are separate from actual Android aesthetic/gesture acceptance.

## §E v11.107 · Live radius footprint and depth guide before sculpt Apply (2026-10-24)

During owner testing of the new visible Pick center on mesh marker, the owner requested the marker to **match the brush radius** and show a **second layer preview for depth** before applying the edit. This new forward patch replaces the fixed-size helper ring with a brush-radius footprint and adds an inset ghost depth ring, tapered spokes and a center displacement axis (inward for intrude, outward for extrude). The preview updates as numeric inputs, mode and orientation change; it uses the native sculpt form's validated radius including screen-pixel to local conversion. It is an **illustrative planning guide**, not a Boolean cut or guaranteed precise deformed topology: the real stroke falloff and surface targeting still determine affected vertices. Editor helpers are non-pickable, are not saved or exported and leave brush history untouched. Preserve the v11.106 render-mode fix, menu sizes, touch scrolling, and drag behavior. Preflight assembled **139 ordered patches / 68 preserved assets / 6,545,909 HTML bytes**, SHA-256 `9aa81dd84b445e3cb51e84279a4141acd9a83069305332720753fea42f8946d0`. Production verification and actual Android visual/gesture acceptance are separate gates.

## §E v11.106 · Rebuild sculpt geometry without losing Wireframe/X-Ray (2026-10-24)

User's Android screenshot shows Render mode remains **Wireframe** but the actual sphere changes to a shaded solid immediately after pressing **Apply brush**. v11.105 targeted stroke Undo but did not enforce a viewport material invariant after *geometry edits*. §E v11.106 adds an after-render mesh/material consistency check for the global/selected viewport modes and explicitly requests an HD redraw whenever meshes or render display are rebuilt. It avoids extra geometry reconstruction and retains untouched the approved model window size/spacing/dragging, center marker, touch controls, assets, saved meshes and undo history. Source preflight measured **138 ordered patches, 68 preserved assets, 6,541,671 HTML bytes**, SHA-256 `18da40e3e728b97d0822494bb8038a6fe52a299603e11bebc6cd5aae8e4c3356`. Final hosted verification and Android Wireframe/X-Ray acceptance are still separate gates.

## §E v11.105 · Sculpt undo retains viewport mode; roomier floating menus (2026-10-24)

On Android v11.104 the owner confirmed surface-pick marker visibility but reported that clicking **Remove last stroke** while in X-Ray changes the render mode, and the right inspector remains cramped. Code inspection found the stroke-removal handler triggered `signalEdited()` **and** `select(p.id)`, redundantly rebuilding both geometry and view. The new forward patch eliminates the extra select/rebuild and independently preserves the global/per-part viewport display state and the All/Selected scope before refreshing mode UI; no sculpt geometry is altered. The panel becomes slightly wider, keeping 12px+ side trim, and increases vertical rhythm between labeled fields, paragraphs, sections and controls. Previously accepted v11.103 height, window dragging, scrolling gutters, touch-to-hold numeric pad, picked-point marker, 68 assets and all projects remain unchanged. Preflight measured **137 ordered patches, 68 preserved assets, 6,539,743 HTML bytes**, SHA-256 `d845e5ae1b064f4a6e1d7c41a654d1e561bfa8f4e1e02db227b5443ac9af5d3c`. The hosted-file verification and real Android X-Ray/Undo acceptance remain separate release gates.

## §E v11.104 · Visible sculpt pick marker and readable mobile menus (2026-10-24)

User Android screenshots show Pick center on mesh populating XYZ coordinates but no visible marker, and extremely cramped, difficult-to-read floating tool menus. This release adds a non-exporting, depth-test-disabled picked point ring/crosshair and outward surface-normal arrow aligned to the selected mesh, with an accessible XYZ status readout. On deselection or repick the marker is cleaned up. Native menu controls receive consistent typography, spacing, fieldsets, contrast, input alignment and touch-sized buttons while preserving the user-approved v11.103 window dimensions, dragging, scrolling gutters and 380ms hold-to-edit numeric keypad. Drilled cylindrical subtraction is **not** implied or added by this UI change; it requires a separate audited geometry feature. Preflight measured **136 ordered patches, 68 preserved assets, 6,535,811 HTML bytes**, SHA-256 `e205d04d8bd66d69994cbeca52b8a089468a6275146bfae59ba884bda6f443f1`. Live-host source verification and owner Android acceptance remain separate release gates.

## §E v11.103 · Double mobile inspector height only (2026-10-24)

After testing v11.102 on Android, the owner confirmed the floating Model Atelier window is better positioned and sized horizontally but asked to make the menu **twice as tall**. The new forward patch changes only mobile inspector height from 34dvh/350px to 68dvh/700px max, with an expanded state of 78dvh/800px max. The default 390px max width, original drag behavior, scrolling gutters, hold-to-edit keypad, 68 bundled assets, scenes and meshes are unchanged. Source preflight measured **135 patches, 68 preserved assets, 6,526,071 HTML bytes**, SHA-256 `7ce2d65c328d3c14f417062daaeb6f37f30b592c8f0b99f5cb305fd3bf1ee395`. Final hosted integrity verification and actual Android viewport acceptance remain separate gates.

## §E v11.102 · Balanced mobile size and real inspector dragging (2026-10-23)

Owner's next Android screenshot confirms the quarter-screen size in v11.101 is now too small and the inspector cannot be dragged. The existing v11.60 header pointer handler does calculate a new position, but later mobile CSS applies `top:auto!important`, `left:auto!important`, fixed `right` and `bottom`, so the script's inline top/left values never win. v11.102 retains that exact original pointer handler, preserves its model/tool behavior and translates its actual coordinates into scoped CSS variables which override mobile docking only after dragging. Default size is balanced at max 34dvh / 350 CSS px high, 390px wide; Expand reaches max 43dvh / 440px high and 440px wide. Side swipe gutters, hold-to-edit numeric pads, all scene geometry and exports remain untouched. Preflight measured **134 ordered patches, 68 preserved assets, 6,525,097 HTML bytes**, SHA-256 `fb2ec79211686c3aa4a69deaaa06570b83e8137abf9fb85b2d7a4869a2b1bb7c`. Production hosted verification and owner Android drag/scroll acceptance are separate gates.

## §E v11.101 · True quarter-screen compact mobile tools (2026-10-23)

Following real Android testing of v11.100, the owner reported that the supposedly compact tool panel still occupies roughly half the screen. The underlying 49dvh inspector default and 62dvh Expanded value caused that directly; an older mobile-adaptive inspector also carries higher-specificity !important sizing. The new additive release overrides both selectors: mobile inspector starts at no more than 26dvh / 255 CSS px, up to 320px wide, and Expand grows only to 38dvh / 385px and up to 375px wide. Context-sheet defaults are correspondingly reduced. All scroll gutters, deliberate number-field holds, brush controls and prior models remain unchanged. Compiled release measurement: **133 ordered patches / 68 preserved assets / 6,521,969 HTML bytes**, SHA-256 `011f44a659a6f0a76d482ba375476735b5f43c038082d3321f19f24bd2416162`. Full production verification and Android touch acceptance follow separately.

## §E v11.100 · Compact mobile panels, side swipe gutters and hold-to-edit (2026-10-23)

Owner Android screenshot confirms v11.99 panel scrolling but its full-width enlarged overlay covers too much of the modeling viewport. Owner asks for a near-original floating default size, a slightly larger optional expansion button, clear left/right scrolling gutters, and deliberate short press-and-hold to open numeric editing so scroll gestures never accidentally open the keypad. v11.100 is a presentation/input-only release. It restores compact floating sheets, adds a native Expand/Shrink button, widens internal scroll padding on both sides, and requires a stationary 380ms touch before the mobile numeric pad opens. Taps and moving touches do not open inputs. All existing mesh, brush, export, keypad Apply and saved-model logic is preserved. Package preflight measured **132 ordered patches / 68 preserved assets / 6,519,939 HTML bytes**, SHA-256 `aca02a1034c5ce79a70b024a2aa692344894493c9b4c79bc1d51b50d25a0eed1`. Independent hosted verification follows the separate deployment request; the actual Android press/scroll behavior still requires owner acceptance.

## §E v11.99 · Larger touch-scrollable Model Atelier menus (2026-10-23)

Owner Android testing confirmed the v11.98 keypad works, but scrolling the small floating sculpt panel is difficult and the other tool menus also feel undersized. Root cause candidates identified in the older floating dock are `pointer-events:none` over inspector background and a mobile supervisor width rule that can omit coarse-pointer/desktop-site phones. This mobile-only patch re-enables inspector touch hit testing, explicitly allows vertical panning on scroll surfaces, expands native inspector and context panels, and makes the horizontal tool rail larger. Existing modeling algorithms, the reliable v11.98 keypad, all 68 bundled assets and saved character geometry remain untouched. Preflight measured **131 ordered patches / 68 preserved assets / 6,513,741 HTML bytes**, SHA-256 `726cae0905ef5e2f8a381bebc109856b618451c68f7fa4afb5a0401332d2c783`. Production publication and owner-device swipe/scroll acceptance remain separate gates.

## §E v11.98 · Mobile number pad tap-through repair (2026-10-23)

On the user's Android browser, tapping a numeric field caused the new v11.97 in-editor keypad to appear and immediately disappear. The touch opened the keypad during `pointerdown`; the same gesture's following `click` could land on its Cancel backdrop. v11.98 gates pad click activation to controls that actually received the initiating pointer/touch press. Keyboard activation remains supported; original numeric change handlers, gesture controls, material editors and historical models are untouched. A mobile Chromium touchscreen simulation of the isolated dialog flow passed: opening does not close, numeric Apply reaches the native input, and a subsequent backdrop tap dismisses it. This test revealed that opening-tap click events can report `detail=0`, so v11.98 does not rely on `detail` alone for keyboard detection. Exact preflight measurement: **130 patches / 68 preserved assets / 6,509,696 HTML bytes**, SHA-256 `9b5033ee9bfcd3714ee4e52c0dd4dc46c2f06b78fb87eae441ffeac33aabe76d`. The separate manual deployment and owner touch acceptance are still required.

## §E v11.97 · Mobile viewport and focus-free number pad (2026-10-23)

Android owner screenshots confirm that §e v11.96's 16px numeric input style did not prevent browser page magnification. The actual document head contained one viewport tag with `maximum-scale=1` (two additional occurrences were inside historical runtime templates, not active document tags). The real head now uses `width=device-width, initial-scale=1` while preserving user pinch zoom and leaving historical templates untouched.

On coarse-pointer devices, tapping a Model Atelier numeric field opens a 44px-button in-engine number pad without focusing the browser input. The pad supports decimal, negative values, backspace, clear, validation against field bounds, Apply/Cancel and dispatches the original native change event. Desktop keyboard input remains unchanged. The v11.96 spherical blank starter stays uniform at `0.6/0.6/0.6`.

Preflight measured **129 patches / 68 preserved assets / 6,508,578 HTML bytes**, SHA-256 `9b3725919cce4c3cb135609dc815b449ceac8711658cc276afd6ba2a80882534`. Deployment and actual Android touch acceptance are separate release gates. Existing character geometry, history and stored assets are unchanged.

## §E v11.96 · Mobile input zoom and spherical blank model (2026-10-23)

New Model Project now opens with a uniformly scaled sphere (`0.6 / 0.6 / 0.6`) instead of the old nonuniform `0.5 / 0.6 / 0.8` blockout. On mobile/coarse-pointer layouts, Model Atelier number/text inputs, selects and text areas use at least 16px fonts to avoid the browser's small-field focus zoom. This changes only the new-model starter and editor input styling: all historical scenes, artwork and game models are preserved. Integrity preflight measured **128 patches / 68 preserved assets / 6,502,021 HTML bytes**, SHA-256 `c779e0889632a773341a78cbf0c3162932e5c7c9a6da17b20a60fc1166b3f3f9`. Model geometry and historical starter assets are unchanged; phone-browser focus behavior requires owner-device acceptance. Publication follows the separate final deployment request.

## §E v11.95 · Fitted festival skirt waist (2026-10-24)

The upper skirt now follows the existing waist and bodice more closely, then blends smoothly into the lower flare. Matching trim and the waist jewel follow the fitted surface. The lower skirt, knee-limit heights, opaque underlayer, smooth anatomy, soft portrait and original attached hair piñatas are preserved.

Release **127 patches / 68 assets**, **6,501,581 HTML bytes**, SHA-256 `a0d61bfac63c666ae7037edfb6b92f509abf8f7d4314615decb3b39bffa7ce8c`, marker `V11_95_FITTED_SKIRT_WAIST`. Targeted waist dimensions, coverage, native editing/save/export and immutable source lineage are recorded in [FITTED_SKIRT_WAIST_V11_95.md](reports/FITTED_SKIRT_WAIST_V11_95.md). Publication follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md), with ordinary source publication and a separate final deployment-request commit. Owner-device waist-fit acceptance follows the release.

## §E v11.94 · Full knee-length festival armor skirt and softer portrait (2026-10-24)

All nine existing lower armor panels now overlap around the hips and thighs as a continuous festival skirt, with matching piping, insets, stitches, brocade, baubles and tassels. Every lower costume piece ends above the kneecaps; the fitted opaque shorts retain crotch coverage. The nose has a softer bridge and rounded tip, and the head is subtly narrower with a smooth neck transition. Original hair piñatas, grips, sockets, rising amber eyes and smooth leg contours remain preserved.

Release **126 patches / 67 assets**, **6,495,464 HTML bytes**, SHA-256 `ede8f335dc9f9086d5d6f1ec6abf7d73711aa56bf3ea123c7494af2daac5d78c`, marker `V11_94_KNEE_SKIRT_SOFT_PORTRAIT`. The native model retains all **327 editable meshes / 1,755,616 triangles** and unchanged UV/index arrays. All **309** previous runtime/patch sources, **66** previous packaged assets and **117** companion meshes remain exact. Targeted validation and release evidence: [KNEE_SKIRT_SOFT_PORTRAIT_V11_94.md](reports/KNEE_SKIRT_SOFT_PORTRAIT_V11_94.md). Publication follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md), with a separate final deployment request after source publication; owner-device visual acceptance follows.

## §E v11.93 · Smooth anatomy, visible hair piñatas and fitted coverage (2026-10-23)

Both original hair-attached piñatas are visible in the normal opening/body view, with their original braid grips and sockets. Detail views retain the attached companions; the full-body camera fits their combined bounds. Eyes now rise clearly from lower corners near the nose to higher outer corners, with shallow round pupils and fitted lash wings. The face, cheeks, jaw and rounded chin use a continuous smooth skin contour. Exposed shoulder/arm muscles blend smoothly; thigh, knee, calf and ankle profiles remove the abrupt calf shoulder. A new Leg detail view makes that contour inspectable.

Compact hair locks leave the piñatas as the upper silhouette. More angular overlapping dress panels retain the longer festival tailoring. The existing under-skirt is replaced with fitted opaque shorts, and armor/cuff linings follow the actual finished skin to prevent poke-through and pelvis exposure. Saved originals, previous scenes, all piñata meshes and native socket data remain preserved. Release **125 patches/66 assets/6,477,235 HTML bytes**, SHA-256 `caad492d5e7ee95808c36102b47b24fcff816c340f242f9db1fc5d24a4316cf6`, marker `V11_93_SMOOTH_ANATOMY_PINATAS`. Source/editor/coverage/native-export checks passed; the separate final deployment request follows source publication. Source, editor, coverage and export evidence belongs to [SMOOTH_ANATOMY_PINATAS_V11_93.md](reports/SMOOTH_ANATOMY_PINATAS_V11_93.md). Publication follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md); local source completion does not claim production or owner-device acceptance.



## §E v11.92 · Reference face, swept hair and longer festival dress (2026-10-23)

The female Model Atelier starter follows the owner's festival references with amber almond eyes, finer arched brows, softer cheeks and a small rounded chin. The cyan/coral hair uses overlapping swept bangs, sculpted layers and cheek-framing locks. The layered teal, ivory and pale-cyan dress extends farther down; its yellow pointed tail reaches toward the knee. Native pleats, raised brocade, running stitches, pastel hem ornaments and a fine gold fringe add editable detail.

The connected skin mesh, original companions, 4K color/normal materials, native material editing/Undo, JSON save/import and textured GLB stay supported. The saved 283-part original and complete v11.91 scene remain packaged byte-exact. Release **124 patches / 65 assets**, **6,442,424 HTML bytes**, SHA-256 `eba0e3000950a95053dc7000bf9387d89e6fefa81e7d11cacdd722f765ddf6c5`, marker `V11_92_FESTIVAL_REFERENCE`. Local native/editor/save/export checks passed; canonical publication follows the separate final deployment request. This changes the existing authoring starter; it does not add skeletal rigging. Release details and validation: [FESTIVAL_REFERENCE_V11_92.md](reports/FESTIVAL_REFERENCE_V11_92.md). Publication follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md); owner-device visual acceptance follows the dedicated release.




## §E v11.91 · Saved Festival Girl and organic anime sculpt (2026-10-23)

The previous **283-part girl starter is preserved** as **Saved Festival Girl · v11.90** (`?project=festival-girl-saved`). The main Model Atelier card now opens **Prism · Organic Anime Girl** (`?project=organic-anime-girl`). Her complete skin is one closed, connected mesh from scalp and ears through the neck, torso, arms, ten fingers, legs and feet: **254,588 vertices / 509,172 triangles**. A more inward-tapering jaw ends in a narrow, rounded chin; shaped cheeks, orbital wells, a refined nose, fitted amber eyes tilted upward six degrees at the outer corners, and lips, hands with nail plates, knees, rear calves and Achilles transitions replace the old separate primitive anatomy.

The full sculpt has **353 editable topology meshes / 1,634,372 triangles**, including the asymmetric festival outfit, original paper-ferret companions and bunny. **72 tapered 3D hair filaments**, modeled stitches, knuckle folds and fitted closed sleeve/yoke shells add geometry detail. Dedicated **4096×4096 color and normal maps** provide skin, hair flow, weave, embroidery, leather, metal and radial iris detail. Body, face, hand and full-character views support close inspection; companion isolation changes the viewport only. Native material editing/Undo, JSON save/import and textured GLB retain the complete model. Detailed native import supports **256 MB**, and a part supports **300,000 vertices / 600,000 triangles**. This is a detailed authoring sculpt; skeletal weight painting has not been added.

Release **123 patches / 64 assets**, HTML **6,421,818 bytes**, SHA-256 `ba0105f62f2e7451d4e78148cae425f4ce5e3684093fc3954d3c1f0e1105b934`, marker `V11_91_ORGANIC_ANIME_GIRL`. All **294** prior runtime/patch sources and **60** prior packaged assets preserve exact bytes. Sheep Tag retains the v11.90 collision, controls and optimized game models. See [targeted verification](reports/ORGANIC_ANIME_GIRL_V11_91.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.90 · Solid house blockers, furred Astra and match performance (2026-10-23)

Houses stop sheep on contact. Holding the joystick first walks up to the blocker, then follows a cached, collision-checked route around it; releasing stops immediately. The previous nearest-side/lane-center pulling and construction ejection are retired. Placing a structure over its builder is rejected without moving the sheep or spending gold. Real narrow lanes, rotated houses, unit traffic and automatic ramp/walkway traversal retain native swept collision.

Astra now has flowing shoulder/ribcage/waist contours, **one connected skull-and-ear mesh**, inset velvet pinnae and **1,100 closed curved 3D fur locks** on its body, chest and limbs. The high-resolution wolf starter has **96 editable parts / 639,772 rendered triangles**, with all **37 original courier gear/comet-tail parts byte-exact** and the original **4096×4096 color and normal images**. Native rebuild, edit/Undo, JSON save/reload and textured GLB remain available; detailed native import supports 128 MB.

Sheep Tag uses a separate optimized copy: **69,471 triangles / 29 draw meshes per wolf**, compared with **274,980 / 106** previously. Compatible meshes are merged within each independently animated head/tail/leg joint, sharing cached geometry and materials. Broad-phase collision rejects distant houses before identical narrow-phase samples; footprints cache per navigation revision. Held-stick routes avoid repeated whole-map grid searches. On phones, full-rate run recording uses **10 Hz world snapshots**, preserving command/event captures and explicitly selected slower cadences. These changes target CPU, GPU and recording overhead; owner-device FPS still needs hands-on acceptance. Clover, compact corner controls, the 320×320 m map and seven-minute rounds remain.

Release **122 patches / 60 assets**, HTML **6,390,662 bytes**, SHA-256 `c76e61f6c4b8457ce1f49d3781c8aa0710d7e44adaf7176d17744fdbda5c663a`, marker `V11_90_SOLID_BLOCKERS_FURRED_ASTRA`. All **290** previous runtime/patch files and **58** previous assets preserve exact bytes. See [targeted validation](reports/SOLID_BLOCKERS_FURRED_ASTRA_V11_90.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.89 · Living Astra, Clover flock and compact corner controls (2026-10-23)

**Astra's full anatomy pass** replaces separate tube-like legs/toe pieces with four welded anatomical limb/paw meshes, including elbows, wrists, hocks, tendons and four toes per paw. The seated torso has shaped shoulders, ribs, pelvis and tucked belly; the ivory chest now tapers naturally and fits beneath the original harness. The face has orbital wells, a defined brow stop, tapered muzzle/lower jaw, canine pupils and nostrils. Closed cupped pinnae and curved fur surfaces replace the remaining biological primitive parts. All **24 original gear parts and 13 comet-tail/stardust parts** remain byte-exact. The native model contains **92 editable meshes / 547,676 rendered triangles**, retaining the original **4K color/normal atlases**. It remains rebuildable with the editor's organic volume/sweep tools and supports material editing, Undo, native JSON and textured GLB.

**Clover replaces the sheep in Sheep Tag**, including all eight starter sheep and reconstructed/spawned `st-sheep` actors. It uses the same 31 source parts, fleece/face/ears/hooves, native atlas bindings and shared **4096×4096** images as the new independent sheep model. A game copy made with Model Atelier's native mesh reducer uses **33,087 triangles**, while the original **275,872-triangle** authoring starter remains unchanged. Cached geometry/materials are shared across independently animated head, tail and four leg joints. Fleece width fits within the existing sheep collision diameter; routes, capture/wisps, construction and timer retain native logic.

**Controls corrected to the owner's screenshot:** at 926 px portrait width, the joystick and building/skill diameters are about **45% of v11.88**, with the joystick anchored **18 px from the left / 22 px from the bottom**. Separate compact right-side arcs retain spacing, readable labels and safe margins. Narrow screens keep a minimum 44 px ability target and 50 px building target. Landscape moves auxiliary actions beside the joystick to clear the minimap.

Release **121 patches / 58 assets**, HTML **4,557,192 bytes**, SHA-256 `a9f6b48036c852be5a75150f18ebc9e31633c43acaa28c3b08a79b1d67506ed0`, marker `V11_89_LIVING_ASTRA_CLOVER`. All **285** prior runtime/patch sources and **56** previous assets preserve exact bytes. See [targeted validation and anatomy references](reports/LIVING_ASTRA_CLOVER_V11_89.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.88 · Roomier passages, reachable controls and original Astra (2026-10-23)

Sheep prioritize alignment through nearby usable house lanes before steering around an outside corner. Short joystick targets refresh immediately, so previous corner routes cannot keep a sheep trapped. Existing 0.60 m lanes remain usable; new deliberate house-lane snapping leaves **0.75 m**, with native footprint, collision and traffic checks shared by preview and construction.

The joystick moves inward/up and scales to **65% of portrait viewport width**. Building buttons use **21%**, the main house **22%**, and abilities **18%**, with two separated arcs. At the 926 px screenshot width that means roughly **194–204 px building buttons**, about three times the previous size. Phone/landscape sizing and short-screen minimap clearance adapt to the available viewport.

The wolf starter again opens **Astra · Comet Courier**, retaining the original blue/ivory design, amber eyes, tall ears, cape, harness, satchel, compass, scroll, lantern and giant curled comet tail. All **37 original gear/tail parts** remain byte-exact. Three native welded anatomical surfaces add **134,348 triangles** across the torso/shoulders/haunches, skull/jaw and continuous muzzle; the original **4K color and normal maps** remain. Clover sheep stays available as its independent starter. Detailed native editing, material Undo, save/import and textured GLB export remain supported.

Release **120 patches / 56 assets**, HTML **3,371,397 bytes**, SHA-256 `6d4ce7a4f95c2c90fb988d99867ee240c7a505df13b43c7be4b2038f506e4c2e`, marker `V11_88_PASSAGES_CONTROLS_ORIGINAL_WOLF`. All **281** preceding runtime/patch sources and **55** assets preserve exact bytes. See [targeted validation](reports/PASSAGES_CONTROLS_ASTRA_V11_88.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.87 · Organic sheep and wolf model starters (2026-10-22)

**Clover · Meadow Sheep** is a new independent Model Atelier starter. **Fen · Wildwood Wolf** replaces the wolf model starter entry and the earlier `comet-courier` shortcut. The wolf is a natural quadruped with a fused ribcage/shoulder/neck/skull/muzzle surface, a tucked waist, bent hocks, four-toed paws, short alert ears and a low brush tail. The sheep has continuous fleece over shoulders/barrel/haunches, a tapered bare muzzle, folded pinnae, horizontal pupils, lower-leg tendons and split hooves. Visible parts are editable indexed organic meshes; there are no sphere, box, cylinder or cone model parts.

The native organic volume tool blends anatomy fields into a connected, welded surface. Model Atelier exposes `loadAnimal(species, {force, rebuild})` to rebuild with that tool, alongside the standard component, sculpt, group, undo, material and export controls. Both starters use a shared **4096×4096 color atlas and matching 4096×4096 normal map**. Native model import supports 64 MB detailed saves and meshes up to 65,536 vertices / 120,000 triangles per part; high detail remains authored data. Textured GLB export embeds the proper atlas, including mixed original/animal materials. Studio view opens with a clear silhouette and an Edit model button. Saved project payloads are compressed losslessly in `payload/organic-animals`; packaging emits the portable native JSON scenes.

Release **119 patches / 55 assets**, HTML **3,359,239 bytes**, SHA-256 `c2dda3de1cb7bf262e347a47c9dfde2f9c4af267ed1124fee068a804fb6cda40`, marker `V11_87_ORGANIC_ANIMAL_STARTERS`. All **277** previous runtime/patch sources and **51** assets preserve exact bytes. Sheep Tag retains v11.86 nearest-side house steering, 7-minute matches, large controls and the 320×320 m map. These model projects are independent authoring starters. See [targeted validation](reports/ORGANIC_ANIMALS_V11_87.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.86 · Sheep steer around houses (2026-10-22)

Holding the joystick into a house now steers a living sheep toward the **nearest clear side/corner**, then continues in the held direction. A blocked side falls back to the other clear side. Fully blocked exits stop safely. This uses the native swept movement and analog speed; it never relocates a sheep through a structure. Rotated houses, other creatures, narrow sheep-only gaps, joystick reversal and release are checked. Wolves, wisps and automatic ramp/deck movement keep their existing controls.

Release **118 patches / 51 assets**, HTML **3,340,927 bytes**, SHA-256 `01b695c06bc5636b762d87914d76e2511224345add0e80c93ce6a1e6f04eba0b`, marker `V11_86_SHEEP_HOUSE_SLIDE`. All **275** previous runtime/patch sources and **51** assets preserve exact bytes. The 320×320 m map, 4K textures, enlarged controls, 7-minute timer and versioned update history remain available. See [targeted validation](reports/SHEEP_HOUSE_SLIDE_V11_86.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.85 · Bigger controls and seven-minute matches (2026-10-22)

The portrait joystick grows from **156 to 224 px** and moves diagonally **up and right**. Compact portrait uses 192 px; landscape uses 208 px, or 176 px on a short phone. The knob and direction mark grow with it. Right-side buildings and abilities grow by roughly 12–23% in the main layouts, with adaptive compact sizes and the two separated arcs retained. Larger labels wrap within their circles. Landscape score, utility buttons and feedback shift to keep the enlarged controls accessible.

The default match lasts **7 minutes (420 seconds)**. The portable starter carries that duration, and saved maps using the previous 20-minute default migrate to seven minutes. Other explicitly tuned durations remain editable. The native countdown, head start, win conditions, movement, ramps and placement use their existing game clock and rules. The editor’s versioned update panel automatically lists this release.

Release **117 patches / 51 assets**, HTML **3,338,122 bytes**, SHA-256 `76ea088b19a441ed0e846ffdd4a02197eb131b45a3ea55255eeb032f7c5d13f4`, marker `V11_85_LARGE_CONTROLS_SEVEN_MINUTES`. All **272** earlier runtime/patch sources and **50** preceding assets preserve exact bytes; the additional asset is the seven-minute starter scene. See [targeted validation](reports/SHEEP_LARGE_CONTROLS_V11_85.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.84 · Reliable building, connected walkways and update history (2026-10-22)

- **Building recovery:** one placement pointer owner handles icon and meadow drags. Rejected/cancelled drops release capture, remove the ghost and clear the selected tool. Unaffordable buttons show a cost message without entering placement, so the free house remains available.
- **Automatic ramps:** joystick steering ascends and descends completed ramps directly, follows connected decks and stops at unsupported edges. The ground/upper-route and descent toggles are hidden. Species radii, traffic, wolf ramp permissions, capture and hunt-release restrictions remain native.
- **Connected extensions:** walkways and exit ramps snap to existing deck/ramp high edges and rotate toward the selected side. Straight extensions and side turns share physical seams and the native route graph. Sheep already on a connected deck can construct a nearby extension; normal costs, occupancy, sanctuary and completion rules still apply. Player-built side connections open a gap in the parent rail when complete.
- **Touch controls:** abilities occupy an inner arc beside the outer building arc. A larger joystick and separated compact layouts keep targets at least 44 px. Touch aim rises **128–180 px** above the finger, with top-readout clamping.
- **Larger map:** the new starter is **320 × 320 m**, 25% wider and 56.25% more area than the preceding 256 m meadow. Authored scenery, roads and the 4K ground scale with the layout; previous scene files remain unchanged.
- **Editor updates:** an automatic latest-update panel includes **107 previous versions**, grouping every previous patch. Its checkbox hides only this exact version; the next release appears again. The editor footer’s **Updates** button reopens it, and unchecking restores the popup. Future source versions derive notes and history automatically from the manifest and new patch summaries.

Release **116 patches / 50 assets**, HTML **3,333,468 bytes**, SHA-256 `82ae2d5fdac77f9a63cb4375aae2d93939c8cdf3338395f7120995f62d2bc411`, marker `V11_84_BUILD_RECOVERY_WALKWAYS`. All **264** preceding runtime/patch files and **49** prior assets preserve exact bytes. The additional asset is the larger native scene. See [targeted implementation and evidence](reports/SHEEP_RECOVERY_WALKWAYS_V11_84.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.83 · Drag houses to build, joystick movement and smooth fog (2026-10-22)

Manual movement now uses the **left joystick**, including the desktop pointer layout; ground clicks/taps no longer issue move orders. Drag a building skill icon onto the meadow, aim with the house **above your finger**, and release on a green footprint to order construction. A tap can also arm the building tool for a subsequent ground drag. Visible house/unit selection, wolf attack, rescue, camera pan and minimap camera navigation remain available. Construction retains its native approach, collision, footprint, cost and completion rules. Accepting a build releases held joystick ownership so the next frame cannot overwrite the construction order. Steering again deliberately replaces that order. Blocked/cancelled drops do not charge gold or build. The preview rechecks affordability and occupancy while held still, avoiding a stale red “Need gold” message after income arrives.

Fog uses **soft circular vision edges**, linear sampling and a 4× display mask (512×512 on the 256 m meadow), updated at most ten times per game second. The minimap shares that smooth display. Logical visibility, explored cells, enemy filtering, bot knowledge and pre-hunt restrictions remain native. All **262** preceding runtime/patch files and **49** assets retain exact bytes, including the 4K artwork.

Release: **115 patches / 49 assets**, HTML **3,288,058 bytes**, SHA-256 `41b34b31203777afffc242d42a83b32157e61442760fa9549960600ed27d7962`, marker `V11_83_DRAG_BUILD_SOFT_FOG`. See [targeted implementation and validation](reports/SHEEP_DRAG_V11_83.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.82 · Mobile building skills, joystick and clear touch placement (2026-10-22)

Sheep Tag now uses **round illustrated building skill buttons at the bottom right** on phones/tablets: house, income house, fortified house, wall and ramp. The existing native buttons retain their costs, availability, active state and build commands. A **left movement joystick** steers the actual sheep/wolf through native swept collisions and traffic, supports proportional speed, and stops on release/cancel/pause/blur. Captured wisps keep their slow crawl/leash; wolves remain immobile before release. The minimap moves to the top left. A compact **••• unit-actions drawer** keeps camera, upgrades, selling and archive controls accessible, while the editor footer returns after Stop. Desktop controls retain their original layout.

Touch building aim is **72–112 screen pixels above the finger**, with a dotted guide to the exact snapped footprint. Preview and release use the same native build target. Separate pointer owners let one thumb steer while another aims; two simultaneous placement fingers still cancel safely. Portrait, landscape and compact screen layouts keep touch controls at least 44 px. Camera following and normal frame updates keep the ghost aligned; resizing cancels held gestures.

Release **114 patches / 49 assets**, HTML **3,279,865 bytes**, SHA-256 `e0bfe63ddae1f5430cf0f80f7f17bd9745a5d0147d68fb96afbb441353d9b6c2`, marker `V11_82_TOUCH_BUILD_SKILLS`. All **259** preceding runtime/patch sources and all **49** bundled assets retain exact bytes, including the Astra and ground 4K textures. See [implementation and targeted evidence](reports/SHEEP_TOUCH_V11_82.md). Publication follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md): cohesive source, separate final deployment request and exact hosted-package confirmation.

## §E v11.81 · Building clearance, protected sanctuary and hidden hunters (2026-10-22)

House foundations and outlines now reach the real blocking footprint. Nearby face-to-face gaps show their measured width and a colored label: **red BLOCKED**, **cyan SHEEP ONLY**, or **gold BOTH**. Classification uses the native swept collision checks, surrounding visible structures and actual species radii. Exact lane entry points let sheep use fitting narrow passages even between navigation-grid lines. Default sheep need **0.54 m** and wolves **1.80 m**. The gold sanctuary boundary marks a **22 m no-build radius** on the default 256 m map; the whole structure must fit outside it. Both player placement and AI construction use this rule. Bots choose reachable outward bases instead of falling back to their central spawn.

Wolves are hidden and nonphysical during the countdown, with no perception, target memory, minimap markers or pre-release scent information. A waiting wolf role has no sheep/building vision. After release, bot hunting requires actual sightings; lost sheep leave only their last observed position. Default sheep speed rises from **5.4 to 6 m/s** and Astra hunters are **15.4% larger**, with collision radius increasing from **0.78 to 0.90 m**. The 106-mesh/274,980-triangle hunter and original 4K atlases remain. Captured-wisp crawl/leash/rescue behavior is retained.

Release **113 patches / 49 assets**, HTML **3,258,318 bytes**, SHA-256 `9fb46459d3ca870f766ff7c90c18a1649ffbfc68352da25c493bc5ffe284186c`, marker `V11_81_SHEEP_CLEARANCE`. All **257** previous patch/runtime sources and **49** assets preserve exact bytes. Details and targeted validation are in [the release report](reports/SHEEP_CLARITY_V11_81.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md): cohesive source commit, separate final deploy request, terminal production success and exact hosted-source/asset confirmation.


## §E v11.80 · Vast Wildwood, central starts and captive wisps (2026-10-22)

The default map is now **256 × 256 m**, **4× the previous playable area**. All eight sheep start **9.5 m from the central respawn sanctuary**, rather than around the outer map. The existing four-region roads/ground/minimap and 4K Astra hunters remain. Fine **0.15 m** pathfinding now uses direct clear trips and cached local windows for most obstructed routes in large maps, with an unrestricted fallback for longer detours.

Captured wisps crawl at **0.35 m/s**. They may drift **2.5 m beyond each side of the pen**; crossing that leash teleports the still-captured wisp to its own capture spot and clears its movement/rescue progress. Reaching the leash never revives a sheep. The existing other-living-sheep rescue/hold/protection behavior remains the only revival path. Native move controls and help text describe this behavior.

Release **112 patches / 49 assets**, HTML **3,243,526 bytes**, SHA-256 `a4b58b9da3991fdd10fee42c4fd18648c65a79932b0af69ceea1a117ce5f151d`, marker `V11_80_VAST_WILDWOOD_WISPS`. The new native scene has 196 editable actors, eight central sheep, three Astra hunters and nine map layers. All 255 preceding patch/runtime sources and 48 previous assets retain exact bytes. Targeted CPU/browser checks and publication evidence are recorded in [the release report](reports/VAST_WISPS_V11_80.md). Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and terminal production run under current [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.79 · Moonbell Wildwood — larger Sheep Tag map (2026-10-22)

The default Sheep Tag starter is now **Moonbell Wildwood**, **128 × 128 m** versus the previous 80 × 80 m (**2.56× the area**). Four color-separated woodland regions — Pinewatch, Moonflower, Amberglade and Willowmere — surround open building glades, an octagonal road loop, cardinal/diagonal roads, four merchant plazas, four ponds and a central sanctuary with stone markers. Four genuine narrow stone passages admit sheep while hunters detour. The terrain and fog-respecting minimap share original **4096 × 4096 ground artwork**. There are **176 individually editable native actors** in nine map layers, retaining eight sheep and three 4K Astra hunters. Match timing, movement/combat rules and optional archive settings remain intact; the previous 80 m map is preserved as a separate source and remains loadable.

Release **111 patches / 48 assets**, HTML **3,222,398 bytes**, SHA-256 `f2d2c22aa4620f76407494767e27a4227c3d178af3f8a52f7fc736c6eb28e9ec`, marker `V11_79_MOONBELL_WILDWOOD`. All 253 preceding runtime/patch sources and 46 earlier assets retain exact bytes. Targeted desktop/phone-layout checks cover start validity, full map framing, all spawn/outer-road connectivity, four species-sized passages, native/portable save/load, generated floor scale, movement/construction outside the old boundary, terrain minimap and previous-map compatibility. Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and its terminal production receipt. See [map design and evidence](reports/SHEEP_WILDWOOD_V11_79.md); delivery follows current [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.78 · Astra hunters in Sheep Tag (2026-10-22)

Sheep Tag's `st-wolf` prefab now renders the complete **Astra · Comet Courier** model, with all 106 native meshes and the original 4096 × 4096 color/normal atlases. The three canonical hunters, newly spawned hunters and wolves reconstructed from older native project saves all use the same visual. Independent head, tail and four leg pivots connect the saved model to the existing walk and attack animations; geometry/materials and texture images are reused across instances. Logical wolf roles, IDs, names, teams, navigation/collision radii, combat, economy and map data are preserved. The independent editable Astra project remains available.

Release **110 patches / 46 assets**, HTML **3,152,424 bytes**, SHA-256 `234ddf6065f89438a3cabbcd9e3521d82fb08245830525131e3976d4f86b9ad4`, marker `V11_78_SHEEP_TAG_COURIER`. All 250 preceding runtime/patch files and 46 bundled assets are byte-preserved. Targeted local desktop/phone-layout checks cover loaded 4K maps, native spawn/save/reload, movement/four-leg gait, building attacks/head animation, sheep tagging and Stop/restart restoration. Deployment status and source commit resolve through the final separate `DEPLOY_REQUEST.json` and its terminal production run; owner device acceptance follows publication. See [integration evidence](reports/SHEEP_COURIER_V11_78.md). Delivery follows current [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

# §wyrl§ Engine v11.77

This Space publishes the governed engine build. Project release details, historical verification evidence, and update notes are maintained in `projects/swrlz-forge-moba/README.md` and `§tart_§E.md` in the source repository. Historical Space documentation remains available in Git history.

Model Atelier includes native portrait and cloth shaping, tapered ferret muzzles, selected-part framing, independent piñata sockets and saved model motion.

The current portrait/body starter adds saved chin/nose/skin warmth, surface-fitted facial contours, softer shoulder/arm transitions, HD sampling and native calf/shin anatomy.

Native anatomical head sections define skull, temples, cheekbones, jaw and chin independently. Facial contours fit the rebuilt surface. Release: v11.20 / V11_20_ANATOMICAL_HEAD, 90 patches and 43 assets.

§E v11.59 adds the cumulative precision Model Atelier toolkit: camera-visible connected-surface sculpting, native lasso/mask editing, vertex gizmos, photo references and feathered UV cutouts, controlled topology/UV-aware LOD and geometry export. The original anatomical character scene and historical projects/assets remain preserved. Marker: `V11_59_PRECISION_MODEL_ATELIER`; 91 patches and 43 original assets.

§E v11.60 replaces the fixed bottom phone inspector with a vertical tool rail, collapsible draggable floating controls and a full-height viewport. Native controls, saved 283-part scene and all 43 historical media assets remain unchanged. Marker: `V11_60_FLOATING_MODEL_ATELIER_DOCK`; 92 patches and 43 assets.

§E v11.61 adds the optional ◫ Context secondary split floating tool workbench in Model Atelier: select an operation and adjust actual native properties in the adjacent panel. Supports Meshes, Sculpt, Lasso, Face, Topology, References, Motion and Appearance where actual controls exist, explicit saved presets and original inspector access. This does not add unrelated anime/game editor adapters. Marker: V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH; 93 patches, 43 original assets.


§E v11.62 introduced the mobile-first unified Model Atelier tool sheet above the bottom category rail with Compact/Half/Expanded sizes, operation search and All/Quick/Recent, per-operation favorites, handedness and a return to the original native inspector. Desktop retains its movable workbench. All 283 original model parts and 43 assets persist. Marker: V11_62_MOBILE_ADAPTIVE_TOOL_SHEET; 94 patches. This previous feature release is retained for historical context.

§E v11.63 is a version-only deployment smoke test. No modeling, gaming or animation behavior changes; 95 ordered patches, original 283-part canonical model, and 43 historical assets. Marker: `V11_63_VERSION_SMOKE_TEST`. The verified live deploy receipt determines whether v11.63 is actually hosted.

§E v11.64 is a version-only §§§ release speed test. No modeling, gaming, or animation behavior changes; 96 ordered patches, original 283-part canonical model, and the same 43 historical assets. Marker: `V11_64_VERSION_SMOKE_TEST`. Hosted status requires a successful deployment receipt.

§E v11.65 adds a contextual selection-based mesh transform strip next to the picked model part. Move/Rotate/Scale gizmo axes and plus/minus nudges, multi-mesh grouping and baked Join are native/Undo-enabled. Show vertices opens the existing real vertex-point overlay. U/V steppers make procedural density discoverable for sphere/loft/box/cone/cylinder and face-sheet meshes within bounded geometry budgets; nonparametric topology uses the existing refinement tools. Joined topology mesh material uses the first selected mesh. Original 283-part starter and 43 historical assets are preserved. Marker: `V11_65_SELECTION_MESH_GIZMOS`; 97 ordered patches. Hosted status requires the final verified release receipt.

§E v11.66 repairs Model Atelier mesh transform usability: removes doubled selection BoxHelper, bounds camera-scaled axis dragging to ≤0.45 world units per gesture, adds Undo/Redo/Frame mesh in the selection strip, persists a draggable popup position per-device, and coordinates a cybernetic cyan/indigo visual treatment across existing tool panels. Current mesh functionality, original 283-part scene and the 43 historical assets remain unchanged. Marker: `V11_66_MESH_SELECTION_UX_REPAIR`; 98 ordered patches. Physical-device usability remains owner-tested.

§E v11.67 is a focused Model Atelier performance update: whole-mesh Move/Rotate/Scale commits now update only their existing Three.js mesh transforms and inspector/history state, avoiding the v11.66 full 283-part geometry rebuild on release. Canceled/no-op drags also avoid the rebuild. Undo/Redo/JSON/OBJ remain available. 99 ordered patches; unchanged original 283-part character and 43 packaged assets. Marker `V11_67_MESH_TRANSFORM_PERFORMANCE`; mobile responsiveness awaits owner testing.

§E v11.68 improves touch editing of native Model Atelier parts: while dragging the X/Y/Z gizmo, selected meshes, bounding outlines and transform handles all follow live without rebuilding their geometry or resetting a captured handle. Tapping a different object updates its existing selection BoxHelper immediately instead of rebuilding all 283 character parts. Transform release still uses the v11.67 fast commit path and native Undo/Redo. The canonical 283-part project and 43 original assets remain preserved. Version marker `V11_68_LIVE_MESH_GIZMO_FEEDBACK`, 100 patches. Touch smoothness remains subject to the owner's live Android test.

§E v11.69 corrects delayed mesh drag preview in Model Atelier. Pointer movement updates the already-rendered native geometry and axis handles, computes gizmo location directly from captured pivot and delta (without recalculating mesh bounding boxes every move), and paints a WebGL frame immediately during active drags. No source topology, model geometry, or original material changes. Native saved transforms/Undo/Redo retain v11.67 behavior. A real Chromium pointer-drag regression confirmed both mesh and handle moved before mouse release (9 movement + 9 render updates); Android owner testing is still needed. Original 283-part starter and 43 packaged assets retained. Marker `V11_69_DRAG_PREVIEW_RENDER`; 101 ordered patches.

§E v11.70 improves phone authoring workflow: the viewport top bar groups Render/Target, a horizontally scrollable camera direction row, and a collapsible Display/Wire/Interior section, preserving all original controls and handlers. A compact Fine–Fast transform sensitivity slider in the selected-mesh popup sets persistent **per-mode** Move/Rotate/Scale multipliers from ⅛× to 4× for both pointer drags and ± nudges. This adjusts operation responsiveness, **not vertex count**, which remains in Grid U/V. Undo/Redo and live-gizmo renderer are unchanged. A real Chromium pointer test verified 0.180-unit standard versus 0.0225-unit ⅛× movement for identical 25-pixel drags, mode-specific setting retention, navigation visibility and 390px layout. 102 patches, original 283-part canonical starter, 43 bundled assets. Marker `V11_70_PRECISION_GIZMO_TOOLBAR`.

§E v11.71 adds an actual three-axis 3D **curved rotation ruler** to Model Atelier. When Rotate is active, instead of three straight arrows the selected mesh shows colored X/Y/Z partial rings with graduated 15°/30° tick marks and mobile-sized draggable beads. Touching a bead rotates the selected mesh live along the corresponding axis while the bead follows its arc. The Mesh Tools dialog shows the angle plus optional off/5°/15° snapping. Existing per-mode Fine↔Fast sensitivity also applies. Move/Scale, native Undo/Redo, source meshes, original 283-part character and 43 packaged assets remain unchanged. Browser pointer interaction verified rotation changed **before release**, 12 live WebGL updates and persisted changes; phone behavior awaits owner test. Marker `V11_71_ARC_ROTATION_RULER` with 103 ordered patches.

§E v11.72 calibrates the rotation arc gizmos to each selected mesh instead of camera zoom; a selected anatomical head now receives a radius of about 0.573 model units rather than 0.952 in the earlier zoom-only implementation. Pointer angles are derived from a 3D ray/rotation-plane intersection (with stable screen tangent fallback for edge-on arcs), while colored axis focus separates overlapping rings and a screen-pixel hit radius prevents accidental selection of distant ring handles. The popup explicitly labels each **rotation delta**, not absolute Euler orientation. X, Y and Z were separately tested in Chromium against the selected head before pointer release, with visible mesh transforms and persisted Undo-able changes; owner Android acceptance remains pending. The original 283-part canonical model, all 43 bundled assets, snapping, Fine/Fast sensitivity, Move/Scale and history remain intact. Marker `V11_72_ROTATION_ARC_ALIGNMENT`; 104 ordered patches.

§E v11.73 fixes Model Atelier gizmo mode switching and arc hit testing on Android. Move/Rotate/Scale and X/Y/Z button presses synchronously paint the rebuilt gizmo without waiting for an orbit or pan gesture. The existing selected-mesh-relative rotation rulers now use thicker 3D tube geometry and larger visible beads, with camera-projected screen-space hit testing across *any point on a curved arc* rather than only tiny endpoint grips. Where colored arcs overlap, the actively selected axis in the floating popup takes priority. Existing per-mode Fine/Fast sensitivity, live object rotation, rotation snap, native Undo/Redo, original 283-part character and all 43 assets remain unchanged. Chromium interaction verified immediate mode switching, live rotation by grabbing a curve away from its bead, and phone-width touch hit areas. Marker `V11_73_INSTANT_GIZMO_ROTATION_TOUCH`; 105 patches.

§E v11.74 adds non-destructive editable flat mesh groups and persistent mobile Multi-Select to Model Atelier. Tap Multi-Select to toggle selected parts, Clear/Done, Select first 32, then Group selected; switch between Edit group (shared Move/Rotate/Scale with world-space pivot) and Edit child (individual member controls), Update members, Remove child and Ungroup without destroying geometry or per-part materials. The existing **Join selected** remains intentionally destructive and separate. Group membership is saved in modelAtelier.meshGroups and validated on model JSON import. The native full-model Undo/Redo snapshots preserve original animation/socket assemblies and revert group creation, group transforms, edits and ungrouping. The original 283-part starter and 43 assets remain untouched. Chromium regression verified group/ungroup, live selection toggling, group transform, Undo/Redo, exported/imported group identities, 390px responsive multi-select and preservation of every original part/material. Release marker `V11_74_NONDESTRUCTIVE_MESH_GROUPS`, 106 patches. Owner physical touchscreen test remains pending.

§E v11.75 introduces native per-mesh Mesh/Vertex/Edge/Face component modes, mobile touch-select, multi-select, box/lasso region tools, selectable geometry overlays, and live Move/Rotate/Scale gizmo transforms and precision nudges at shared component pivot. Real mesh changes persist as existing indexed `sculptVertexEdits` in the Model Atelier project and participate in Undo/Redo, JSON, and OBJ output; parent part geometry/material/transform and v11.74 non-destructive groups are untouched. Vertex/edge taps raycast the visible native face and find nearby components rather than scanning every edge on every Android tap. Dense selected meshes sample edge/face overlays for performance. Live drag clamps local displacement to the existing ±0.5-unit safe edit budget before paint, with final validation on release. Refinement meshes with enabled refinement layers are deliberately not component-editable until stable vertex indices can be assured. 283 canonical parts, 43 original assets, 107 ordered patches. Marker `V11_75_COMPONENT_EDIT_FOUNDATIONS`. Real Chrome testing covered native geometry edits, Undo/Redo, one-finger gizmo dragging before release and saved offsets, edge/face selection, multi-select, rectangular/lasso selections, 390px controls; owner Android testing remains pending.

§E v11.77 repairs desktop Model Atelier after the owner's real gaming-monitor test. Desktop mouse gizmo drags use opt-in-by-interaction pointer lock with virtual cumulative mouse movement so a physical pointer needn't stop at the screen edge. Scale/move/rotation gizmo motion no longer uses the legacy 3× scale-per-drag ceiling; instead transforms preview and commit only up to native valid model scale/position bounds, and scale commits rebuild the actual procedural scene once so piñata/hair meshes visibly update before Undo. The non-destructive wireframe display dims unrelated dense lines, brightens the selected wire mesh and allows real sampled native mesh vertex dots to be independently displayed via accessible View > Display, wire & interior toggles; the open top menu stacks above the movable mesh gizmo dialog. Wheel, zoom button and pinch share a closer 0.16 world-unit minimum with safe near clipping, retaining camera reset presets. The 283 original character parts and 43 packaged assets remain unchanged. Chromium browser test run 39674744767 validated >3× scale (9× candidate), immediate native scale, Undo/Redo, 1,677 selected-mesh vertex markers, wire dimming, vertex toggle, and minimum zoom 0.16 with near 0.018. Pointer-lock usability and piñata-specific acceptance await owner PC verification. Release marker `V11_76_DESKTOP_MODELING_REPAIR`, 108 patches.

New: Astra · Comet Courier, an independent textured model project with 4K base color/normal atlases and embedded-texture GLB export. Open ?project=comet-courier or create ?project=blank-model.


## §E v11.274 · Toggleable viewport Nerd Stats

The Game, Modeling, Particle, and Materials browser viewports now have an optional **▥ Nerd Stats** overlay (tap its button or press F3 on desktop). It reuses the existing RAF cadence, Three.js render counts, and disposable stress-test data and updates at 800 ms intervals; it does not add a WebGL context or renderer loop. Frame timing is an approximate callback measurement, not GPU time. Sheep Tag live browser diagnostics and the Quest VR L3 metrics panel remain separate and unchanged.


## §E v11.276 · Left-controller immersive Nerd Stats

In immersive WebXR Sheep Tag, clicking the left joystick opens the same three-page Nerd Stats panel, now following the left controller and orienting the visible text toward the headset rather than freezing in the world or showing its back. Click L3 again to hide. In a normal Quest Browser floating 2D window, the HTML statistics overlay remains browser-bound; controller mounting works after entering immersive VR. No extra VR renderer or game/AI logic changes.


## §E v11.278 · Quest menu performance comparison

Nerd Stats in immersive VR sits 12 cm farther forward and 6 cm higher over the left controller. The existing L3 toggle remains; in-world text repaint is limited to approximately two seconds except on immediate page changes. Metrics **page 4/4** compares approximate frame cadence for no panels, Nerd Stats only, radial menu only and both open, helping test Quest 2 menu-induced lag. Values are WebXR callback intervals, not GPU render time; observations at different house counts should not be treated as a controlled performance comparison.
