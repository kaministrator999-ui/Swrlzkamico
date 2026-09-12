# Server 2.3.82 — Ice Dragon instant cached wallpaper preview

**Status:** source/live delivery verified; browser acceptance pending
**Server:** 2.3.82
**Chat:** 1.4.74
**Web Frontend:** 1.0.1
**LALM/R39:** unchanged
**Deployment:** NONE
**Restart:** NONE

## Update notes

- Keeps the frontend-first Chat architecture and adds a synchronous device-local Ice Dragon preview path for repeat visits.
- Ice Dragon v16 stores the successfully decoded 864x1536 adult wallpaper and companion as local data-URL previews in addition to the existing Cache Storage copies.
- On later refreshes, `chat_frontend_boot.js` reads those small persistent preview entries synchronously and paints the selected Ice Dragon wallpaper/companion before asynchronous runtime, account, server, or LALM hydration finishes.
- The existing persistent Cache Storage source remains authoritative for normal asset reuse. If the optional 4320x7680 WebP tier exists, v16 can replace the preview with that cached tier after boot without blocking the shell.
- Six-part runtime reconstruction remains only a cache-fill fallback rather than an every-refresh requirement.
- No stable API, authentication, LALM engine, deployment configuration, or server infrastructure changed.

## Why

User screenshots showed that the full-resolution wallpaper looked substantially better once loaded, but refresh could briefly show an incomplete/base Chat state and sometimes required repeated refreshes before the intended theme converged. Cache Storage alone is asynchronous, so this event adds a synchronous repeat-boot preview rather than making background paint depend on server/runtime timing.

## Verification

- Deployment configuration re-read before mutation: Vercel Git deployment remains disabled; runtime changes require no deployment.
- Event baseline: Server 2.3.81, Chat 1.4.73, Web Frontend 1.0.0.
- Authorities were re-read immediately before version assignment and were unchanged.
- Live `/live/manifest.json` returns manifest v13 and selects `ice-dragon-art-loader-v16.js`.
- Live `/live/assets/chat_frontend_boot.js` returns frontend-first v2 logic with synchronous cached preview paint.
- Live `/live/assets/themes/ice-dragon/ice-dragon-art-loader-v16.js` returns the persistent preview/cache logic.
- Final browser acceptance remains user-visible: first v16 load may seed the local preview; subsequent refreshes should paint Ice Dragon immediately while higher tiers hydrate asynchronously.

## Lineage

- Ice Dragon v16 creation: `e81022906db80f18f70db2190a897aebd9eeb712`
- Frontend boot v2: `53e401910f5dd85d43f0ddcdd50eb052bf763591`
- Manifest v13: `03fe124b30ad2bd29bd34f854445213c525460cf`
- Server authority 2.3.82: `cff66de222f0c1ef0def5e7c11a6c32009aac692`
- Chat authority 1.4.74: `5bf405cdd9b53f1b1a5a5d453231b919bd690a54`
- Web Frontend authority 1.0.1: `8bee31e96362d2bd8089dbe4c0bbb72eb73d6b3e`

## Rollback / migration

- No server data migration is required.
- Browser preview/cache entries are disposable and version-keyed.
- Rolling back the manifest to v12 restores v15 behavior without a server restart or deployment.
