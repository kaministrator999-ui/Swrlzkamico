# §E v11.197 — Sheep Tag meadow anti-aliasing and efficient fog/camera

## What prompted this
The Quest 2 screenshots supplied by the owner show thin stripes, moiré and frequent shimmer across the meadow/fog even inside the ordinary floating browser screen. v11.196 fixed a translucent fog-depth overlap and VR radial/camera drift; further inspection found a second, independent cause: the meadow canvas painter draws a 1-pixel periodic grid every 30.72 texture pixels. Minification of such fine repeated lines at oblique angles makes them crawl visually as the camera moves.

## Changes

- **Actual starter terrain:** current Sheep Tag's main playable map uses the original 4K **Moonbell Wildwood** image, rather than the legacy 1024px meadow canvas. Explicitly configure mipmaps for its texture; when Quest Browser is detected, draw a one-time high-quality 2048px prefiltered copy before the GPU upload. Leave original 4K source art and desktop detail untouched. This is the rendering path tested in live gameplay.
- **Meadow visual:** remove only that repetitive decorative crosshatch while retaining paths, foliage, color stippling, the original 80×80 native ground, collision, and saved map geometry. Use linear mipmap minification, linear magnification and hardware-bounded anisotropy up to 8 for steadier oblique views. This applies to fresh native meadow visuals in both browser and WebXR (without replacing the engine or project files).
- **One fog presentation owner:** do not let the standalone soft fog canvas overwrite the multiplayer Sheep Tag fog visual painter when the LAN match is active. Team-vision calculation, enemy hiding, shared building vision, gameplay rules and networking stay owned by existing match logic. Solo visual fog retains v11.196 depth separation and paint budget.
- **Flat browser camera:** replace the 60-Hz full `stStatus()` serialization inside `stUpdateCamera` with direct selected/controlled native unit coordinates, maintaining WASD/arrows pan, follow flag, camera zoom/portrait fit and two original selection rings. Recalculate projection only when fov actually changes. Do not override the immersive WebXR camera owned by v11.196.
- **Diagnostics:** `window.SWYRL_ENGINE_SHEEP_VISUAL_197.diagnose()` reports meadow mipmapping/anisotropy, frames and avoided snapshot calls, fog painter suppression and normal renderer call count.

## Validation
Focused test `tests/test_v11_197_sheep_visual_stability.cjs` validates direct follow, camera panning, ring selection, no per-frame `stStatus`, exclusive LAN fog painter and no unwanted immersive camera updates. Run previous Quest and Emberfall tests. Strict `scripts/verify_v11_197_release.py` reconstructs all 229 ordered patches, 68 existing assets, exactly 7,300,640 HTML bytes, SHA-256 `315e2acb7f54118fce4e428e534cceac14a0ecbaac596291df29ba6dbd7cc54d`. A one-time headless Chrome test additionally verifies the actual native Sheep Tag game meadow texture properties and flow.

## Hardware acceptance
The supplied images support a visual aliasing diagnosis, not a measured Quest GPU trace. Mipmapping and removing the subpixel grid address a known source of shimmer but do **not** establish that every terrain/fog artifact or delayed frame drop is solved. Confirm on Quest 2 in an extended match; compare visual stability and comfort with v11.196. Save a debug capture/JSON if an artifact remains. This is distinct from the earlier mirrored menu and moving-camera fix, retained unchanged.

No unrelated starter, Dragon Den, §C Chat, Model Atelier, saved project, VR camera or controller mapping changes in this release.
