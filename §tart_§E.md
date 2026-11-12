## §E v11.419 · Quest Sheep Tag congestion recovery

If several sheep enter a tight passage between houses, the engine now limits **AI sheep** collision-recovery route searches in solo Quest play to one per simulation tick and staggers failed-path retries. Their movement and building rules are still active; your controlled sheep and multiplayer input are not throttled. To compare the effect, use the v11.418 **Start Game → AI sheep count** dialog and try the same houses with **0, 2, then 5** AI teammates; note whether headset freezes still occur at the crowded gap. The v11.417 Object Index and v11.416 Satchel tutorial are retained. Quest performance acceptance pending.

## §E v11.418 · Pick AI Sheep teammates before starting Sheep Tag

Open Sheep Tag's main menu, choose **Start Game**, then set how many AI sheep should help your player sheep (**0–5** on the default map). Use +/− or the slider on your phone, or use the Quest radial menu's **−1 / +1 / START MATCH** buttons while in VR. **Start Match** begins the normal game with your selected team. This is a per-match choice; the edited map, wolf team and multiplayer matches are unchanged. All v11.417 Model VR Object Index and v11.416 Apprentice Satchel Academy features remain available.

## §E v11.416 · Interactive Apprentice Satchel training

Open Projects → Tutorials → Apprentice Satchel. Press **Show Me** to highlight the original editor tool, or enable **Ghost guide** to see transparent sample placement without having the engine do the modeling. **Verify** checks the editable project's real geometry and material assignments and explains any unmet criteria. Use **Save checkpoint** to make a local, validated recovery snapshot; **Restore checkpoint** requires confirmation and retains native Undo. Only deliberate native Save to Account syncs the project and completed objectives—snapshot geometry remains local to the device. In Quest 2 Model VR, the quest includes Show, Ghost, Checkpoint, Restore, selected-mesh Leather/Metal/Shade, and grip-movable world-space placement independent of the model/camera. Phone/Quest physical testing still pending.

## §E v11.415 · Clear tool pictograms throughout Model Studio VR (2026-11-11)

The independent world-space VR tool console now shows distinct pictograms for selection, swipe/front/through lasso, Save Project, Save to Account, Clone, Projects, menu controls, controller aim, display modes and labeled viewpoints. Move/Rotate/Scale/Grab retain their original actions; Rotate is visually different from Undo. Increment/decrement cards show +/- marks. Existing hover/selected/disabled feedback, controller mappings, save schema, XR loop and the v11.414 satchel tutorial's native button references remain intact. Physical headset readability remains owner acceptance testing.

## §E v11.414 · Tool buttons shown beside their tutorial names (2026-11-11)

In Projects → Tutorials → Apprentice Satchel, each action instruction now shows a miniature of the existing §E control beside the corresponding tool name. On the phone/desktop, those previews reuse the native button labels, glyphs and presentation. Inside Model VR, the quest shows icons drawn by §E's existing VR menu icon renderer for the actual controller-selectable tool. The tutorial explains the correct Add sphere then Shape → box sequence in the flat editor, versus Create → Cube in VR. The preview chips are not duplicate controls, and canonical starter/project saves, tool panels, and world-space Quest behavior remain unchanged. Hardware acceptance pending.

## §E v11.413 · Interactive satchel tutorial in Model VR (2026-11-11)

**Projects → Tutorials → Apprentice Satchel** starts a safe independent practice model. The corrected step 2 turns the practice cube into a floor and adds four thin wall boxes, giving the bag an actual hollow open top. The regular Model Studio lesson now shows collapsible front/side/top diagrams and can focus the native tool category. On the Quest Browser, open the lesson, enter **Model VR**, and use a **stationary world-space tutorial window** with controller-ray Prev/Verify/Done/Next actions. It does not follow the head or orbit, does not replace the existing floating model tool console, and shares the device-local progress keyed to that saved model project. Save Project and optional account sync remain separate. On-headset interaction needs owner verification.

## §E v11.412 · Apprentice Satchel tutorial (2026-11-11)

The first tutorial project adds **Projects → Tutorials → Apprentice Satchel**. Start an independent beginner model from a practice cube, follow seven mesh/material/save objectives in a movable/collapsible quest panel, and resume on the same device. Real model geometry and native Save Project remain the source of truth. Basic shape and material checks can read native data; hollow geometry, flap and strap placement require user visual confirmation. No original starter or cloud mage is modified by the tutorial. Existing VR modeling and accessories remain intact. Actual deployment must be confirmed against the v11.412 source seal.

## §E v11.410 · VR accessory workshop (2026-11-11)

Model Studio VR adds **Create → Accessories → Hip pouch**: a rounded leather bag with a curved flap, belt loops, closure strap, clasp, edge stitching and a leaf/star emblem. Separate **Body**, **Details** and **Fit** pages adjust a live preview with coordinated leather colors, readable dimensions and clear selected states. The starting body is approximately **14 cm high** in the immersive workspace; it scales with the placement controls.

Aim freely or choose Surface fit against a character's hip. The preview holds its pose while the pointer operates the menu; the right stick turns/resizes it. After releasing the menu click, a fresh primary Trigger places the default eight editable native components as one selected group and one Undo step, ready for Grab. B or the first Y cancels an uncommitted preview. After placement, native mesh tools edit the components; the recipe controls do not persist as a parametric object. No saved cloud mage is modified by this checkpoint.

See [the accessory workshop checkpoint](projects/swrlz-forge-moba/docs/MODEL_VR_ACCESSORY_WORKSHOP_V11_410.md) for the workflow, geometry and transaction boundaries. The source package, 17 native test groups, nine spatial UI checks, 12 controller workflows and five disposable mage-reference checks passed. [Deployment 42961445702](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42961445702) succeeded; the RUNNING hosted editor and Modeler match the exact tested source seal. Physical Quest comfort remains owner acceptance.

## §E v11.390 · Fluent controller selection, Grab and creation (2026-11-10)

Selecting from Inspect now arms Grab: grip moves and turns the existing selection, the stick sizes it, and the off-hand trigger provides smooth fine motion. A taps cycle Move/Rotate/Scale; hold A for broader tools. X+A opens Create with native Cube/Sphere/Cylinder/Cone placement previews; X+Trigger duplicates a group in one Undo step. Confirmed creations and copies become the selection and hand directly to Grab. Cancel and tracking/source changes discard uncommitted previews.

See [the v11.390 controller checkpoint](projects/swrlz-forge-moba/docs/MODEL_VR_FLUENT_HOTKEYS_V11_390.md) for controls, transaction boundaries and validation. Current Selector, menu drag, camera, image/UV, graphics and Quest guest synchronization work remains included. Deployment [run 42925139497](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42925139497) succeeded. The RUNNING hosted editor and Modeler match the tested source seal and asset receipts.

## §E v11.378 — Parallel 2D and improved 3D reference experiments (2026-11-10)

Import a five-view sheet in §C; first inspect and correct 2D outlines (existing v11.377 workflow). The optional experimental 3D button now consumes those edited contours, generates three aligned native loft sections instead of twisted full-row loft bands, and uses bounded side-view depth. A detached slender prop may still be included. This is intentionally rough and untextured; use a fresh blank Model Studio project to test it separately without overwriting an existing mage or starter. Normal project clone/save protections remain. Physical device validation still required.

## §E v11.377 — Image reference → editable 2D outlines (2026-11-10)

The original §C reference importer now proposes local color-region and silhouette traces before trying to construct any 3D meshes. The existing in-panel 2D work area offers five orthographic view choices, region selection and names, show/hide, vertex editing, re-tracing and SVG export. Automatic segmentation is only a draft; the mage's individual hood/face/robe pieces need user review. The experimental v11.375 rough 3D generator remains tucked away and must be explicitly chosen. No starter project or existing mesh is changed simply by loading an image. Owner phone/Quest trial follows deployment.

## §E v11.376 — Model VR Selector with Left Grip area lasso (2026-11-10)

The existing left-trigger swipe/add/retrace selector remains available. A dedicated VR **Select** navigation tab now offers Sweep, Front Lasso and Through Lasso. While a lasso choice is armed, holding **Left Grip** draws a visible 2D selection loop projected into the model workspace; releasing it adds the mesh parts in the outlined area. Front restricts to a nearby depth band, and Through includes overlapping parts behind one another. Earlier selections remain. Menu Grip dragging takes priority when aimed at the menu; returning to other menu tabs restores Left Grip workspace motion. Source model, saved data/UV, §C image blockout, existing quick controls, and project/account safeguards are preserved. Quest 2 interaction acceptance follows deployment.

## §E v11.375 — Integrated image-to-editable 3D blockout (2026-11-10)

A blank Model Studio project can now use the existing § Chat panel's local image upload to generate an approximate four-part, editable 3D silhouette from a five-view sheet, optionally including a narrow side prop. Existing source cloning, Undo and Save apply; original images are not stored in account projects by this feature. This is an experimental blockout, not a complete UV-textured or rigged character. See `projects/swrlz-forge-moba/docs/IMAGE_TURNAROUND_BLOCKOUT_V11_375.md`.

## §E v11.374 — Quest 2 feedback corrections for Phase 1 (2026-11-10)

The VR Model Studio menu can be dragged using the controller pointer rather than tiny Grip-position differences. Multiselection now displays a clearly expanding group boundary, and raycast contact with active transformation gizmos displays the normal pointer indicator. A permanent **Projects** navigation tab makes Save to Account, Save Project and Clone Project easy to find without opening §C chat. Legacy controller hints, model manipulation, Undo/Redo and save/UV/account revision safeguards stay intact. Physical Quest 2 acceptance remains the owner's test after the protected release.

## §E v11.373 — Reversible VR sweep handoff correction (2026-11-10)

The left-trigger multi-mesh gesture now receives the original target from the press before the native selector clears cached hover hits. It keeps tap-to-select and undo/redo, preserves preexisting selected parts on reverse swipes, and leaves VR menu grips, model transform grips, UV texture/account storage and Quest controller hints untouched. Automated source and regression checks are distinct from owner Quest 2 confirmation.

## §E v11.372 — Quest 2 Model Studio Phase 1 (2026-11-09)

Our immediate implementation pass addresses existing-mesh manipulation before construction, rigging and animation. Native left-trigger hold can sweep-select meshes and reverse the same stroke to remove only freshly swept additions. Model transformation gizmos and a temporary Grip-activated controller guide clarify selected-pivot orientation, with optional axis-limited move/rotation. The orbit thumbstick corrects left/right direction and provides proportional speed. The tool menu can be dragged with Grip and hidden/restored; it does not follow real head movement or rotate with the mage. The VR Studio console exposes on-device Save, account synchronization and detached Clone; §E's ordinary toolbar also shows Save to Account using its existing account link. This checkpoint is source-validated; Quest 2 comfort and cross-device UV-texture persistence require owner testing after hosted publication.

## §E v11.371 — Save Project, Clone Project, immutable starters (2026-11-09)

The native project library supports full-document Save and Clone in the Game, Model, and Particle studios. Starters are read-only templates: first Save forks them into My Projects; future Save on a named project updates only that project ID. Clone always creates a separate copy and identity. The existing Google-authenticated Chat account project RPC is reused for account sync with optimistic revisions, and local IndexedDB always retains a full independent copy. v11.371's source manifest, actual SHA-256, and focused clone tests govern the release; mobile/Quest acceptance stays with the owner.

## §E v11.360 · Spatial VR menus, tactile buttons and smoother feedback (2026-11-09)

Model Studio VR gains a larger, clearer spatial console with persistent studio navigation, icon tool cards, stronger button states and polished controller wheels. Hover/press feedback and page/panel transitions run in the existing XR loop, respect reduced motion and pause when hidden. Menu ray feedback updates at headset frame cadence while native model-surface hover remains bounded. Current camera orbit, selected-only grip controls, native modeling history, wireframe-first UV painting and the new reference-hand starters stay intact.

See [the v11.360 menu checkpoint](projects/swrlz-forge-moba/docs/MODEL_STUDIO_VR_MENUS_V11_360.md) for behavior, source integrity and verification. Physical Quest acceptance remains owner testing. Deployment [run 42553034002](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42553034002) succeeded. The RUNNING hosted index and Modeler pages match the tested source seal exactly.

## §E v11.357 · Wireframe-first UV editor (2026-11-08)

Selected-mesh texture work is again **export the ordinary UV wireframe → paint art → import image → slide UV placement on the mesh**. The exact UV wireframe is shown by default in the popup; directional guides and mapping JSON are optional advanced reference tools. This keeps the smooth artwork workflow and the original UV coordinates intact, without extra projection/baking steps. The latest VR, transforms, model JSON and Undo remain unchanged.

## §E v11.350 · Two-hand VR modeling, live profiles and native surface tools (2026-11-08)

Model VR now uses the active Controller Studio profile to drive real editing. Right-hand tools and left-hand view controls add multi-part selection, explicit two-hand geometry transforms, A/X hold wheels, focus/precision shortcuts and safe Undo/Redo. Native sculpt strokes, saved lasso masks, planar outline creation and signed closed extrusion stay inside the same immersive editor. Cancel and tracking loss discard previews; each completed operation commits one native history step. Camera/aim/display tools, UV sheets and the owner UV image import correction remain included.

See [the v11.350 checkpoint](projects/swrlz-forge-moba/docs/MODEL_STUDIO_VR_V11_350.md) for controls, source integrity, targeted verification and deliberate geometry limits. Physical Quest feel and performance remain owner acceptance testing. Deployment [run 42461483101](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42461483101) succeeded. The RUNNING hosted index and Modeler pages match the tested seal exactly; physical headset acceptance remains owner testing.

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

The actual native model root, geometry, materials and rigs are reused in an isolated Model VR scene through the existing main XR loop. Exit restores the browser Model Studio. Game/Arcane XR, the Materials workspace and owner hand/UV releases through v11.337 remain preserved. Deployment [run 42442450957](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42442450957) succeeded; the RUNNING hosted index and Modeler artifacts match the exact tested build. Controller emulation, source verification and physical headset acceptance are separate gates; current receipts and supported controls are recorded in [the checkpoint](projects/swrlz-forge-moba/docs/MODEL_STUDIO_VR_V11_340.md).

## §E v11.330 · Dedicated Material & Texture Studio (deployed)

Materials opens a dedicated library, preview/painting workspace and property inspector. Desktop uses reserved columns; phones and wider portrait frames use Library, Preview & paint and Properties tabs. An empty library hides unavailable fields and offers a clear first-material action. The default texture view covers the underlying game editor; an explicit native 3D scene preview remains available. Covered 3D drawing pauses while editing textures, then resumes for the visible scene preview; native updates and history continue.

The existing material definitions, PBR controls, direct texture painting, brush undo, scene assignments, project saves and PNG/JSON import/export handlers remain authoritative. Opening Materials does not create a material or replace the current project. Model, Game and Particle studios retain the v11.320 navigation changes and the owner's v11.321 sightline/Quest work. Source and browser verification plus publication receipts are recorded in [the checkpoint](projects/swrlz-forge-moba/docs/MATERIAL_STUDIO_LAYOUT_V11_330.md); physical-device appearance remains owner acceptance. Deployment [run 42365572126](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42365572126) succeeded; the RUNNING hosted index and Modeler files independently match the browser-tested source seal.

## §E v11.321 · Sheep Tag house sightlines and crowded Quest diagnostics (2026-11-07)

The owner's Quest testing found the v11.306 last-sheep chase much smoother, but severe slowdown remains while turning the headset with living teammate sheep and many houses under construction. Gameplay source confirmed enemy sight used distance-only checks, not building obstruction. In fog-enabled matches, visible wolf/sheep pairs now test house line-of-sight, while true last-observed enemy memory, scent clues, allied shared sight and fog-off behavior remain intact. Sight results are reused within the same simulation update. Crowded Quest gameplay (2+ living sheep, 8+ houses) keeps the existing escape-search scoring but spreads its candidate checks across more frames. Nerd Stats adds pages **9/10 and 10/10** to compare head-turn versus still frame gaps and draw-call counts while busy, and show sight checks and AI budget. The v11.306 wolf-radius A* counter now uses the actual configured radius. Other studios, controllers, assets and saved projects are unchanged. **342 patches, 71 assets, 8,451,859 bytes**, SHA-256 `47e8cc9f9f54fb1592715961ecd4faab13fc94f56e0f8208c250efc3306b2079`. [Release checkpoint](projects/swrlz-forge-moba/docs/SHEEP_SIGHT_XR_CROWD_V11_321.md). Quest performance improvement and visibility fairness require owner-device confirmation.

## §E v11.320 · Organized studios and automatic project navigation (deployed)

Game Engine, Modeling and Particle Studio now use distinct navigation and action rows, clearer labels and deliberate tool docks. The model category rail occupies its own column immediately left of the inspector, remains usable when that inspector collapses, and becomes a separate scrollable row in Compact mode. Selection, component and group controls live in the inspector. A dedicated Projects action is available from Modeling; Particle menus stay reachable on phones and their layout selectors live under Tools.

Project Library reserves separate header, Starter Projects / My Projects tabs and a scrolling content pane, eliminating the fixed-offset overlap. Completed native model, game and saved particle-workspace loads select the corresponding studio. New exports retain an editor workspace hint; a valid emitter-library import opens Particle Studio. Explicitly loaded documents suppress the deferred first-game bootstrap so navigation preserves the loaded data.

The complete 59-part Little Crystal Mage is now the only account project with that name: the older 41-part checkpoint was removed after both cloud documents and revisions were verified. The 59-part save remains unchanged at revision 2. Existing Vanguard mesh/UV, Sheep pursuit cache and Arcane VR glove releases through v11.309 are preserved. See [the checkpoint](projects/swrlz-forge-moba/docs/STUDIO_NAVIGATION_LAYOUT_V11_320.md) for browser checks and exact source receipts. Exact packaging, desktop/phone browser checks and the authenticated Game → Model Studio cloud-load flow passed. Deployment [run 42345232697](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42345232697) succeeded. The RUNNING Hugging Face release and both hosted HTML pages match the exact v11.320 source seal. Owner-device visual acceptance remains separate.

## §E v11.306 · Sheep Tag wolf pursuit cache and simulation diagnostics (2026-11-06)

The owner isolated two distinct stress cases: occasional stutter when **all sheep and all wolves** move, and sustained game-wide slowdown when three wolves switch from attacking maximum houses to pursuing the last surviving sheep. Review of the *effective* `sheep_lanes.js` route resolver identified an overstrict 0.2-unit moving-target cache that could repeat up to nine A* approach tests almost every frame during pursuit. The new shared 0.40–0.56-second cache reuses reachable and blocked approach decisions across both wolf AI and target resolution, with movement and navigation invalidation. Preserves existing v11.256 frame-budgeted sheep evasions, all building/capture rules and WebXR controls. Nerd Stats pages 7/8 and 8/8 report path CPU, cache reuse and the simulation/wall-clock ratio; GPU timing and live Quest acceptance are not claimed. Source sealed at 337 patches / 71 assets / 8,397,357 bytes (SHA-256 `a47415627055cda09f2152e9c6adc311347ed709971e6c0bea1be6bc7195910c`). [Focused checkpoint](projects/swrlz-forge-moba/docs/SHEEP_PURSUIT_CACHE_V11_306.md).

## §E v11.304 · Loaded models refresh the open Modeler (deployed)

Loading a saved native model into an already-open Model Atelier now rebuilds its derived mesh scene, mesh list and inspector in place. Previously, the document and JSON could contain every saved part while the old empty viewport and GLB export still contained no meshes. The synchronization follows the effective native/scratch model that was actually rendered, so valid empty scratch documents also clear the previous view correctly.

The existing renderer, canvas, camera, render loop, native document and Undo/Redo history are retained. Stale document-specific selection, component and drag targets are cleared; repeated synchronization of the same rendered document preserves selection and global view preferences. It does not close/reopen Model Atelier or initialize Game. All owner Vanguard releases through v11.303 (image/UV, mesh, mapped PBR and anatomical portrait) and outward Chat-loft lighting are preserved. Focused real-Three scene/list/GLB tests and the exact package seal are recorded in [the checkpoint](projects/swrlz-forge-moba/docs/MODELER_DOCUMENT_VIEW_SYNC_V11_304.md); the fresh v11.304 browser automatically displayed all 59 parts and exported 59 exact named GLB meshes through the native buttons. Deployment [run 42333988830](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42333988830) succeeded. Hugging Face revision `97345e21b5c240d61e44fda90d806afacc42978a` is RUNNING; both official index and Modeler HTML independently match the verified 8,377,905-byte SHA-256 `c2f005b86f9c6e925272c052d429d8b01139d30cb121af7553d38a61788eac5b` seal (335 patches, 71 assets). Owner-device visual acceptance remains separate.

The complete **Little Crystal Mage** has **59 editable parts**, all authored through embedded §c across66 receipt-backed native model operations. Its newest account save is a durable revision 2, independently cloud-reloaded at 59 parts under the earlier sync candidate. The final v11.304 check used the unchanged native-project file through the ordinary file picker because account resume returned 401 after a later Chat release. It automatically populated59 mesh rows and exported a 232,076-byte editable JSON plus 1,092,072-byte GLB with 59 exact mesh names. No geometry was injected during reload verification.

## §E v11.295 · Correct lighting on Chat-created curved meshes (deployed)

Plain loft meshes authored through §c now present outward-facing triangles and recomputed surface normals to the existing renderer. This corrects the inverted shading that made saved ivory hair and other curved parts catch the cyan backlight from the wrong side. The saved part colors, paths, radii, UVs and transforms remain unchanged.

The repair is limited to plain Chat-authored lofts. Existing textured and styled surfaces keep their established rendering path; Hooded Vanguard's v11.294 loader repair, all model provenance, native editing/history, Chat progress and account saves are preserved. Focused real-Three geometry checks, the existing native character-tool checks and the exact source package seal are recorded in [the checkpoint](projects/swrlz-forge-moba/docs/CHAT_LOFT_SURFACE_NORMALS_V11_295.md). [Deployment run 42247315758](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42247315758) succeeded. The RUNNING hosted v11.295 HTML and SOURCE receipt match the verified 8,263,130-byte, 326-patch, 71-asset seal. The final 59-part mage was subsequently viewed with corrected surfaces and passed fresh v11.304 import/display/native-export checks; owner-device visual acceptance remains pending.

## §E v11.294 · Hooded Vanguard Starter Models loader correction (2026-11-06)

Targeted hosted mobile Chromium check on v11.293 reproduced the owner's report: Hooded Vanguard generated **14 meshes / 61,476 triangles** correctly, then `loadProject()` threw **`Invalid named socket.`** Native Prism Jester assemblies/sockets had been inherited from the canonical project while all original part IDs and groups had been replaced. New `patches/v11_294_vanguard_socket_loader_fix.py` clears only this starter's obsolete `model.assemblies` graph before loading; its own native geometry, texture maps, and existing model editing path remain intact. Other model starters, the v11.292 Cliff Hand material work, Chat character tools, saved projects, and game/VR flows are unchanged.

Verification gates: exact assembled source SHA/bytes, targeted JS syntax and native hosted load, then owner Android/Quest appearance acceptance. The release is static until a dedicated full-body skeleton is authored.

## §E v11.293 — §c character geometry and visible editor work (candidate)

Negotiated Chat mesh tools add curved lofts, open lathe surfaces and native framing. Reviewed plans support 64 operations, painted between edits with named native progress; snapshots retain the backward-compatible 48-row cap and truthful full totals. Closing Chat, Stop and intervening edits halt subsequent work. Native persistence, scratch authority and history remain in place.

Preserves the latest Cliff Hand, Hooded Vanguard, project picker, XR and particle changes. The paired Chat source also repairs interrupted-stream delivery, grounded no-edit inspection, bounded error reporting and heartbeat CAS retries. Source seal, verification and deployment evidence are recorded in [the checkpoint](projects/swrlz-forge-moba/docs/CHAT_CHARACTER_TOOLS_V11_293.md). Actual mage construction and owner device acceptance are separate evidence.

## §E v11.291 · Hooded Vanguard native material-first starter (2026-11-06)

New **Starter Models → Hooded Vanguard · Material Study** recreates the owner's hooded-armored character concept as an original editable male model **without the weapon or bird**. Rather than assembling hundreds of trim objects, the generator produces one continuous male silhouette and dedicated shaped face, hood, hair, scarf, chest armor, pauldrons, coat tails, belt, boots and gloves: **14 editable native mesh entries**. Decorative chest filigree, clothing grain, gold trim, leather and scarf details are drawn onto aligned per-part 256px base-color / normal / roughness UV maps. Coat tails and shoulder armor stay independent for potential future animation.

The first release is **a static visual/modeling study, not a full-body skinned rig**. The engine source and JavaScript are checked through a targeted build; real Android/Quest appearance, export/material persistence, and detailed visual fidelity require owner's acceptance. The previous 121-piece rock hand, updated connected cliff hand, Scorchette and all existing projects remain unchanged.

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

## §E v11.247 — Editor preview controls (2026-11-03)

**Owner benchmark:** Full editor viewport/model rotation is smooth on Quest 2 while active Sheep Tag can lag; preserve the editor as baseline for future runtime profiling.

**Source update:** `projects/swrlz-forge-moba/patches/v11_247_editor_live_previews.py` adds a compact native Game Editor ✦ Preview panel with independent Particle and Cinematic animation switches. Preview is entirely optional and reset when leaving Edit mode; existing particle renderer and storyboard timeline are reused, with no new loop or persisted gameplay changes. The cinematic control is available only where the native Storyboard episode exists. Version v11.247, 278 ordered patches, 69 assets, 7,810,723 bytes, SHA-256 `0069237edcb5f32d53a349caeb7505cc9fd6466f389def849ed442e8b30cfbb4`.

**Validation:** Focused source reconstruction and JS/Python syntax passed; Meta Quest 2/Moto G Power owner acceptance pending. Preserve historical lineage, single native renderer, Quest input mappings and saved projects.

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

## §E v11.238 — Quest VR circular-menu responsiveness and streamlined browser tools (2026-11-03)

**Owner Quest 2 source:** Sheep Tag works under normal headset movement until opening the VIEW / BACK / FORWARD / TACTICAL circular menu. Then the app stalls and hides its own menu. The browser Game Engine and Model Atelier top controls overlap in floating Quest windows.

**Source change:** Preserve the app radial across a still-visible 170–650 ms WebXR frame delay rather than incorrectly entering the Meta OS overlay suppression path; keep genuine hidden/blurred/long-gap safety behavior. Reuse menu hit tests and GPU text textures. The Quest Browser layout reorganizes existing Game Engine commands under Controls and the modeler's original actions and tool rail under Model actions / Edit tools, preserving native button handlers and the Close control. No new WebXR camera, game mechanics, fog-masking or Meta OS window controller.

**Exact governed v11.238 source:** 269 ordered patches, 68 preserved assets, 7,759,927 HTML bytes, SHA-256 `b732a8868cd74ead21e085365d6c3004f5e71e63a9cfd473ae676b955179e13c`. Full Quest 2 UX acceptance is owner-tested. See `projects/swrlz-forge-moba/docs/QUEST_RADIAL_WORKSPACE_V11_238.md`. Separate draft PRs #362 and #363 are excluded.

## §E v11.236 — Complete Sheep House gables, Wolf root preview, starter categories (2026-11-02)

**Owner inspection / source diagnosis:** The four enclosed Sheep Tag house models had rectangular walls and sloped roof pitches but **no front or rear triangular gable geometry**, leaving large attic openings. Astra's separately authored nose and cheek ruff meshes inherited torso/neck weights even when the skull turned. Procedural walk/run/stalk bob and spine pitch caused global rocking. The existing Starter Projects gallery mixed game and model assets.

**Append-only fix:** `patches/v11_236_sheep_gables_wolf_root_starter_groups.py` adds independent solid, closed front/rear triangular indexed 3D gable parts and interior floor to Thatched Starter Hut, Cozy Cottage, Flock Barn and Ram House; leaves Free Shelter intentionally open. Gives nose/philtrum/cheek/smile parts rigid head-bone weighting in Astra's native Model Atelier. Adds two reversible Wolf Motion **preview-only** controls: **In place · lock root height** (on for walk/run/stalk) and **Steady torso · reduce walk/run rocking** (18% authored spine pitch). They do not modify saved clips; IK/foot planting and full generic character-controller root motion are future work. Under the existing Project Hub **Starter Projects**, adds accessible **Starter Games / Starter Models** tabs without cloning cards, losing default-starter checkboxes or altering **My Projects**.

**Verification:** One focused 390px native browser acceptance [run 41575593800](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41575593800) passed all five house starter part counts (Free Shelter 18, Hut 62, Cottage 71, Barn 40, Ram House 63); real front/rear indexed 3D gables and a floor on all four enclosed houses; six Starter Games and eleven Starter Models with all existing start-default checkboxes; My Projects preserved; four face detail parts (nose, philtrum, cheek ruff, smile) 100% head/0% spine; Run root bob toggles 0 ↔ .06928 and spine pitch .07794 ↔ .01403, proving stabilization can be disabled without modifying clip keys.

**Source receipt:** §wyrl§ Engine **v11.236**, 268 ordered patches, 68 unchanged assets, **7,735,923 generated HTML bytes**, SHA-256 `02056c0d0ff3722b503a03d6fe31ebfc4a99adbdeb2ba132b58d1ba447d105ae`. Preserve saved user projects/animations, gameplay/LAN collision, sheep build placements, wolf materials, other editors and one native renderer. New starter models are generated from updated templates; no silent migration of existing custom saved models. Physical Moto G Power / Quest visual acceptance still belongs to the owner.

## §E v11.235 — Astra Wolf preview, anatomy and Motion panel repair (2026-11-02)

**Owner screenshots and reproduction:** Astra Wolf displayed severe limb/body deformations during Run; its playhead and bones advanced but rendered canvas frames froze until the camera moved. The focused browser diagnostic found **128 animation updates, zero rendered frame changes and zero changed screenshot pixels**. Root cause: the high-definition idle-frame render guard skipped drawing when bones changed because the pose updater did not mark `atelierHDDirty`. Separate UX issue: selecting the generic **Motion** category hid Astra's original Wolf Rig & Motion panel under the generic context inspector, making Play, clip selection and Save pose appear missing.

**Append-only fixes:** `patches/v11_234_wolf_anatomical_skinning.py` aligns head/neck/elbow/hock rest positions with the authored Astra geometry and weights full limb/fur/claw regions to the appropriate upper/lower bones instead of dragging toes toward the torso. `patches/v11_235_wolf_motion_tools_visibility.py` marks the **existing** HD renderer dirty on wolf pose changes, directs **Motion** to the single original Wolf Rig & Motion inspector, and positions **Set keyframe at playhead** alongside Play. No duplicated renderer, RAF, clip editor, WebGL canvas or camera controls.

**Evidence:** Focused Android-size 390px browser tests passed for clip selection, Play/Stop, Playhead, Bone sliders and Set keyframe near the top, with **Run changing sampled viewport pixels without touching the camera**; [v11.235 final candidate run 41572757012](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41572757012). Source seal: §E **v11.235**, **267 ordered patches**, **68 preserved assets**, **7,729,335 generated HTML bytes**, SHA-256 `446edd4f0d7ff1fc8d59216035eef315159437bc70952457203e9a266ce728a5`. Exact integrity verifier: `scripts/verify_v11_235_release.py`.

**Scope:** Native Astra Model Atelier authoring only. Preserve saved models and keys, Sheep Tag game-loop animation/collision/LAN authority, glove rig, house starter models, workspace layout, all other studios, editor tool integrations and the §C Studio Commands bridge. Physical Moto G Power and Quest motion-quality evaluation remains owner-operated; no claim that all ten clips have professional-grade animation yet.

## §E v11.233 — §C native Material, Particle and Rig Studio commands (source candidate)

**New native host bridge:** The existing paired Chat side panel now advertises versioned, live-context Studio Commands v1 only in the correct studio tab. Supported operations are material create/edit/assign-to-scene-actor, particle emitter create/edit, existing hand/wolf bone pose, and animation keyframe save. Each is a bounded **single operation**, validated by both Chat server and native host against exact IDs, current project/studio/edit mode, and approved through the existing immutable design-preview/consent/receipt flow. The native material/particle transaction owners, Model Atelier rig storage, Sheep Tag gameplay and one WebGL renderer remain authoritative. No arbitrary JS, file imports, material-to-modeler-parts application, new hand-tracking capture, or code-based auto-rig generation is added.

**Measured and sealed candidate:** v11.233, 265 ordered patches, 68 unchanged assets, **7,725,488 bytes** HTML, SHA-256 `936e49ec155d091a8e0e651a6043713554e6ac5c776a7b6fec45884c2967b34c`. Candidate source reconstruction passed in GitHub Actions; full release-package/source verification, Chat-server promotion, HF deployment and owner Moto/Quest physical acceptance are separate pending gates. The prior v11.232 workspace-start fix is preserved.

## §E v11.232 — Native model starter now opens Modeling workspace (2026-11-02)

**Owner screenshots / definitive regression:** When loading Sheep · Ram House or Astra · Furred Comet Courier, the game scene title/background changed but Game Engine remained highlighted and the outliner showed only World Ground. v11.188 deliberately prevents the native Model Atelier popup from opening while the game workspace remains active. The starter loaders were calling `ModelAtelier.open()` without activating the Modeling workspace first. This was a **workspace routing bug**, not missing 3D meshes and not primarily camera framing.

**Focused fix:** Explicit model starter selections activate `window.SWYRL_ENGINE_WORKSPACES.change('modeler')` after their model data is fully loaded/rigged and before attempting the native Model Atelier view. The router opens the existing renderer once, updates the active tab and in-place route to `/modeler.html`, and shows the editor/parts list. Applies to five sheep houses, active Astra wolf, independent Comet Courier, blank-model, sheep model, floating glove and canonical Model Atelier starter. The houses now open in edit mode rather than hiding controls behind the Courier Studio presentation. Main page **still boots Game Engine first**; normal saved game projects, VR controls and Sheep Tag gameplay are not altered.

**Live source receipt:** §E **v11.232**, 264 ordered patches, 68 packaged assets, 7,714,177 HTML bytes, SHA-256 `a5f840685f618872d69b3e1dc1e197e496e68d2500bfb46008883bfb5c6df9d9`. Append-only `patches/v11_232_model_starter_workspace_activation.py`; strict release validator `scripts/verify_v11_232_release.py`. Narrow 390px mobile Chromium candidate check [run 41567721790](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41567721790) **passed** initial Game-only startup, explicit Ram House (60 editable parts), rigged Astra Wolf (108 parts, 10 clips) and Blank Model (1 part) opening with **Modeling selected, real Model Atelier visible, /modeler.html routing and no second model render**. Final hosting and physical Android/Quest acceptance remain separate release gates.

## §E v11.231 — Full-building sheep house camera framing (2026-11-02)

**Owner report:** Houses now load but are not visible in the Model Atelier viewport. The actual 390px mobile browser screenshot revealed geometry drawn massively zoomed-in (the Barn showed a cropped wall/roof), rather than missing meshes. All five models had valid bounds/visible GPU meshes, but they used the ordinary fixed-distance character viewport instead of the existing large-model bounding-box camera.

**Focused v11.231 repair:** The five IDs `sheep-free-shelter`, `sheep-thatched-hut`, `sheep-cottage`, `sheep-barn`, and `sheep-ram-house` now route front, side, three-quarter, and top/bottom views through the existing geometry-bounds camera framing. It accounts for the live canvas aspect ratio and adjusts studio fog for large house viewing only. Native mesh contents, UVs, parts/groups, saved projects, Sheep Tag buildings/collisions and LAN authority, wolf/glove rigs, GUI/Materials/Particle studios and VR controller behavior remain unchanged.

**Receipts:** §E **v11.231**, 263 ordered patches, 68 unchanged assets, 7,713,229 assembled HTML bytes; SHA-256 `0e960a32760f081f20bfb8e8ed1cd61cf3a0eec8d1f5e583b865311d2bd6e4d0`. Narrow Chromium 390px test [run 41561484650](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41561484650) passed all five full projected model bounds, native live scene mesh counts, and visibly rendered red Barn. Owner's Moto G Power and Quest hardware visual acceptance remains outstanding.

## §E v11.229 — Sheep house Model Atelier loading repair (2026-11-02)

**Owner report reproduced and repaired:** All five v11.226 sheep-faction house starters failed actual native Model Atelier loading despite the initial geometry-only tests. The root causes were material names passed as box rotation angles (non-finite transforms), an undefined `P.trim` used for window mullions (invalid native colors), and inherited festival-character `modelAtelier.assemblies` named socket references pointing to deleted parts. The v11.229 append-only patch corrects only the assembled house builder's callsites and deletes inherited assemblies when creating fresh sheep-house starter copies. Existing saved user models and gameplay remain untouched.

**Actual browser acceptance evidence:** Focused mobile-size (390px) Chromium native Model Atelier checks passed for direct `modeler.html?project=sheep-free-shelter` and independent open calls for Free Shelter (18 parts), Thatched Hut (59), Cozy Cottage (68), Flock Barn (37), and Ram House (60). All panels opened and displayed the expected number of editable parts; nonfinite-transform, color, mesh/topology, group and inherited-socket checks also passed. See GitHub Actions run `41540380010`. Physical Moto G Power/Quest visual and performance approval remains owner-operated.

**Source authority:** §wyrl§ Engine **v11.229**, **261 ordered patches**, **68 unchanged assets**, **7,712,062 HTML bytes**, SHA-256 `38012d3e068347a65045da180ef0e2e3f6dcff42a5bc334569aecce203c4a53d`; `patches/v11_229_sheep_house_model_loader_repair.py`, `tests/test_v11_229_sheep_house_native_loading.cjs`, `tests/ui_v11_229_sheep_building_loader.mjs`. Strict source, HF deploy and live served checks are separate gates; preserve v11.228 Game GUI/Menus, wolf rig, Sheep Tag matchmaking/LAN authority, studio tabs and §C.

## §E v11.228 — Game Engine GUI / Menu Setup sub-tab (2026-11-02)

Inside **Game Engine**, compact **Scene | GUI / Menus** child tabs and a **Show/Hide UI** editor-preview switch organize existing menus without adding another top-level studio. The new inspector reuses Sheep Tag's editable Main Menu UI (title, subtitle, Start button, color, cinematic orbit) and adds up to 24 validated project-native label/button/panel layers with editable content, colors, viewport-percent layout, and safe Play actions (Start, Next, Stop, display only). Per-layer eye visibility and Show all/Hide all are editor-only; each layer has an independent saved Show in Play flag. GUI definitions participate in project save/export, authored level capture and native Undo/Redo; no new renderer or Quest input loop.

**Verified source:** v11.228, **260 ordered patches**, **68 packaged assets**, **7,712,043 generated HTML bytes**, SHA-256 `16b6e24f471b79a1a9c6ec7ce7df2565dfeb5de8a0c527196e7b9008a907ca2d`. One-shot actual source build, JavaScript syntax, and focused GUI save/restore/visibility tests passed. Device UI acceptance on Moto/Quest is pending. Code: `runtime/game_gui_menu_subtab_v11_228.js`, `.css`, append-only `patches/v11_228_game_gui_menu_subtab.py`.

## §E v11.226 — Five Sheep-Faction 3D Building Model Starters (2026-11-02)

**Owner concept → actual native projects:** Free Sheep Shelter, Thatched Starter Hut, Cozy Sheep Cottage, Flock Barn, and Ram House now have separate starter cards under **Projects → Starter Projects**. Each opens editable native Model Atelier geometry, not a 2D reference image. The pack includes original straw/blue-roof shapes, timber walls, roof pitches, window frames, doorways, sheep crests, hay and cottage decorations. Individual starter IDs: `sheep-free-shelter`, `sheep-thatched-hut`, `sheep-cottage`, `sheep-barn`, `sheep-ram-house`. Use `modeler.html?project=<id>` for a direct route, or select one saved startup default.

**Source receipt:** §wyrl§ Engine **v11.226**, **258 ordered patches**, **68 unchanged packaged assets**, **7,656,704 source HTML bytes**, SHA-256 `7395e442f324b33cf67f49aa1eb1be9349f07c2e4d7f00aa5872d3312112129d`. Code: `runtime/sheep_building_model_starters_v11_226.js`, `patches/v11_226_sheep_building_starters.py`. Focused five-model mesh validation and candidate assembly passed. Strict release verification, HF hosting and physical Moto/Quest acceptance are separate evidence stages. See `docs/SHEEP_BUILDING_MODEL_STARTERS_V11_226.md`.

**Authority boundary:** These are **Model Atelier building assets** only; current Sheep Tag resource costs, build placement, block collisions, wolf movement and LAN authority remain unchanged until deliberately integrated into the in-match asset factory. Preserve existing model, materials/particle tabs, glove/wolf rigs, saved projects, and §C.

## §E v11.225 — Material & Texture Studio + Four Workspace Tabs (2026-11-02)

**Native top workspaces:** Game Engine | Modeling | Particle Studio | Materials & Textures. The existing two editor tabs remain intact, Particle Studio now has its own native tab and full-screen preview workspace, and the new Material & Texture Studio has its own tab with the same live §E Three.js scene (no second rendering loop). The game viewport toolbar's ✨ Particles shortcut enters the Particle Studio tab. Tab switching preserves unsaved scene/model data and native controls.

**Material authoring:** Create/duplicate/delete up to 12 project-native PBR materials using ten starters (steel, gold, wood, stone, brick, fabric, leather, arcane glow, glass and ceramic). Edit roughness, metalness, opacity, emissive color/glow, base/accent colors, seeded procedural detail, UV tiling and texture pattern. Generate eight 256×256 procedural/paintable patterns, draw bounded brush strokes (including Undo/Clear), import PNG/JPEG under strict limits, and export PNG textures or validated JSON material libraries. Apply authored materials to specific scene actors, preview with a native rotating 3D sample sphere, and restore the exact original actor material. Scene assignments and material definitions persist in project snapshots, native Undo/Redo and level records. GPU resources are temporary and disposed on changes. User projects, §C, Sheep Tag authority, native glove rigs and previous Particle Studio VFX data are preserved.

**Exact source receipt:** §wyrl§ Engine **v11.225**, **257 ordered patches**, **68 unchanged packaged assets**, **7,642,539 generated HTML bytes**, SHA-256 `7407ca6b520912437c280035c1f4258f5b1e7a8ab577f3701b855db26f7bf3a7`. Focused generated-JS syntax, procedural texture, material validation, painting, actor assignment/restore, JSON import and project-switch tests passed. Physical Android/Quest 2 layout and rendering remain owner acceptance pending; material-to-Model Atelier part assignment is not yet exposed (PNG/JSON asset export is available).

Read `docs/MATERIAL_TEXTURE_STUDIO_V11_225.md` for workflow, source contracts and limits.

## §E v11.224 — Native Particle Studio · VFX creator and editor (2026-11-02)

The new **✨ Particles** toolbar entry opens a touch-friendly, draggable Particle Studio with ten reusable particle presets (Arcane, Flame, Smoke, Sparks, Snow, Rain, Healing, Building, Portal and Confetti). Create, duplicate, delete, preview and trigger effects; edit continuous/burst emission, rate, particle count/lifetime, four 3D spawn shapes, initial speed/direction/spread, drag, gravity, spawn radius, point size, start/end colors and blending. Place effects in the camera view or attach to a selected actor. Strict `swyrl-particle-studio-v1` import/export and project-local definitions survive Save, Undo/Redo and multiple levels; externally loaded emitter data is validated before rendering. Effects share the existing §E 2D/WebXR renderer and tick, remain cosmetic, and cap at 12 emitters / 96 each / 576 globally. **v11.224:** 256 ordered patches, 68 original assets, 7,590,193 generated HTML bytes, SHA-256 `29583040d840e7bd328d7417d0abb8a0d0c8cebf5a6db2db8014b602bdfb6a54`. Source/syntax and focused emitter lifecycle tests PASS; publication and owner Quest/Android acceptance tracked separately. See `docs/PARTICLE_STUDIO_V11_224.md`. The preceding v11.223 tighter-fist/wrist-wave hand changes remain preserved.

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

## Current §E owner handoff — Quest spatial editor v11.198 (2026-11-01)

**Authority:** §E 230 ordered patches, 68 assets, 7,320,589 bytes SHA-256 `c5e42de3a9c6dca98d72843b70c4cb2eb549c22589aae4a7fb0d4f7e8ba00f0f`. The new editor adapter implements 6DoF right-grip object grabbing, trigger-selectable native XYZ gizmo, adjustable smooth free flight and speed boost, per-device snap-turn settings, in-world controls legend, smaller controller visuals and robust cleanup. Only editing runtime changes; prior project data, Sheep Tag game authority, Chat, Modeler, and saved settings remain independent. Read `docs/QUEST_SPATIAL_EDITOR_FLIGHT_GIZMO_V11_198.md` before further VR changes. Release after strict verifier and a separate pinned deploy request. Quest 2 hardware acceptance pending.

## Current §E handoff — Sheep Tag meadow/fog v11.197 (2026-10-31)

Native source authority: 229 patches, 68 assets, 7,300,640-byte HTML SHA-256 `315e2acb7f54118fce4e428e534cceac14a0ecbaac596291df29ba6dbd7cc54d`. This source-only update removes the legacy 1px aliasing grid, explicitly mipmaps the active Moonbell Wildwood and prefilters its 4K art to 2K for Quest Browser, adding anisotropic filtering, prevents fog painter conflicts in LAN, and reduces flat camera cost. See `docs/SHEEP_MEADOW_VISUAL_STABILITY_V11_197.md`. Preserve VR editor, Sheep Tag input and all prior source history; deployment only after strict verifier and separate pinned request. Quest hardware acceptance pending.

## Current §E owner handoff — Sheep Tag 2D fog/Quest camera v11.196 (2026-10-31)

**Source of truth:** 228 patches, 68 assets, 7,295,859-byte HTML SHA-256 `679d14774b8abb97254f1adf072b98f0db51bbad152a2567142105155b944ca1`. Appendix `docs/SHEEP_VR_FOG_CAMERA_RECOVERY_V11_196.md` documents independent 2D fog-plane depth fight, VR mirrored drifting radial and colliding cinematic/editor rig movements. Strict source verifier `scripts/verify_v11_196_release.py`; deployment must be a separate pinned request commit after checks. Quest 2 physical testing remains pending.

## Current §E owner handoff — Quest Sheep VR stability v11.195 (2026-10-31)

**Authority:** The source manifest pins v11.195 to 227 patches, 68 assets, 7,288,202 HTML bytes, SHA-256 `7fa6242cfeeb6f9b44e8887cf86b905ed5e6ee9c55e7e12696a64fc77a0a31ad`. This repair adds a stable-base XR follow rig, Quest fog/render/raycast optimizations, authored menu cinematic, right-hand radial controllers, calibrated glow beams/particles, no duplicate Exit VR sign and an XR photo mode/debug metadata. See `docs/QUEST_SHEEP_VR_STABILITY_V11_195.md`. Update desktop/Quest only via strict verifier plus separate pinned deploy request; device performance acceptance remains pending.

## Current §E owner handoff — Emberfall v11.194 ARPG starter (2026-10-31)

**Source:** `projects/swrlz-forge-moba/source-manifest.json` is authoritative for v11.194, SHA-256 `740bfa088414731cd6b397aaf85290ef550461d8708ade833f9f3742a27aa2f4` and 7,259,828 bytes. New Projects starter is `emberfall-arpg`; native authored scene & Play-only ARPG loop with spells, loot, enemy AI, quest and companion. See `docs/EMBERFALL_ARPG_STARTER_V11_194.md`. Save/Load and existing startup defaults remain independent. Source-validation gate precedes the separate final `DEPLOY_REQUEST.json` commit and hosted Space verification. Gameplay acceptance on owner devices is pending; do not claim full ARPG/VR support.

## Current §E owner handoff — v11.193 Quest VR candidate (2026-10-31)

**Authority:** `projects/swrlz-forge-moba/source-manifest.json` now pins §wyrl§ Engine **v11.193**, 225 ordered patches, 68 assets, 7,230,728 bytes SHA-256 `f4e7aa71b4d40d1081645eb2b0a7954a4a7b7e06a10e02338b9cd7e7b6a2574b`. Source verification PASS [GitHub run #41266488354](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41266488354). The VR feature extends the single canonical renderer with native Sheep Tag main menu, elevated follow/free orbit, game-authoritative controller building, and clean/debug/stereo scene capture. Existing desktop/mobile, Chat and Model Atelier boundaries remain unchanged.

**Release path:** Follow `projects/swrlz-forge-moba/RELEASE_PROCESS.md`: coherent source update to main, then only `DEPLOY_REQUEST.json` in a separate final commit pinned to exact source SHA/hash; check terminal deploy and hosted Space source before claiming live. A GitHub mock pass is not a physical Quest 2 acceptance. Dragon Den in-world interactive floating 2D workstation is not yet implemented in this release.

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

## §E v11.154 — Registered guest input receipt and host movement (2026-10-27)

The owner physically verified shared host world but guest joystick still would not move the sheep. Guest v11.153 overlay displayed joystick ACTIVE / 35 sent, which was only local send attempts, NOT proof the host received commands. v11.154 introduces distinct sequence-numbered WebRTC input packets, a connection-bound registered host listener, explicit receipt acknowledgements, and native-frame host movement of the guest-assigned sheep with native obstacle checks. Guest HUD exposes TX attempts, host ACK and host movement frames; host HUD exposes input RX and movement counts. Existing v11.152 host world snapshots/game modes preserved. Focused isolated JS input/receipt/movement test passed; two-device acceptance still pending. GitHub Action remains build+HF upload only.

## §E v11.153 — Physical guest-input follow-through (2026-10-27)

User verified two Android browsers share the same host-authoritative world and can see the host move; guest joystick did not move the assigned guest animal. The narrow fix disconnects native guest-local simulation gating from joystick input, sends live guest pointer intent across the already connected PeerJS/WebRTC DataChannel, and moves the assigned guest animal in the native host game frame with world bounds/obstacle checks and stale-intent timeout. Host and guest HUD diagnostics show input send/receive counts. The previous shared-world snapshots, build commands, Sheep Tag level and all assets remain. Dedicated HF Action still only packages and uploads. Await physical two-browser guest movement acceptance.

## §E v11.152 · Owner phone/laptop shared-world correction (2026-10-27)

Owner's two physical devices connected and both started gameplay, but each ran independent sheep/wolf AI and building simulation. v11.152 instead runs Sheep Tag's existing single authoritative native simulation on host; registered WebRTC guests receive approximately 130-ms snapshots and send bounded build/move/attack orders and mobile joystick intent for their distinct assigned animal. Guest local world tick is disabled; existing project, canvas, assets and authoritative build/collision rules preserved. Existing PeerJS Cloud only facilitates WebRTC signaling. This is the first multiplayer state-sync candidate; owner two-device acceptance remains pending. Dedicated HF deploy workflow stays build+upload only (no Chromium, remote asset audit or live polling).

## §E v11.151 — Owner-requested simplified LAN flow and deploy (2026-10-27)

Primary hosted HTTPS LAN workflow is now one-code: the guest only enters host's invite; automatic offer-answer uses PeerJS Cloud; no manual guest reply. Guest fills a real room slot only after its direct WebRTC channel establishes. Start Match coordinates local Gameplay launch but **does not synchronize sheep/wolves/houses/physics**. The public PeerJS Cloud handles signaling, not game content. GitHub deploy workflow is intentionally only build/package + upload to the dedicated HF Space; no Chromium/full-suite/live asset audits on deploy. Keep 183 historical engine patches and 68 assets. Owner mobile+laptop acceptance pending.

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

## §E v11.143 · Real mobile viewport mounting fix — playable Start Game and Project Levels (2026-10-26)

Owner Android screenshot after pressing Play on the independent Main Menu Level showed **no Start Game button**, no Project Levels strip and an unchanged editor gizmo. The v11.142 synthetic tests had checked the existence of DOM nodes without checking actual layout or mobile tap hit targets. **Real Chromium mobile instrumentation established the exact defect:** the native renderer element identified by **#viewport is a CANVAS**, not a wrapping DIV. The v11.141/v11.142 scripts appended the interactive Start Game overlay, editable menu preview and Project Levels toolbar directly **inside the canvas**. These appear in the HTML DOM but are fallback canvas children, have zero-sized layout boxes, and are never rendered or touchable. The camera/cinematic session could still start behind the apparently unchanged editor.

**Repair:** Mount those existing DOM widgets as normal siblings of the canvas inside its actual parent `main.viewport-wrap`, which is a positioned, layered HTML host. Move existing elements; do not recreate them or alter their saved data/event handlers. Bind the runtime menu with an absolute full-viewport overlay and a visibly tappable Start Game button; keep the editor preview pointer-transparent, and Project Levels visible only in Edit mode. Maintain the existing authored menu and gameplay level content, native session transition, 3D camera and leg animation, Stop, Project Levels/New Map, all original gameplay rules and 68 source assets. No new actors, physics, network endpoints or simulation loops.

**Acceptance:** Rebuild exact source with 175 ordered patches. Run genuine headless Android-size Chromium with touch enabled, dismiss first-run release notes, open Sheep Tag starter, assert both Project Levels and static editable preview have nonzero geometry and parent MAIN rather than CANVAS, tap the actual Play control, assert Start Game overlay has a nonzero rectangle and is the hit-tested touch target, then tap Start Game and verify the linked native Gameplay level/session starts and menu UI disappears. Preserve older Sheep Tag and level bundle regression tests. Real owner Android is the final acceptance check.

## §E v11.142 · Android STOP, Start Game overlay and character gait corrections (2026-10-26)

**Owner report on v11.141:** On Android the native **Stop** button disappeared from the top area beside Play/Pause; sheep and wolves in the playing cinematic slid without locomotion; the **Start Game** GUI button was absent.

**Root handling:** The project-level bar had been inserted directly into the cramped native Play/Pause/Stop toolbar, moving playback buttons offscreen. The cinematic translated/rotated authored animal roots but did not drive their existing stLeg0..3, stHead and stTail joint pivots. The menu eligibility check depended exclusively on an optional level root metadata property that the native scene loader may drop.

**v11.142 fix:** The **Project Levels** strip is mounted over the editable viewport, out of the main playback toolbar. Native Stop is placed beside Pause, visible and enabled during menu Play and regular sessions, and shown disabled during idle editing; it still invokes native session/scene Stop. Menu eligibility recovers from the current level's project identity and the known authored level record; missing level metadata is restored after loading. The main menu exposes an interactive Start Game button during menu playback, and **Play Game** in the editor level strip can launch via the menu (while native Play continues to run a selected level). Menu sheep and wolves animate their original leg/head/tail pivots from travel distance, restoring joint and actor pose exactly on Stop or Start Game.

This patch does not invent additional wolf gameplay, move collision/capture code, modify original assets, or discard §e multi-level serialization. Existing gameplay already contains distance-based walk pivots and remains unmodified.

**Acceptance:** On Android Stop must remain near Play/Pause; Play Menu displays Start Game; sheep and wolves move their legs instead of sliding; Stop returns to an unchanged editable authored menu; Start Game transitions to the independent gameplay level; Project Levels/New Map/Save/Load and original 68 assets remain intact. Synthetic CI tests and real-device visual acceptance are separate.

## §E v11.141 · Project-wide separate editable levels, new maps and connected Play flow (2026-10-26)

Owner correction to v11.140: the menu cinematic must **not** animate inside the editor as an uneditable overlay on the gameplay level. Levels are separately authored, editable maps that may be connected for runtime loading, not scenes that silently run when opened for editing.

**Project-wide level system:** In the native §e editor, opening any project exposes a **Project Levels** selector, **+ New Map**, editable level name, **Next** connection, and **Export Level**. Each level owns a separate native scene snapshot (actors, transforms, editor layers, metadata); switching loads that snapshot in the editor without invoking Play. New blank maps inherit compatible project settings and a Sheep Tag meadow ground, but no phantom bots or unapproved gameplay spawns. The existing native Play command runs the selected map separately; the connected next map is available via the **Next Level** runtime action or the public `SWYRL_ENGINE_LEVELS.transition` API.

**Persistence:** The native `projectData()` now serializes an explicit `project.levelPack` collection with schema `se-levels-v1` and one nonrecursive saved project snapshot per level. Whole-project Save/Export includes all levels and their navigation links even when only one is open. Opening the saved project restores the level collection and last selected level. Individual levels can also be exported as standard `.swyrl.json` scenes. Level switch preserves edited scene snapshots in project memory; the native undo timeline resets per newly opened level, so Save Project before closing the browser/editor.

**Sheep Tag starter first example:** Two native levels: **Main Menu** (separately versioned `scenes/sheep-tag-main-menu-v11-141.swyrl.json`, 13 editable sheep/wolf/house/landscape actors), and **Gameplay** (existing untouched Grand Moonbell Wildwood, 196 actors). The menu UI text, colors and orbit speed are editable in **Menu UI**. Editor view is static. Only the user pressing Play animates the actual authored menu actors with a low-cost chase/house build camera sequence; the visible **Start Game** transitions to the linked Gameplay level and calls native Sheep Tag Play/preflight. Stopping returns to the unanimated authored menu with transforms restored. The retired v11.140 editor-time transient cinematic does not run. No wolves, sheep mechanics, resource rules, Rapid Build or local multiplayer gameplay is changed.

**Acceptance gate:** separate editable menu and gameplay scenes, new project map creation, project bundle Save/Load roundtrip, transition links, no editor-time animation, native gameplay Start Game, original 68 assets preserved and source checksum validated; real Android editor usability remains an independent check.

## §E v11.140 · Sheep Tag starter main menu & 3D attract background (2026-10-26)

**Owner request:** Open Sheep Tag as an actual game with a simple main menu containing only **Start Game**, rather than immediately throwing the player into the native editor/game controls. Behind the menu, show a slowly circling 3D camera, sheep moving/building/fleeing, and a wolf chasing/tagging sheep.

**Implementation scope:** The canonical `stLoadStarter()` completes the existing authored starter load and then overlays a responsive Sheep Tag title, “Build. Flee. Survive.” and one prominent Start Game button over the viewport. Its backdrop is **real Three.js scene geometry**: three sheep, one wolf, a small house cluster, ground/trees, a growing construction house and scripted chase/tag disappearance on a 17-second repeat. It advances from the **existing editor frame loop** with a slowly orbiting camera—no second game clock, render loop, navigation load, bot simulation or online API usage. It does **not** modify actor arrays, saved maps, history, collisions, gold or captured counts.

**Start Game:** The button first removes the overlay and every temporary demo mesh/material, restores the saved editor camera/orbit state, then invokes the existing native `playBtn.click()`. The real match uses its already established preflight, game engine, HUD, bots, timer, rules and fresh source-of-truth session. Switching projects similarly destroys the menu/demo before loading another project. The standard editor toolbars remain outside the viewport overlay; other §e starter projects are unaffected.

**Acceptance:** Check Sheep Tag starter opens at menu, the scene animates while the real timer stays stopped, Start Game works with mouse and Android touch, the demo vanishes completely, match starts with original sheep/wolf/structure counts and physics, pressing Play in other projects remains unchanged, and exiting to a different project cannot leave ghost menu actors behind. Automated source/verifier and synthetic scene/transition checks are distinct from owner Android visual acceptance. Preserve all previous 171 patches, original 68 packaged assets, and local multiplayer being future work.

## §E v11.139 · Safe Rapid near-corner house magnet (2026-10-26)

Owner Android screenshot (v11.138) showed a red house hologram beside a compact cluster of existing Free Houses, with the exact native validator error **"A diagonal crack is not a sheep passage. Join houses or leave 1.20 m."** This is not a lost touch; the existing v11.124 diagonal clearance rule is correctly rejecting an intermediate narrow slit. The ergonomic weakness is that the prior house snap only magnetizes side-aligned footprints, so a close diagonal corner cannot easily snap flush on the phone.

The v11.139 Rapid-only improvement checks the rejected diagonal house against nearby existing house corners. It proposes the closest **fully flush x-and-z corner** when the correction is within the current sheep-safe-lane width (typically 1.20 m), and calls the full previous native `stCanBuild` validator on that candidate. Only a valid return changes the ghost to green and updates the actual build destination; if another house, collision, boundary or route rule rejects it, the original red rejection remains. It never relaxes the 1.20m clear lane, alters occupied structures, creates a building during preview or auto-places a faraway ghost. Rapid OFF and non-house structures behave as before; v11.138 same-screen Rapid cursor memory remains.

Sealed target: **171 ordered patches, 68 unchanged assets, 6,719,389 HTML bytes**, SHA256 `f605af72628643e87d8fca5d97a08fcba438c43f2d9ffa693e4f6014032ce6fb`. The regression tests the red original, legal corner snapping, occupied-corner refusal, other build kinds, Rapid OFF, and assembled patch/marker. Android visual and gameplay acceptance remains pending after hosted verification.

## §E v11.138 · Rapid Build remembers last successful build SCREEN position (2026-10-26)

Owner design request: with Rapid ON, the next ghost should start at **the same spot on the player's phone screen as the last successfully built house**, rather than restarting at the sheep or remaining attached to the old house's world coordinates. This allows sheep to move and the follow camera to pan while maintaining a consistent placement cursor position.

Source behavior: on successful Rapid placement, project the actual validated build center through the current camera and store normalized viewport coordinates, scoped to the current session and controlled sheep. After reselecting the same build tool, seed the next ghost by raycasting that screen coordinate into the **current** world; while idle, camera follow refreshes the ghost without issuing build commands (with throttled re-projection to limit mobile cost). On a new meadow drag, the remembered on-screen site moves by the finger's on-screen delta. Changed camera position must not make the preview jump back to the previous world site. Invalid, canceled, unpaid or blocked placements do not alter the anchor. First build in Rapid remains sheep-origin; turning Rapid OFF and ending/restarting the match clear the memory.

The actual structure is always created only after native movement, resource and collision validation. Single-tap meadow placement, non-Rapid builds, Rapid repeated selection, construction timing, Mirror/Totem, wolves, local multiplayer state, original 68 assets and all existing game behavior remain unchanged. Source seal target: 170 patches, 68 assets, 6,717,316 bytes, SHA-256 `384558ce7af5993f36ef002824455d850fdfebf635a881eea1fe4878931f7385`. Android touch acceptance remains separate from automated checks.

## §E v11.137 · Full-screen meadow-first touch construction (2026-10-26)

The owner confirmed the sheep-origin building hologram appears correctly, but the old continuous touch-drag began from the bottom-right build icon, leaving almost no room to move downward/right on the phone display. **v11.137 separates selection from aiming on touch/pen:** tap Free/Income/Fortified/Ramp/Walkway to select, release to leave the hologram visible at the sheep, then touch *any open meadow position* and drag from that fresh anchor to move the preview. Release on valid ground to place, or simply tap a meadow target for single-tap placement. The button-touch alone cannot place a building or move its preview off the sheep. Native single-placement and optional Rapid repeat both still work. Desktop mouse direct-icon dragging stays available; all existing game/safety constraints remain authoritative.

Source seal target: **169 historical-plus-new patches, 68 preserved assets**; build hash/byte count populated only by the isolated exact-source measurement and verification. Real Android comfort/placement remains owner acceptance. No wolf-side development or multiplayer changes.

## §E v11.136 · Camera-stable sheep preview and capture performance (2026-10-26)

Owner Android gameplay report: v11.135 build hologram now originates at the sheep, but is still slightly inconsistent while dragging; phone frame rate appears to dip when sheep are rapidly captured and their buildings vanish. This is a *source-level optimization* pending Android acceptance, not a claim of measured FPS gains.

The previous sheep-origin drag stored its initial ground ray, which could become stale when the follow camera moved. v11.136 casts the drag anchor and live finger from the same current camera, then offsets the living sheep's current position by their difference; the player still sees/commits the authoritative snapped footprint. The placement grid skips redundant geometry uploads for unchanged snapped destinations while revalidating on changed navigation topology.

Capture still immediately marks each owned building destroyed, removes its scene mesh from visibility/collision, triggers Archive callbacks and makes it unavailable to wolves/sheep. A capture wave now emits **one** navigation cache invalidation rather than one per house. Expensive GPU geometry/material disposal is drained over subsequent update frames (2 per frame) and flushed on match stop. No houses persist in gameplay because their disposal is deferred. The performance diagnostics include capture batches, retired/disposed mesh counts, pending queue and grid skip count.

Scope is strictly Sheep Tag's client simulation and UI. Wolf behavior, capture balance, sheep builds/costs, Rapid toggle, Mirror/Totem, saved maps and all native assets are untouched. The exact release seal is **168 source patches / 68 assets / 6,711,684 HTML bytes**, SHA-256 `b6114ad2b3f8e6c3352869336845df015fdf18da40e580e5cb4ef819fc5476af`. The new regression tests same-camera aiming, single nav invalidation per capture, immediate detachment, bounded disposal, stop flush, and placement grid reuse. Android touch feel and actual phone frame-time still require user acceptance.

## §E v11.135 · Sheep-origin relative hologram, bigger Free House, visible Mirror (2026-10-26)

**Owner Android screenshot:** selecting a house still showed its hologram and placement grid near the bottom-right skill ring rather than visibly originating at the controlled sheep. Free House also needed to trade screen positions with Fortified House and grow larger. Totem was visible, but Mirror/decoy was missing from the sheep's touch HUD. The owner explicitly deferred wolf-side gameplay; no owl scout or wolf behavior is changed in this release.

**Input root and scoped correction:** the previous v11.134 sheep-origin preview only adjusted the ghost mesh after selection. The earlier `sheep_touch_offset.js` camera updater still re-raycast an active touch gesture each frame, and the old v11.84 pointer aim jumped to an absolute finger-based target. v11.135 prevents that re-aim while the placement pointer is active, plants the hologram at the controlled sheep on selection and first meadow contact, then translates it from the sheep using the deliberate meadow drag delta. The initial detached placement grid stays hidden until a target is aimed. One-tap meadow placement remains valid, and final issuance uses the exact displayed and native-validated building site rather than a separate finger ray. Construction costs, permitted structures, resource checks, safe placement, wolf collision and Rapid Build remain unchanged.

**Phone HUD:** Free House occupies Fortified's former slot at 112% of the former large house size; Fortified occupies the former Free slot. Income House stays bottom-right. Mirror and Totem are explicitly attached to the native ability ring with separate visible hit targets for sheep; rules-disabled skills stay disabled rather than overriding custom-map settings. Mouse/keyboard and wolves remain unaffected.

**Source integrity:** 167 ordered patches / 68 original assets; compiled HTML **6,708,052 bytes**, SHA-256 `40cf34d1322b071812e0061d25a3be5353a4ad81820714d32eb06608161a09b5`. Dedicated build and targeted DOM/native regression form the release gate. Hosted publication must still be verified through the dedicated `DEPLOY_REQUEST.json` trigger; real Android placement and button appearance remain separate owner acceptance checks.

## §E v11.134 · Live deployment audit success (2026-10-26)

Protected §E deployment [GitHub Actions #40386472509](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40386472509) completed **SUCCESS**. The Hugging Face static Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` reported **RUNNING** at revision `eefecb5562811d7c59feee23396d4d4e1ca88df0`. First live verification retrieved and matched the exact **6,700,691-byte v11.134** HTML, SHA-256 `71a6056da0404f81f09337a2dddb45c87b81450ce49b327f8525fccd5d4efdbe`, **166 ordered patches**, all **68 bundled assets**, and the canonical `SOURCE.json` receipt. Source commit `a2c274ede9bdfbef75c7aa97676c7240c62305e4`, deployment trigger commit `f34278515cf9be52971498dd784ca98060b49b70`.

Owner Android acceptance remains separate: switch Rapid ON/OFF while its ghost is unplaced; verify tapping each house starts its hologram on the actual sheep before dragging; verify both Mirror and Totem remain visible (disabled when custom rules require); check the swapped bottom-right Income/Free house buttons do not overlap other controls. Automated source and DOM tests passed, but they cannot certify device-specific touch/visual layout.

## §E v11.134 · Rapid OFF cancels ghost, exact sheep-origin marker, restored ability slots, Free/Income HUD swap (2026-10-26)

The owner's Android acceptance exposed three post-v11.133 problems and one missing skill slot. **Rapid Build OFF** now immediately exits the active build mode and removes any unplaced ghost, touch gesture/placement marker and selected tool; it never removes already constructed houses or interferes with issued build orders. Turning Rapid ON leaves selected tools alone. **Selecting any build skill** immediately displays its hologram at the controlled sheep's *actual* X/Z (not a snapped construction site), on touchscreen, mouse and keyboard; after selection a meadow drag still drives native ghost placement with original collision, snap and resource checks.

**Mobile ability HUD:** both original sheep skills—Mirror and Totem—remain present. If a user-created map disables one in Sheep Tag rules, the icon stays visible but disabled with an accessible explanation; this release intentionally does not override owner's custom rules. The canonical starter's existing enabled ability settings and cooldowns remain unchanged.

**Bottom-right skill circles:** swapped the *physical screen positions* of Income House (now bottom-right) and Free House (now the previous Income slot), updating the circle and SVG sizes. Real game building types, free/paid costs, permissions, keyboard shortcuts, IDs, joystick, decoy, rapid position, and all 165 older patches are unchanged.

**[Full build + UI regression #40385878910](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40385878910) SUCCESS:** exact prior v11.133 seal independently verified, then **166 patches** assembled and JS syntax validated. DOM regression tested Rapid OFF with/without in-flight pointers, automatic exact sheep-centered preview after selecting Free/Income, visible-but-disabled custom-rule ability slots, intact wolf HUD hiding, and positional CSS swaps. Official output: **6,700,691 HTML bytes**, SHA-256 **`71a6056da0404f81f09337a2dddb45c87b81450ce49b327f8525fccd5d4efdbe`**; all **68 original assets** preserved. Protected live deployment and owner's Android real-device test remain separate verification gates.

## §E v11.133 · Deployed; Android owner acceptance pending (2026-10-26)

**Production [GitHub Actions #40382749397](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40382749397) SUCCESS.** The exact guarded release of §E v11.133 was uploaded to `https://kamiloki-swrlz-forge-moba.static.hf.space/` and the **first live audit passed**. Hugging Face Space reported `RUNNING`, revision `e87a981cf9bb48bd54c2109d6f0185b8a5956d5a`. Live audit verified the exact HTML (**6,696,326 bytes**; SHA-256 `2c2b40a507bc91950479ac9983eb365c6c5d9319a5e85c9fe3b7ac18f27860b8`), all **165 ordered source patches**, all **68 original bundled assets**, and exact `SOURCE.json` receipt.

**Owner Android acceptance still needed:** confirm circular Rapid toggle is touchable beside Income (bottom right), visibly changes OFF/ON, selected House skill leaves a hologram at controlled sheep, same-finger skill-to-meadow drag and separate meadow drag both move preview, and successful Rapid orders retain build mode. Existing live sheep occlusion wireframe remains. Passing DOM synthetic click tests demonstrates handler logic, not conclusive Android touch UX.

## §E v11.133 · Rapid next to Income, touchable, and sheep-origin build ghost persists (2026-10-26)

**Owner's actual Android screenshot and test:** §E v11.132 rendered the circular Rapid toggle around mid-screen as an unexpectedly **small square**; owner could not turn it on or off. The house skill also frequently failed to leave a working holographic preview after tapping/dragging, although the **cyan sheep occlusion wireframe already worked**. Owner specified Rapid's intended location **immediately left of the Income house icon in the bottom-right build cluster**.

**Root causes and fix:** The native Sheep Tag HUD root has `pointer-events:none` and only certain child controls explicitly re-enable pointer input; v11.132's free-floating Rapid button inherited the no-pointer policy. The generic HUD button's higher selector specificity also overrode Rapid's circular border. v11.133 mounts Rapid/Rotate inside the actual `.st-builds` skill cluster and positions the circular Rapid ON/OFF icon to the left of Income, with `pointer-events:auto!important`, accessible pressed state, and strong circle styling. Rotation remains context-sensitive.

A second, independent defect: touching the House skill caused native `pointerup` to select the tool and seed its preview at the sheep, **then Chrome dispatched a synthesized click** to the skill button, running `stUiChooseBuild(kind)` again. That function **toggles the already-selected build tool OFF**, removing the hologram. The fix suppresses just the one matching touch-derived click after a handled skill pointer release, not keyboard, mouse or subsequent intentional taps. The ghost is also seeded while the button is held without triggering the old invalid-touch hide path. A continuous drag from icon onto clear meadow now moves the preview when the finger reaches valid ground; a normal tap followed by meadow drag also remains supported. If a skill drag ends above HUD/blocked ground, the selected tool and sheep-origin preview are retained.

**[Full source + Android click/ghost regression #40381957434](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40381957434) PASS:** exact prior v11.132 seal reconstructed; 165 patches compiled and JavaScript syntax checked, `jsdom` reproduced synthetic touch click and verified selection persistence, keyboard/mouse input, clickable Rapid, parent-location near Income, circle/ON/OFF CSS, meadow child canvas hits and all previous §E gameplay integrations. Exact build **6,696,326 bytes**, SHA-256 **`2c2b40a507bc91950479ac9983eb365c6c5d9319a5e85c9fe3b7ac18f27860b8`**, 165 ordered patches and original 68 assets. Owner's live Android acceptance is still needed after deployment; automated DOM events do not prove real Chrome behavior.

## §E v11.132 · Live deployment verified (2026-10-26)

**Official production [GitHub Actions #40379238352](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40379238352): SUCCESS.** Isolated deployment commit `33ac9b0e7a7674e7bf4be8e9f5a45ab88bf38efa` requested exact sealed engine source `41e020d6e92ec432dcbccf0d00ce011b774e0780`. Dedicated static Hugging Face Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` reported **RUNNING**, revision `374e0eb1fa35699895e0b851f6b19ea0c9acb84a`. **Live verification attempt 1 passed**, matching the entire **6,691,218-byte HTML**, SHA-256 `6d678e0886907007de501b5f9d68916f09246eb25f6fa865a36e56481fa64920`, **164 source patches**, all **68 bundled assets**, and exact `SOURCE.json` source receipt. 

Live publication has succeeded, but the user's **Android gameplay acceptance** is still pending: test meadow drag after tool selection, Rapid mode consecutive placements, cancelable build recovery, three rotated permanent ramp groups, walking under a completed walkway, and occluded sheep wireframe appearing only when visually covered. Physical touch and game feel are not proven by automated test suites.

## §E v11.132 · Dragging sheep-centered hologram, Rapid Build, rotated raised crossings and occlusion wireframes (2026-10-26)

**Owner gameplay report:** tapping House correctly placed the preview ghost at the sheep after v11.131, but dragging on the meadow **did not move the hologram**. The native v11.84 pointerdown callback was discarding the selected tool and calling `stUiChooseBuild(kind)` again; that API **toggles the same selection off**. The final patch differentiates the selected skill-button event from a subsequent meadow drag, preserves the selected active tool on meadow pointerdown, recognizes viewport descendant targets, follows actual pointermove with native preview/snapping, and commits only upon valid pointerup/resource/collision checks. Finger drag on the skill icon is still separate from moving the hologram.

New **circular, accessible RAPID ON/OFF button near the middle of the mobile screen** keeps the selected house/structure after a successful native building order and reseeds the next hologram at the sheep. Off mode restores one-and-done placement. A companion **⟳ rotate control** exposes the existing 90° rotation for player-built ramps and walkways. On actually constructing any new owned building, the sheep pauses automatically for **0.28 s**; a movement order or joystick direction cancels that recovery immediately, while the game clock, captures, effects and AI remain updated.

All nine indestructible authored prebuilt ramp/deck pieces in **three Moonbell crossings** remain: Pinewatch at 0°, Moonflower at 90°, Amberglade at -90°. Opposing ramp high ends still join their real 6 m deck endpoints exactly. **Completed elevated walkways** now admit sheep/wolves travelling at ground level beneath the 3.3 m platform, without changing upper path surfaces; ramps and incomplete platforms remain blocking until complete. Occluded living sheep receive a **cyan see-through wireframe clone of their own actual animated sheep mesh** only when physically under a walkway or when a house/deck blocks the camera's sightline; it hides once clear and never changes unit physics, controls or original materials.

**[Complete 164-patch gameplay CI #40378516848](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40378516848) PASS**. The run rebuilt the exact preceding v11.131 release, assembled all **164 ordered patches** into **6,691,218 bytes**, SHA-256 **`6d678e0886907007de501b5f9d68916f09246eb25f6fa865a36e56481fa64920`**, checked compiled JavaScript syntax, and exercised actual Three.js wireframe materials, underpass blocking, three rotated crossing groups, responsive rapid toggle and rotation UI, interruptible construction recovery, and required assembled native pointer handler changes. Original 68 bundled assets and all earlier behaviors remain intact. Production deploy and real owner's Android touch acceptance remain separate gates.

## §E v11.131 · Production deployment and live-source audit completed (2026-10-26)

**Protected deployment [Actions #40373327088](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40373327088) SUCCESS.** Source commit `e155e7d2bf5acb19443134851a465ddcba2ab45d`; isolated deployment request commit `d4931bcdbddd9ce4a2f414bc135d1041ba510980`. Hugging Face static Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` reported **RUNNING** at revision `4315ca0665a372b10d000c806ddb73b17403f597`. The first hosted audit verified the exact **6,679,918-byte v11.131** HTML, SHA-256 `ae889b96eaeddf58d290a6214809463cf84930f88a02b5070cda83ae47080218`, **163 ordered patches**, **68 bundled assets**, and byte-for-byte matching `SOURCE.json` receipt.

Owner Android Chrome acceptance is still required: repeatedly tap starter project selections to test page zoom, choose a house and confirm sheep-position preview, hold sheep joystick and drag the Mirror icon to send the illusion in a chosen direction, observe countdown and lifetime. Hosted integrity proves deployment correctness, **not mobile device UX acceptance**.

## §E v11.131 · Drag-directed sheep Mirror decoy and ready-to-use mobile fixes (2026-10-26)

Following §E v11.130's successful **sealed-source** check, the owner additionally requested a **visible cooldown counter on the Mirror/decoy skill**, reliable casting while the sheep is moving, **drag-to-direct** the decoy and **short-lived disappearance**. The real archive gameplay `stArchiveSplit` now creates only a **separate decoy**, routes it toward the direction dragged from its skill button using the existing safe ground/upper path planner, boosts only the decoy's speed, and leaves the real sheep's movement/order/joystick completely untouched. A simple tap aims along the sheep's current velocity or facing direction. A blocked destination rejects without using cooldown, and existing unit validity and Classic-off rules remain enforced.

The Mirror skill icon gains a **live numeric cooldown badge** (not merely an info row) and accessible status label. The existing starter's **12-second Mirror cooldown** still comes from the game rules; successful casting sets the normal `archiveSplitAt`. Decoys expire after **at most four seconds**, or any shorter authored lifetime; they fade their own cloned materials in the final 0.7 seconds and can still dissolve earlier on wolf contact. The new touch ability owns only its own pointer; it does not cancel a second finger holding the sheep's mobile joystick, alter the camera, or spend gold.

Also includes the **v11.130 source fixes verified earlier but not independently deployed**: Android browser zoom is suppressed at the second single-finger starter-selection `touchstart` without blocking a true two-finger pinch; skill-button pointer movement and release no longer overwrite sheep-origin building previews. All original v11.129 and prior editor/Sheep Tag features remain intact, including the Clover model, startup gate, starter defaults, non-destructible walkways, player-build clearance, and all 68 bundled assets.

**[v11.130 sealed main preflight #40371349066](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40371349066) SUCCESS.** **[v11.131 full 163-patch CI #40372653251](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40372653251) SUCCESS**: rebuilt exact prior v11.130 seal, assembled 163 ordered patches, passed JavaScript syntax and automated Mirror ability tests for joystick-independent movement, drag direction, cooldown badge, short expiry, decoy-only material fade, tap use, no duplicate cast and original rule restrictions. Official new HTML: **6,679,918 bytes**, SHA-256 **`ae889b96eaeddf58d290a6214809463cf84930f88a02b5070cda83ae47080218`**, **163 patches, 68 assets**. Guarded production upload, live HTML/SOURCE audit and actual Android thumbstick/gesture acceptance are separate gates.

## §E v11.130 · Second-touch Android page zoom protection + true sheep-origin house preview (2026-10-26)

**Owner Android acceptance feedback:** §E v11.129 reduced browser magnification during rapid starter-project taps but **small browser PAGE zoom still reproduced**. This is not the 3D camera. The new `passive:false`, capture-phase `touchstart` guard observes a short stationary single-finger starter-card touch and prevents default on the **second** rapid single-finger touchstart within 670 ms, before mobile Chrome can decide to smart-zoom. Previous native `touch-action:manipulation` and post-click 420 ms handoff shield are retained as layered protection. Two-finger pinch, editable input interactions, long press, mouse/keyboard, viewport camera controls and general scrolling remain unaffected. This is a targeted browser-page control; no global viewport zoom restrictions are imposed.

**Owner also reproduced a construction regression:** tapping a Sheep Tag build skill still sometimes caused the house preview to spawn **at the skill icon**, despite v11.126 sheep-centered seeding. Root cause: the older v11.84 `stBuildInputAim(event)` unconditionally re-aimed the preview during **skill-button pointermove and pointerup**, overwriting the later sheep seed with the button's screen ray. v11.130 preserves native meadow pointer-down/aim/release but stops handling the skill-button finger as an aiming pointer. A skill tap simply selects the house tool and **re-seeds the preview at the controlled sheep** on release; only touching the meadow can aim or order a house. Native `stCanBuild`, collisions, unit relocation on valid build, resource costs, original joystick and safe lanes remain unchanged.

**[Full 162-patch source and DOM/native handler preflight #40370882999](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40370882999) PASS:** reconstructed exact v11.129 release; measured **6,672,532 bytes**, SHA-256 **`6156d4261621b38b570792f24acff2f126baaf2384b2f4f79acd5975a13b5a26`**; checked compiled module syntax. DOM tests confirmed rapid second `touchstart` cancellation, true pinch and editable-field exceptions, movement threshold, and actual extracted native skill-button `pointerup` handler re-seeding without ever aiming toward the button. Original **68 assets** and 161 earlier patches are preserved. Protected production deployment and owner real-device acceptance are separate checks.

## §E v11.129 · Live Android project-transition zoom guard verified (2026-10-26)

**Release:** [GitHub production Actions #40368794102](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40368794102) **SUCCESS**. Live Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` was **RUNNING**, revision `d77fbb1dec6a43c2e49edad774d897f78ace1d63`. First hosted audit checked exact HTML (**6,669,441 bytes**, SHA-256 `34caf41b05e3c404e12d0da122a79db61c8187aaea1692b2cd07c380a69a4f7f`), **161 source patches**, all **68 packaged assets**, and `SOURCE.json`. Browser page-zoom defense on project handoff deployed; preserve pinch zoom, native scene input and checkbox selection.

**Manual Android acceptance pending:** repeatedly tap project starters and test rapid taps around modal close; observe whether browser **page scale** changes versus the 3D camera. The synthetic event regression proves controls and transition shield behavior but does not reproduce the physical mobile browser gesture.

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

## §E v11.126 · Live production verified (2026-10-26)

**Production confirmed:** [GitHub deployment Actions #40344188092](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40344188092) completed **SUCCESS** (deployment request `ce590802d9e9a2403bd359fc85cbec04ea5a67ae`). Hugging Face static Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` reported **RUNNING**, revision `eb0fd0ecf3286501ae62faff0664e50416913b80`. Live verification attempt **1** matched the exact v11.126 compiled HTML SHA-256 `dbbc8d1ac954e3e93ec9f8feb74ed0371575c6378a9b27ef77c021c20dabcec5`, **6,651,868 bytes**, **158 patches**, all **68 bundled assets**, and the `SOURCE.json` receipt. This certifies production publishing/integrity, **not manual Android gameplay acceptance**.

**User acceptance next:** open a newly loaded canonical **Grand Moonbell Wildwood Sheep Tag starter** to see three indestructible prebuilt raised crossings; a previously saved personal map is deliberately not overwritten. Tap a house skill, verify its ghost starts on the controlled sheep, drag within the meadow and release to build. Verify the sheep can traverse both ramps/decks without jumping; Mirror ready at level 1 with a 12 s cooldown; Totem becomes usable after constructing one house, with 25 s repeats. Player-built structures remain demolishable. Preserve report of any Android-specific problem and exact game mode/map source.

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

## §E v11.123 · Sheep-safe snap placement, Projects-first editor toolbar and inset mobile controls (2026-10-25)

User Android screenshot of Sheep Tag showed four small farms with misleading narrow clearances and the nearest gap explicitly labeled BLOCKED. Requested new house placements snap either directly against another house or with enough open passage for a sheep, instead of leaving no-man's-land slots. User also requested the native §E main header reorganized with Projects at the far left alongside Play/Pause/Simulate/Stop and slightly larger buttons, plus Sheep Tag skill icons and movement joystick shifted modestly inward.

**Implementation:** Existing Sheep Tag house placement now uses a 0.3-world-unit lattice instead of arbitrary 0.15 fine steps; when side-adjacent it magnetizes to visual flush contact (approximately 0.015 world units) or an unobstructed *width* of at least 0.9 world units (raised automatically for user-configured larger sheep collision radii). Existing polygon/rotated collision, sanctuary, resources, construction, navigation, and camera rules remain authoritative; the same validation runs on the preview and the actual build order, denying a narrow misleading slit. The native ground placement guide uses matching 0.3 grid. The native header's existing DOM buttons—not replacement controls—are reordered Projects, Play, Pause, Simulate, Stop before other tools, retaining handlers; mobile controls are gently enlarged. The right-side Sheep Tag ability/build icons shift approximately 18–28 CSS pixels toward center and movement stick is inset on the left without changing their touch gesture implementation.

**Verification:** targeted source-assembled tests [v11.123 preflight](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40249141658) passed grid-lane behavior, header reordering, HUD offsets and earlier gesture/inspector regressions. Full official seal tracks **155 patches, 68 assets, 6,637,490 HTML bytes**, SHA-256 `858c08fae2edd165aec884363672d41a5591db6456e8cb5389e25d73d2668376`. Neither mathematical clearance nor static tests prove a sheep can navigate every *connected* neighborhood if other walls or obstacles intervene. Release receipt and owner Android gameplay remain separate verification steps.

## §E v11.122 · Full-workspace mobile gesture boundaries (2026-10-25)

Owner feedback clarified that the Model Atelier-only v11.117 and v11.120 guards did **not** apply to the normal §E maker/editor page: double-tapping starter projects in the main workspace still triggered browser page zoom, and holding non-editable text/controls still opened Android/Chrome selection menus.

**Fix:** Apply document-level `touch-action:manipulation` to §E's HTML/body (not the Chrome application or unrelated websites) so rapid taps do not cause browser *page* zoom, while native browser pinch zoom and the editor's specialized touch/drawing/camera rules remain intact. Capture and cancel `contextmenu` and `selectstart` only on non-editable content across the full engine. Restore CSS callouts, caret, copy/paste and selection specifically for input, textarea, contenteditable and textbox surfaces, including those inside Model Atelier whose older styles blocked them. Do not cancel touchstart, pointerdown, pinch, dragging, scrolling or clicks.

**Evidence:** Chromium mobile-emulation smoke test (viewport scale remained 1× after two fast taps, noneditable menus prevented, editable fields allowed); §E scoped Node tests plus camera, gizmo, preview, inspector and earlier toolbars passed in [focused preflight](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40236170378). The Android owner still needs to verify actual Chrome/WebView behavior and any operating-system-controlled copy menus. Version **v11.122**, **154 ordered patches**, **68 assets**, **6,630,708 HTML bytes** SHA-256 `9e88c9b1c7cbf96f18d7e0720b02562812233ba664facb833368ce71f3a5b449`.

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

Release **127 patches / 68 assets**, **6,501,581 HTML bytes**, SHA-256 `a0d61bfac63c666ae7037edfb6b92f509abf8f7d4314615decb3b39bffa7ce8c`, marker `V11_95_FITTED_SKIRT_WAIST`. Targeted waist dimensions, coverage, native editing/save/export and immutable source lineage are recorded in [FITTED_SKIRT_WAIST_V11_95.md](projects/swrlz-forge-moba/reports/FITTED_SKIRT_WAIST_V11_95.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md), with ordinary source publication and a separate final deployment-request commit. Owner-device waist-fit acceptance follows the release.

## §E v11.94 · Full knee-length festival armor skirt and softer portrait (2026-10-24)

All nine existing lower armor panels now overlap around the hips and thighs as a continuous festival skirt, with matching piping, insets, stitches, brocade, baubles and tassels. Every lower costume piece ends above the kneecaps; the fitted opaque shorts retain crotch coverage. The nose has a softer bridge and rounded tip, and the head is subtly narrower with a smooth neck transition. Original hair piñatas, grips, sockets, rising amber eyes and smooth leg contours remain preserved.

Release **126 patches / 67 assets**, **6,495,464 HTML bytes**, SHA-256 `ede8f335dc9f9086d5d6f1ec6abf7d73711aa56bf3ea123c7494af2daac5d78c`, marker `V11_94_KNEE_SKIRT_SOFT_PORTRAIT`. The native model retains all **327 editable meshes / 1,755,616 triangles** and unchanged UV/index arrays. All **309** previous runtime/patch sources, **66** previous packaged assets and **117** companion meshes remain exact. Targeted validation and release evidence: [KNEE_SKIRT_SOFT_PORTRAIT_V11_94.md](projects/swrlz-forge-moba/reports/KNEE_SKIRT_SOFT_PORTRAIT_V11_94.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md), with a separate final deployment request after source publication; owner-device visual acceptance follows.

## §E v11.93 · Smooth anatomy, visible hair piñatas and fitted coverage (2026-10-23)

Both original hair-attached piñatas are visible in the normal opening/body view, with their original braid grips and sockets. Detail views retain the attached companions; the full-body camera fits their combined bounds. Eyes now rise clearly from lower corners near the nose to higher outer corners, with shallow round pupils and fitted lash wings. The face, cheeks, jaw and rounded chin use a continuous smooth skin contour. Exposed shoulder/arm muscles blend smoothly; thigh, knee, calf and ankle profiles remove the abrupt calf shoulder. A new Leg detail view makes that contour inspectable.

Compact hair locks leave the piñatas as the upper silhouette. More angular overlapping dress panels retain the longer festival tailoring. The existing under-skirt is replaced with fitted opaque shorts, and armor/cuff linings follow the actual finished skin to prevent poke-through and pelvis exposure. Saved originals, previous scenes, all piñata meshes and native socket data remain preserved. Release **125 patches/66 assets/6,477,235 HTML bytes**, SHA-256 `caad492d5e7ee95808c36102b47b24fcff816c340f242f9db1fc5d24a4316cf6`, marker `V11_93_SMOOTH_ANATOMY_PINATAS`. Source/editor/coverage/native-export checks passed; the separate final deployment request follows source publication. Source, editor, coverage and export evidence belongs to [SMOOTH_ANATOMY_PINATAS_V11_93.md](projects/swrlz-forge-moba/reports/SMOOTH_ANATOMY_PINATAS_V11_93.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md); local source completion does not claim production or owner-device acceptance.

## §E v11.92 · Reference face, swept hair and longer festival dress (2026-10-23)

The female Model Atelier starter follows the owner's festival references with amber almond eyes, finer arched brows, softer cheeks and a small rounded chin. The cyan/coral hair uses overlapping swept bangs, sculpted layers and cheek-framing locks. The layered teal, ivory and pale-cyan dress extends farther down; its yellow pointed tail reaches toward the knee. Native pleats, raised brocade, running stitches, pastel hem ornaments and a fine gold fringe add editable detail.

The connected skin mesh, original companions, 4K color/normal materials, native material editing/Undo, JSON save/import and textured GLB stay supported. The saved 283-part original and complete v11.91 scene remain packaged byte-exact. Release **124 patches / 65 assets**, **6,442,424 HTML bytes**, SHA-256 `eba0e3000950a95053dc7000bf9387d89e6fefa81e7d11cacdd722f765ddf6c5`, marker `V11_92_FESTIVAL_REFERENCE`. Local native/editor/save/export checks passed; canonical publication follows the separate final deployment request. This changes the existing authoring starter; it does not add skeletal rigging. Release details and validation: [FESTIVAL_REFERENCE_V11_92.md](projects/swrlz-forge-moba/reports/FESTIVAL_REFERENCE_V11_92.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md); owner-device visual acceptance follows the dedicated release.

## §E v11.91 · Saved Festival Girl and organic anime sculpt (2026-10-23)

The previous **283-part girl starter is preserved** as **Saved Festival Girl · v11.90** (`?project=festival-girl-saved`). The main Model Atelier card now opens **Prism · Organic Anime Girl** (`?project=organic-anime-girl`). Her complete skin is one closed, connected mesh from scalp and ears through the neck, torso, arms, ten fingers, legs and feet: **254,588 vertices / 509,172 triangles**. A more inward-tapering jaw ends in a narrow, rounded chin; shaped cheeks, orbital wells, a refined nose, fitted amber eyes tilted upward six degrees at the outer corners, and lips, hands with nail plates, knees, rear calves and Achilles transitions replace the old separate primitive anatomy.

The full sculpt has **353 editable topology meshes / 1,634,372 triangles**, including the asymmetric festival outfit, original paper-ferret companions and bunny. **72 tapered 3D hair filaments**, modeled stitches, knuckle folds and fitted closed sleeve/yoke shells add geometry detail. Dedicated **4096×4096 color and normal maps** provide skin, hair flow, weave, embroidery, leather, metal and radial iris detail. Body, face, hand and full-character views support close inspection; companion isolation changes the viewport only. Native material editing/Undo, JSON save/import and textured GLB retain the complete model. Detailed native import supports **256 MB**, and a part supports **300,000 vertices / 600,000 triangles**. This is a detailed authoring sculpt; skeletal weight painting has not been added.

Release **123 patches / 64 assets**, HTML **6,421,818 bytes**, SHA-256 `ba0105f62f2e7451d4e78148cae425f4ce5e3684093fc3954d3c1f0e1105b934`, marker `V11_91_ORGANIC_ANIME_GIRL`. All **294** prior runtime/patch sources and **60** prior packaged assets preserve exact bytes. Sheep Tag retains the v11.90 collision, controls and optimized game models. See [targeted verification](projects/swrlz-forge-moba/reports/ORGANIC_ANIME_GIRL_V11_91.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.90 · Solid house blockers, furred Astra and match performance (2026-10-23)

Houses stop sheep on contact. Holding the joystick first walks up to the blocker, then follows a cached, collision-checked route around it; releasing stops immediately. The previous nearest-side/lane-center pulling and construction ejection are retired. Placing a structure over its builder is rejected without moving the sheep or spending gold. Real narrow lanes, rotated houses, unit traffic and automatic ramp/walkway traversal retain native swept collision.

Astra now has flowing shoulder/ribcage/waist contours, **one connected skull-and-ear mesh**, inset velvet pinnae and **1,100 closed curved 3D fur locks** on its body, chest and limbs. The high-resolution wolf starter has **96 editable parts / 639,772 rendered triangles**, with all **37 original courier gear/comet-tail parts byte-exact** and the original **4096×4096 color and normal images**. Native rebuild, edit/Undo, JSON save/reload and textured GLB remain available; detailed native import supports 128 MB.

Sheep Tag uses a separate optimized copy: **69,471 triangles / 29 draw meshes per wolf**, compared with **274,980 / 106** previously. Compatible meshes are merged within each independently animated head/tail/leg joint, sharing cached geometry and materials. Broad-phase collision rejects distant houses before identical narrow-phase samples; footprints cache per navigation revision. Held-stick routes avoid repeated whole-map grid searches. On phones, full-rate run recording uses **10 Hz world snapshots**, preserving command/event captures and explicitly selected slower cadences. These changes target CPU, GPU and recording overhead; owner-device FPS still needs hands-on acceptance. Clover, compact corner controls, the 320×320 m map and seven-minute rounds remain.

Release **122 patches / 60 assets**, HTML **6,390,662 bytes**, SHA-256 `c76e61f6c4b8457ce1f49d3781c8aa0710d7e44adaf7176d17744fdbda5c663a`, marker `V11_90_SOLID_BLOCKERS_FURRED_ASTRA`. All **290** previous runtime/patch files and **58** previous assets preserve exact bytes. See [targeted validation](projects/swrlz-forge-moba/reports/SOLID_BLOCKERS_FURRED_ASTRA_V11_90.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.89 · Living Astra, Clover flock and compact corner controls (2026-10-23)

**Astra's full anatomy pass** replaces separate tube-like legs/toe pieces with four welded anatomical limb/paw meshes, including elbows, wrists, hocks, tendons and four toes per paw. The seated torso has shaped shoulders, ribs, pelvis and tucked belly; the ivory chest now tapers naturally and fits beneath the original harness. The face has orbital wells, a defined brow stop, tapered muzzle/lower jaw, canine pupils and nostrils. Closed cupped pinnae and curved fur surfaces replace the remaining biological primitive parts. All **24 original gear parts and 13 comet-tail/stardust parts** remain byte-exact. The native model contains **92 editable meshes / 547,676 rendered triangles**, retaining the original **4K color/normal atlases**. It remains rebuildable with the editor's organic volume/sweep tools and supports material editing, Undo, native JSON and textured GLB.

**Clover replaces the sheep in Sheep Tag**, including all eight starter sheep and reconstructed/spawned `st-sheep` actors. It uses the same 31 source parts, fleece/face/ears/hooves, native atlas bindings and shared **4096×4096** images as the new independent sheep model. A game copy made with Model Atelier's native mesh reducer uses **33,087 triangles**, while the original **275,872-triangle** authoring starter remains unchanged. Cached geometry/materials are shared across independently animated head, tail and four leg joints. Fleece width fits within the existing sheep collision diameter; routes, capture/wisps, construction and timer retain native logic.

**Controls corrected to the owner's screenshot:** at 926 px portrait width, the joystick and building/skill diameters are about **45% of v11.88**, with the joystick anchored **18 px from the left / 22 px from the bottom**. Separate compact right-side arcs retain spacing, readable labels and safe margins. Narrow screens keep a minimum 44 px ability target and 50 px building target. Landscape moves auxiliary actions beside the joystick to clear the minimap.

Release **121 patches / 58 assets**, HTML **4,557,192 bytes**, SHA-256 `a9f6b48036c852be5a75150f18ebc9e31633c43acaa28c3b08a79b1d67506ed0`, marker `V11_89_LIVING_ASTRA_CLOVER`. All **285** prior runtime/patch sources and **56** previous assets preserve exact bytes. See [targeted validation and anatomy references](projects/swrlz-forge-moba/reports/LIVING_ASTRA_CLOVER_V11_89.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.88 · Roomier passages, reachable controls and original Astra (2026-10-23)

Sheep prioritize alignment through nearby usable house lanes before steering around an outside corner. Short joystick targets refresh immediately, so previous corner routes cannot keep a sheep trapped. Existing 0.60 m lanes remain usable; new deliberate house-lane snapping leaves **0.75 m**, with native footprint, collision and traffic checks shared by preview and construction.

The joystick moves inward/up and scales to **65% of portrait viewport width**. Building buttons use **21%**, the main house **22%**, and abilities **18%**, with two separated arcs. At the 926 px screenshot width that means roughly **194–204 px building buttons**, about three times the previous size. Phone/landscape sizing and short-screen minimap clearance adapt to the available viewport.

The wolf starter again opens **Astra · Comet Courier**, retaining the original blue/ivory design, amber eyes, tall ears, cape, harness, satchel, compass, scroll, lantern and giant curled comet tail. All **37 original gear/tail parts** remain byte-exact. Three native welded anatomical surfaces add **134,348 triangles** across the torso/shoulders/haunches, skull/jaw and continuous muzzle; the original **4K color and normal maps** remain. Clover sheep stays available as its independent starter. Detailed native editing, material Undo, save/import and textured GLB export remain supported.

Release **120 patches / 56 assets**, HTML **3,371,397 bytes**, SHA-256 `6d4ce7a4f95c2c90fb988d99867ee240c7a505df13b43c7be4b2038f506e4c2e`, marker `V11_88_PASSAGES_CONTROLS_ORIGINAL_WOLF`. All **281** preceding runtime/patch sources and **55** assets preserve exact bytes. See [targeted validation](projects/swrlz-forge-moba/reports/PASSAGES_CONTROLS_ASTRA_V11_88.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.87 · Organic sheep and wolf model starters (2026-10-22)

**Clover · Meadow Sheep** is a new independent Model Atelier starter. **Fen · Wildwood Wolf** replaces the wolf model starter entry and the earlier `comet-courier` shortcut. The wolf is a natural quadruped with a fused ribcage/shoulder/neck/skull/muzzle surface, a tucked waist, bent hocks, four-toed paws, short alert ears and a low brush tail. The sheep has continuous fleece over shoulders/barrel/haunches, a tapered bare muzzle, folded pinnae, horizontal pupils, lower-leg tendons and split hooves. Visible parts are editable indexed organic meshes; there are no sphere, box, cylinder or cone model parts.

The native organic volume tool blends anatomy fields into a connected, welded surface. Model Atelier exposes `loadAnimal(species, {force, rebuild})` to rebuild with that tool, alongside the standard component, sculpt, group, undo, material and export controls. Both starters use a shared **4096×4096 color atlas and matching 4096×4096 normal map**. Native model import supports 64 MB detailed saves and meshes up to 65,536 vertices / 120,000 triangles per part; high detail remains authored data. Textured GLB export embeds the proper atlas, including mixed original/animal materials. Studio view opens with a clear silhouette and an Edit model button. Saved project payloads are compressed losslessly in `payload/organic-animals`; packaging emits the portable native JSON scenes.

Release **119 patches / 55 assets**, HTML **3,359,239 bytes**, SHA-256 `c2dda3de1cb7bf262e347a47c9dfde2f9c4af267ed1124fee068a804fb6cda40`, marker `V11_87_ORGANIC_ANIMAL_STARTERS`. All **277** previous runtime/patch sources and **51** assets preserve exact bytes. Sheep Tag retains v11.86 nearest-side house steering, 7-minute matches, large controls and the 320×320 m map. These model projects are independent authoring starters. See [targeted validation](projects/swrlz-forge-moba/reports/ORGANIC_ANIMALS_V11_87.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.86 · Sheep steer around houses (2026-10-22)

Holding the joystick into a house now steers a living sheep toward the **nearest clear side/corner**, then continues in the held direction. A blocked side falls back to the other clear side. Fully blocked exits stop safely. This uses the native swept movement and analog speed; it never relocates a sheep through a structure. Rotated houses, other creatures, narrow sheep-only gaps, joystick reversal and release are checked. Wolves, wisps and automatic ramp/deck movement keep their existing controls.

Release **118 patches / 51 assets**, HTML **3,340,927 bytes**, SHA-256 `01b695c06bc5636b762d87914d76e2511224345add0e80c93ce6a1e6f04eba0b`, marker `V11_86_SHEEP_HOUSE_SLIDE`. All **275** previous runtime/patch sources and **51** assets preserve exact bytes. The 320×320 m map, 4K textures, enlarged controls, 7-minute timer and versioned update history remain available. See [targeted validation](projects/swrlz-forge-moba/reports/SHEEP_HOUSE_SLIDE_V11_86.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.85 · Bigger controls and seven-minute matches (2026-10-22)

The portrait joystick grows from **156 to 224 px** and moves diagonally **up and right**. Compact portrait uses 192 px; landscape uses 208 px, or 176 px on a short phone. The knob and direction mark grow with it. Right-side buildings and abilities grow by roughly 12–23% in the main layouts, with adaptive compact sizes and the two separated arcs retained. Larger labels wrap within their circles. Landscape score, utility buttons and feedback shift to keep the enlarged controls accessible.

The default match lasts **7 minutes (420 seconds)**. The portable starter carries that duration, and saved maps using the previous 20-minute default migrate to seven minutes. Other explicitly tuned durations remain editable. The native countdown, head start, win conditions, movement, ramps and placement use their existing game clock and rules. The editor’s versioned update panel automatically lists this release.

Release **117 patches / 51 assets**, HTML **3,338,122 bytes**, SHA-256 `76ea088b19a441ed0e846ffdd4a02197eb131b45a3ea55255eeb032f7c5d13f4`, marker `V11_85_LARGE_CONTROLS_SEVEN_MINUTES`. All **272** earlier runtime/patch sources and **50** preceding assets preserve exact bytes; the additional asset is the seven-minute starter scene. See [targeted validation](projects/swrlz-forge-moba/reports/SHEEP_LARGE_CONTROLS_V11_85.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.84 · Reliable building, connected walkways and update history (2026-10-22)

- **Building recovery:** one placement pointer owner handles icon and meadow drags. Rejected/cancelled drops release capture, remove the ghost and clear the selected tool. Unaffordable buttons show a cost message without entering placement, so the free house remains available.
- **Automatic ramps:** joystick steering ascends and descends completed ramps directly, follows connected decks and stops at unsupported edges. The ground/upper-route and descent toggles are hidden. Species radii, traffic, wolf ramp permissions, capture and hunt-release restrictions remain native.
- **Connected extensions:** walkways and exit ramps snap to existing deck/ramp high edges and rotate toward the selected side. Straight extensions and side turns share physical seams and the native route graph. Sheep already on a connected deck can construct a nearby extension; normal costs, occupancy, sanctuary and completion rules still apply. Player-built side connections open a gap in the parent rail when complete.
- **Touch controls:** abilities occupy an inner arc beside the outer building arc. A larger joystick and separated compact layouts keep targets at least 44 px. Touch aim rises **128–180 px** above the finger, with top-readout clamping.
- **Larger map:** the new starter is **320 × 320 m**, 25% wider and 56.25% more area than the preceding 256 m meadow. Authored scenery, roads and the 4K ground scale with the layout; previous scene files remain unchanged.
- **Editor updates:** an automatic latest-update panel includes **107 previous versions**, grouping every previous patch. Its checkbox hides only this exact version; the next release appears again. The editor footer’s **Updates** button reopens it, and unchecking restores the popup. Future source versions derive notes and history automatically from the manifest and new patch summaries.

Release **116 patches / 50 assets**, HTML **3,333,468 bytes**, SHA-256 `82ae2d5fdac77f9a63cb4375aae2d93939c8cdf3338395f7120995f62d2bc411`, marker `V11_84_BUILD_RECOVERY_WALKWAYS`. All **264** preceding runtime/patch files and **49** prior assets preserve exact bytes. The additional asset is the larger native scene. See [targeted implementation and evidence](projects/swrlz-forge-moba/reports/SHEEP_RECOVERY_WALKWAYS_V11_84.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.83 · Drag houses to build, joystick movement and smooth fog (2026-10-22)

Manual movement now uses the **left joystick**, including the desktop pointer layout; ground clicks/taps no longer issue move orders. Drag a building skill icon onto the meadow, aim with the house **above your finger**, and release on a green footprint to order construction. A tap can also arm the building tool for a subsequent ground drag. Visible house/unit selection, wolf attack, rescue, camera pan and minimap camera navigation remain available. Construction retains its native approach, collision, footprint, cost and completion rules. Accepting a build releases held joystick ownership so the next frame cannot overwrite the construction order. Steering again deliberately replaces that order. Blocked/cancelled drops do not charge gold or build. The preview rechecks affordability and occupancy while held still, avoiding a stale red “Need gold” message after income arrives.

Fog uses **soft circular vision edges**, linear sampling and a 4× display mask (512×512 on the 256 m meadow), updated at most ten times per game second. The minimap shares that smooth display. Logical visibility, explored cells, enemy filtering, bot knowledge and pre-hunt restrictions remain native. All **262** preceding runtime/patch files and **49** assets retain exact bytes, including the 4K artwork.

Release: **115 patches / 49 assets**, HTML **3,288,058 bytes**, SHA-256 `41b34b31203777afffc242d42a83b32157e61442760fa9549960600ed27d7962`, marker `V11_83_DRAG_BUILD_SOFT_FOG`. See [targeted implementation and validation](projects/swrlz-forge-moba/reports/SHEEP_DRAG_V11_83.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.82 · Mobile building skills, joystick and clear touch placement (2026-10-22)

Sheep Tag now uses **round illustrated building skill buttons at the bottom right** on phones/tablets: house, income house, fortified house, wall and ramp. The existing native buttons retain their costs, availability, active state and build commands. A **left movement joystick** steers the actual sheep/wolf through native swept collisions and traffic, supports proportional speed, and stops on release/cancel/pause/blur. Captured wisps keep their slow crawl/leash; wolves remain immobile before release. The minimap moves to the top left. A compact **••• unit-actions drawer** keeps camera, upgrades, selling and archive controls accessible, while the editor footer returns after Stop. Desktop controls retain their original layout.

Touch building aim is **72–112 screen pixels above the finger**, with a dotted guide to the exact snapped footprint. Preview and release use the same native build target. Separate pointer owners let one thumb steer while another aims; two simultaneous placement fingers still cancel safely. Portrait, landscape and compact screen layouts keep touch controls at least 44 px. Camera following and normal frame updates keep the ghost aligned; resizing cancels held gestures.

Release **114 patches / 49 assets**, HTML **3,279,865 bytes**, SHA-256 `e0bfe63ddae1f5430cf0f80f7f17bd9745a5d0147d68fb96afbb441353d9b6c2`, marker `V11_82_TOUCH_BUILD_SKILLS`. All **259** preceding runtime/patch sources and all **49** bundled assets retain exact bytes, including the Astra and ground 4K textures. See [implementation and targeted evidence](projects/swrlz-forge-moba/reports/SHEEP_TOUCH_V11_82.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md): cohesive source, separate final deployment request and exact hosted-package confirmation.

## §E v11.81 · Building clearance, protected sanctuary and hidden hunters (2026-10-22)

House foundations and outlines now reach the real blocking footprint. Nearby face-to-face gaps show their measured width and a colored label: **red BLOCKED**, **cyan SHEEP ONLY**, or **gold BOTH**. Classification uses the native swept collision checks, surrounding visible structures and actual species radii. Exact lane entry points let sheep use fitting narrow passages even between navigation-grid lines. Default sheep need **0.54 m** and wolves **1.80 m**. The gold sanctuary boundary marks a **22 m no-build radius** on the default 256 m map; the whole structure must fit outside it. Both player placement and AI construction use this rule. Bots choose reachable outward bases instead of falling back to their central spawn.

Wolves are hidden and nonphysical during the countdown, with no perception, target memory, minimap markers or pre-release scent information. A waiting wolf role has no sheep/building vision. After release, bot hunting requires actual sightings; lost sheep leave only their last observed position. Default sheep speed rises from **5.4 to 6 m/s** and Astra hunters are **15.4% larger**, with collision radius increasing from **0.78 to 0.90 m**. The 106-mesh/274,980-triangle hunter and original 4K atlases remain. Captured-wisp crawl/leash/rescue behavior is retained.

Release **113 patches / 49 assets**, HTML **3,258,318 bytes**, SHA-256 `9fb46459d3ca870f766ff7c90c18a1649ffbfc68352da25c493bc5ffe284186c`, marker `V11_81_SHEEP_CLEARANCE`. All **257** previous patch/runtime sources and **49** assets preserve exact bytes. Details and targeted validation are in [the release report](projects/swrlz-forge-moba/reports/SHEEP_CLARITY_V11_81.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md): cohesive source commit, separate final deploy request, terminal production success and exact hosted-source/asset confirmation.

## §E v11.80 · Vast Wildwood, central starts and captive wisps (2026-10-22)

The default map is now **256 × 256 m**, **4× the previous playable area**. All eight sheep start **9.5 m from the central respawn sanctuary**, rather than around the outer map. The existing four-region roads/ground/minimap and 4K Astra hunters remain. Fine **0.15 m** pathfinding now uses direct clear trips and cached local windows for most obstructed routes in large maps, with an unrestricted fallback for longer detours.

Captured wisps crawl at **0.35 m/s**. They may drift **2.5 m beyond each side of the pen**; crossing that leash teleports the still-captured wisp to its own capture spot and clears its movement/rescue progress. Reaching the leash never revives a sheep. The existing other-living-sheep rescue/hold/protection behavior remains the only revival path. Native move controls and help text describe this behavior.

Release **112 patches / 49 assets**, HTML **3,243,526 bytes**, SHA-256 `a4b58b9da3991fdd10fee42c4fd18648c65a79932b0af69ceea1a117ce5f151d`, marker `V11_80_VAST_WILDWOOD_WISPS`. The new native scene has 196 editable actors, eight central sheep, three Astra hunters and nine map layers. All 255 preceding patch/runtime sources and 48 previous assets retain exact bytes. Targeted CPU/browser checks and publication evidence are recorded in [the release report](projects/swrlz-forge-moba/reports/VAST_WISPS_V11_80.md). Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and terminal production run under current [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.79 · Moonbell Wildwood — larger Sheep Tag map (2026-10-22)

The default Sheep Tag starter is now **Moonbell Wildwood**, **128 × 128 m** versus the previous 80 × 80 m (**2.56× the area**). Four color-separated woodland regions — Pinewatch, Moonflower, Amberglade and Willowmere — surround open building glades, an octagonal road loop, cardinal/diagonal roads, four merchant plazas, four ponds and a central sanctuary with stone markers. Four genuine narrow stone passages admit sheep while hunters detour. The terrain and fog-respecting minimap share original **4096 × 4096 ground artwork**. There are **176 individually editable native actors** in nine map layers, retaining eight sheep and three 4K Astra hunters. Match timing, movement/combat rules and optional archive settings remain intact; the previous 80 m map is preserved as a separate source and remains loadable.

Release **111 patches / 48 assets**, HTML **3,222,398 bytes**, SHA-256 `f2d2c22aa4620f76407494767e27a4227c3d178af3f8a52f7fc736c6eb28e9ec`, marker `V11_79_MOONBELL_WILDWOOD`. All 253 preceding runtime/patch sources and 46 earlier assets retain exact bytes. Targeted desktop/phone-layout checks cover start validity, full map framing, all spawn/outer-road connectivity, four species-sized passages, native/portable save/load, generated floor scale, movement/construction outside the old boundary, terrain minimap and previous-map compatibility. Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and its terminal production receipt. See [map design and evidence](projects/swrlz-forge-moba/reports/SHEEP_WILDWOOD_V11_79.md); delivery follows current [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.78 · Astra hunters in Sheep Tag (2026-10-22)

Sheep Tag's `st-wolf` prefab now renders the complete **Astra · Comet Courier** model, with all 106 native meshes and the original 4096 × 4096 color/normal atlases. The three canonical hunters, newly spawned hunters and wolves reconstructed from older native project saves all use the same visual. Independent head, tail and four leg pivots connect the saved model to the existing walk and attack animations; geometry/materials and texture images are reused across instances. Logical wolf roles, IDs, names, teams, navigation/collision radii, combat, economy and map data are preserved. The independent editable Astra project remains available.

Release **110 patches / 46 assets**, HTML **3,152,424 bytes**, SHA-256 `234ddf6065f89438a3cabbcd9e3521d82fb08245830525131e3976d4f86b9ad4`, marker `V11_78_SHEEP_TAG_COURIER`. All 250 preceding runtime/patch files and 46 bundled assets are byte-preserved. Targeted local desktop/phone-layout checks cover loaded 4K maps, native spawn/save/reload, movement/four-leg gait, building attacks/head animation, sheep tagging and Stop/restart restoration. Deployment status and source commit resolve through the final separate `DEPLOY_REQUEST.json` and its terminal production run; owner device acceptance follows publication. See [integration evidence](projects/swrlz-forge-moba/reports/SHEEP_COURIER_V11_78.md). Delivery follows current [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.77 · Astra, Comet Courier model project (2026-10-22)

New independent **Astra · Comet Courier** project and **New Model Project** starter. A celestial fox with sculpted ears/muzzle, four articulated legs, a flowing comet tail, travelling mantle, satchel and lantern is authored through native tools. Eight material regions use original 4096 × 4096 base-color and normal atlases. Saved atlas bindings support Undo; a textured GLB embeds real mesh/UV/material data and both 4K images. Six editable assemblies organise the model.

The existing 283-part festival model, all previous runtime/patch sources and 43 original assets are preserved. Release has 109 patches / 46 assets, marker `V11_77_COMET_COURIER_MODEL_PROJECT`. Exact bytes/SHA resolve through `source-manifest.json`; source/deploy commit and live status resolve through the final separate `DEPLOY_REQUEST.json` commit and terminal production receipt. Current delivery authority is `RELEASE_PROCESS.md` (§§§); targeted model checks precede direct-main source publication and the final dedicated deployment trigger. [Design and authoring](reports/COMET_COURIER_V11_77.md).

## 2026-10-21 · §E v11.76 — desktop modeling drag, scale, wire vertices and zoom

Owner PC gaming-monitor photos revealed four specific problems: gizmo drag would stop before available mouse/screen travel was exhausted, large piñata-related scaling appeared only after Undo triggered a procedural rebuild, dense whole-character wireframe washed out into nearly solid white rather than exposing vertex points, and scroll zoom had a hard minimum too far from the character. The v11.76 repair keeps §E's original **283 native Model Atelier parts, 43 original assets, existing object/assembly/component editors, geometry, history and full source lineage**.

- Desktop pointer-lock acquisition on a real mouse gizmo drag accumulates relative movement while the mouse cursor is locked; falling back to native pointer events when pointer lock is unavailable. Release or Esc exits lock. A native validity-bounded transform replaces the arbitrary *3× per-drag scale limit*. Preview amounts stop at safe mesh position/scale bounds rather than moving into invalid territory and reverting on release. Touch behavior remains intact. Real owner mouse acceptance remains outstanding.
- Scale commits trigger **one** post-commit procedural model redraw (not rebuild on every drag frame), ensuring native procedural hair and piñata structures update visibly without requiring an Undo event. The original Undo/Redo record is still the authority and correctly reverses and reapplies the scale.
- Global wireframe now draws muted low-opacity lines for all nonselected objects and a cyan outline for the selected object; users can control **Focus selected wire** and **Vertex points** within *Display, wire & interior*. Up to 2,000 actual sampled mesh vertices are drawn as contrasting yellow 5px points for the selected part. This is viewport-only and does **not** lower mesh topology or change materials in saved project. Open display controls are layered above movable gizmo panels, fixing an additional desktop click interception discovered during testing.
- The active mouse-wheel zoom, +/- buttons and touch pinch reach **0.16 model units** (previous min 1.2 framed / other historical higher floors), with close-range near clipping adjusted to **0.018**; preset camera views and original geometry are preserved.

[Real Chromium v11.76 test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39674744767) passed with 283 original mesh count; selected native Rear dyed lock scaled at a valid **9×** candidate, immediate scene transform update, Undo/Redo; **1,677** shown vertex markers on a wireframe mesh, contrasting selected/other wire opacity and toggle; 0.16 camera minimum with 0.018 near plane. No uncaught browser errors. Desktop pointer-lock ergonomics and piñata-specific real-device review remain for the owner. **108 ordered patches**, **3,091,496-byte** HTML, SHA-256 `ae0764bcdaef131a8d404b43ca20b4a3b6ed9bad66897709919b6f3f1bccf1ef`, marker `V11_76_DESKTOP_MODELING_REPAIR`. Maintain §§§ source → separate deployment request → exact hosted artifact verification.

## 2026-10-21 · §E v11.75 — Component Edit Foundations

Owner-approved mobile-first geometry editing update. Model Atelier adds **Mesh / Vertex / Edge / Face** mode buttons and keeps whole-object/group editing separate from component editing. Tappable vertex points, edge lines and tinted face selections; tap + independent component **Multi**, **Box** and **Lasso** tools; component count, Clear, and axis Move/Rotate/Scale with existing Fine↔Fast sensitivity and ± nudges around the selected component center. Transforms edit actual indexed positions of the selected native mesh with lightweight live WebGL preview. Edit offsets are saved using the preexisting bounded sculptVertexEdits project schema, retain Undo/Redo, native model JSON and OBJ geometry output. Weld-equivalent duplicated vertex slots move together. Editing is deliberately limited to one chosen mesh at a time and to stable (non-active-refinement) vertex indices; large selections obey existing 256-slot edit chunks, 64 history record and ±0.5 local-unit validation budgets. With a scaled character head, live drag now clamps **before preview** so no visually moved-but-invalid commit occurs. Performance protection raycasts the touched triangle for vertex/edge selection, caches topology per rendered geometry, samples dense overlays and avoids full mesh normal recomputation on each drag frame. The character's original **283 parts, individual materials**, old 2.5D/3D tools, v11.74 mesh groups and all **43 packaged assets** are retained.

[Real Chromium v11.75 component test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39664122664) **passed**: native indexed edit persisted, Undo/Redo restored it, both edge and face selection/nudges, component multiselect, box/lasso, live pointer drag changing geometry *while held* and saving on release, 390px phone controls with 44px targets, and no browser errors. Release seal: **107 ordered patches**, **3,083,471 bytes**, SHA-256 `910e4565727243256154adb8707bf0eaff9021338860b5b34146d04cc02474d1`, marker `V11_75_COMPONENT_EDIT_FOUNDATIONS`. Owner Android acceptance remains pending. Future extrude/inset/bevel/advanced loop tools remain deliberately out of this foundation release.

## 2026-10-21 · §E v11.74 — non-destructive mesh assemblies and mobile Multi-Select

Owner requested a mobile-friendly tap-to-toggle multi-selection mode and a reversible mesh group hierarchy, distinct from the existing destructive **Join selected** operation. v11.74 adds a permanent viewport Multi-Select control, selection counter, Select first 32, Clear and Done. With Multi on, tap meshes to add/remove them without Shift/Ctrl and tapping empty space retains the selection. The contextual Assemblies disclosure offers **Group selected**, **Edit group / Edit child**, **Update members**, **Remove child**, **Ungroup**, and an assembly picker. A flat assembly links the original part IDs using modelAtelier.meshGroups; meshes retain independent kind, topology, materials, color and source transforms, and group transforms reuse the existing smooth Move/Rotate/Scale gizmo around the common pivot. No geometry is flattened and the separately labeled native Join remains available. Group membership survives native project save and model JSON export/import; the preexisting whole-model Undo history, which also stores other original animation/socket and pose data, now captures membership edits without replacing those structures. One mesh belongs to at most one flat group, up to 32 parts/group, with up to 96 groups.

[Real Chromium full-workflow regression](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39631075995) **passed**: tap toggles and empty-tap retention, grouped selection, linked translations, independent child editing, membership updates, Undo/Redo for group creation and transforms, JSON round-trip, ungroup/Undo, and a 390px viewport with ~100×44px Multi button. It checked that all **283** original character parts, their materials and initial transforms remained identical after group creation. Sealed source **v11.74**, **106 ordered patches**, **3,056,562 HTML bytes**, SHA-256 `25ca54b95366258f3bc76912f90299aca42667c8f1938ea37a0a789da4399cc6`, marker `V11_74_NONDESTRUCTIVE_MESH_GROUPS`. The original 43 packaged assets remain unchanged. On-device owner testing remains required after deployment.

## 2026-10-21 · §E v11.73 — instant transform mode redraw and mobile-friendly rotation ruler grabs

Owner on Android observed Move/Rotate/Scale buttons did not visibly change handles until orbiting camera, plus arc lines were too small to grab. Source showed the contextual popup rebuilt the gizmo on button clicks but did not synchronously draw WebGL; curved rotation picking was limited to small slider beads. v11.73 explicitly paints a WebGL frame after mode/axis changes, without touching the camera, and adds thicker axis-colored 3D arc tubes, visibly larger slider beads, and screen-pixel curve hit testing for any position along a rotation arc. The user-chosen axis has precedence when projected rings overlap. Selecting a curve segment starts a native live rotation and moves the bead with the finger from the grabbed arc point. Native Undo/Redo, snap options, previous smooth drag behavior, geometry and materials remain unchanged.

The [real Chromium regression](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39617462205) passed after fixing a genuine X/Z projected-ring ambiguity found in the initial run. It verified immediate WebGL painting on each tool switch without camera movement, exactly one gizmo root, 3 thick Rotate arcs versus 0 for Move/Scale, off-bead Z-axis live rotation, and touch tolerance at 390px viewport. Release source **v11.73**, **105 ordered patches**, **3,040,330 HTML bytes**, SHA-256 `57998cfe4d71530e4f82fc0b0f0ec18c4bc858bc5f8f35d2d3ee5cdca7c56fe8`, marker `V11_73_INSTANT_GIZMO_ROTATION_TOUCH`. Preserve the canonical 283-part reference model and all 43 original assets. Owner's physical Android touch acceptance follows hosting verification.

## 2026-10-21 · §E v11.72 — rotation ruler alignment and accurate touch mapping

Owner Android screenshots of v11.71 showed rotation bands disproportionately large relative to the selected anatomical head, with overlapping axes and questionable rotation feel. Root cause: the original arc radius was camera-distance based, pointer-angle inference was an affine 2D ellipse approximation instead of an exact 3D angle, and the popup showed the previous gesture delta without labeling it as such. In v11.72 the arc radius is measured from the selected mesh's actual world-space bounding sphere with a minimum screen-size allowance for phone usability; the ring's plane is intersected with the camera ray to calculate angular movement, falling back to a tangent when the ring is seen edge-on. Each axis has its own colored ticks/bead; the selected axis is emphasized, inactive rings dim, and handle selection uses pixel distance instead of an oversized world-space collision sphere. The readout now labels live **Δ** and **Last Δ** separately rather than pretending to show absolute Euler orientation.

The [focused real Chromium test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39609712872) passed for X/Y/Z on the actual anatomical head, measured the head ring radius **0.573 vs 0.952** world units, confirmed the gizmo is centered, tested live mesh rotation and bead movement before pointer release for all three axes, verified saved changes, and checked Move/Scale remain distinct. Preserve the 283-part original model, 43 historical assets, native Undo/Redo, per-mode Fine/Fast and 5°/15° snapping. The rotation amount is a world-axis delta and can differ from individual Euler components after multiple-axis rotations; no mesh hierarchy or skeleton grouping was changed. Sealed v11.72: **104 patches**, **3,036,186 bytes**, SHA-256 `9b0d791a66bce68a28f21911d2de4bad703d9d676edd2076622c9b4060e0cae8`, marker `V11_72_ROTATION_ARC_ALIGNMENT`. Physical Android UX pending owner acceptance.

## 2026-10-21 · §E v11.71 — true curved 3-axis rotation rulers

Owner provided a screenshot reference showing overlapping colored curved rotation gizmo rings with ticked rulers and sliding points. v11.71 replaces the straight 3-axis handles *only in Rotate mode* with 3D X/Y/Z arcs in red/green/blue, 15° graduations and emphasized 30° ticks, plus large invisible touch targets on the draggable bead for each ring. A drag maps pointer position onto the corresponding world-space arc, uses the native XYZ quaternion transform path, and displays the mesh rotation and bead movement live before release; the per-mode Fine/Fast transform slider remains active. The nearby floating popup shows the current angle and optional Off/5°/15° snapping, saved as a local UI preference rather than model state. Move/Scale and source geometry remain untouched. The native Undo/Redo transaction persists transform edits.

[Focused real Chromium rotation test passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39605565651), including three visible rotation arcs, 12 live pointer updates/rendered frames, ~39.4° Z-axis rotation *before pointer release*, saved rotation, optional snap controls, and preserved Move/Scale. Original 283-part canonical model and 43 packaged assets remain preserved. Sealed source: **v11.71**, **103 patches**, **3,029,622 HTML bytes**, SHA-256 `44ae1de39f81874ccf2a06cfae8e067b06633053656283562523579850034c6b`, marker `V11_71_ARC_ROTATION_RULER`. Mobile touch usability remains subject to owner test after hosted deployment.

## 2026-10-21 · §E v11.70 — Fine/Fast gizmo sensitivity and responsive top tools

Owner accepted v11.69 live drag smoothness and requested a less cluttered top viewport control area and a fine-positioning slider in the selection gizmo popup. v11.70 groups the **Render mode / Target**, camera-direction presets and center-pan control, and an expandable **Display, wire & interior** section without recreating existing controls or handlers. The selection popup now offers **Fine ↔ Fast** sensitivity with ⅛×, ¼×, ½×, ¾×, 1×, 1½×, 2×, 3× and 4× for each of Move, Rotate and Scale independently, retained per device, affecting both drag gestures and plus/minus nudges. This does **not** adjust geometry subdivisions: the existing Grid U/V tool remains the dedicated vertex-count feature. Existing native bounded transforms, smooth live preview, Undo/Redo and original project data are preserved. [Focused real Chromium UI and drag test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39602536277) passed, including 25px movement of ~0.180 units at 1× versus ~0.0225 units at ⅛×, saved sensitivity per mode, preserved camera buttons and 390px screen layout. An initial test failed with advanced settings open over the interaction area, and was corrected to test with the expandable panel closed during gizmo operation. 

Release seal: **v11.70**, **102 patches**, **3,019,798 HTML bytes**, SHA-256 `67a36e4efc75bf0a585463643b1e48ce70437add1b65087d9d1967df97204ca3`, marker `V11_70_PRECISION_GIZMO_TOOLBAR`. Original 283-part character and all 43 packaged assets remain unchanged. §§§: source commit directly to main, dedicated final deployment trigger, exact hosted/source audit, owner mobile acceptance.

## 2026-10-21 · §E v11.69 — proven in-browser drag feedback before pointer release

Owner reported that v11.68 mesh motion improved slightly but the selection gizmo and mesh still appeared static during touch-drag, then snapped to position on release. The v11.68 code updated Three.js transforms but repeatedly recalculated selected mesh world bounds on every pointer movement and depended on the ongoing render loop for visible paint. v11.69 uses the captured pivot and drag delta to update the existing selected part(s), native outline, and gizmo position directly without a geometry rebake or whole-model rebuild, and issues a WebGL render on active pointermove. Native Undo/Redo, full commit validation and previous selection optimizations are unchanged. A **real Chromium pointer interaction test** [passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39594806708): 9 movement events / 9 frames, selected mesh moved 0.45 units and handle followed **before pointerup**, with the saved position persisting after release. This is stronger than build-only validation; physical Android performance remains a separate owner test.

Sealed source: **v11.69**, **101 patches**, **3,012,114 bytes**, SHA-256 `6ed5ae18211945d86d2a73db45aadb173b377d656c57eeab6714105c26d8e471`, marker `V11_69_DRAG_PREVIEW_RENDER`; original 283-part starter and 43 packaged assets retained. This is an additive fix and does not change any other §wyrlz projects.

## 2026-10-20 · §E v11.68 — immediate native selection and live gizmo drag

Owner tested live v11.67 and confirmed that completed transforms landed correctly but the chosen mesh and gizmo did not visibly follow the finger during drag, and selecting an object had a small delay before its bounding outline appeared. The v11.68 additive patch retains the captured transform gizmo through pointer movement, applies candidate changes directly to existing Three.js mesh objects, refreshes the native selection BoxHelper and gizmo center on each live preview, and leaves v11.67 fast commit/Undo intact. Switching selection now re-targets the existing selection BoxHelper without `renderParts()` rebuilding the 283-part model. Native geometry-edit workflows remain unchanged. This is a scoped optimization, not a model reconstruction. **100 patches; 3,010,876 HTML bytes; SHA-256 `ddd1e5e5c7e09dc6635b6c32c2170c4c5f3d08e19f816530348667abc602ba93`; marker `V11_68_LIVE_MESH_GIZMO_FEEDBACK`.** Original 283-part canonical scene and 43 historical assets remain intact. [Targeted source assembly and syntax check passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39542983666); Android motion/selection responsiveness awaits owner test after deployment.

## 2026-10-20 · §E v11.67 — mobile mesh transform performance

Owner reproduced a pause after dragging one face/head mesh in live v11.66. The previous `atelierMeshCommit()` invoked `signalEdited()` to rebuild all 283 model parts on every valid Move/Rotate/Scale commit. v11.67 now stores the validated transform in native project data, uses the existing mesh and material in Three.js, updates selected-object helpers, inspector and Undo/Redo state, and preserves JSON/OBJ. Canceled or zero-motion drags restore the live transform without replacing geometry. Actual geometry edits still use their existing rebuild path. 99 ordered patches; 3,009,500 assembled HTML bytes; SHA-256 `a2122de3a296da3319de5d861875f7c3efd4663d714b31820d4e27acf5ca8017`; marker `V11_67_MESH_TRANSFORM_PERFORMANCE`. The original 283-part starter and 43 packaged assets remain intact. [Targeted build and syntax check passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39532595474). Live deployment and owner Android responsiveness checks are separate stages.

## 2026-10-20 · §E v11.66 — owner-reported selection gizmo & mobile popup repair

From owner screenshots on a physical Android phone: an extra yellow bounding helper appeared above the model, a face/part could be moved out of view, the floating toolbar obstructed the character, and Undo/Redo were hard to find. This version **removes the duplicate transformed selection outline** (native selection outline remains); **caps each touch/drag translation at 0.45 native world units** with fine camera-distance-scaled sensitivity; places **Undo / Redo / Frame mesh** directly in the floating selection strip; and makes its title bar **draggable with normalized on-device saved position**, maintained across viewport layout/orientation. Cybernetic cyan/indigo styling was added to the popup and scoped to existing Model Atelier tool windows; other projects are not restyled.

No model-source changes. Preserve the exact original 283-part canonical character and all 43 packaged assets. One targeted build and Node syntax check passed ([Actions run 39531500631](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39531500631)); physical-device gesture/position UX is explicitly awaiting owner acceptance. Release seal: **98 ordered patches**, **3,008,188 bytes**, SHA-256 `ab960990d91641c0a03c453181710ae2a6739c247a632e238e4aa1745e16e35f`, marker `V11_66_MESH_SELECTION_UX_REPAIR`. §§§ release: direct source commit to main, final independent deployment trigger, hosted source verification, then hands-on owner testing.

## 2026-10-20 · §E v11.65 — selected-mesh gizmos, group Join and vertex grid controls

Owner-requested modeling edit: select a native mesh and a nearby contextual strip exposes **Move / Rotate / Scale**, X/Y/Z gizmo handles plus step nudges; **＋ Add mesh** selects multiple parts for shared pivot transforms, **Join selected** bakes selected meshes into one editable `topologyMesh` within the supported budget (single material, first selected). Native Undo applies. **Show vertices** invokes the existing pickable source-vertex map and point gizmo, and **Grid U/V** adjusts actual procedural rows/columns with bounded budgets: sphere/loft use the native resampler, face sheets use their existing face-sheet grid, and box/cone/cylinder gain bounded parametric subdivisions. Changes to grid density clear indexed point edits after user confirmation; original part history is preserved through Undo and JSON/OBJ. Custom topology retains its dedicated native refinement tools instead of pretending it has rectangular U/V topology. The canonical **283-part starter** and all **43 packaged assets** remain byte-preserved.

Source seal: `§wyrl§ Engine v11.65`, **97 ordered patches**, **3,000,400 bytes**, SHA-256 `a7e1514e34261d115472e6e6db68b88da8277d4e73e4e31cc19f9f99a138f38f`, marker `V11_65_SELECTION_MESH_GIZMOS`. [Single focused source build and JS syntax check passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39529266779). Release follows §§§: commit coherent source directly to `main`, separate last `DEPLOY_REQUEST.json` trigger, confirm exact hosted source and assets, then owner device testing. No unrelated starter suites required. Do not claim physical-device UX acceptance from automated syntax/build validation.

## 2026-10-20 · §E v11.64 — §§§ minimal version/deployment timing test

Owner-directed version-only increment from v11.63 to v11.64, without changing Model Atelier, game or animation behavior. New additive patch `patches/v11_64_version_smoke.py` preserves the original 283-part character scene and 43 packaged assets. The rebuilt v11.64 HTML is **2,976,568 bytes** (96 ordered patches), SHA-256 `bd818ae35f08f5648c0a38ffce4d5bae620a46df8e56291dadba0b7cc53f6282`, marker `V11_64_VERSION_SMOKE_TEST`. A single targeted GitHub measurement run [39527720786](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39527720786) computed the seal. §§§ delivery: direct source commit to `main`, separate final deployment-request commit, one dedicated HF deploy workflow, then owner device acceptance. Never label v11.64 live without a successful hosted deploy receipt.

## 2026-10-20 · §E v11.63 — §§§ minimal version/deploy smoke test

This release changes **version metadata only** (v11.62 → v11.63), with no new modeling tools or changed game/animation behavior. `patches/v11_63_version_smoke.py` preserves the 283-part canonical model. `source-manifest.json` now seals **95 ordered patches**, **2,976,568 bytes**, SHA-256 `6adbda8d53e0b11fe6e98ae59605176362e0fc2b159c558e52087e96ed1274ec`, marker `V11_63_VERSION_SMOKE_TEST`, and the same 43 assets. This small release exercises the §§§ flow: build/version/manifest → commit to `main` → separate `DEPLOY_REQUEST.json` trigger → GitHub-to-Hugging-Face deploy → owner tests. Only the deployment's successful live receipt establishes hosted status. The v11.62 candidate paragraphs below are historical and superseded by this version.

## 2026-10-20 · §E v11.62 mobile adaptive tool sheet — SEALED SOURCE CANDIDATE (NOT LIVE)

This is a **source candidate only**; the publicly hosted §wyrl§ Engine remains verified v11.61 until the v11.62 release and hosted checks complete. The 94-patch candidate is byte-sealed at **2,976,576 bytes**, SHA-256 `215240cd453031834f76e90efd4d125466b6ecb1467dfe9941f3d69b8e08b931`, marker `V11_62_MOBILE_ADAPTIVE_TOOL_SHEET`. [Independent 94-patch measurement and source-preservation proof](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39511087814). The original 283-part anatomical model and 43 bundled historical assets are preserved.

**New editor layout (after release):** Model Atelier → bottom thumb-reachable category rail → choose Lasso, Sculpt, Topology, Face etc. → contextual phone sheet with real native properties, All/Quick/Recent operation discovery, favorites, Compact/Half/Expanded size and left/right-thumb layout; return to the original native inspector with **Original inspector**. Short landscape uses split operations/settings; desktop retains the movable original workbench. Repeated **More → References → More** now restores the original inspector while native-only More still toggles hide/reopen. The six-viewport browser regression for that fix passed at [39510184874](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39510184874).

**Source-of-truth owners:** `projects/swrlz-forge-moba/source-manifest.json` (94 patches and exact seal), `patches/v11_62_mobile_adaptive.py` (governed wrapper), `patches/v11_62_mobile_adaptive_preview.py` (tested presentation), `scripts/verify_v11_62_release.py` (signed build), `scripts/measure_v11_62_release.py` (independent measurement), `.github/workflows/verify-atelier-v11-62-production.yml` (browser/geometry integration), and `.github/workflows/deploy-swrlz-forge-moba.yml` (dedicated gated publication). [Stacked source release PR #283](https://github.com/kaministrator999-ui/Swrlzkamico/pull/283) derives from [preview #278](https://github.com/kaministrator999-ui/Swrlzkamico/pull/278).

**Required acceptance before LIVE:** exact sealed build, full applicable desktop/phone and cross-workspace regression matrix, verify no 283-part/43-asset changes, merge governed candidate into main, and make the **sole LAST release mutation** to `DEPLOY_REQUEST.json`. Observe terminal engine deploy and exact served HTML/SOURCE/all 43 assets plus hosted desktop/phone native editing. Owner on-physical-device UX acceptance remains separately unverified; other §E workspaces (Anime, Story Studio, Maul, Sheep Tag) do not acquire new contextual adapters in this release. Do not use the independent AI Chat/LALM deployment path or Vercel.

## 2026-10-20 · §E v11.62 phone tool-sheet continuity — STACKED PREVIEW (NOT LIVE)

**Authority:** production is verified **v11.61**, not the older v11.60 closeout or v11.61 candidate text retained below. [Engine deployment](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39452004741), [exact live v11.61 HTML and all bundled assets](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39452462102) and [live editor browser verification](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39452462260) passed; source commit `d17aaf3fdad799956c8e6224f5a7e0e6b3de2b82`, 93 patches, 43 assets, 2,958,383 bytes, SHA-256 `cd33b05e3e27304fe9d3e753e488d46fcb844841fd06e19b8058a81516e7d01e`.

**Current continuation:** [§E v11.62 preview #278](https://github.com/kaministrator999-ui/Swrlzkamico/pull/278), base/head source `5ef0df796ba0e68afb12158fd365d18393cee88c` for the 6-viewport preview success ([Actions receipt](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39466710392)). The v11.62 layout is **preview-only**, not included in production manifest or deployed HTML. It covers the native Model Atelier tool families; other game/animation workspaces require their own adapters.

**This follow-through slice:** on an isolated branch stacked onto #278, repair the native **More → References contextual sheet → More** repeat-selection edge case that could leave both tool surfaces closed. Preserve the v11.60 dock's original click handler and native controls; add a phone regression to the v11.62 six-viewport test rather than weakening its existing assertions. Revalidate the exact candidate through the v11.62 CI. The older standalone v11.60 preview job fails its *version-pinned manifest* assertion against v11.61, not a demonstrated defect in the v11.62 mobile UI; current v11.62 test independently exercises the inherited dock on desktop.

**Release boundary:** no change to source-manifest.json, protected 283-part scene, 43 assets or DEPLOY_REQUEST.json in this stacked preview. Before any production v11.62 release, reconcile and seal 94 patches, version/marker/hash, full required regression matrix, merge, final dedicated deploy trigger, hosted exact-source/all-assets audit and owner physical-device UX signoff separately. Original historical notes remain below.

## 2026-10-20 · §E v11.61 contextual native tool workbench — GOVERNED RELEASE CANDIDATE

**Not production live until final verified deploy.** Source adds an optional second split floating tool window. To find it: **Model Atelier → ⠿ Move tools → ◫ Context**. Pick a family in the right rail, a relevant operation on the left, and its native inputs/actions on the right. **Save my values / Apply saved values** are explicit per-operation presets. All original controls and projects remain accessible, with unchanged 283-part canonical model and 43 media assets.

Eight native Model Atelier category families: Meshes, Sculpt, Lasso, Face, Topology, References, Motion, Appearance; only existing compatible controls are exposed. No other §E editor (Anime, timeline, game builders) adapter is yet implemented. 93 patches, v11.61 marker `V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH`, exact generated **2,958,383 bytes / SHA-256 `cd33b05e3e27304fe9d3e753e488d46fcb844841fd06e19b8058a81516e7d01e`**. [Desktop & Android browser preview PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39435151694) and [independent seal measurement PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39435615603). [Feature controls and location guide](https://github.com/kaministrator999-ui/Swrlzkamico/blob/feature/se-adaptive-context-workbench-v11-61/projects/swrlz-forge-moba/reports/CONTEXT_WORKBENCH_V11_61_PREVIEW.md).

Release gates remaining: full production CI/regressions, merge, sole final `DEPLOY_REQUEST.json` trigger, terminal hosted deploy, 43-asset live audit, hosted desktop/Android tests. Historical v11.60 receipts below remain valid for that previous version.

## 2026-10-20 · v11.60 LIVE PRODUCTION CLOSEOUT (post-release)

**Current release: §wyrl§ Engine v11.60 is live.** This verified post-release receipt supersedes the historical *release candidate / not live until* status below; those original checkpoints remain intact.

- Source commit: [`67f835019f850788cc4b4eddf9ca57729e1c11ac`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/67f835019f850788cc4b4eddf9ca57729e1c11ac), containing 92 ordered patches, preserved original 283-part character and 43 bundled assets.
- Final dedicated `DEPLOY_REQUEST.json` trigger: [`e8cad46238e735135012a4c87319f5fe692d4639`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/e8cad46238e735135012a4c87319f5fe692d4639). [Production deployment 39369014929](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369014929): **SUCCESS**.
- [Independent hosted source/all-43-assets audit 39369120445](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369120445): **SUCCESS**, matched `SOURCE.json` and exact served normalized HTML **2,933,954 bytes**, SHA-256 `fe11e3e748184db1797ef66bc327f7867a25f91d431823a4c8794f157117d97f`, marker `SWYRL_ENGINE_DEPLOY_MARKER: V11_60_FLOATING_MODEL_ATELIER_DOCK`.
- [Live desktop and Android-browser character editor verification 39369120456](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369120456): **SUCCESS**. Automated browser evidence is not owner signoff on a physical phone.
- [Open §wyrl§ Engine](https://kamiloki-swrlz-forge-moba.static.hf.space/) → **Model Atelier**. The persistent **right-side vertical category rail** offers **Meshes / Sculpt / Lasso / Face / Topology / More**. Tap a category to show the floating inspector; drag its **⠿ Move tools** handle to reposition; use **✕ Hide** and a rail button to close/reopen. Original Model Atelier edit handlers and saved model state remain preserved.
- Scope: shipped floating dock, not automatic photograph-to-head reconstruction, high-end QEM retopology, physical-device GPU profiling, or subjective likeness approval. Those are separate, unfinished acceptances.

**This closeout is documentation-only; no engine binary, source-manifest, 283-part scene, release version, hosted content or deploy-trigger mutation is requested.**

## v11.60 · draggable vertical Model Atelier tool dock — governed release candidate (2026-10-19)

Owner requested the precision tools leave the bottom mobile viewport and become immediately discoverable. The v11.60 candidate adds a persistent slim vertical category rail and draggable, collapsible scrollable inspector overlay, **without changing** original 283-part model or all 43 asset files. The cumulative editor includes all v11.59 precision tools; `patches/v11_60_floating_tool_dock.py` is the additive 92nd patch. Exact source seal: **2,933,954 bytes**, SHA-256 `fe11e3e748184db1797ef66bc327f7867a25f91d431823a4c8794f157117d97f`, marker `V11_60_FLOATING_MODEL_ATELIER_DOCK`. The separate [v11.60 acceptance report](projects/swrlz-forge-moba/reports/FLOATING_TOOL_DOCK_V11_60_RELEASE.md) retains CI and release lineage. **Not live until merge, final dedicated deploy request, successful terminal deployment, exact hosted 43-asset receipt and desktop/mobile UI acceptance.** Older v11.59 source and preview records are retained as history.

## v11.59 · precision Model Atelier production release candidate (2026-10-19)

Owner-directed promotion of the fully **preview-verified** cumulative §E Model Atelier toolset from **v11.21–v11.59** into the governed release pipeline. The additive `patches/v11_59_precision_model_atelier.py` reproduces all previously tested precision tools on the sealed v11.20 anatomical starter, preserving its **283 editable parts** and the original **43 bundled assets**. Highlights: vertex/face sculpting and Undo; camera occlusion + geodesic surface targeting; pixel-radius and editable falloff; lasso geometry, painted Add/Erase masks and native grouped gizmos; multi-image floating reference windows; manually traced feathered photographic cutouts; face landmarks/profile depth/extrusion; native topology, conservative UV island-safe LOD and mesh audit/export.

**Scope and acceptance:** These are implemented modeling tools, *not* automatic human head photogrammetry, curvature-QEM professional retopology, universal 3D pin manipulators, or measured performance on physical Android hardware. Owner requested the production upgrade; appearance/likeness signoff for actual reconstructed faces remains separate.

**Release seal:** `SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER`, **91** ordered patches, **43** original packaged assets, **2,927,005** HTML bytes, SHA-256 `f4d72c72a5fc4ee90c921198d7086b5898b89941de3efadd7f52c063d3dab0b3`. Release-source QA and full browser/legacy compatibility are distinct from the earlier isolated [v11.59 preview success](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39271247522). Dedicated DEPLOY_REQUEST.json trigger must remain the very **last GitHub release mutation** after PR merge and full production validation; live status requires terminal deployment, served exact HTML/43 assets and hosted desktop/Android acceptance. [v11.59 governed release plan](projects/swrlz-forge-moba/reports/PRECISION_MODEL_ATELIER_V11_59_RELEASE.md).

## §E v11.47 verified preview and unfinished original spec — 2026-10-18

[Open v11.47 precision preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-47/index.html?project=model-atelier). [CI 39186091212 SUCCESS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39186091212) at code SHA `d27cc62a73c1cedd911753b3f5654a5da95d36c3` across full six-part desktop/Android browser matrix and CPU geometry; exact served HTML (2,852,736 bytes; SHA256 `5a49c4886db81403a516d18fdf69dbed0ebba6ad8e6355fd9d0db606b9ef76f7`), SOURCE.json and original 283-part anatomy scene verified. Scope adds [PR #256](https://github.com/kaministrator999-ui/Swrlzkamico/pull/256) adaptive local topology/UV stitching and [stacked PR #257](https://github.com/kaministrator999-ui/Swrlzkamico/pull/257) owner-calibrated profile photograph feature-depth maps; no automatic anatomy/perspective claims. The [private owner-spec acceptance tracker](projects/swrlz-forge-moba/reports/MODEL_ATELIER_OWNER_SPEC_ACCEPTANCE_V11_47.md) lists outstanding §2–§12 feature and dense mobile/art QA requirements. Both PRs draft, no production main merge, production sealed v11.20 original remains intact, DEPLOY_REQUEST stays the LAST authorized gate. **The complete modeling document is NOT finished.** Prioritize true ray-visible selection, on-canvas pin gizmos/painted lasso and full actual photographic head/neck reconstruction separately with evidence and owner visual approval.

## §E v11.42 published precision preview handoff — NOT MAIN ROOT PRODUCTION (2026-10-18)

[Open v11.42 verified preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-42/index.html?project=model-atelier). [CI run 39178855114 terminal SUCCESS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39178855114), second attempt same code revision `10101d16a6ed65ba63875b2d742bd11e756c00c6`; all four cumulative desktop/Android browser groups and native geometry schema passed. Final actual hosted HTML + SOURCE + original anatomy scene SHA matched; first simultaneous publication attempt was correctly blocked due to overlapping source receipts, rerun in isolation succeeded. See [v11.42 acceptance](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_42.md). Stacked draft [#250](https://github.com/kaministrator999-ui/Swrlzkamico/pull/250), [#251](https://github.com/kaministrator999-ui/Swrlzkamico/pull/251), [#252](https://github.com/kaministrator999-ui/Swrlzkamico/pull/252) remain unmerged. Original v11.20 production and 283 parts are **untouched**. Unimplemented milestone A–C remainder: automatic runtime LOD, high-quality remeshing/manifold repair, freehand image clipping and alpha, calibrated multi-camera skull/neck, true camera-space brush occlusion, full 3D gizmos and dense-device QA. Do not declare full spec complete; keep deploy request last after gated promotion and owner visual approval.

## §E v11.42 precision editing handoff — additive draft, production not replaced (2026-10-18)

Current owner Milestones A–C continuation: [v11.42 acceptance addendum](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_42.md) → [PR #252](https://github.com/kaministrator999-ui/Swrlzkamico/pull/252) stacked on [#251](https://github.com/kaministrator999-ui/Swrlzkamico/pull/251) on [#250](https://github.com/kaministrator999-ui/Swrlzkamico/pull/250) and prior v11.39 preview. Dedicated CPU and desktop/Android gates passed for explicit indexed edge split/vertex translate/face remove, authored radial image silhouette and opt-in reference image tap → true saved UV facial landmarks. Full integrated [v11.42 verification/preview workflow](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39178855114) must pass before sharing any new v11.42 hosted URL. **No stable main merge, source-manifest rewrite or DEPLOY_REQUEST mutation for these drafts.** Open gaps: manifold-sound arbitrary edge/bevel/retopo and QEM decimation; runtime distance-switched LOD/thresholds; freehand mask silhouettes and transparent alpha repair; calibrated front/profile matching into skull/neck; true camera-space occlusion, brush-painted lasso, graphical rotate/scale gizmos and dense mobile performance gates. Continue with explicit user-approved design scope and actual visual acceptance.

## CURRENT §E v11.39 precision modeling continuation (2026-10-18)

Two **verified preview-only** owner-priority slices: (1) [PR #248](https://github.com/kaministrator999-ui/Swrlzkamico/pull/248) actual indexed low-poly topology copy + UV OBJ LOD authoring and (2) stacked [PR #249](https://github.com/kaministrator999-ui/Swrlzkamico/pull/249) manual photo-UV face landmark displacement; source of truth [v11.39 acceptance addendum](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_39.md). Cumulative [CI 39174642704 PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39174642704) across geometry and desktop/Android preview UI; [exact v11.39 hosted review candidate](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-39/index.html?project=model-atelier). It retains the prior v11.37 tools in [PR #247](https://github.com/kaministrator999-ui/Swrlzkamico/pull/247). **No main merge / production deployment or full owner-spec completeness.** Keep original 283-part v11.20 figure and references unchanged; develop feature-preserving decimation, robust arbitrary edge/face operations and automatic LOD separately from photo silhouette and calibrated front/side head/neck construction. Owner artistic acceptance, full source-version sync and governed release remain gates; `DEPLOY_REQUEST.json` is the last release mutation, never touched for preview.

## CURRENT §E precision Model Atelier — v11.36 DRAFT continuation, not production (2026-10-18)

Continue development from [v11.36 acceptance addendum](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_36.md) and stacked [PR #246](https://github.com/kaministrator999-ui/Swrlzkamico/pull/246) → #245 → #243 → #241 → #240/#238/#235/#234/#233/#232/#231/#230/#229/#219. Earlier [v11.32](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_32.md) and [v11.29](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md) documents preserve original history. Recent tested candidate tools: CI exact 90-sealed-patch routing, actual named-region Add/Subtract/Intersect selection across sculpt and local refinement, separately rounded boundary interpolation, and single-edge surface-constrained lasso grow/shrink. Each has a passing dedicated CPU + desktop/Android browser Actions receipt.

**DO NOT** conflate the drafts with merged/deployed §E or a finished character likeness. The original v11.20 283-part anatomical head and source seal remain canonical. Unfinished: true camera occlusion, painted masks, arbitrary retopology/decimation and exported runtime LOD, visual pin rotate/scale handles, multi-view photo-to-skull manual modeling, full integrated mobile/source/artistic release acceptance. Keep unrelated source and personal reference images untouched. Full release requires governed version/manifest sync, owner visual approval, exact integration tests and `DEPLOY_REQUEST.json` as the **last release mutation** after merging validated code. Continue in isolated slices; don't press deploy for an incomplete feature candidate.

## Current precision-editor handoff — v11.32 DRAFT continuation (2026-10-18)

Source of truth: [v11.30–v11.32 verified addendum](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_32.md) and [v11.29 baseline acceptance ledger](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md). Current stacked draft PR [#240](https://github.com/kaministrator999-ui/Swrlzkamico/pull/240) → #238 → #235 → #234/#233/#232/#231/#230/#229/#219. New native editor tools verified on desktop/Android: bounded group surface-pin transform, lock and disabled duplication of detail layers, user-sized and pinned floating references. **The full design, full Codex-operated character sculpt, artistic likeness, production merge and deployment are NOT complete.** Preserve original v11.20 283-part anatomical scene and independent project boundaries. Continue true camera occlusion, lasso booleans, real decimation/runtime LOD, visual rotate/scale gizmos, multi-view face modeling and cross-tool testing in small evidence-backed slices. Govern version/release and press `DEPLOY_REQUEST.json` only as the last mutation after total release acceptance.

## Current §E precision-sculpt handoff — v11.29 stacked DRAFT ONLY (2026-10-18)

**Continue from** [v11.29 implementation and acceptance ledger](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md) and current development PR [#234](https://github.com/kaministrator999-ui/Swrlzkamico/pull/234), stacked on #233 → #232 → #231 → #230 → #229 → #219. The v11.20 original 283-part, eleven-section anatomical scene and sealed source manifest remain production truth. This is **not** a finished spec, merged release, deployed preview or completed character sculpt.

Verified tested candidate additions since v11.23: freehand surface 📌 lasso; interior camera and deliberate opposite-normal sculpt; measured local triangle preview; smooth/flatten/inflate/pinch/translate and mirrored-X brush (base asymmetry remains); parametric sphere/loft sampling presets with true-generator vertex/triangle previews (not exported LODs); opt-in nearest-facing projected-depth safeguard (not accurate camera visibility). See the ledger for exact terminal CI receipts, corrected failures and remaining design requirements. Continue with source-of-truth-first small slices and real device/geometry tests. Do not merge/deploy this draft or press `DEPLOY_REQUEST.json` until full release gates, owner visual review and original v11.20 character protection are satisfied.

## Draft v11.23 precision Model Atelier — Codex operator entry (preview only)

The owner requested **Codex to operate the actual §E Model Atelier controls** for reference-matched character sculpting, not to instruct the owner to manually edit the mesh. The stable release is still **v11.20**; do not merge this draft, overwrite production, or replace the original eleven-section anatomical head/283-part scene.

**Interactive preview:** https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-sculpt-preview/index.html?project=model-atelier

**Read before editing:** [Precision Editor Codex Readiness & Operating Contract](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_CODEX_READINESS_V11_22.md). It enumerates the actual inspector control IDs and bounded workflow for native surface brushes (front/connected/through), vertex matrix and numeric group transforms, lasso boundary pins, conforming local-refinement layers, floating references, UV face-sheet/explicit oval head closure, distortion visualization, Undo and Save/Reload. The original references and sculpt must remain separate assets.

**Acceptance:** the new modules are reviewed by dedicated CPU and desktop/mobile browser tests; exact hosted-preview digest is checked. Test green ≠ artistic likeness approved or a completed Codex modeling session. The advanced freehand cutout, arbitrary decimation/LOD, fully generalized layer stack and automatic reconstruction are not represented as finished.

## v11.20 · anatomical head reconstruction

The owner rejected the round head foundation. A new native surface builds the skull, temples, cheekbones, jaw angles and chin from eleven editable sections, with a flatter facial mask, eye sockets and an integrated nasal profile. Facial contours are refitted and the neck extends into the jaw underside; the corrected legs and remaining body retain their prior data. Saved Apply/Undo and bounded JSON import support the new anatomy controls.

The native starter is `scenes/model-atelier-festival-anatomy-v11-20.swyrl.json`; 90 patches / 43 assets, marker `V11_20_ANATOMICAL_HEAD`. All 179 predecessor patch/runtime sources and 42 assets remain byte-preserved. Exact integrity is recorded in the manifest. Source/deploy commit and live status resolve through the final dedicated deploy request and terminal deployment/audit/native receipts. [Workflow and geometry evidence](reports/ANATOMICAL_HEAD_V11_20.md).

## v11.19 · portrait and body polish

The supplied portrait/body references guide a shorter, softer chin, integrated nose-tip relief and skin warmth, finer eyes/lashes, surface-fitted lips and brows, a smoother neck/shoulder transition and shaped upper arms. Saved native **Portrait finish** and **Fit facial contour** tools support Apply, Undo and validated imports. The existing calf, ankle, foot and independent creature data remain unchanged.

The new starter is `scenes/model-atelier-festival-polish-v11-19.swyrl.json`. The release appends one patch/runtime and one asset, preserving all 177 predecessor patch/runtime files and 41 assets. Package: 89 patches/42 assets. Marker: `V11_19_PORTRAIT_BODY_POLISH`. Exact source integrity is in `source-manifest.json`; publication authority resolves through the final dedicated `DEPLOY_REQUEST.json`, terminal deployment, hosted all-assets audit and desktop/phone native checks. Owner visual acceptance remains separate.

[Native portrait/body workflow](reports/PORTRAIT_BODY_POLISH_V11_19.md). Sealed HTML: 2,614,804 bytes / SHA-256 `d3f8ddb34a964a3955bc1546b7b83db74d29da86ea92f45beb0dbcb998317e72`.

# Current v11.18 · corrected legs and reference portrait

The supplied side-view screenshot identified a knee depth reversal. Both native leg splines now use a gradual hip–knee–ankle profile with actual posterior calf volume, restrained shin contours and an Achilles taper, while preserving ankle endpoints and all foot placements. The new close-up guides warmer amber eyes, finer lids/lashes/lips, swept fringe, a grooved crown, open knotted hair wraps, a fitted collar and refined coral/ivory neckline. All changes remain individually editable and save through native Model Atelier JSON.

New native leg anatomy, crown/wrap finishes and saved iris pigment controls include undo and validated import. The saved starter is `scenes/model-atelier-festival-reference-v11-18.swyrl.json`. All 175 predecessor patch/runtime sources and 40 assets are preserved; the new package has 88 patches and 41 assets. Version/marker: **v11.18 / V11_18_LEG_REFERENCE_CORRECTION**. Sealed HTML: **2,594,314 bytes**, SHA-256 `82f833c7a7771d167e582f381b655e01b5a63e5f6d50a3abb5e2f604467b234b`. Exact source integrity is recorded by the manifest; source/deploy commits and publication authority resolve through the final dedicated deployment request and terminal hosted receipts.

[Correction workflow and evidence](projects/swrlz-forge-moba/reports/LEG_REFERENCE_CORRECTION_V11_18.md). Full native replay, all 18 desktop/phone compatibility suites, merge, dedicated deployment and exact hosted checks are separate gates. Owner visual review remains separate.

## v11.17 · HD character sculpt and native studio finish (2026-10-16)

The owner requested unrestricted high-definition quality. The new native starter refines the continuous portrait surface, integrated iris/pupil fibers and corneal highlights, thin eyelids and smiling lips, transported hair sweeps with a harmonious split-dye fringe, black woven pigtail wraps, embroidered curved garment panels, ribbed draped socks, welted leather shoes and pinched satin bows. Each ferret plume now has a continuous core beneath genuinely creased, overlapping paper leaves with cut edge thickness. Floating cheek/nose decorations and stacked sock-fold primitives were replaced with continuous surfaces.

Native **HD surface finish**, relief, compatible matching-spline application, **Fit trim to cloth**, and saved sampling controls are editable, undoable and validated during import. Physical materials, ACES studio lighting and clean **Render PNG · 2k** support close-up review. The HD starter has **283 editable meshes**, **1,619,108 measured triangles** in the complete set, **1,335,220 in the heroine** and **48,768 in the head**. These are generated buffer measurements, not a quality score or a device-performance claim. The lighter preview and standard detail presets remain available; HD is the saved default.

The saved scene was authored and reimported through real Model Atelier controls. All **173 predecessor patch/runtime files and 39 historical assets** remain byte-preserved. The current package has **87 ordered patches and 40 assets**. Sealed HTML: **2,582,080 bytes**, SHA-256 `623283cc9589fa166ea00f985350f55092606818ab6be4188302f256a0fdb854`. Native geometry checks, desktop/phone editor tests, the full compatibility matrix, merge, final dedicated deployment, exact hosted digest/all-assets audit and hosted editor workflow are separate release gates. Owner visual acceptance remains separate; UV texture painting and weighted skeletal skinning are still outside this release.

Repeatable authoring, measured evidence and art-review limits: [HD character workflow](projects/swrlz-forge-moba/reports/HD_CHARACTER_SCULPT_V11_17.md).

## v11.16 · facial contours and adjustable native mesh detail (2026-10-16)

Owner requested a much more detailed face and asked to verify the proposed 20k mobile triangle budget against UE4 guidance. The current heroine uses **92,028 triangles**, including **12,096 in the continuous head surface** (previously 77,444 and 1,944 respectively). Native nose bridge, eye socket and cheek controls shape the actual head vertices. Smooth jaw transitions remove the hard chin/cheek sampling discontinuity exposed by denser topology. Spline body surfaces, eyes, hair and garment panels have saved sampling controls, with a triangle-edge preview and exact selected/heroine/whole-set counts.

The optional mobile preset is **26,908 heroine triangles**, including **6,016 in the head**. The two independent paper ferrets and bunny retain **32,112 triangles** across both presets, so the complete sets are **124,140 close-up / 59,020 mobile**. The high detail preset is the saved starter. This is selectable native authoring detail; it is not automatic distance LOD or a measured physical-device FPS guarantee. Mesh sampling and continuous facial forms are independently editable, undoable and retained by native JSON/OBJ export.

Epic's [UE4.27 mobile performance guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-guidelines-for-mobile-devices?application_version=4.27) discusses about 500k triangles for the entire view on older iPad targets, rather than a 20k per-character rule. Its [optimization guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/optimization-and-development-best-practices-for-mobile?application_version=4.27) emphasizes profiling target hardware and material/draw-call costs. Preset budgets here are project choices, not Epic character limits.

Native asset: `scenes/model-atelier-festival-detail-v11-16.swyrl.json`, saved and reimported through real Model Atelier controls; **301 editable meshes**, with all 85 prior patches/runtime sources and 38 historical assets preserved. The independent audit's asset list now includes the v11.15 and v11.16 native scenes. Seal: **2,501,987 HTML bytes**, SHA-256 `fd9deed8f22f5b111eadcb59501d47b00061bd4bd219bae6e8e894c82138c97a`, **86 patches and 39 assets**. Native desktop/phone, full compatibility CI, validated merge, the final dedicated deployment and exact hosted verification remain separate gates; owner visual acceptance remains separate.

Recipe and evidence details: [Native detail workflow](projects/swrlz-forge-moba/reports/CHARACTER_DETAIL_V11_16.md).

## v11.15 · native portrait, cloth and ferret surface study (2026-10-16)

The owner requested continued native-editor work against the supplied Honor of Kings Scorchet turnaround. The new starter is the actual model saved and reimported through Model Atelier after **80 native inspector operations**: shorter facial proportions and smiling lip contours, subtler brows/blush, a continuous cyan/coral crown, clearer tapered ferret muzzles and exposed ears/masks, paper bodies swept behind the face in profile, flatter fitted skirt panels with matching borders, a broader coral wrap and corrected rear shoulder layering.

Reusable native tools add portrait jaw taper, tapered muzzle and split-dye crown surfaces, a second dye color, cloth curvature/fold depth and **Frame selected** with detail zoom. New parameters are bounded on import, retained by model JSON and whole-model Undo/Redo, and drive the rendered geometry. The independent ferret sockets, flex, model motion keys, detach/reattach, bunny and native JSON/OBJ exports remain available. Historical defaults retain their old geometry when the new surface fields are absent. Repeated model import now accepts the empty neutral pose emitted by native save/load while retaining validation of actual pose frames.

Native asset: `scenes/model-atelier-festival-surface-v11-15.swyrl.json`; **301 editable parts and 109,556 measured triangles**. [Native authoring and multiview evidence](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38956922273) comes from the real CI browser operating the editor, saving/reimporting JSON and capturing front, three-quarter, profile, rear, portrait, ferret and cloth views plus a phone view. Authoring source: `b411aa3b9592d1ec9d9b3fb1d5f3ebe28f354d02`.

Source seal: **2,487,712 bytes**, SHA-256 `c4c7356c35827eeaea2f24ca943c0dd431c65f5898dbcd325440f0821fc10a3a`, **85 patches and 38 packaged assets**. All 84 predecessor patches/runtime sources and 37 assets are preserved. Full independent compatibility CI, merge, the final dedicated deploy request, exact hosted digest/all-asset audit and native hosted phone/desktop controls are distinct release gates. Source/deploy commits and current publication authority are recorded by `DEPLOY_REQUEST.json`, its final trigger commit and the dedicated deployment/audit receipts; this source note does not substitute for those receipts. Owner visual acceptance remains separate. UV painting and weighted skeletal skinning are outside this release.

Details and repeatable editor authoring: [Native surface workflow](projects/swrlz-forge-moba/reports/NATIVE_SURFACE_STUDY_V11_15.md).

# §wyrl§ Engine · current v11.14 reference refinement

## v11.14 · portrait, silhouette and cloth refinement

The owner requested a closer match to the festival turnaround after reviewing v11.13. This pass refines swept cyan/coral hair into closed elliptical ribbon locks, narrows the round sclera, improves ferret muzzle/eye/ear readability, varies paper edges and color, opens the relaxed A stance, reshapes sock folds and shoes, adds inset garment stitching, and gives the skirt real curved side panels with an opaque fitted underlayer. The separate bunny is moved clear of the wider shoe stance. Front, three-quarter, back and profile views are required; a front-only screenshot cannot reveal missing side cloth.

New native asset: `scenes/model-atelier-festival-refined-v11-14.swyrl.json`; **301 editable parts and 108,260 measured triangles**. Native editor Save model JSON retains the authored result. All three creatures keep independent motion, sockets, detach/reattach, transform keys and exports. The new geometry uses deterministic variation so save/load and OBJ exports reproduce the same surfaces.

Candidate seal: **2,482,877 bytes**, SHA-256 `1154b86d8a8c027fc3b94a39254ff77d5d136a0fcc8283061ef1d0b6d6fe1803`, 84 patches and 37 assets. All 83 predecessor patches/runtime sources and 36 assets remain preserved. Baseline v11.13 was verified live at `25b33e64c5211d47dde7bb8cb77e0f58d1917d5c55971938bf732c2d1371b9d8` before this work. Branch `feature/model-reference-refinement`. Full compatibility CI, the final dedicated deploy request, hosted digest/asset audit and live native controls are release gates; owner visual acceptance remains separate. This is an editable original geometric study, with UV painting and skeletal weight painting still outside the implemented tools.

# §wyrl§ Engine · current v11.13 reference sculpt update

## v11.13 · native reference sculpt and independent living piñatas

Measured candidate seal: **2,467,619 HTML bytes**, SHA-256 `25b33e64c5211d47dde7bb8cb77e0f58d1917d5c55971938bf732c2d1371b9d8`; 83 ordered patches and 36 assets. Native model-save authoring, twenty focused desktop/phone cases and twelve phone/desktop-site/multiview framing checks passed; full independent release CI remains required.

The owner-provided festival turnaround now drives a new 275-part native starter: sculpted facial planes and almond eyes, swept dyed hair, asymmetric layered outfit, bare anatomical legs and socks, two three-dimensional tissue-paper ferrets attached to actual hair sockets, and a separate paper bunny. The living-model inspector provides reversible attach/detach, per-model flex, saved transform keys, a six-second transformation preview, independent model JSON exports and actual rendered OBJ export. Whole model history, native save/load and the measured geometry profiler remain available. Default generated geometry is approximately 82,396 triangles, measured from the buffers rather than guessed from mesh count.

Candidate branch `feature/model-reference-sockets`; source and hosted baseline `43dd6db` / v11.12, 2,352,463 bytes, SHA-256 `76051c90fda3b9f32fef582977fb8af872edc14de44781e253f90ed3f0f9bc6f`. The new release appends patch 83 and native asset 36. All 82 predecessor patches/runtime modules and 35 packaged assets are preserved. The exact earlier v11.12 default remains independently loadable for its full regression.

Research, native format, controls and limitations: [Festival reference workflow](projects/swrlz-forge-moba/reports/FESTIVAL_REFERENCE_WORKFLOW.md). This is an original editable geometric study; production retopology, UV painting and skeletal skin weights are not implemented. Full desktop/phone compatibility, final dedicated deploy, exact hosted audit and the owner's visual response are separate gates. This candidate section does not claim publication before those checks pass.

# §tart §E — §wyrl§ Engine Build & Deploy Router

## v11.12 grounded pose correction — validated and merged; deploy pending (2026-10-15)

**Owner rejection:** three-quarter, profile and rear phone screenshots of live v11.11 reveal visible “banana/rubber legs” and unnatural apparent knee pain when Idle/Victory is applied. The v11.11 pose algorithm displaced most leg spline knots with a bell-shaped depth weight while fixing both hips and ankles; a clean knee hinge and believable weight-bearing stance did not result. Earlier numerical tests rewarded **more bend**, so green CI was not visual acceptance.

**Implementation:** append-only `patches/v11_12_grounded_stance_poses.py` replaces only the inlined v11.11 built-in pose handlers, preserving saved-frame schema, face refinement, ferret-piñatas and older scene assets. For each six-knot continuous anatomical leg, interpolate each interior point along either a hip–knee or knee–ankle segment with restrained depth displacement. Give one leg a stable near-straight support posture and let the other leg relax to a modest step; translate the whole sock/shoe/toe/sole assembly with its ankle in X/Z while preserving every foot's Y-ground contact. Avoid moving the face independently of torso and ferret sockets. `Neutral`, `Relaxed idle`, `Victory` and `Victory B` remain reversible/editable.

**Validated merge:** [PR #194](https://github.com/kaministrator999-ui/Swrlzkamico/pull/194) merged as `f2fa861fe65742f7a3dce1b60db358a6e6472368` from validated head `6ab1a126ffcc73b904436d6603a51c1428bc59aa`. **17/17 desktop/mobile browser suites and all nine applicable workflows passed** including the new grounded-joint, anchored-sole and neutral-restoration assertions. Source seal 2,352,463 bytes / SHA-256 `76051c90fda3b9f32fef582977fb8af872edc14de44781e253f90ed3f0f9bc6f`. Hosted release and owner visual acceptance remain separate.\n\n**Acceptance gates:** exact source SHA and 82-patch/35-asset seal; 811-part source preservation; native geometry CPU test validates near-straight thigh/shin, maximum knee angle, both anchored soles, idempotent pose application and neutral restoration; desktop/mobile screenshot/UI test rejects support-leg banana deformation and airborne footwear; all historic game/rig browser suites must pass. Once merged, update only `DEPLOY_REQUEST.json` as the last main mutation; independent hosted digest/asset audit and owner's subsequent multi-angle screenshot review remain mandatory. This is **still not** a skin-weighted skeleton or authored animation.


## v11.11 facial + native pose/frame studio — validated and merged; deployment gate pending (2026-10-15)

The owner's mobile front/rear/side screenshots of live v11.10 showed a too-stiff straight-legged standing pose and overly flat face. A new append-only `patches/v11_11_face_pose_frame_studio.py` changes **only the generated canonical starter** to subtly soften the jaw, eyes, brow, cheeks, nose and smile while preserving the original v11.9 811-part scene asset. The new in-viewport collapsible Pose & camera frames panel supports **Neutral, Relaxed idle, Victory, Victory B** and front/back/left/right/three-quarter camera choices. Leg poses are actual edits to existing native smooth loft knee spline knots (not animation bones), remain undoable, and preserve all 811 editable parts. Eight named custom pose+camera frames can be saved, restored, renamed through save-overwrite, deleted and carried in validated native project JSON / Save Project. Original ferret bodies remain distinct; no commercial game asset is extracted.

**Technical boundary:** No skeletal skinning, pose interpolation, animation timeline, imported animation libraries or guaranteed facial likeness in this release. Do not claim visual approval without comparing new front, rear and profile screenshots to the provided references.

**Validated PR:** [#193](https://github.com/kaministrator999-ui/Swrlzkamico/pull/193), head `ccca615f79960f7cb0ec65a76daa466d6b178b3e`, squash merge `16faf1b8a7b42f15e9e01b56da010b100ac6dc6b`. All 17 desktop/mobile browser acceptance jobs passed and all eight related §E source/audit workflows reached terminal success. This is validated merged source, **not** hosted release or owner visual approval.\n\n**Sealed candidate:** 81 ordered patches, 35 unchanged historical packaged native assets; independently reconstructed **2,350,741 bytes**, SHA-256 `e89ea40f0b7609d0b5cf376666aaba4a58971a3a294c3225ad303ce9f6ef4792`. Source syntax + controlled knee spline CPU acceptance passed. Full package/browser CI, merge, dedicated deploy request as last `main` source mutation, successful Hugging Face delivery and independent hosted SHA/assets audit are required before calling v11.11 live.


## v11.10 measured model statistics — merged source, release gate pending (2026-10-15)

Owner-directed Modeling Engineering Brief implementation slice: [PR #190](https://github.com/kaministrator999-ui/Swrlzkamico/pull/190) merged with source commit `7e38e623ed24801becd6afd738519652d79d9909` after all seven §E CI workflows and all 17 independent desktop/mobile browser jobs passed on validated head `4e89457c990e654e96e80bec8138148b25637dcf`. New append-only `patches/v11_10_model_geometry_profiler.py` adds measured generated BufferGeometry triangles, buffer vertices, CPU geometry memory, grouped component breakdown and native JSON statistics export with a mobile-friendly collapsed inspector. No source character meshes were replaced: the 811-part v11.9 original native scene and all 35 historical game/media assets remain preserved. Source seal: **2,339,787 HTML bytes, SHA-256 `e8b2ca7b4e12d9981475a861d40eabf513f5d26a40c8f6627d393b93d03dddf6`, 80 patches, 35 assets**. See `projects/swrlz-forge-moba/reports/MODEL_ATELIER_ASSET_PIPELINE_2026_10_15.md` for scoped next slices: reversible independent creature sockets, character identity and skins, skeletal rigging, animation, material/LOD tools, VFX and chat orchestration. These later systems are **planned, not implemented** in v11.10. Do not mistake reported buffer vertices for welded topology or estimated meshes for actual GPU draw calls.

**Release authority:** this merged source remains only a candidate until the deliberately changed `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` triggers the dedicated HF pipeline, that workflow reaches terminal success, and an independent hosted SHA/asset audit confirms serving the new digest. Human owner front/side/back visual acceptance remains separate. Never deploy via §wyrlz AI Chat or weaken historical game/browser checks.


## Active v11.9 model starter candidate — owner-approved ferret-and-figure refinement (2026-10-15)

Owner reference is the primary cyan/coral carnival mage and approved character turnaround; other skins are anatomy/material context, not replacements. The two ferret-piñatas are independent native creature bodies gripping separate dyed hair at the head, each with a 36-tier faceted editable loft and a narrow root (r=.115), broad midbody (peak r=.77) and tapered far end (r=.20). The default candidate adds a continuous sculpted neck/torso, refined human arms/legs/hands/shoes, eight actual editable cloth panels and a separate paper bunny. The prior 253/303/539/653/733/749-part scenes are preserved. Branch `feature/engine-v119-figure-ferret-silhouette`, PR #187, 811 current editable parts, 79 governed patches, 35 native assets. Exact source candidate: 2,335,886 HTML bytes, SHA-256 `987f074e111420126715142da652d4907c7d1a0e493215ee9784e35da48966dd`. Full CI, merge, dedicated deploy trigger, independent hosted SHA/assets audit and owner's multi-angle likeness review remain distinct gates. This is procedural unrigged original geometry, **not** skeletal skinning or animation; do not call it visually accepted without owner screenshots.

## Active v11.8 · approved model sheet → functional sculpt, not primitive inflation

Owner-approved character correction for this release: giant paper ferrets originate behind the heroine's head, sweep back in 3D and twist forward along opposed broken-S paths; the girl becomes taller, with continuous loft-shaped arms/legs and no discrete bead knees/elbows. Native spline controls must edit twist, depth profile, smoothing, X-mirror and paper fringe, while smooth anatomical loft creation remains available. The implementation uses a procedural native loft tool; **rigged skinning, invisible armatures, bone weights, UV painting and volumetric sculpt brushes are still future tools** and must not be claimed as implemented. Meshes and material colors alone are not proof of quality: inspect actual front/side/back output against owner-approved concept sheet. Only merged, validated, deployed, independently audited artifacts may be called live.


## Current §E v11.7 model fidelity gate — owner corrective screenshots

The live v11.6 reference study failed the visual acceptance gate. The owner identified smooth boomerang/sausage loop geometry, fake detail inflation, insufficient piñata construction, flat rear treatment, blockout facial/garment anatomy and inconsistent mobile presentation. **When this is reported, implement the authorized code changes immediately rather than responding with another plan or menu of options.**

**Current construction contract:** The two ferret bodies must be distinct, visibly stepped chains of **36 capped truncated-pyramid disk slices each**, with angular flat-shaded faces, interlayer recesses, torn paper edges and colored overlaps on the front, sides, underside and rear. There must be actual gripped dyed hair braids, prominent elongated ferret muzzles, jaw/brow/eyes/ears, and sculpted front/rear apparel, hair and footwear. This is structural geometry, not tiny box inflation. Loft control paths and radii must remain editable, and each historical scene must remain loadable.

**Proof, not assertion:** Native 3D object data, shader/geometry flags, model counts, front/side/back screenshots, mobile and desktop interaction, import/export and full regression must be tested. Passing a source seal or adding hundreds of objects does not establish visual quality. Record unsatisfied art-direction differences and keep iterating on observed defects. Group fixes and test expectation updates into atomic commits to avoid needless CI churn. Gate merging and the dedicated last-main-mutation deployment trigger on independently returned CI results, then confirm production served digest and owner visual response.

**Release candidate:** v11.7 — faceted tiered piñata spine surfaces, 733 editable pieces (474 old wafer decorations retired; 554 structurally placed additions), 77 governed patches and 33 native assets, pending measured artifact seal, complete browser tests and hosted audit. Production remains v11.6 until independently verified.


## Active owner workflow contract — §E (2026-10-15)

**Entry rule:** When owner reports a defect, supplies screenshots, or approves work, do the authorized scoped change in this session where tools permit. Do not stop after a plan, handoff, diagnosis, or recommendation. Read this router and the governed source manifest; identify actual code/artifact and live deployment state. Repeat tool calls as needed within available limits, and report genuine connector limits rather than pretending a build deployed.

**Completion loop:** observe → isolate → modify narrowly → test targeted code and visual behavior → run necessary regression suite → merge validated work → edit only the dedicated `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` as the **last main mutation** → wait for terminal deploy result → independently audit exact served HTML hash, native asset list, and production behavior → review owner's front/side/back screenshots and continue corrections if acceptance fails. A green workflow, branch commit, merged PR, or mesh count alone is *never* equivalent to visual or live acceptance.

**Release efficiency:** batch logically related changes; avoid a new PR or tiny CI-triggering commit for every discovery. Centralize version/patch/asset expectations. Use branch-level concurrency cancellation for superseded *validation* only; never cancel a production release. Run cheap syntax, scene schema and editor checks before expensive browser matrix. Reuse built artifacts and cached browser dependencies where safely feasible. Keep full release regression coverage before deployment; do not delete or weaken tests to manufacture green checks.

**Model acceptance:** assess silhouette, depth, readable head and muzzle anatomy, actual hair gripped by two separately modeled living piñata-ferrets, paper fringe on front *and back*, face/garment proportions, and front/side/rear evidence. Added parts must produce noticeable improvements, not merely a higher counter. Preserve historical native scenes and provenance; do not extract commercial models.

**Mobile acceptance:** prioritize practical viewport height, sensible camera framing, touch controls, compact accessible inspector, independently scrollable object list, and no giant unused screen space; check both actual mobile browser viewport and desktop-site mobile mode. The owner's screenshots are first-class regression evidence.

**Truth and release status:** distinguish requested, source edited, tests pass, merged, deploy triggered, deploy succeeded, independently audited live, and visually accepted. If a blocker remains, name the failing gate and continue working when tools allow; do not claim finished early.


## Current project: §wyrl§ Engine v11.6 — visual/mobile candidate (not deployed)

Owner screenshots of **live v11.5** established the correct 539-mesh release but exposed flat piñata reverse surfaces, thin angular loft silhouette, underdeveloped face/back detail, tiny default model framing and excessive empty mobile workspace. The **separate v11.6 candidate** includes native 653-editable-part festival scene and a compact mobile viewport/inspector stylesheet. Its measured source seal is **2,279,438 bytes / SHA-256 `d5f8dce1cbaf221a9f03719f99d53a10b26c6a68fc980ccd38359c4cbbb3a6d0`** with 76 governed patches and 32 native assets. Test and screenshot review are required; do not call v11.6 live until dedicated deploy succeeds and independently hosted audit confirms exact source. Historical v11.5 source verification notes below must not override this current release state.

## Historical v11.5 candidate · now deployed successfully 2026-10-15

The new 539-part original festival character variant keeps historical 253- and 303-part editable native scenes intact. The 75th governed patch adds editable loft path/radius control, raises the Model Atelier capacity to 1,200 parts and JSON import allowance to 8 MB; the new native variant is packaged independently. The exact candidate rebuilt in GitHub Actions [#38747495949](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38747495949) at 2,253,004 HTML bytes, SHA-256 `325f286e0dd3166e34bff57b1e721a6e244089a02cc01d33f8bc3025bace324a`, marker `V11_5_FESTIVAL_LOFT_ATELIER`. **This is source candidate evidence, not a hosted v11.5 deployment confirmation.** Full legacy browser CI, integration review, final §E manual trigger, independent hosted audit and owner visual acceptance are distinct gates. Previous v11.4 production receipts below remain historical evidence.


## Current verified live v11.4 · Prism Jester ferret-piñata fidelity

**Owner direction:** stay on the original cyan/coral **carnival mage** concept. The apparent oversized pigtails are **two living ferret-like paper piñatas biting/holding the real pigtails**—separate muzzle, ears, eyes, paws, and gracefully arched paper bodies—not just curved hair tubes. Other skins are material/render references only.

A separate native **303-part** model variant at `scenes/model-atelier-prism-jester-ferret-v11-4.swyrl.json` replaces only the default Model Atelier sample at Projects; the original 253-part v11.3 scene remains packaged for historical import. Append-only `patches/v11_4_prism_ferret_fidelity.py` adds two smooth variable-radius editable `loft` meshes with paper fringe, improved facial layers and costume detail; engine runtime defaults and existing Maul/Sheep/anime starter saves remain preserved. `reports/PRISM_JESTER_FERRET_ART_DIRECTION.md` contains the comparison criteria, implementation notes, official Blender/Three.js learning references and limitations.

**Verified live v11.4 (2026-10-15 CDT):** [PR #171](https://github.com/kaministrator999-ui/Swrlzkamico/pull/171) merged at `0540cfbfc29129548941881f659f26a767038ed3`. [All 17 desktop/phone browser suites passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364328) with all five candidate source workflows green. [Guarded production deploy #38729222214](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38729222214) and [independent hosted audit #38729291039](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38729291039) both SUCCESS from release trigger `2dba7e6da30fef16c8bb1f4a35f979bcfbffb9b4`. Published Hugging Face Space revision `f88b57b39893f556e380cef7c279d93860800a95`, marker `V11_4_PRISM_FERRET_FIDELITY`, 74 patches, 30 assets, 2,197,108 HTML bytes, SHA-256 `40d1e985bd3754b7a2996e6be14056be9c22164995d83b84ad253b4ae7a24658`; independent hosted audit reported `HOSTED_AUDIT_SCOPE=current-requested-release` and `LIVE_SOURCE_AND_ALL_ASSETS_VERIFIED`. Original 253-part scene remains available historically. This is a procedural fidelity study, not an exact extracted game mesh or advanced sculpt/UV/rig/animation toolset.

## Current verified live v11.3 · Native 3D Model Atelier and Prism Jester

The new **Projects → Model Atelier · Prism Jester** starter is a separate, editable native `scenes/model-atelier-prism-jester.swyrl.json`, not an overwrite of the 30-wave Frostveil or existing Animation Studio. Its original scene contains **253 individually editable meshes**: layered hat/hair, face details, costume, limbs, and two sweeping segmented coral/cyan forms, inspired by owner-provided reference screenshots. It is an original approximation, **not extracted proprietary game geometry or a pixel-exact replica**.

Model Atelier adds a dedicated responsive WebGL viewport, orbit/touch camera, raycast part selection, XYZ position/rotation/scale editing, shape/color/material controls, adding/duplicating/removing meshes, bounded local undo/redo, validated JSON import/export, and triangulated OBJ export. Its data is stored under `project.modelAtelier` in the standard §E native save envelope. The Scene/project launcher and historical native assets remain preserved. Advanced vertex sculpting, texture painting/UV mapping, bone-rigging, mesh deformation and animation have not been implemented.

**Verified live v11.3 (2026-10-14 CDT):** [PR #167](https://github.com/kaministrator999-ui/Swrlzkamico/pull/167) merged as `abfe8a495b3a7c166f2bebe9151887b2cef6b807`. [All 17 desktop/phone browser suites passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608237) and five candidate §E validations passed. [Dedicated deploy #38677061503](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38677061503) and [independent hosted audit #38677099743](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38677099743) both completed SUCCESS on source trigger `44a594f534c92c723079adcb33d8a80962bc7e0f`. Host audit scope `current-requested-release` reported `LIVE_SOURCE_AND_ALL_ASSETS_VERIFIED`; published `V11_3_MODEL_ATELIER_PRISM_JESTER`, 73 patches, 29 assets, 2,175,921 HTML bytes, SHA-256 `a2ec94f418f294ea5ebd50363833d37025a6e6cc804732116a7cb927d0b069db`. This verifies production integrity, not personal human gameplay acceptance or advanced vertex sculpt/UV painting/rigging.

**Starter-pack source of truth (verified live v11.2):** The default **Projects → Frostveil Maul** tile now opens the independently authored `scenes/maul-frostveil-flight.swyrl.json` (78 actors, nine builders, 30 rounds) directly, instead of relying on hidden mutations to the older grouped starter. It saves `maulConstruction: walk-v1`, `maulSpawnProtection: full-pad-v1`, `maulBuilderFlight: hover-v1`, and `maulVisualStyle: glacial-v2` inside the native project. Its own package asset is shipped beside the older `scenes/maul-frostveil-groups.swyrl.json` and classic Maul files, never overwriting the earlier scenes. Browser CI must verify that the editor’s default starter is identical in critical profile and builder identity to the downloadable native pack. The v11.2 release passed candidate CI, dedicated deployment, and independent hosted audit.

## Current verified v11.2 · Hover construction and glacial battlefield polish

New canonical Frostveil starter opts into `maulBuilderFlight: hover-v1` and `maulVisualStyle: glacial-v2`. Each sector's winged builder flies directly across terrain and existing towers at **15 world units/second**, hovers approximately **3.25 units above the ground**, and constructs the tower directly underneath its position after travel and the existing route/gold/footprint rechecks. Manual flight remains inside its assigned territory; build placement still forbids protected entrances, gates, exits and occupied ground. Moving cancels a pending build, pause suspends movement, and legacy walk-v1 imported projects keep their original ground pathing and side-cell construction.

The native visual update adds bounded, cached, original procedural 256px snow/ice and harbor-water textures, layered cliff/ice accents, highlighted entrances, pine snow, and lightweight animated builder wings. These are visual-only: no Maul route/wave schema or project asset is overwritten. The baseline 30-wave co-op and earlier Sheep Tag/anime/Den releases remain intact.

**Status:** completed [PR #159](https://github.com/kaministrator999-ui/Swrlzkamico/pull/159), ordered 72nd patch `patches/v11_2_maul_flight_glacial_art.py`. **Verified live v11.2 (2026-10-14 CDT):** [PR #159](https://github.com/kaministrator999-ui/Swrlzkamico/pull/159) merged as `b3ef6130f0d9685018debb06fcdd4ef2912d9f6e`. Six candidate Forge workflows and all 16 native desktop/phone suites succeeded on `716a2bc81b01c79b65ed7771eb3dc794248ce55b`. [Dedicated deploy #38668840620](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668840620) and [independent hosted audit #38668893410](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668893410) both completed SUCCESS on trigger `e47c027816fa5029f0c27ac273e040ae62fd1a5f`. Space revision: `ef8f325b2d8d45cf67da2c54bc4f8e3455df263e`. Published binary: **72 patches, 28 assets, 2,097,069 HTML bytes**, SHA-256 `1fab5e61f2065c02a56658c6e8e8ef999eb525ac16c373b310826ca970e10e59`, marker `V11_2_MAUL_FLIGHT_GLACIAL_ART`. Exact served HTML, SOURCE receipt, and all 28 assets matched. Owner gameplay acceptance remains separate.

**Next separate engineering slices:** physical creep spacing and congested-lane traffic; legal blocked-route response with tower aggression; distinct enemy fast/stealth/detection/typed immunity/teleport/heal/Hydra/Infernal archetypes with counters; adjustable wave mixes and recorder events; optional endless and two-team automatically synchronized Mirror Survival (no player-sent monsters); neutral-balanced thematic builder sets; and a native Maul-specific map/route/wave creator. None of these remaining systems is claimed implemented by v11.2.

**Frostveil implementation ledger:** [Wintermaul v11.1 shipped-versus-planned minion waves and gameplay](projects/swrlz-forge-moba/reports/WINTERMAUL_DESIGN_ARCHITECTURE.md#verified-v111-minion-wave-status-2026-10-14). Three grouped arrival batches, flying/boss rounds and walk-to-build are live; collision/congestion, stealth, immunity, teleport, split/Hydra/Infernal and healer archetypes, endless and Mirror Survival remain planned. The report's acceptance gates govern future claims of completion.

## Historical verified v11.1 · Physical builders, tower mazes, protected entrances

The v11.1 **Frostveil Maul** starter (not historical imported maps) introduced **walk-to-build**: tower placement queues the chosen sector builder to path to a clear adjacent cell; the tower only exists after the builder arrives, when the game rechecks the route, footprint and available gold. Pausing freezes the walk. Moving a builder deliberately cancels their pending construction; changing sectors does not. Building in an entrance pad, gate, or exit is forbidden, and the spawn pads are visibly outlined. Standalone maze walls are hidden from the current build menu; the four combat tower families still physically obstruct ground routes and form staggered, jagged mazes. Historical saved walls are not deleted, and old Maul imports preserve legacy rules.

This is the **first playable delivery** against the larger Wintermaul specification, not a claim that every discussed feature exists. Remaining distinct design/engineering work includes physical crowding/no overlap, completely blocked-path creep aggression against towers, stealth/detection, speed and immunity variations, teleport, hydra/infernal splits, healing creeps, themed balanced builders, Mirror Survival (identical automatic waves for both teams; no player-sent waves), endless scaling/rewards and the dedicated in-editor Maul creator. Keep both player territory independence and team-shared survival. Extend in separate validated slices rather than silently enabling unimplemented mechanics. Older 30-wave rules, animated story projects, Sheep Tag and recorder formats are preserved.

Release: **71 governed patches**, **27 assets**; final patch `patches/v11_1_maul_walk_builder.py`. The exact source, CI, full desktop/phone native acceptance matrix, deployed revision, and independent hosted audit were verified.


**Verified live v11.1 release (2026-10-14):** Merged source [`bbe56716867e`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/bbe56716867e046d3a4f887aa2f5829f25709cd1) includes recorder PR #154 and walked-builder PR #156 through reviewed PR #157. The exact candidate passed [all six Forge workflows and 16 native desktop/phone browser suites](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38643766910). Dedicated [Forge deployment #38646048742](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38646048742) and independent [hosted artifact/asset audit #38646122359](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38646122359) both completed **SUCCESS** for the existing `kamiloki/swrlz-forge-moba` Space. Published v11.1 contains **71 patches, 27 assets, 2,027,727 HTML bytes**, SHA-256 `c96e5fea45bd316750e2fcc60ff1cbd96feadd6a90a56a5667dddad0aaf21121`; Space revision `70a5a943fa302668a2b46bf5c5765f7bfa5349cf`. Published source and all bundled assets were matched independently; future owner gameplay feedback remains separate from these CI/hosted receipts.


## Included v11.0 contribution · Compressed recordings and clear Maul spectator

Frostveil Maul Play-run review now renders recorded snowfields, water, cliffs, tower families, maze walls, builders, creeps and the exit as distinct visual layers, with camera framing adjusted to the actual Maul map dimensions. The original Sheep Tag recorder presentation and recording schema remain intact. A new **Export compressed (.json.gz)** control uses lossless browser-native gzip; the recorder also imports these gzip files with format validation and a bounded 256 MiB decompressed limit. Existing raw JSON, text, HTML spectator, camera, timelines, events and saved projects continue to work.

This v11.0 source contribution added the seventieth governed patch and retained **27 packaged assets**. It was integrated into the cumulative, verified v11.1 publication; v11.0 was not released separately.


## Previous v10.9 candidate · Story actions and an animated first episode

Open **Projects → Ghosts in Different Forms**, or `?project=anime-ghosts-ep01`, then use **Play** or **Watch Episode 01**. Kami and §wyrlz now act through the story: greeting and reaching, recoiling and bracing, casting, writing, stepping, hovering and recovering. Their arm chains, attached full-length staff, heads and costume depth pieces move together. Short dialogue windows leave room for a character to listen and react between lines. Kami's first attempt to burn a doorway nearly erases the library and makes §wyrlz fade. They recover by joining Kami's light with §wyrlz's written names, build a doorway that remembers them and step toward a world that answers, ‘Welcome back.’

The native **Animation Studio** adds **Story Actions** and **Story effects**. Saved action clips control character, action, time, duration, strength and side; effect cues control page motion, bursts, ink and a portal. Preview Frame, editor Play and Watch sample the same saved story time, including reverse and fast playback. Disabling an overlay leaves the underlying limb, face and scenery keys available. Native Undo/Redo and Save/Load retain the clips and cues separately from those keys.

The current native export is `scenes/ghosts-in-different-forms-ep01-performance.swyrl.json`. It retains **70 actors, 11 layers, eight contiguous story beats, nine stage/camera tracks, 134 seconds**, the 12-second book opening and the fitted full staff/socket/relief settings. Its native save contains 175 stage/camera keys, 468 limb/face keys, 383 scenery keys, 36 action clips and 11 effect cues. `project.animePerformance` uses `anime-performance-v1`; `project.animeStoryEffects` uses `anime-story-effects-v1`. The previous full-staff scene and every earlier project/artwork asset remain packaged unchanged for import.

Publication appends `patches/v10_9_episode_story_actions.py`, for **69 governed patches and 27 assets**. All 68 published patches, previous runtime modules, 26 predecessor assets and payload chunks remain byte-identical. Artifact: `swyrl_engine_v10_9.html`; marker: `SWYRL_ENGINE_DEPLOY_MARKER: V10_9_EPISODE_STORY_ACTIONS`. The starter count remains **seven**.

Acceptance requires all **six engine workflows**, **sixteen desktop/phone browser suites**, thirteen sealed Sheep Tag geometry cases, seventeen preserved Maul CPU cases, twelve classic-layout CPU cases and fifteen grouped-spawn CPU cases. The new episode suite checks the saved action/effect data and actual native authoring, Preview/Play/Watch movement, playback controls and lifecycle on both layouts. Completion requires the final dedicated `DEPLOY_REQUEST.json`, terminal successful deployment and exact hosted HTML/SOURCE/all-asset audit. Candidate documentation does not assert publication before those checks pass.

## Historical verified v10.8 · Grouped Maul rounds and visible phone placement

The v10.8 release is verified live: merged source `d371df09a37d44d40d9b05425e01f977eabfa62a`, final trigger `507d11b93e7af81359614e6d56d98a35adbf0b6b`, [deployment 38567626510](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38567626510) and [hosted audit 38567696344](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38567696344). It seals **68 patches, 26 assets and 1,905,846 bytes**, SHA-256 `775d7dfab363da120c2c779b5d8d129d7c75ee6a9681911958bdb9cef3fa1e3e`. All six engine workflows, fifteen desktop/phone browser suites and the four sealed CPU suites passed, followed by native live desktop and phone gameplay and recorder exports. Marker: `V10_8_MAUL_BATCH_PLACEMENT`; artifact: `swyrl_engine_v10_8.html`.

Each cooperative Maul round releases three scattered groups at 0, 2.5 and 5 seconds. The saved `classic-v2` map adds `maulSpawnStyle: "grouped-v1"`; its native `scenes/maul-frostveil-groups.swyrl.json` starts with no authored towers. Phone placement lifts the complete ghost and footprint 140 CSS pixels above the finger. These receipts certify v10.8; the story-action revision requires its own deployment and exact hosted audit.

## Historical verified v10.7 · Classic Maul map layout

The v10.7 release is verified live: merged source `c80e0b98e33ad2c68943415d8c767f836f849f0f`, final trigger `c26630d0f8fce2ba5f3c10c2edfec6e92cf5b109`, [deployment 38513639622](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38513639622) and [hosted audit 38513700470](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38513700470). It seals **67 patches, 25 assets and 1,833,206 bytes**, SHA-256 `c3f24f05ba745a5e834e964d7e06f0637b57b1115fe242bc86d7920738984ddc`. All six engine workflows, fourteen desktop/phone browser suites, twelve classic-layout CPU cases, seventeen preserved Maul CPU cases and thirteen Sheep Tag geometry cases passed, followed by native live desktop and phone gameplay and actual recorder exports. Marker: `V10_7_CLASSIC_MAUL_MAP`; artifact: `swyrl_engine_v10_7.html`.

This release established three long northern snowy bays, a broad crossbar, winding lower defense lanes, editable route turns and one shared ship exit. Its original `scenes/maul-frostveil-classic.swyrl.json` remains packaged unchanged for import. These receipts certify v10.7; the grouped-spawn and placement revision requires its own deployment and exact hosted audit.

## Historical verified v10.6 · Frostveil Maul tower defense

The v10.6 release is verified live: merged source `52862f6a2f8a869d21a03103888b4a094ad19969`, final trigger `6200148fcc7c4ba83bfe76883b4fd49c7d20c53f`, [deployment 38434348748](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38434348748) and [hosted audit 38434414319](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38434414319). It seals **66 patches, 24 assets and 1,748,442 bytes**, SHA-256 `01d7fff6e2a943a326e4582670640d60eec78475c75ab12e16d92c12ee2a9843`. All six engine workflows, thirteen desktop/phone browser suites, 17 Maul CPU cases and 13 Sheep Tag geometry CPU cases passed, followed by native live tower placement/selection, waves, Pause/Stop and actual recorder exports on desktop and phone. Marker: `V10_6_MAUL_TOWER_DEFENSE`; artifact: `swyrl_engine_v10_6.html`.

The cooperative starter introduced nine linked sectors, thirty waves, shared lives, tower mazes, upgrades, air/boss rounds, optional support and native rules authoring. Its original `scenes/maul-frostveil.swyrl.json` remains packaged unchanged. These receipts certify v10.6; the revised classic map requires its own deployment and exact hosted audit.

## Historical verified v10.5 · Editor play-run recorder

The v10.5 release is verified live: merged source `6da367913c0eecc89c67a4976c3db407d851da15`, final trigger `e3b252b6850dfd84824563d1209333930321b268`, [deployment 38344147035](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38344147035) and [hosted audit 38344188938](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38344188938). It seals **65 patches, 23 assets and 1,594,471 bytes**, SHA-256 `cd3b50f06d3a802c025b3e530e743446d284633961bff0dacd46a656eb7e8ace`. All six engine workflows, twelve desktop/phone browser suites and 13 geometry CPU scenarios passed, followed by native live recorder downloads on desktop and phone. Marker: `V10_5_SHEEP_RUN_RECORDER`; artifact: `swyrl_engine_v10_5.html`.

The opt-in recorder introduced by v10.5 works across native starters and custom projects. Full capture records each observed Play update; 10 Hz and 2 Hz settings offer smaller state logs while retaining timed commands/events. It retains the starting map, actual seed, hierarchical object/limb poses, camera, input, health/lifecycle and game state. After Stop, the latest three runs can be scrubbed through a spectator schematic, object-follow view or recorded camera and exported as JSON, text or offline HTML. Simulate creates no recordings. Exports preserve a run beyond the current tab; the viewer reconstructs captured states rather than rerunning gameplay or exporting a rendered video.

## Historical verified v10.4 · House lanes and physical creature traffic

The v10.4 release is verified live: merged source `6d04109c27dfcd7e732e2550f3184db82755e999`, final trigger `04ba3ef018d4715cd51fd56ff51b1f96d8530bc6`, [deployment 38317704872](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38317704872) and [hosted audit 38317774602](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38317774602). It seals **64 patches, 23 assets and 1,520,413 bytes**, SHA-256 `f2c2eeb2a28d91239b3cb7afd48c0d189373a260bd12a851e3aaa8fd92524a2d`. All six engine workflows, eleven desktop/phone browser suites and 13 continuous-geometry CPU scenarios passed, followed by 17 live controls cases per layout and exact hosted source/assets. Marker: `V10_4_SHEEP_LANES`; artifact: `swyrl_engine_v10_4.html`.

Sheep can build at their feet, moving to the nearest clear side; blocked construction rejects without moving the builder or charging gold. Houses remain **2.4 × 2.4** and snap flush together or with a **0.6-unit lane**, with preview and collision using the same placement. Wolves retain **0.78-unit** default bodies and approximately 15% larger artwork; sheep retain **0.27**. Wolf bots prioritize reachable visible sheep over buildings. Physical creatures do not overlap on the same floor: blocked ground traffic replans or backs out; raised-route traffic waits. Wisps and decoys stay intangible, rescue chooses a free landing, and native preflight rejects overlapping same-species starts.

## Historical verified v10.3 · Placement above the finger

The v10.3 release is verified live: merged source `de24b04c95e13993313b0abd3496b6fb2602c9be`, final trigger `d0442216bf82ee82fb9df0aaefc8aa345d3f36c0`, [deployment 38312154843](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38312154843) and [hosted audit 38312197696](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38312197696). It seals **63 patches, 23 assets and 1,501,714 bytes**, SHA-256 `6b0f2f461ea2bb1595e0be2ef4dbc58a114ecb39bd8e1828ac745cd0b7ed2653`. All six workflows and eleven desktop/phone suites passed, followed by 13 live controls cases per layout and exact hosted source/assets. Marker: `V10_3_SHEEP_TOUCH_OFFSET`; artifact: `swyrl_engine_v10_3.html`. Touch previews remain above the finger and release builds at that displayed footprint.

## Historical verified v10.2 · Sheep selection and ground placement

The v10.2 release is verified live: merged source `0144031ae3b35630de1eb969fd05f7c0efbade74`, final trigger `3bf7004e716c3bea29f3f3e683d33c0700ef8669`, [deployment 38273428696](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38273428696) and [hosted audit 38273499402](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38273499402). It seals **62 patches, 23 assets and 1,487,394 bytes**, SHA-256 `2c0d10636bda9cf6062e6ec49d8173a77a104fa208c841d6eda4d48409a9ba35`. All six workflows and eleven desktop/phone suites passed, followed by eleven live controls cases on each layout and normal Projects/Play checks. Sheep use deliberate double taps to select buildings; single taps keep movement available. A terrain-following grid, filled footprint and green/red boundary show full house, wall and ramp extent. Marker: `V10_2_SHEEP_TOUCH_PLACEMENT`; artifact: `swyrl_engine_v10_2.html`.

## Historical verified v10.1 · Sheep Tag Design Archive

The v10.1 release is verified live: merged source `86aa05b494db007d9aebc073f0c7242756376447`, final trigger `1779223f8b92024f2625e68046ad9582ca80f594`, [deployment 38223924840](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38223924840) and [hosted audit 38224004659](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38224004659). It seals **61 patches, 23 assets and 1,464,129 bytes**, SHA-256 `ef72eb9177a81537c5f6f56f65d620ac9593b4e08da6eae4f1bc4e34b5c9b8f1`. All six engine CI workflows and ten desktop/phone browser suites passed, followed by nineteen live archive cases on each layout. Marker: `V10_1_SHEEP_TAG_ARCHIVE`; artifact: `swyrl_engine_v10_1.html`. These receipts certify v10.1.

The player's **SE_Sheep_Tag_Complete_Design_Archive.docx**, prepared 11 October 2026, guides this starter. Choose **Sheep Tag · Moonbell Meadow** in **Projects** or use `?project=sheep-tag-meadow`; `scenes/sheep-tag-moonbell-archive.swyrl.json` retains **92 baked actors, six populated layers, eight sheep and three wolves**, with twelve thorns, two no-build zones, the central wisp pen and four merchants. The default **Archive** preset enables thorn sensing, nine-house totem conversion, connected raised routes and Illusive Split; events remain off. **Classic** independently retains survival, construction, wolf demolition and wisp rescue. Values remain provisional and adjustable.

**Map Creator** provides terrain painting, hazards, landmarks, spawns, no-build zones, species path previews, independent map Save/Load and native Play/Stop revision. The released 66-actor meadow and all prior media remain preserved. Pond cleansing, advanced illusion tiers, automatic structural collapse and a future multi-game hub remain outside this release's scope.

## Historical verified v10.0 · Sheep Tag Starter

The v10.0 release is verified live: [PR #106](https://github.com/kaministrator999-ui/Swrlzkamico/pull/106) merged engine source `a06c89ed9e6cd65737de111efc11cac268519449`; [deployment 38174454216](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174454216) and [hosted audit 38174501776](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174501776) succeeded on final trigger `87b6a4be9319be30ac22b99212d773a289d2b199`. It seals **60 patches, 1,290,101 bytes**, SHA-256 `abcab023bbec0b5cacc72d7b845096060feb56418ab12b9eacee62bf9b7bf8c4`, and 22 assets. All six engine CI workflows and all nine desktop/phone browser suites passed, followed by fourteen live gameplay cases on each layout. The native Save Project map retains 66 actors in four populated layers, six sheep, two wolves, one pen and four merchants. Editor validation reported zero issues and warnings. Marker: `V10_0_SHEEP_TAG_STARTER`; artifact: `swyrl_engine_v10_0.html`. These receipts certify the released v10.0 starter.

## Historical verified v9.9 · Episode Shuttle Controls

The v9.9 release is verified live: [deployment 38150826816](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150826816) and [hosted audit 38150874160](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150874160) succeeded on final trigger `a382b4ea577c0a72f0223ef2aa4aad650121a5bf`. Merged engine source `4eb6021976e999bb84b9b915d2a9546cdb569a18` seals **59 patches, 1,139,928 bytes**, SHA-256 `60dfa8da434eaa6cfe578f441a93be1fb9139676933e985a19919c13938b60c9`, and the unchanged 21 media assets. All eight desktop/phone browser suites and six engine checks passed. Watch Episode Rewind/Fast forward buttons cycle **2× → 4× → 8× → normal 1×** beside the chapter skips. Pause, scrubbing and chapter changes preserve signed speed; boundaries pause at normal speed, and Replay/Stop/Explore/close/new screening restore 1×. Player speed remains session data. Marker: `V9_9_EPISODE_SHUTTLE_CONTROLS`; artifact: `swyrl_engine_v9_9.html`. These receipts certify v9.9; v10.0 requires its own validation and final deployment.

## Historical verified v9.8 · Full-length Mage Staff

The v9.8 release is verified live: [deployment 38115297536](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38115297536) and [hosted audit 38115324306](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38115324306) succeeded on final trigger `6cd814f925a79759a8b65b11af46895ce14014a2`. Merged source `35936a688fe14eeb06a4db90d1c3d8a5a1a8fb70` seals **58 patches, 1,133,438 bytes**, SHA-256 `d486985beb2e92ba9ad237ea6e5313dcffb7f53e9b5e69c3b54aca24e4a9b5b8`, and 21 assets. Its flaming skull crown, uninterrupted black-and-gold shaft, fitted hand grip and pointed foot stay connected during poses and the opening from the book. The saved `staffArt: "painted-full-v1"` profile and **Use full-length staff** preset retain native fitting, Undo/Redo and Save/Load; original/custom atlases retain their artwork. All seven desktop/phone browser suites and hosted native Play/Watch, Reset, Undo/Redo and Save/Load passed. Marker: `V9_8_FULL_LENGTH_MAGE_STAFF`; artifact: `swyrl_engine_v9_8.html`. These receipts certify v9.8; v10.0 requires its own final deployment and hosted audit.

## Historical verified v9.7 · Ornate Mage Staff

The v9.7 release is verified live: [deployment 38099380535](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38099380535) and [hosted audit 38099404177](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38099404177) both succeeded on final trigger `a5366aaf269ee3ad248dc380855ef440cdc67358`. Merged source `63d5924557598706f79703324a5eac0ad0114a7b` seals **57 patches, 1,111,978 bytes**, SHA-256 `0e1d8a7cbf90e956714245364d923107d7c8d0e8ab8476aa7b81e0fcbad43ac3`, and nineteen assets. It added ebony grain, gold inlay, slim rounded bands and fitted end caps to the existing round pole while preserving the natural grip. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_7_ORNATE_MAGE_STAFF`; artifact: `swyrl_engine_v9_7.html`. Its short painted staff-head cutout remained separate from that long core; v9.8 replaces that cutout with full-length painted artwork. These receipts certify v9.7; the v10.0 candidate requires its own final deployment and hosted verification.

## Historical verified v9.6 · Natural Staff and Painted Faces

The v9.6 release is verified live: [deployment 38071280266](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38071280266) and [hosted audit 38071311391](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38071311391) passed on final trigger `f164ccd37ce8ffd28cbc28ce4dea9b4f64ed7178`. Merged source `b21f0dd3072ada0f157e4f75b041c008d861a8cb` seals **56 patches, 1,099,583 bytes**, SHA-256 `d78dedc68ae0fe7bcbd368ee949bb2926c6f9bf321586e5254ad3fb97c1f07bd`, and nineteen assets. It introduced the saved natural-grip profile, continuous round shaft, fitted crest, larger painted facial features, exact face-cache inputs, consistent Canvas rasterization, opacity-preserving mouth blending and deterministic staff motes. All seven desktop/phone browser suites passed before deployment; hosted native Play and Watch passed on desktop and phone. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_6_NATURAL_STAFF_PAINTED_FACES`; artifact: `swyrl_engine_v9_6.html`. These receipts certify v9.6; the v10.0 candidate requires its own final deployment and hosted verification.

## Historical verified v9.5 · Fitted Staff and Character Relief

The v9.5 release is the previous verified checkpoint: [deployment 38013962412](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013962412) and [hosted audit 38013986565](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013986565) passed. Source `49b82022de841a26a4692359751395ca792efc9f`, final trigger `dcab50950603fb4160615e0d6bf5e0ec8558b06e`, seals 55 patches, 1,075,201 bytes, SHA-256 `bbfee8886ae48164b8bda7864a6d5ae773994a91cd953bea0f1d7820a44ccedb`, and 16 assets. It introduced the saved staff mount and per-piece character relief. These receipts certify v9.5; the v10.0 candidate requires its own final deployment and hosted verification.

## Historical verified v9.4

The previous v9.4 Socket Puppets and Book Emergence release is verified live: [deployment 37942614513](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942614513) and [hosted audit 37942679834](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942679834) passed. Source `511668bf024b1c225ff3280ef14837152e4602a2`, final trigger `fd1b3812a5445ee335328da7e6a34e1e7c0e1c1d`, seals 53 patches, 1,044,257 bytes, SHA-256 `cd761d29218dc36d0f0626968bfa9882584388c55f84411ce37caac16f4c1f01`, and 15 assets. These receipts certify v9.4; the v10.0 candidate requires its own final deployment and hosted verification.


**Role:** canonical entrypoint for §wyrl§ Engine / browser world-engine work.

**Invocation:** `§tart §E` or `@GitHub §tart §E` means enter the dedicated §wyrl§ Engine lane, reconstruct current GitHub/Hugging Face truth, and continue independently from the §wyrlz AI Chat/LALM application.

## Canonical lane

```text
§wyrl§ Engine
GitHub: kaministrator999-ui/Swrlzkamico
  -> projects/swrlz-forge-moba/    (legacy path retained for lineage)
  -> .github/workflows/deploy-swrlz-forge-moba.yml
  -> HF Space: kamiloki/swrlz-forge-moba
  -> https://kamiloki-swrlz-forge-moba.static.hf.space/
```

## Startup contract

### Inherited full-station execution ownership

`§tart §E` inherits the **Cross-chat full-station execution ownership** rule from `§wyrlz_§tart.md` even though it routes into a separate engine lane.

For §E work:

- the user owns fundamental engine/product/design decisions;
- §wyrlz owns implementation/finishing, validation, dedicated-engine deployment handoff, and repair of §wyrlz-caused implementation/deployment defects;
- a syntax/build/package/deploy defect introduced by §wyrlz is repaired and revalidated/redeployed in the same work turn when safely possible;
- a failure showing the underlying engine behavior/design itself must change returns to the user for that product decision;
- retries remain bounded and evidence-driven, and must reuse the existing §E GitHub/Hugging Face lane rather than creating replacement infrastructure.

A fresh ChatGPT conversation must reconstruct this behavior from the repository; do not depend on prior-chat memory.

On `§tart §E`:

1. Read this router and the engine README.
2. Read `source-manifest.json`, `build_space.py`, every listed patch module, and `SPACE_README.md`.
3. Inspect current GitHub main, latest §wyrl§ Engine deployment workflow, and Hugging Face Space state.
4. Preserve the hard deployment boundary from the main §wyrlz AI Chat/LALM Space.
5. Preserve project separation: Engine core ≠ MOBA example ≠ Dragon's Den project data.
6. Preserve source integrity and compatibility aliases.
7. Validate final generated HTML and JavaScript before merge.
8. Merge validated changes to `main`.
9. Follow the dedicated engine deployment to terminal state.
10. Require the actual served static host to contain the current deploy marker before reporting success.

### Atomic starter-pack draft & engine-upgrade handoff (v215 source guidance)

For user-owned §E work that derives a native project seed into an eventual editor starter or new game mode, read [`docs/engineering/SWRLZ_ENGINE_PACK_AUTHORING_V215.md`](docs/engineering/SWRLZ_ENGINE_PACK_AUTHORING_V215.md) alongside the v214 ladder. This describes the current two-file **unregistered data draft** and the separate steps for Projects registration, per-game controls, mode-specific rules, deterministic ordered engine patching, desktop/phone tests, PR review and dedicated §E release. A plain scene clone or descriptor must never be reported as a playable mode, and no AI Chat Hugging Face deployment may publish engine work. This documentation has no deployment authority.

### GitHub/AI editor-and-starter development ladder (source-only)

For a §wyrlz AI session that aims to edit this §E editor, derive native starter packs, build new playable modes or update engine internals, consult `docs/engineering/SWRLZ_ENGINE_AGENT_V214_BUILD_LADDER.md` after this start router. It distinguishes real current GitHub tool capabilities (verified source mapping, planned work, approval-gated scene draft and draft PR) from not-yet-supported multi-file patch generation, automatic starter registration, engine release, or verified live gameplay. The specialized §E build and dedicated deploy rules in this document remain authoritative. Reading this reference is non-deploying.

### Coder education cross-reference (conditional, non-deploying)

When teaching a coding model about §wyrl§ Engine source, Three.js, Python ordered patches, animation data, character sockets or Forge build validation, also read `training/coder/PROJECT_STACK_ARCHITECTURE_V1.md` and its public practice exercises `training/coder/project_stack_architecture_v1.json`. If a *new language* or platform integration is specifically being studied (Kotlin/Java/TypeScript/Rust), also inspect `training/coder/CROSS_LANGUAGE_CURRICULUM_V2.md` as **non-executable education**; it does not convert this engine to another toolchain or change the governed engine build. Post-discovery task-size coaching is continued in `training/coder/MODEL_MATURITY_DISCOVERY_V4.md` (only optional educational examples; no engine/runtime activation or release authority). Model task-size and verification coaching is separately taught by `training/coder/MODEL_MATURITY_EFFORT_V3.md`; this reference cannot activate the v182 opt-in classifier or touch the dedicated §E release gate. Those exercises are **ungraded**, do not train model weights, and do not replace this router's mandatory engine source-manifest/build/deploy rules. Chat/LALM model-route instruction remains owned by the separate Programming LALM Runtime Architecture. This curriculum link itself is documentation-only and must not trigger an engine deployment.

## Supported book opening and limb sockets

The existing coordinated opening brings Kami, §wyrlz, architecture, props, effects and the three star-depth shells out of the pages before they reach their saved stage positions. Preview Frame, Play and Watch use the same saved opening. Persistent limb sockets keep snapped children attached while their pose keys rotate around the connection.

In **Animation Studio → Book Opening · unfold from the pages**, enable **Expand from book** and set **Opening duration (s)**. Choose an **Opening layer**, adjust **Start delay (s)** and **Expansion time (s)**, then use **Apply Book Opening**. Preview the first seconds and use Play to inspect the expansion. Changing the overall duration scales the other layers’ timings; every layer must finish within the opening. Native Undo/Redo and Save/Load preserve the opening separately from the stage, limb, face and scenery keys.

To connect and pose a limb, select **Kami** or **§wyrlz** in Animation Studio and expand **Character Rig · limbs and face → Limb Sockets · snap and rotate**. Choose a **Socket body piece** and its incoming attachment or a named outgoing socket. **Socket X/Y/Z** use the painted piece’s centre: incoming **attach** defines the rotation pivot, while an outgoing socket places its attached child. Use **Apply Socket** to place the connection. **Detach Piece** releases the selected child; **Snap to Socket** reconnects it to its anatomical parent. Animate the snapped limb with the existing pose controls. **Show joint sockets** displays editor guides; Running Play and Watch hide those guides. **Reset Piece Sockets** restores the selected connections while preserving pose keys. Snapped pieces stay connected through shoulder, elbow, wrist, hip, knee and ankle motion; each hand has a prop grip.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-performance.swyrl.json`; the full-staff export remains preserved for import. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Saved per-character rest layouts, 468 limb/face keys, 383 scenery keys and the action/effect overlays remain independent. The v9.6 natural-grip, v9.5 staff-grip, v9.4 sockets, v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all eleven artwork PNGs and the historical episode HTML.

The 54th and 55th patches retain the staff mount and per-piece relief. The 56th, `patches/v9_6_natural_staff_painted_faces.py`, retains the compact grip and painted facial features; the 57th, `patches/v9_7_ornate_staff.py`, retains socket-attached shaft ornament. The 58th, `patches/v9_8_full_length_staff.py`, integrates the full painted staff and native preset; artifact `swyrl_engine_v9_8.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_8_FULL_LENGTH_MAGE_STAFF`. The 59th, `patches/v9_9_episode_shuttle.py`, adds signed episode shuttle playback; v9.9 artifact `swyrl_engine_v9_9.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_9_EPISODE_SHUTTLE_CONTROLS`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging contains nine episode scene JSON exports, the historical episode HTML and eleven PNGs, for twenty-one media assets. The 60th patch, `patches/v10_0_sheep_tag.py`, adds the separate native Sheep Tag starter; v10.0 artifact `swyrl_engine_v10_0.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V10_0_SHEEP_TAG_STARTER`. The native meadow map raised the v10.0 package to 22 assets. The 61st patch, `patches/v10_1_sheep_tag_archive.py`, adds the verified archive rules and creator. The 62nd, `patches/v10_2_sheep_touch_placement.py`, adds double-tap sheep building selection and ground placement guides; `swyrl_engine_v10_2.html` and `V10_2_SHEEP_TOUCH_PLACEMENT` identify the historical v10.2 release with the same 23 assets. The 63rd patch retains touch aim above the finger, the 64th retains house lanes and physical creature traffic, and the 65th adds the opt-in Play-run recorder and post-Stop review. The 66th adds the separate Frostveil Maul tower-defense starter, with its native scene as the 24th packaged asset. The 67th reshapes that starter around the classic upper bays, crossbar and shared ship funnel, with a new native scene as the 25th asset. The 68th adds scattered grouped arrivals, visible phone placement and an empty default build area; its separate native map is the 26th asset. The 69th adds the animated story and native action/effect editors; the new performance export is the 27th asset.

The verified v10.8 source and production receipts are recorded above. The current v10.9 candidate requires its own sixteen-suite desktop/phone browser matrix, six engine workflows, all four sealed CPU suites, final dedicated deployment and exact hosted package audit.

## Historical verified v9.3 · Connected Character Pieces

The previous **v9.3 Connected Character Pieces** release is verified live: [deployment 37893678594](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893678594) and [exact hosted audit 37893722231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893722231) passed. Source [`84d8966f4240`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/84d8966f4240cef8ebe037dbc03baac43099c06e) seals 52 patches, **980,767 bytes**, SHA-256 `caba518b67524567899d93a74308bc894cf40413fd69b330b8f7f5f7b6c042be`, with all fourteen media assets. These receipts certify v9.3; v10.0 requires its own final deployment and hosted audit.

## Historical verified v9.2 · Layered Scenery and Fitted Faces

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-depth.swyrl.json`; the v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

Open **Animation Studio**, select **Background**, **Midground**, **Atmosphere**, or **Effects**, then expand **Scenery Depth · individual cutouts**. Choose a **Scenery piece**, set its depth and pose at the shared playhead, and use **Add/Update Scenery Key**. **Layered scenery**, **Pop-out depth**, and **Apply Scenery Depth** control the depth assembly. Preview Frame, editor Play and the native Watch cinema use the same saved renderer; native Undo/Redo and Save/Load retain each piece’s edits. Pause running Play before authoring. Camera protection keeps the background behind the mages and the foreground/book below their face and body corridor.

The 51st governed patch is `patches/v9_2_depth_theatre.py`; artifact `swyrl_engine_v9_2.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_2_LAYERED_SCENERY_FACES`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging includes four episode scene JSON exports, the historical episode HTML, and eight PNGs including the new transparent `assets/anime/scenery-parts.png` atlas.

The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify the historical v9.2 release.

## Historical verified v9.1 · Articulated Paper Rigs

Kami and §wyrlz now use separate articulated paper rigs. Each mage has independently jointed torso, pelvis, head, cape, upper/lower arms, hands, upper/lower legs, and feet, plus character-specific staff/quill or grimoire props. Joint keys save real X/Y/Z rotations and part depth; per-character paper thickness and pop-out depth give the limbs room in front of the scenery. Faces save Neutral, Happy, Determined, Surprised, or Sad expressions together with blink, mouth openness, smile, brow, gaze, and optional mouth motion driven by saved dialogue cues.

The project keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Limb and face tracks live separately under `project.animeRigs` (`anime-character-rigs-v1`), so posing one mage does not overwrite the other mage or the existing shot timeline. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json`; the v9.0 storybook export and original 62-actor production scene remain bundled.

Open **Animation Studio**, select **Kami** or **§wyrlz**, then expand **Character Rig · limbs and face**. Use **Apply Character Depth** to save thickness/pop-out settings. Choose a body part and edit **Lean X**, **Turn Y**, **Bend Z**, or **Part depth**, then **Add Pose Key** / **Update Pose Key** at the shared playhead. **Face & Expression** exposes expression, blink and mouth; **Gaze, smile and dialogue motion** adds smile, brow, gaze and saved-dialogue mouth movement. Pose and face keys use Linear/Smooth/Hold easing, Preview Frame, native Play/Pause, Undo/Redo, and Save/Load.

The 50th governed patch is `patches/v9_1_character_rigs.py`; artifact `swyrl_engine_v9_1.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_1_ARTICULATED_PAPER_RIGS`. Exact bytes and SHA-256 come from the final sealed manifest and generated receipt. The package includes the new rigged scene and `assets/anime/kami-rig.png` / `swyrlz-rig.png`, while preserving all previous artwork, scenes, and screening assets.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

These are jointed 2.5D paper characters with rigid overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history.

## Historical v9.0 · Native Animation Studio and Paper Theatre

The **Ghosts in Different Forms · The Page That Remembered** starter is now authored and saved through the native editor. Its 134 second episode has eight story beats and nine independent tracks: Camera, Kami, §wyrlz, Background, Atmosphere, Midground, Effects, Foreground, and Book. Kami is the larger horn-hooded mage; §wyrlz is the smaller hovering skull mage. Newly generated transparent character artwork and independent scenery plates follow the supplied gothic amber/gold references.

The exported `projects/swrlz-forge-moba/scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json` contains **70 actors and 11 editor layers**. Eight new saved paper actors each own a layer; the original 62 production set actors, three production layers, eight workstations, and eight destinations are preserved. Native `animeCel` and `animeBook` actors persist through Save/Load, with the timeline under `project.animeTimeline`.

**Animation Studio** edits camera position/target/FOV, individual cast/scenery/book keys, numeric transforms, easing, visibility, opacity, unfolding, episode title, and timed dialogue. Preview Frame and the editor Play button use the same native renderer. Timeline and artwork changes use native Undo/Redo and Save Project; PNG, WebP, and JPEG artwork can replace a saved layer. The **Capture Actor Pose** workflow copies a track's native Inspector pose into a keyframe.

Reusable engine implementation lives in `runtime/anime_timeline.js`, `runtime/anime_stage.js`, `runtime/anime_editor.js`, their CSS, and the 49th governed patch `patches/v9_0_animation_studio.py`. Physical mesh cards unfold around bottom-edge hinges, with protective scenery depth, a low foreground/book, and adaptive portrait framing. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_0_AUTHORED_PAPER_THEATRE`; artifact: `swyrl_engine_v9_0.html`. Exact integrity is recorded in the sealed manifest/build receipt.

Native desktop and phone authoring/Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555). Production authority is recorded in the final `DEPLOY_REQUEST.json`, the dedicated deployment receipt, and the exact hosted-release audit. Live completion requires terminal deployment success and exact served source/artwork verification. The original **Watch Episode 01** remains the historical 2D screening; native Play runs the saved paper theatre. Skeletal posing, lip sync, audio authoring, and MP4 export remain unimplemented. See `ANIMATION_STUDIO.md` and `VERIFICATION.md` in the engine project.

Direct starter: https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01 .

## Historical verified v8.9 · Camera-safe Pop-Up Storybook

Android playback revealed the v8.8 set/desk card and book obscuring the actors. Source patch `projects/swrlz-forge-moba/patches/v8_9_cinematic_staging.py` lowers the animated book, makes the foreground a thin bottom border with transparent upper pixels, and enforces behind-the-cast architecture and effects. Tests check first/later scene occlusion geometry at phone and desktop sizes. v8.9 source: **48 patches**, `swyrl_engine_v8_9.html`, **647,639 bytes**, SHA-256 `da9f48941543c81062a232417ed8897e8c82e912852474cf2154e209c12ddf37`, marker `SWYRL_ENGINE_DEPLOY_MARKER: V8_9_CINEMATIC_STAGING_SAFE`. [Desktop/mobile Play/Save acceptance passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728474772); [production deployment passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728665723) and [independent hosted source+both media asset audit passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728754278). v8.9 is an earlier verified camera-safety checkpoint; its exact receipts and the older source remain preserved.

## Historical v8.8 candidate · 3D Pop-Up Storybook Video Creator

The **same Ghosts in Different Forms anime starter** now owns a proper popup-book miniature stage in the §wyrl§ Engine. A physical two-half-book/page model opens below individually hinged scenery planes: moonlit fantasy city, swirling atmosphere, gothic arches, decorated workshop, magic runes and desk props. **Kami** is the taller horned main wizard, **§wyrlz** the smaller book-wielding wizard, each a separate CanvasTexture cel and independently toggleable/animatable layer; the unrequested mascot is absent during the video cinematic.

**✦ Pop-Up Director** in the existing editor and cinematic controls authors each layer's Z depth, lateral offset, parallax, unfold delay and animation duration, serialized under `project.animePopUp` with safe bounds and included by **Save Project**. The first scenes pop open from a book rather than just replacing a flat slide.

- Patch: `projects/swrlz-forge-moba/patches/v8_8_popup_storybook.py`, appended after v8.7 (47 governed patches).
- Contract and honest art limits: `projects/swrlz-forge-moba/POPUP_VIDEO_CREATOR.md`.
- Regression test: `projects/swrlz-forge-moba/tests/native_anime_playwright.mjs` checks Play, director docking, individual cels, hinged pop-up cards, real project JSON save, mobile fit, Pause/seek/Explore/Stop.
- Governed v8.8 HTML: `swyrl_engine_v8_8.html`, **644,951 bytes**, SHA-256 `06c55a0d090bd6ffa9383ff44f914b922a841de7dc03284a50955cb4036478cd`, marker `SWYRL_ENGINE_DEPLOY_MARKER: V8_8_POPUP_STORYBOOK_DIRECTOR`.
- Candidate source and desktop/mobile Chromium editor + Play + Save verification [Actions 37726896000](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37726896000) passed; dedicated production deployment and exact live-host receipt still required.
- Existing projects and the separately bundled 2D Episode 01 remain intact. Native arbitrary keyframe editing, imported art assets and video export are **not yet implemented**.

## Previous v8.7 source authority · Layered 2.5D Anime Cels

The Anime Studio **Ghosts in Different Forms** starter is now a **2.5D cel/parallax experiment**: six independent sprite-depth layers (background sky, atmospheric effects, midground buildings, character cels, magical FX, foreground framing), original illustrated anime-style figures, and a real Three.js perspective camera for parallax. During **Play**, 3D editor actors/signs are temporarily hidden to keep shots readable, then restored on **Stop/Explore Set**. Subtitles are phone-safe; the in-cinematic **Layers** control toggles each render layer. Other starter project Play modes remain unchanged.

- New governed patch: `projects/swrlz-forge-moba/patches/v8_7_anime_cel_layers.py`, placed after v8.6 in `source-manifest.json`.
- Full governed composite: **46 patches**, `swyrl_engine_v8_7.html`, **624,633 bytes**, SHA-256 `6a58245bc1d19e3513ddc3a280a454c2d69e7c6c836ad18c65821f1b0816747b`.
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V8_7_ANIME_CEL_PARALLAX`.
- [CI candidate 37721928687](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37721928687) passed full source reconstruction, generated JS syntax, and actual desktop/phone Chromium cinematic/layer controls.
- **Limits:** The cels and shot transforms are authored programmatically; a general-purpose visual cel/timeline editor and audio/lip-sync/export remain future work. No claim of those features.
- Production success still requires dedicated `DEPLOY_REQUEST.json` triggering, terminal workflow completion, and exact served HTML and asset receipt validation.

## Previous v8.6 source authority · Native Anime Studio Play

Native 3D cinematic Play is now implemented specifically for the **Ghosts in Different Forms** starter. The 45th governed patch is `projects/swrlz-forge-moba/patches/v8_6_native_anime_cinematic.py`. Other engine starter templates continue to use ordinary first-person Play.

- Native Play sequence: scripted moving perspective camera, real-time temporary procedural performers, native dragon actor animation, particles and lighting, station-owned script captions, playhead slider, scene stepping, Pause/Resume, Stop, and **Explore Set** to hand control back to walking first-person runtime.
- Separate `Watch Episode 01` still opens the canvas animation. Do not confuse the 2D screening with the real-time 3D scene.
- The native cinematic shots are currently programmed, not authored through a general-purpose visual keyframe editor; MP4 export and lip sync are not implemented.
- Current governed artifact: `swyrl_engine_v8_6.html`; **611,675 bytes**, SHA-256 `1468357c5ce082b71548de983fd11f818cf4eeccb34eca3df92a0f15e3e94dc0`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V8_6_NATIVE_ANIME_CINEMATIC`.
- Reconstructed candidate and module syntax verified by [Actions 37719407233](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407233). Actual Chromium desktop/mobile Play, timeline, seek, subtitle, Pause, Explore and Stop verified by [Actions 37719407234](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407234).
- Production completion still requires dedicated deployment triggered by `DEPLOY_REQUEST.json`, terminal Actions success, served HTML SHA, and both episode/set asset hash checks.

## Previous v8.5 source authority · Anime Studio starter

Governed release candidate **v8.5 — Anime Studio Starter** extends v8.4's verified 43-patch chain with a 44th patch, `patches/v8_5_anime_starter.py`, keeping all existing releases and independent projects.

- Native selectable third starter: **Ghosts in Different Forms · Episode 01** (`anime-ghosts-ep01`).
- Native 62-actor stage scene, three layers, eight production stations, eight Play teleport destinations, guardian dragon, and wisp visitor.
- Original 2m14s procedural anime episode is **screened inside an editor modal**, not executed by a native 3D character/camera animation timeline.
- Scene source: `projects/swrlz-forge-moba/scenes/ghosts-in-different-forms-ep01.swyrl.json`.
- Episode source: `projects/swrlz-forge-moba/episodes/ghosts-in-different-forms-ep01.html`.
- Studio spec: `projects/swrlz-forge-moba/ANIME_STARTER.md`.
- Source manifest: `projects/swrlz-forge-moba/source-manifest.json`.
- Final HTML: **597,990 bytes**, SHA-256 `1d9111211897151c091a313dd0fbfa59bc3819ac744567dfd0465e7208e39f8c`.
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V8_5_ANIME_STUDIO_STARTER`.
- Dedicated Space still `kamiloki/swrlz-forge-moba`; deployed anime entry `?project=anime-ghosts-ep01`.

Candidate check [GitHub Actions #37717718014](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37717718014) reconstructed the source and passed generated JavaScript and Python syntax checks. This is **build evidence, not proof that the live host has deployed v8.5**. The deployment contract below remains mandatory.

## Previous v8.4 source authority

The governed release is **v8.4 — Wayfinding & Destination Preview**. Embervault remains the default Dragon Den. Starforge is an independent celestial workshop with its own scene, workspaces, environment, and travel zones. This contract supersedes the historical default-avatar and layout checkpoints below.

```text
base:
  swrlz_forge_v4.html
  bytes 99591
  sha256 a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856

patch chain:
  patches/v4_1.py
  patches/v5_projects.py
  patches/v5_1_swyl_engine_seed_den.py
  patches/v5_2_first_person_twin_stick.py
  patches/v5_3_groups_immersive_den.py
  patches/v5_4_wisp_avatar.py
  patches/v5_5_dragons_natural_look.py
  patches/v5_6_dragon_ground_contact.py
  patches/v5_7_precision_contact_camera_speed.py
  patches/v5_8_wisp_alpha_foot_support.py
  patches/v5_9_wisp_soft_contact_history.py
  patches/v6_0_researched_glitch_dragon_den.py
  patches/v6_1_glitch_den_project_card.py
  patches/v6_2_glitch_den_parity.py
  patches/v6_3_glitch_den_apex.py
  patches/v6_4_single_glitch_den_dragon_v3.py
  patches/v6_5_glitch_den_runtime_default.py
  patches/v6_6_wisp_hover_dragon_ik_idle.py
  patches/v6_7_contact_tools_fix.py
  patches/v6_8_den2_ground_snap.py
  patches/v7_0_fracture_forge_ascendant.py
  patches/v7_1_fracture_forge_breathing_room.py
  patches/v7_2_wisp_locomotion_repair.py
  patches/v7_3_engine_health.py
  patches/v7_4_editor_workspaces.py
  patches/v7_5_mobile_editor_chrome.py
  patches/v7_6_desktop_editor_polish.py
  patches/v7_7_canonical_glitch_den_project.py
  patches/v7_8_layers_desktop_docks.py
  patches/v7_9_sanctuary_canonical_project.py
  patches/v8_0_sanctuary_primitives.py
  patches/v8_0_layer_integrity.py
  patches/v8_0_workspace_tools.py
  patches/v8_0_walkable_levels.py
  patches/v8_0_embervault_project.py
  patches/v8_1_performance_graphics.py
  patches/v8_2_bootstrap_repair.py
  patches/v8_3_zone_teleport.py
  patches/v8_3_editor_authoring.py
  patches/v8_3_starforge_assets.py
  patches/v8_3_projects_release.py
  patches/v8_4_zone_editor_preview.py
  patches/v8_4_wayfinding_release.py

final:
  swyrl_engine_v8_4.html
  bytes 533612
  sha256 58252d18ee4fedf3acb9b5ccbb8e19dbc10c421345deb507a016151ab1ceca62

marker:
  SWYRL_ENGINE_DEPLOY_MARKER: V8_4_WAYFINDING_ZONE_PREVIEW
```

### Current projects and editor contract

The Anime Studio starter joins Embervault and Starforge as an independent project. Current v10.9 authoring uses 70 actors, 11 editor layers, nine stage animation tracks, independent limb/face/scenery keys and saved story action/effect overlays in the native Animation Studio editor. The 134 second paper theatre runs through Preview Frame and Play. Watch Episode opens the pop-up cinema using the same native scene and chapter controls; its original static HTML media asset remains bundled. See the current v10.9 contract above.

Embervault Atelier is a spatial workspace for future VR, project work, and conversation. Its native saved scene lives in `projects/swrlz-forge-moba/scenes/embervault-atelier.swyrl.json`. The 170-actor assembly has lower workshops at 0m, a study gallery at 3.4m, and the dragon council at 4.6m, with physical ramps between them. It has six stations and eight teleport destinations. Three organizational editor layers are distinct from these physical elevations.

Starforge Observatory lives in `projects/swrlz-forge-moba/scenes/starforge-observatory.swyrl.json`, with seven floating islands, six stations, seven travel zones, and three organizational layers. Its lower islands, upper archives, companion chamber, and observatory use supported bridges and ramps. Project-owned environment settings control sky, fog, exposure, terrain, and scenery. A project-configured fall threshold returns a walking visitor to the validated Arrival zone.

Both projects store text/code files and notes at their workstations, support file download and workspace JSON import/export, and preserve work through Save Project/reload. Explicit imported project data is authoritative over local drafts. Chat stations open the existing LALM application. Headset rendering, VR controller input, executable coding sessions, and in-room inference remain future integrations.

In Play, **T** or **Zones · T** opens a project-specific travel menu. The editor’s Teleport Zones panel authors name, description, world feet position, yaw, and accent without needing an actor selected. Travel requires a visible approved supporting surface with clearance for the walking visitor; invalid, hidden, blocked, edge, or airborne pads are rejected. Travel releases pointer lock, clears movement, uses a short fade, and preserves prior pause state. Zones persist with project history and Save/Load.

### Destination preview contract

Both projects continue through native editing and Play. The Den's compact arrival directory sits beside the central route, and its signs distinguish lower workshops from upper study. Starforge's Garden guide sits at the perimeter, keeping the Observatory and twin ascents in sight.

The global Teleport Zones panel offers opt-in **Show destination markers** and **Frame destination**. Device-owned preview preferences create transient editor-only rings and heading arrows at authored world feet coordinates. Helpers are not actors, saved project data, selectable objects, supports, or collision blockers. Load, history, destination edits and project changes refresh them; Play/Simulate hides them. Framing is Editor-only, follows the chosen world point, preserves orthographic axes, and leaves visitors and project data untouched. Landing safety still requires testing in Play.

Preserve manual actor visibility separately from layer toggles and runtime shell visibility. Dynamic visitors remain world-root actors. Native prefab calls must return null for unknown assets without modifying the previous selection. New templates must reset inherited empty organizational layers. Use engine source, native editor authoring, and actual Play together; fix capabilities when authoring or walkthroughs expose missing behavior. Plans live in `DEN_DESIGN.md` and `STARFORGE_DESIGN.md`.

### Performance contract

Graphics & Performance retains Auto/Low/Medium/High/Custom presets, render scale, shadows, render caps, and independent FPS/frame-time overlays. Preferences persist locally. Scaling changes rendering, not project data or simulation semantics. Initialization runs only after scene creation at final bootstrap.

### Historical v8.4 release receipt contract

This documentation stages the release; it does not claim production completion. Source authority resolves to the validated normal release commit immediately preceding the final v8.4 `DEPLOY_REQUEST.json` commit. Deployment authority resolves to that trigger and the dedicated Actions run whose `head_sha` matches it. Require terminal success, marker, and exact served-source integrity after removing only the recognized Hugging Face creator script. Report the exact run and live page after verification, without mutating release content after the trigger.

Previous verified release: v8.3, 528670 bytes, SHA-256 `ca4d43e2e560aee39a0fff48b07885d180d96dc64cbeb5c5bd00bdf23490d548`, deployment [37697374632](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37697374632), trigger `d10953ee23fcefc8e66a6e2ee86b7b2e51421313`, validated normal source `9c357e8adac2a1728842405dbb9d4c2fc6b806fd`. Its exact live SOURCE/marker/hash and both desktop projects were verified.

Historical verified release: v8.2, 393393 bytes, SHA-256 `d7dc50a0697eb9bf5286131ff6dcaaae4fda7f3db7a3ecede90e8e1b0ef38935`, deployment [37689304845](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37689304845), trigger `177ecda58e928f6d9f590069e1bdb1ddb538145e`.

## Grouping contract

§wyrl§ Engine now supports hierarchical editor groups.

- desktop additive selection: Shift/Ctrl/Cmd
- mobile additive selection: Multi Select mode
- Group creates one transform parent without destroying child objects
- Ungroup restores child world transforms
- groups serialize their IDs and parent/child relationships
- groups can be nested and duplicated
- grouped child collisions use world transforms
- dynamic actors with CharacterMovement, PhysicsBody, LaunchPad, or Combat remain independent for runtime correctness

The default Den must use grouping for architectural assemblies where useful rather than leaving dozens of structural pieces as unrelated root objects.

## Historical Dragon's Den v5.7 contract

The default Den is an **immersive cavern**, not an outdoor/MOBA-style map.

Organization at this checkpoint:

```text
Wake Nook
    ↓
Main Council Chamber
├── Creator Alcove
├── Throne Side
├── Dragon Perch Side
├── Portal Hall Exit
├── Memory Vault Exit
└── Inference Core Exit
```

Environment requirements:

- cave/stone floor palette; no visible creek/grass treatment
- high enclosed cavern shell
- roof may be multi-piece internally but should be grouped as one editor object
- runtime roof/shell must not obstruct ordinary editor visibility
- preserve first-person immersion
- default Den visitor/player avatar is the Wisp form, not the old blue capsule
- Wisp visuals are procedural glow/particle-style geometry; do not depend on copied Warcraft assets
- keep arbitrary launch-pad mechanics out unless explicitly requested

## Engine naming and compatibility

User-facing name: **§wyrl§ Engine**.

Preferred APIs:

- `window.SWYRL_ENGINE_BUILD`
- `window.SWYRL_ENGINE_AGENT`

Legacy `SWRLZ_FORGE_*` aliases remain active for compatibility.

## Deployment truth contract

```text
reconstruct base
→ apply governed patch chain
→ verify final bytes/SHA
→ syntax-check generated module
→ upload dedicated static Space
→ obtain actual HF host
→ fetch served page
→ require the current manifest/release SWYRL_ENGINE_DEPLOY_MARKER
→ SUCCESS
```

Never equate upload success with live serving success.

## Prior verified checkpoint

v5.2:
- GitHub: `c9c9e03d37ab31cac71342390a27eb0c403cadb3`
- HF: `df0b0f58e31e7b66185b615d6bf489d470d6c924`
- SHA-256: `e3ea58f80f83a2b001f087f5852b6ce7fa5a4dbf4af2f5d67c414eb46c196ad8`

A later verified v5.3 checkpoint must supersede this after deployment.


## Verified v5.3 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.3

GitHub source/deploy commit:
659e9b46f804ad69f2a8f4ea04dd58fc6760323e

Final source:
146986 bytes

SHA-256:
ef68a0906430de83a5da464efe864eed26e757f03d6fdce5e81df6411c75f995

Hugging Face revision:
33b1405f2628d67e81b70021e03d5c947b8d831c

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_3_GROUPS_IMMERSIVE_DEN

Live verification:
PASS on attempt 1
```

v5.3 is the current observed engine state at this checkpoint. The default Den uses hierarchical architectural groups and the improved cave-floor / vaulted-roof layout.


## v5.4 Wisp avatar contract

Dragon's Den boots with **Wisp Visitor / Creator** as its player avatar.

- visually inspired by the classic glowing Wisp / Sheep Tag readability
- built from procedural additive sprites, a bright core, orbiting motes, trailing wisps, team glow, and hover/pulse animation
- no Warcraft model or texture asset is bundled
- serialized as a normal `hero` actor with `avatarStyle: "wisp"` and blueprint `BP_WispVisitor`
- saved projects reconstruct the Wisp correctly
- first-person camera uses the Wisp's lower eye height
- first-person body hiding includes sprites as well as meshes so the glow does not obstruct the camera
- Blank Starter World and MOBA retain their existing player pawn styles


## Verified v5.4 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.4

GitHub source/deploy commit:
afb098ba8a046640608f4b1f2e23e76ab15e09e2

Final source:
151952 bytes

SHA-256:
add2c872e99097285a4ed68372aae3c6f7a42dff4cac4315771c56e8e9c0aea5

Hugging Face revision:
15d26de311d793b41833a83f2b3dc123444d16b3

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_4_WISP_AVATAR

Live verification:
PASS on attempt 1
```

The default Dragon's Den player at this v5.4 checkpoint was **Wisp Visitor / Creator**, using the procedural Wisp visual system. The current v8.0 default is defined above.


## v5.5 camera-look contract

Default first-person look must be non-inverted horizontally:

```text
right stick right → camera turns right
right stick left  → camera turns left
right stick up    → camera looks up
right stick down  → camera looks down

pointer-lock mouse right → camera turns right
pointer-lock mouse left  → camera turns left
```

Do not silently restore inverted horizontal look as the default.

## v5.5 Dragon anatomy contract

The Dragon's Den procedural dragon model is **BP_DragonAvatarV2**.

Required visual direction:

- recognizable dragon silhouette at both near and far camera distances
- articulated bat-like wings; avoid giant rectangular/slab wings
- segmented neck and curved tail
- distinct chest and haunch forms
- four articulated legs with feet/claws
- readable muzzle/jaw/head structure
- horns, brows, eyes, teeth, ears, and dorsal spines
- shaded/tinted belly and dark accents; avoid large pure-black blocks that read like missing geometry
- preserve the deliberately massive scale relative to the Wisp/player


## Verified v5.5 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.5

GitHub source/deploy commit:
e08e45fee17b0fb3cd91057771341b679cd6aefc

Final source:
155355 bytes

SHA-256:
76410c2340664c0754ad2a50e7be858f7223787e89cb6f10c4360577cc27f4e2

Hugging Face revision:
2a7706416cd5c9248c41e0d7347f5cb2d0a11b6c

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_5_DRAGONS_NATURAL_LOOK

Live verification:
PASS on attempt 1
```

v5.5 is the current observed engine state at this checkpoint. The default Den keeps the Wisp player, uses natural horizontal look input, and uses the procedural Dragon anatomy v2 model.


## v5.6 dragon contact contract

- all four dragon feet must be explicit and readable, including rear paws
- wings should use articulated finger bones and segmented membrane panels rather than flat slabs
- `SurfaceFootContact` raycasts each dragon foot downward against baked scene meshes and terrain
- feet may settle onto rocks, pedestals, and uneven architecture
- lower shin orientation follows the planted paw
- slope tilt is clamped to prevent broken poses
- contact range / leg stretch is clamped
- terrain fallback remains armed when no mesh is hit
- this system stays in §wyrl§ Engine only; no chat UI work belongs in this lane


## Verified v5.6 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.6

GitHub source/deploy commit:
3b2f29aac2460d0d184592651b37699477f8329d

Final source:
161347 bytes

SHA-256:
c4c0d88febfdfa2bf1c9b02925c6abd9ddafe05010ec5917dac2cd8eb05886e4

Hugging Face revision:
0e2ed2bdb98b7450931208be0fefe51b3a579f4d

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_6_DRAGON_GROUND_CONTACT

Live verification:
PASS on attempt 1
```

v5.6 is the current observed engine state at this checkpoint. Dragon wings use the detailed multi-finger membrane pass, all four feet are explicit, and dragons use reusable raycast-based surface foot contact for rocks, pedestals, uneven architecture, and terrain fallback.


## v5.7 precision contact + camera-speed contract

- dragon foot grounding uses multiple sole samples, not a single center ray
- highest valid sampled contact controls vertical planting so rock/pedestal corners do not pass through the paw
- nearby hit normals are averaged before slope alignment
- contact sampling is reused across all dragons per frame
- teeth remain inside the mouth silhouette and must not protrude through the lower jaw
- the editor top bar exposes a continuous camera speed slider
- that slider controls orbit rotate, pan, and wheel/scroll zoom together
- range: 0.35× to 3.00×
- the chosen camera speed persists locally
- mobile editor views must keep the slider accessible
- runtime/PIE look sensitivity remains separate from editor camera speed


## Verified v5.7 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.7

GitHub source/deploy commit:
a68a7f363897c1bb4dbdc092eb051e2d176126b5

Final source:
163645 bytes

SHA-256:
62fbe228f4ee412c17be53429239159a400bc02bd1f94b5c1b7760f85645c04a

Hugging Face revision:
12e481b45ffd5b808047ee183ea9b6a9bd79fcca

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_7_PRECISION_CONTACT_CAMERA_SPEED

Live verification:
PASS on attempt 1
```

v5.7 is the current observed engine state at this checkpoint. Dragon feet use multi-sample sole contact to reduce rock/pedestal penetration, dragon teeth are tucked inside the jaw, and the editor top bar includes a persistent 0.35×–3.00× camera speed slider for rotate/pan/scroll zoom.


## v6.x + mandatory §E update protocol

Historical v7.6 preserved Dragon's Den — Seed Chamber and made Glitch Dragon Den — Fracture Forge its exact structural variant: the same architecture, layout, rooms, placements, exits, collision structure, and camera framing with the glitch identity layered on top. The current v8.0 canonical project is Embervault Atelier, defined above.

Every intentional GitHub mutation involving §wyrl§ Engine (§E), its source/build/deploy files, or its §E documentation is a governed §E update. For EVERY such update:

1. Reconstruct current main and live Hugging Face truth before editing.
2. Apply the §E change while preserving the Engine / MOBA example / Dragon's Den project-data boundaries and the separate §wyrlz AI Chat/LALM lane.
3. Synchronize the engine version everywhere the shipped/versioned state changes. Manifest, generated artifact, README, Space README, deploy marker, workflow verification, §tart §E router, and roadmap must not disagree.
4. Update projects/swrlz-forge-moba/ROADMAP.md in the same update. Record what changed, version/marker, source/deploy commit, deployment status, and live verification. Governance-only updates may retain the current engine binary version but still require a roadmap entry.
5. Validate reconstruction, bytes/SHA, generated JavaScript, and compatibility aliases.
6. Commit/merge the governed §E update to main.
7. After every intended §E source/code/UI/docs/version/roadmap change is finished and validated, the **LAST repository mutation** is the deliberate deployment-button update to `projects/swrlz-forge-moba/DEPLOY_REQUEST.json`. Updating this dedicated trigger file is how ChatGPT manually presses deploy. Do not use ordinary §E files as deployment triggers.
8. That final trigger-file commit starts the dedicated production deployment workflow. No §E release content may be changed after pressing it; any required fix starts a new update cycle.
9. Follow the deployment workflow run to terminal state and require that its source/head commit is the final trigger commit.
10. Require the actual served static host to contain the expected current SWYRL_ENGINE_DEPLOY_MARKER. Upload success alone is not live success.
11. In the user-facing completion response, ALWAYS provide both the exact GitHub Actions workflow-run link started by the trigger-file commit and the live §wyrl§ Engine page link: https://kamiloki-swrlz-forge-moba.static.hf.space/ . Do not report completion before both checks pass.

Canonical roadmap: projects/swrlz-forge-moba/ROADMAP.md

### Final deploy button procedure

The production workflow watches **only** `projects/swrlz-forge-moba/DEPLOY_REQUEST.json`. This file is the intentional final deploy button; it is not ordinary release content.

When the §E update is completely ready — source/code/UI work finished, version surfaces synchronized, roadmap updated, exact build/integrity validation passed, and all normal release commits already on `main` — **press deploy exactly once by updating `DEPLOY_REQUEST.json` as the final repository mutation**. Record the release version/marker, current source integrity SHA-256, and a reason identifying the completed release. Commit that trigger update to `main`.

The workflow must not watch patches, manifest, README, router, workflow definition, or other normal §E files. Those can be edited freely during development without deploying live. Do not add broad push paths back to the production workflow.

After pressing the deploy button:

1. Make no further §E release mutations while treating that deployment as current. If something is wrong, begin a new update cycle.
2. Find the Actions run created by the `DEPLOY_REQUEST.json` trigger commit and verify its head/source commit matches that final trigger commit.
3. Follow the exact run to terminal success.
4. Inspect deployment receipt/state and verify the served static page contains the expected current marker/version.
5. Return the exact Actions run URL and live §wyrl§ Engine URL to the user.

**Mental model:** BUILD/EDIT → VERSION → ROADMAP → VALIDATE → FINAL NORMAL COMMIT → update `DEPLOY_REQUEST.json` (PRESS DEPLOY) → WORKFLOW → VERIFY LIVE → COMPLETE.

Never substitute `workflow_dispatch`, an arbitrary watched source file, or an intermediate commit for this repo's dedicated final deploy-button mechanism.

Sealed HTML: **2,621,375 bytes**, SHA-256 `d0db24152221ea1dfd4ecc284f65686af71f74c770d4c7c15134979d98b77494`. Local native authoring completed 14 recorded edit groups, exact Save/reimport and eight review views. The 283-part set retains 1,623,252 measured triangles (heroine 1,339,364; head 48,768). The focused phone Apply/Undo, invalid-section/import and surface-cleanup/Undo checks passed.
