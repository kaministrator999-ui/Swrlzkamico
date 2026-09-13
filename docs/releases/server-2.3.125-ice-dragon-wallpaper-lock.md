# Server 2.3.125 / Web Chat 1.5.5 — Ice Dragon wallpaper lock

## Event
Runtime-hot Web Chat visual fix.

## Reported symptoms
- Refresh could initially show the intended Ice Dragon/castle artwork, then later revert to the former blurry dragon artwork.
- Composer/backing glass was too heavily blurred.
- The desired visual hierarchy was a lighter blurred lower backing layer with a darker shaded input field on top.
- Chat bubbles also blurred the wallpaper more than desired.

## Root cause
`web/themes/ice-dragon/ice-dragon-art-loader-v17.js` still owned an obsolete adult-wallpaper hydration path. After first paint, it could reconstruct/load the former 864×1536 JPEG from the legacy six-part asset/cache path and write that image directly onto `.messages`. This overrode the canonical `.workspace` wallpaper and produced the observed late visual reversion.

`web/chat_frontend_boot.js` also still accepted the legacy `swrlz.theme.iceDragon.adultPreview.v2` localStorage image as an early wallpaper source, leaving another stale-image path available.

## Changes
- Retired adult wallpaper ownership from `ice-dragon-art-loader-v17.js`; the loader now hydrates companion/avatar art only.
- The legacy adult-preview localStorage key is purged.
- Any inline `.messages` wallpaper properties left by the old path are removed; `.messages` remains transparent.
- `chat_frontend_boot.js` always first-paints the canonical repository PNG on `.workspace` and no longer accepts the legacy adult preview.
- `ice-dragon-shell-v1.css` was tuned to use a lighter outer composer glass layer at reduced blur and a darker inner composer field at reduced blur.
- User/assistant bubble backdrop blur was reduced so the wallpaper retains more detail.
- Runtime manifest advanced to v38 for cache invalidation.

## Authorities
- Server Runtime: 2.3.125
- Web Chat: 1.5.5
- Manifest: 38

## Concurrency
Before assigning versions, authorities were re-read and found at Server 2.3.124 / Web Chat 1.5.4 / Manifest 37 due to concurrent Ice Dragon brand work. This event advanced from those values and preserved the v37 brand stylesheet and chat behavior.

## Deployment / restart
Runtime-hot only. No production server redeploy or restart required.

## Verification state
Repository/runtime source update complete. Live/browser visual acceptance pending user refresh.
