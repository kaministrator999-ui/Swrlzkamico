# §E v11.206 — Sheep Tag Quest meadow and fog-art foundation

## Why a focused phase
The physical Quest 2 screenshots show broad dark blue-green terrain areas, noisy fog depth and visually plain grass/roads. The native Sheep Tag scene includes **authored 80m/128m meadow grounds**; the runtime may have solo or LAN team fog. Changing underlying navigation or 2D authoring data for appearance would risk collision, build clearance and other game mechanics.

## Delivered work
The Play-only world renderer adds one transparent, non-interactive ground layer, generated in 12 short incremental batches and uploaded only once. Seeded four-region colors, meadow flowers/clover and a gentle cobbled border around the central sanctuary make the map richer while retaining its existing layout and roads. Visual flowers avoid center, cross and diagonal approach routes; they add no collision or authored editor nodes. Only a single new textured plane is drawn and its texture uses mipmap filtering to avoid distant VR shimmer.

The native fog receives a cosmetic alpha/depth adjustment while retaining the original fog canvas, solo/guest painter functions, team visibility masks, exploration memory and entity filtering. Because the fog plane is above the added ground art, unexplored regions do not reveal new map detail. All material changes are restored when the user leaves immersive VR.

## CPU/GPU budget and cleanup
- One 768×768 transparent texture (~2.3 MB RGBA before GPU formats); one plane and one material.
- At most 110 simple flecks per XR frame during initial decoration; paused whenever Quest system UI, photo mode or §E wrist menu is active. Exactly one texture upload on completion.
- No additional render loops, real-time particles, terrain raycasters, shadows, physics colliders or texture updates while exploring.
- Dispose plane, material and texture on match stop, XR cleanup or session change; restore the native fog material and texture filter state.
- Diagnostics: `window.SWYRL_ENGINE_SHEEP_MEADOW_FOG_206.diagnose()`.

## Compatibility
Keep v11.204 A/X hold and quick house lattice, v11.205 tactical camera and foreground menu pointer, v11.203 mapped controller placement, all editor gizmos, multiplayer visibility authority, saved map/scene data and 68 bundled source assets unchanged.

## Honest remaining scope
This is **not** a total map rebuild and does not claim to eliminate all fog banding observed in-device. Next iterations should inspect Quest frame captures / timing with the new meadow layer, then pursue region-specific landmarks, richer lod/instancing and safe platform-specific fog improvements. Full movable spatial windows and controller remapping are separately tracked in issue #320.

## Verification
Focused regression `node projects/swrlz-forge-moba/tests/test_v11_206_meadow_fog.cjs` and previous v11.205–v11.181 regressions run in CI; strict checksum/ordered-patch verification before merge. Hardware performance/visual acceptance is performed on actual Quest 2 after deployment.
