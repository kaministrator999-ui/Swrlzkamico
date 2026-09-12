# Server 2.3.72 — Ice Dragon full-resolution wallpaper

Date: 2026-09-12

## Versions

- Server runtime: 2.3.72
- Web Chat: 1.4.66
- LALM engine: 2.1.26 unchanged
- LALM UI: 1.0.0 unchanged

## Evidence

The adult Ice Dragon wallpaper was rendering but visibly blurred/pixelated. A user-initiated Vercel redeploy did not improve quality, which ruled out deployment propagation. Runtime inspection showed the active v13 loader still fetched `adult-180x320.jpg.b64` and expanded that source across `.messages` using `background-size: cover`.

The runtime tree already contained the intended full-resolution source split into six ordered Base64 chunks named `adult-864x1536.part000.b64` through `adult-864x1536.part005.b64`. The source JPEG header identifies the intended 864×1536 dimensions.

## Change

Added `web/themes/ice-dragon/ice-dragon-art-loader-v14.js` as the smallest targeted evolution of v13.

- Preserves `.messages` as the single adult wallpaper owner.
- Preserves the proven Blob URL + browser image decode + direct paint path.
- Preserves single-flight hydration and independent companion loading.
- Fetches the six full-resolution chunks concurrently.
- Concatenates them strictly in numeric order.
- Normalizes Base64 once after concatenation.
- Adds explicit logs for part fetch, combined payload length, decode dimensions, and final paint state.
- Rejects unexpectedly low decoded dimensions to prevent silent regression back to a tiny source.

`runtime_pages/manifest.json` advanced from v6 to v7 and points directly to `ice-dragon-art-loader-v14.js`.

## Stale-manifest compatibility

Live verification showed the v14 asset was already served from `runtime`, but the fixed live manifest route was temporarily still returning manifest v6 and therefore referencing v13. Rather than making browser acceptance depend on that propagation window, the existing v13 path was converted into a small compatibility bridge that loads the unique v14 full-resolution script URL.

This makes both manifest generations converge on v14:

- stale manifest v6 → v13 compatibility bridge → v14
- current manifest v7 → v14 directly

The live v13 asset endpoint was verified returning the compatibility bridge, and the live v14 endpoint was verified returning the full-resolution hydrator.

## Concurrency / authority check

The transaction baseline was Server 2.3.71 / Chat 1.4.65. Immediately before assigning versions, both authority files were re-read and remained unchanged. The event therefore advanced to Server 2.3.72 / Chat 1.4.66.

## Deployment state

This is a `runtime` hot update. No new Vercel deployment or server restart is required. The user's preceding redeploy was useful evidence but did not address the actual low-resolution source.

## Acceptance

After Chat reload with Ice Dragon selected, Theme Logs should show:

- `v13-bridge-start` / `v13-bridge-loaded` when the stale manifest path is used, or direct v14 execution when manifest v7 has propagated
- `adult-part-fetch-start parts=6`
- `adult-parts-complete parts=6 ...`
- `adult-decode-ok 864x1536`
- `adult-painted ...`

The adult wallpaper should be materially sharper than the former 180×320 path.

## Lineage

- v14 full-resolution hydrator: `7f82590e30ae6b6da77e3407b739a05c1df32b51`
- Manifest v7 activation: `3c1fce86ce392618e2eff15db26d914faa2c48bc`
- Server version authority: `32ff3c525c0c6471b6bed129414e8ce21d0b9a02`
- Chat version authority: `7074153de81d57d7d4af063b02239cfb5e5a1b8f`
- Roadmap update: `7a4b299cf0d2368c2a097c79647c5fef7aa71aa0`
- v13 stale-manifest bridge: `18eb73b15ee585993c1cadd5d81f5ed4db133533`
