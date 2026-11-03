# §E v11.238 candidate: Quest Game menu slowdown and 2D workspace redesign

## Quest 2 report — 2026-11-02
The owner tested Sheep Tag in immersive VR. Head tilts and turns were acceptable until the
small circular VIEW / BACK / FORWARD / TACTICAL menu was opened. After that, FPS degraded,
world and fog appeared to drift, portions of sheep models vanished, and the circle menu itself
disappeared without a deliberate close action. Quest Browser screenshots of Game Engine and
Model Atelier show overlapping/clipped buttons, especially the top control rails and the
right-hand wolf Motion editor/tool rail.

These are *two separate* issues: **an in-game WebXR modal causing degradation** and a
**narrow floating 2D browser-window layout**. Meta Quest native window tiling is not exposed
to the webpage.

## Confirmed source path
- The circle in the VR screenshot is the §E `se195` tool radial's `view` page, not
  the `se204` A/X quick-build wheel.
- `se195XRFrame` positions and ray-tests the dial every XR frame, with v11.205 adding
  another hover/raycast path. Menu page switches rebuild textured meshes by calling
  `se195Text`, and `se195DisposeRadial` immediately disposes the page's textures.
- `se211OnFrame` assumes any WebXR callback gap over 170 ms (up to 30 seconds)
  indicates a Meta system-overlay interruption, even when the XR visibility state
  is still `visible`. It neutralizes the controller modal, temporarily blocks
  `se193XRFrame`, and `se211Cosmetics` hides the in-game radial for ~950 ms.
  This is a concrete path for the owner's disappearing menu symptom.
- v11.168 forces 48px minimum Quest buttons into the 48px game topbar;
  v11.187 pins a sticky Game Engine nav inside the same horizontal scroll area.
- v11.119 and v11.120 use a dense top Model Atelier action row, and a separate
  floating tool rail can overlap the inspector in a small Quest Browser window.

## Candidate code
1. For visible-session **application menu** gaps between 170 and 650 ms only, avoid
   mistaking a slow menu render for loss of OS focus; preserve the Quest overlay
   guards for actual `visible-blurred`/`hidden`, >650-ms interruptions, and
   existing recovery/held-button-release states.
2. Preserve user-open radial and independent spatial panels during still-visible
   performance recovery instead of hiding them as if a native Meta dialog was open.
3. Cache radial ray-test results once per frame/pose and cache label textures
   across menu page changes, releasing them on XR session cleanup.
4. In the Quest 2D Browser profile only: one horizontally scrollable workspace
   tab strip, existing native Game Engine topbar controls in a real Controls drawer,
   and the Model Atelier's existing header actions in a Model actions menu
   (native Close stays visible). Dock the existing modeling tool rail as an
   on-demand Edit tools popup rather than overlapping the inspector.
5. All real controls move as DOM nodes with existing event listeners intact;
   no duplicates or shadow controls. Quest UI opt-out restores the native
   ordering. No player mechanics, physics, fog visibility, camera position,
   model geometry or VR controller mapping are changed.

## On-headset acceptance
- Enter Sheep Tag Play. Turn the head with radial closed, note responsiveness.
  Open **VIEW** circular menu and hold for >10s; rotate the head, move sheep
  using left stick, select FORWARD / TACTICAL, close/reopen VIEW.
  **Pass**: no spontaneous hiding or immediate lag spiral; selection works.
- Hold **A/X** building-wheel modal while moving the sheep. Left-stick movement,
  wheel selection and house placement must remain unchanged.
- Enter and leave the *actual Meta OS Camera menu* during VR Play.
  **Pass**: genuine blur/hidden still suspends input, then recovers without
  accidental builds or controls triggering.
- Use native game VR diagnostics:
  `SWYRL_ENGINE_QUEST_RADIAL_STABILITY_238.diagnose()`.
  Compare `appMenuSlowFrames` with v11.211's `callbackGaps`; the former
  should no longer force cosmetic menu disappearance.
- With §E opened in a resizable Quest Browser 2D window, check Game Engine
  tabs, Controls popover, Projects, Scene/GUI menus; then Model Atelier's
  Model actions, Edit tools, wolf Motion Play/Set key and inspector.
  Existing controls must remain accessible without covering each other.
  Also test switching Quest UI off and back on.
- If right-eye geometry tearing or sheep mesh disappearance persists with a
  steady radial, investigate stereo frustum/depth issues independently
  (the unmerged PR #363 explores this).

## Release status and coexistence
**Draft candidate only.** Based on `main` v11.236, intentionally independent
of draft PR #362 (camera/browser) and draft PR #363 (stereo culling). Do not
merge the two other candidates without reconciling version identities.

The official §E `RELEASE_PROCESS.md` requires adding the new patch to
`source-manifest.json`, rebuilding HTML to compute its exact SHA-256/length,
updating provenance and release verifiers, committing to main, then making a
separate `DEPLOY_REQUEST.json` release request. Without those checks, no live
publish claim is justified. User's Quest 2 hands-on tests are authoritative
for ergonomic and stereo acceptance; no broad browser CI required.
