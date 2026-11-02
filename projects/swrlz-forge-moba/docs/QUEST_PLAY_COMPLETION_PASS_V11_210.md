# §E v11.210 — Coordinated Quest 2 Play-mode completion pass

## Source-of-truth safeguards
This is Sheep Tag **Play**, not the Game Editor or Model Editor. A/X house/skill radial selection, 3.6m house lattice, unrotated game buildings, native collision/nav/anti-trap, server/team fog, real controller tracking and editor grips must remain unchanged. Meta Quest OS menus are not controlled by the web application.

## Delivered across the remaining work areas
1. **3D level graphics:** world-periphery biome waymarker posts and crystals, two instanced draw calls maximum, only in XR Play. No new scene actors or physical blockers; existing detailed native trees, farms, stone/pond models, forest and sanctuary remain. v11.208 four regional ground styles remain in use. A full new authored world geometry set is not completed by this cosmetic pass.
2. **Rendering and fog:** preserve the earlier v11.208 plane depth guard and original fog masks; collect real fog render CPU timings and texture upload counts. Native compositor work cannot be eliminated from app code; explicitly test Quest system overlays and fog banding on real headset. Quality toggle does not change fog game logic.
3. **Independent spatial workspace:** SESSION → WORKSPACE → CAMERA / BUILD / SKILLS / METRICS / CONTROLS opens world-space panels that can coexist, each with ray priority, right-grip 6DoF movement/tilt, stick scale while grabbed, top-left follow toggle, top-right close and bottom corner scale adjustments. Changes saved in localStorage as head-relative offsets so a later WebXR session can restore a sensible layout without using stale absolute tracking coordinates.
4. **Controller configuration:** WORKSPACE → QUALITY/controls gives classic A/X, both stick-click, hybrid A/left-stick-click, haptic toggle and hold speed. This is configurable **Play-mode quick-wheel** input, not unrestricted arbitrary editor binding. Default remains A hold/tap building and X hold/tap skills; B tools, Y recenter and joystick movement unaffected.
5. **Quest frame diagnostics:** rolling FPS/frameMs, renderer calls/triangles, live GPU texture/geometry counts and measured fog painting time plus Quest visibility-overlay count. Performance/Auto cosmetic profiles hide optional 3D props if low frame rates persist. No unsupported WebXR framebuffer reconfiguration.
6. **Ability polish:** Mirror and Totem panels and radial use native `stArchiveStatus(unit)` remaining cooldown, unlock status, one-use availability and actual density conditions. The actual game validator remains authoritative. Countdowns refresh about once per second, not with fresh textures on every render frame.

## Interaction quick guide
- **Right B**: full app tools menu → SESSION → WORKSPACE.
- **Point+right grip** on a §E panel: move and angle; release pins it.
- **Right stick while gripping**: resize.
- **Trigger on pane top left**: follow-head toggle; **top right**: close; **bottom corners**: scale; **center**: context action (camera view, quality or input profile).
- **Hold A/X then release**: equip house/skill, **tap A/X** to build/cast. Selected input profiles may substitute stick-clicks.
- **WORKSPACE → QUALITY**: select input mapping, haptics and hold-duration profiles.
- Head-relative layout stores contain no identity/biometric data, only panel offsets/settings.

## Evidence and limitations
Unit mocks and SHA-verified builds cannot establish real Quest 2 comfort, fog flashing or sustained frame rate. Leave hardware acceptance and deeper 3D world geometry/independent rich panel styling open in issue #320 until tested and implemented.

Test with the new `test_v11_210_quest_perf.cjs` and `test_v11_210_workspace.cjs` plus all prior v11.209 and older XR/editor/ARPG regressions. Release through deterministic source manifest (242 patches, 68 assets), merge PR and separate checksum-pinned deployment request.
