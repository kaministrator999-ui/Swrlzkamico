# §E v11.196 — Sheep Tag fog and Quest radial/camera recovery

## Owner Quest 2 screenshot evidence
The Oct 31 screenshots show parallel flickering-looking lines over both the fog and underlying textured terrain while Sheep Tag is playing on the **flat floating browser screen**. In the **native immersive XR scene**, the user reports a mirror-read radial, menu movement while pointing, and headset motion sweeping toward unintended areas. These are separately diagnosed; the earlier v11.195 XR-only fog change could not fix the 2D view.

## Source changes
- **Shared 2D + XR fog-depth repair.** The transparent fog plane originally sat at y=0.055, only 0.015 units above the Sheep Tag meadow surface at y=0.04. Keep one coherent fog plane at y>=0.23, with depthTest on, depthWrite off, negative polygon offset. Skip redundant canvas/texture repaints for about 210 ms in 2D and retain the 290 ms XR limit. Only cosmetic fog rendering is batched: authoritative visible/explored arrays, game mechanics and networking remain unchanged.
- **Right-hand radial orientation and stability.** An inverted Matrix4 lookAt turned the plane's back toward the headset (the menu was rendered double-sided, making words appear mirrored). Use Object3D.lookAt(head eye) with the proper +Z-facing plane front. Anchor the menu at open or page-change, once, near the right pointer in the head's field of view; do not chase the pointer while selecting. Preserve modal ray hit interception from v11.195.
- **Safe camera startup.** On entering authored Sheep Tag XR cinematic, preserve the native sheep/house animation but lock a centered viewpoint rather than chasing the animated sheep centroid each frame. Block editor flying and grab movement in that cinematic. On entering the VR match, snap once to an elevated, sheep-centered strategy view instead of flying ~25 world units at high speed. Preserve free camera panning, yaw/zoom and Y follow/recenter during play.
- **Explicit REFOCUS.** The VR main radial now offers PLAY / REFOCUS / CAPTURE / CONTROLS / EDIT. REFOCUS intentionally reanchors the cinematic viewpoint; no hidden automated flying/orbiting occurs.
- **Telemetry.** SWYRL_ENGINE_SHEEP_VR_FIX196.diagnose() exposes fog draw/coalescing counters and radial/camera anchor counts. All previous XR capture, controller visuals, project saving, §C chat, Model Atelier and Emberfall stay available.

## Acceptance
Focused Node regression checks cover VR menu facing/anchoring, modal priority, browser fog depth/render cadence and one-time camera repositioning. Headless Chrome tests should verify native Sheep Tag menu, Play, Stop, fog geometry and console errors. A user Quest 2 run is still needed for actual stereo flicker, FPS, wrist comfort and long-match acceptance—these cannot be established by browser tests.

## Source integrity
228 ordered patches, 68 packaged assets, 7,295,859 bytes HTML, SHA-256 679d14774b8abb97254f1adf072b98f0db51bbad152a2567142105155b944ca1.

Code: runtime/engine_xr_sheep_stability_v11_196.js, patches/v11_196_sheep_fog_radial_camera_recovery.py. Validate with tests/test_v11_196_quest_fog_menu.cjs and scripts/verify_v11_196_release.py. Release requires a separate checksum-pinned DEPLOY_REQUEST.json commit, followed by host-side byte verification.
