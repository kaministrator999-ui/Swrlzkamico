# Server 2.3.78 — Frontend-first device cache

## Scope

This release separates Chat shell/theme readiness from §wyrlz server/LALM connectivity and introduces a persistent client-side Ice Dragon asset cache.

## Authority reconciliation

- Event entry authority observed: Server 2.3.76 / Web Chat 1.4.69.
- Immediately before version assignment, another project event had advanced authority to Server 2.3.77 / Web Chat 1.4.70.
- This event reconciled from those newer authorities and therefore owns Server 2.3.78 / Web Chat 1.4.71.
- New independently evolving module: Web Frontend 1.0.0.

## Changes

- Added `web/chat_frontend_boot.js` as the first Chat runtime script.
- The frontend reads the locally persisted theme before backend/account/LALM readiness and marks the local shell ready independently.
- Reworked `web/chat_boot_guard.css` and `web/chat_boot_guard.js` so the application shell is never hidden behind the prior 1.8 second synchronization curtain.
- Reworked `web/chat_boot_ready.js` so Chat reveal does not wait for Ice Dragon artwork hydration.
- Added Ice Dragon loader v15 with persistent Cache Storage (`swrlz-static-theme-v1`).
- Ice Dragon companion and 864x1536 adult source are stored on-device after the first successful hydration.
- Subsequent refreshes prefer cached assets and avoid the six-part wallpaper network reconstruction.
- Capable devices may promote the cached adult source to a 4320x7680 WebP during idle/background time; the 8K tier is cached and preferred on later visits.
- 8K promotion is not on the critical boot path; the cached 864x1536 source paints first when the 8K tier is absent.
- Runtime manifest advanced to v11 and routes Chat through the frontend-first boot controller and Ice Dragon v15.
- Added `WEB_FRONTEND=versions/web-frontend.txt` with Web Frontend 1.0.0 authority.

## Architecture boundary

The intended responsibility split is now explicit:

`cached/static CLIENT shell + theme -> SERVER API/stream -> LALM`

Server/LALM/account connectivity may lag or fail without preventing the local Chat shell, local conversation state, theme, sidebar, or composer from rendering.

## Verification performed

- New and modified JavaScript files were syntax-checked with Node before repository mutation.
- Runtime manifest v11 was re-read after concurrent project activity and still contained the frontend-first script order and Ice Dragon v15 route.
- Version authorities were re-read immediately before assignment; the concurrent 2.3.77/1.4.70 advance was detected and reconciled rather than overwritten.

## Deployment

- Production deploy: **NONE**
- Server restart: **NONE**
- Update class: runtime-hot / client-side frontend architecture

## Browser acceptance receipts

On the first Ice Dragon load after this release, Theme Logs should show a cache miss followed by cache storage. On a later refresh, they should show `adult-cache-hit` and `companion-cache-hit`. A capable device may additionally show `adult-8k-build-start` and `adult-8k-cache-store`, with later visits reporting `tier=8k`.
