# Web Chat 1.4.85 — Ice Dragon wallpaper v19

## Versions

- Server Runtime: 2.3.101 unchanged
- Web Chat: 1.4.84 -> 1.4.85
- Runtime page manifest: 21 -> 22
- Ice Dragon wallpaper controller: v18 -> v19

## Triggering evidence

- The direct v18 wallpaper URL returned HTTP 503 because the expected binary asset was not available through the live runtime asset route.
- The v17 fallback still renders the older 864×1536 decoded source with `background-size: cover`, which can magnify a portrait image past its native pixel density and visibly soften/pixelate it.
- The user-supplied artwork is already the intended source and must not be browser-upscaled, canvas-resized, or recompressed.

## Repair

- Added `web/themes/ice-dragon/ice-dragon-wallpaper-v19.js`.
- v19 attempts the direct supplied-art asset first and uses the browser bytes as-is: no canvas, no resize, and no recompression.
- A fresh cache namespace/key prevents the older direct-wallpaper cache generation from being treated as current.
- If the direct binary route is unavailable, v19 deliberately falls back to the existing decoded source and changes the chamber geometry to `background-size: contain`, centered, no-repeat. This prevents `cover` from zooming that fallback beyond its native detail while keeping the chat functional.
- Manifest v22 replaces the v18 controller with v19 while preserving the existing theme controller, companion path, committed-output v3, RMCCA transport tracing, and recovery stack.

## Acceptance

- Theme Logs should show `wallpaper-v19-decode-ok` and `wallpaper-v19-painted-direct` when the direct binary asset is available.
- Until that binary route exists, logs should show `wallpaper-v19-direct-unavailable` followed by `wallpaper-v19-fallback-fit`; the visible wallpaper should no longer be cover-zoomed into additional pixelation.
- A direct asset HTTP 200 remains the final gate for using the exact supplied image bytes rather than the fallback source.

## Deployment boundary

- Runtime-hot only; no stable Vercel redeployment is required.
- This event does not modify the LALM engine or Server Runtime version.
