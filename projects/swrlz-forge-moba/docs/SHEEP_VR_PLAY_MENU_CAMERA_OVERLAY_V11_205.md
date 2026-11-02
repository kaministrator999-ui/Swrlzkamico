# §E v11.205 — Play-mode tactical camera, polished Quest menu targeting and OS overlay stabilization

## Issue tracking from the Quest 2 screenshots
**This is Sheep Tag while PLAYING, not the engine editor.** Gameplay rotation and model-editor gizmos are intentionally unaffected.

| Observed issue | v11.205 correction | Acceptance scope |
|---|---|---|
| Current sheep view is too shallow/down at sheep level | Default TACTICAL camera: base vertical 18 vs 6.5, keeps base horizontal 21 and rear bias 2.5; at default 1.4 zoom, about 25.2 above/31.9 behind the sheep (~38° down). | Verify comfortable strategic top-down world angle without forced HMD rotation |
| Need placement near sheep without pointing at the floor | Keep independent v11.203 forward controller-to-ground projection and v11.204 rapid 3.6m housing grid. | Verify actual build ghosts and trigger hits match |
| VR wrist menu pointer appears behind the buttons | Render dot just in front of actual intersected menu button/backplate; raise reticle draw order only while menu open; block world hits when modal | Verify both left and right rays visually terminate on menu surface |
| Hover doesn't clearly highlight | Slightly enlarge/highlight hovered item, brighten label, add lightweight glow plate; optional haptic on hover transitions | Visible interactive feedback, no hidden buttons |
| Big flat/blurred radial | Menu scale 86% of prior, one cached 12-point sparkle ring, subtle halo, better 384x192 cached label resolution | Legibility plus low texture upload count |
| Want an explicit camera option | In Sheep Tag game's existing full VR wrist menu add VIEW → TACTICAL / FORWARD. | User can switch views without resetting headset tracking |
| Quest native settings overlays cause lag and camera reactions | Check WebXR session visibilityState. During visible-blurred/hidden skip camera-reference translation, cosmetic fog paints, and hold-wheel actions; require button release when returning | No involuntary build on resume, XR camera stays anchored |

## Input/optimization guardrails
- Left/right controller default accents remain cyan/amber. Hover on menu changes highlight, not permanent hand identity.
- **No new render loop, particles emitter, heavy postprocessing or physics change.** Glow/points are fixed cached geometry per radial page and cleaned up with the existing XR session.
- Native sheep navigation, rapid A building, independent left X skills, capture/tools, LAN authority, resource/obstacle validators, mobile/desktop controls and both editors remain source-of-truth.
- The Quest OS overlay support cannot command Meta's compositor. It only reacts to the WebXR visibility state exposed to a web page.
- This is a focused Play-mode patch, **not** a completed level/map art overhaul, fog visual redesign, or spatial window editor. Those remain tracked scope.

## Technical test
`node projects/swrlz-forge-moba/tests/test_v11_205_tactical_menu_overlay.cjs` covers camera profiles, menu action routing, exact menu reticle target, left/right beam differentiation, UI focus, allocated cached effects and hardware-overlay input protection. All previous v11.204-v11.181 XR and game regressions plus final deterministic 237-patch HTML verification run in GitHub Actions. Physical Quest 2 FPS and view comfort require actual headset verification.
