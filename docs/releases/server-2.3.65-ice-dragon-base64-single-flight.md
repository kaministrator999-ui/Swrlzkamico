# Server 2.3.65 — Ice Dragon base64 normalization + single-flight hydration

**Date:** 2026-09-11  
**Server runtime:** 2.3.65  
**Web Chat:** 1.4.59  
**Deployment:** NONE  
**Restart:** NONE

## Trigger evidence

The exported in-product theme diagnostics showed the adult wallpaper asset returned HTTP 200 and 7713 characters, then failed at browser `atob()` with `InvalidCharacterError`. The same trace showed the companion asset becoming ready and painting correctly while the adult remained `ready=false`, with `.messages` present. The log also showed multiple overlapping boot-time asset fetches for the same two files.

## Changes

- Added `web/themes/ice-dragon/ice-dragon-art-loader-v13.js` as a new versioned runtime asset.
- Added explicit Base64 normalization before decoding: whitespace removal, URL-safe alphabet normalization, removal of non-Base64 characters, terminal-padding normalization, and an explicit invalid-length guard.
- Added normalization receipts to theme diagnostics so raw/compact/clean/padded lengths are visible.
- Added single-flight promises for companion hydration, adult hydration, and overall theme hydration so overlapping boot triggers join the same in-flight work instead of issuing repeated duplicate requests.
- Preserved independent companion/adult failure domains: adult wallpaper failure cannot remove the juvenile companion.
- Advanced runtime manifest to version 6 and routed Chat to the unique v13 hydrator path.

## Verification

- Runtime authorities were re-read immediately before version assignment and remained Server 2.3.64 / Chat 1.4.58.
- Live Vercel runtime returned the v13 hydrator from the `runtime` branch with HTTP 200.
- Live runtime manifest returned version 6 and references `ice-dragon-art-loader-v13.js`.
- Final Android browser visual verification and a fresh Theme Logs export remain the acceptance gate for adult wallpaper decode/paint.

## Lineage

- v13 hydrator: `71897a437e25671f9b8ffd0c30e4e24f3bdccc86`
- manifest v6: `48542b3d5c84989b72d37eafb8f73188f88fd219`
- Server authority: `9d0c9a74f2396c1dc5d8a8ff5776be9daef5ab93`
- Chat authority: `d34f402afbae88102960fd8b93ddbda69654593b`
