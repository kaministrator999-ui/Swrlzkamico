# §wyrlz Server Roadmap

## Current release

**Server v2.3.79**

**Status: source published; collector deployment BLOCKED by missing GitHub Actions `VERCEL_TOKEN`.**

The authenticated Frozen Web Collector adds durable browser-operated snapshot collection, frozen search, and separate rights-reviewed training preparation. Compatible page and engine updates are sourced from `runtime` without another deployment after this initial stable-host installation.

### Module state

- **Server runtime v2.3.79** — collector release.
- **Frozen Web Collector v1.0.0** — newly registered.
- **Deployment Control v1.0.2** — private Blob provisioning and collector acceptance checks.
- **Chat v1.4.71**, **Web Frontend v1.0.0**, **LALM engine v2.1.30**, **Google Account v1.0.6**, **LALM UI v1.0.0** — unchanged by this event.

The previously stale current-release header showed 2.3.72. Authorities and `docs/releases/` record subsequent 2.3.73–2.3.78 events; their records and source remain preserved.

## Server v2.3.79 — 2026-09-12

### Frozen Web Snapshot Collector 1.0.0

- Added a professional browser control room at `/collector` for configuring sources and budgets; starting, pausing, continuing, stepping, and sealing collection; searching frozen evidence; reviewing training candidates; and inspecting snapshot manifests.
- Added a runtime-owned collector engine that canonicalizes and deduplicates content, extracts text, records provenance and URL revisions, calculates quality/privacy signals, prepares overlapping chunks and a lexical search index, and discards fetched raw HTML after extraction.
- Frozen snapshot evidence and reviewed training corpora are separate. Snapshot inclusion never authorizes training; acceptance requires an explicit operator decision and rights/provenance confirmation.
- Added fixed robots compliance, public-address-only outbound resolution, hostname-verified TLS over IP-pinned connections, redirect revalidation, source/domain boundaries, MIME and byte limits, politeness delays, run/page/document/domain/storage budgets, exploration reserve, and automatic pressure handling at 70/85/95 percent.
- Durable mutable control state and immutable snapshot/training artifacts use a private Vercel Blob store. `/tmp` remains cache-only and is never authoritative.
- Registered `FROZEN_WEB_COLLECTOR` in `VERSION.txt` with module authority `versions/frozen-web-collector.txt` at `1.0.0`.
- The collector page and compatible engine updates are owned by `runtime`. A single stable-host deployment is required for initial installation; subsequent compatible revisions do not require server redeployment.

### Concurrency reconciliation

- The collector was originally designed against Server `2.3.58` and a planned `2.3.59` event.
- Before the first release-boundary revalidation, the authoritative runtime branch had advanced through Server `2.3.67` / Chat `1.4.61` for later Ice Dragon and RMCCA work.
- At the final publication boundary it had advanced through Server `2.3.78` / Chat `1.4.71` / LALM `2.1.30`; Google sign-in and frontend-first caching changes were preserved.
- Stale planned Server versions were discarded, all concurrent work was preserved, and the collector event was reassigned to Server `2.3.79`.
- The older `2.3.67` current-state display called Deployment Control `1.0.0`; its module authority was already `1.0.1`. This event advances that authority to `1.0.2` without rewriting prior version history.

### Verification / deployment state

- **Source:** implemented on reconciled release branches and preserved in GitHub checkpoints.
- **Static verification:** collector engine, storage contract, SSRF rejection, redirect/robots handling, lifecycle/checkpointing, lexical search, deterministic immutable sealing, training separation, console safety, and stable-host dispatch all pass focused verification.
- **Production deployment:** explicitly approved; pending at this release-record stage.
- **Server restart:** represented by the approved Vercel production deployment only; no recurring restart is required for compatible runtime updates.
- **Live browser/API evidence:** pending the approved deployment and will be appended without rewriting the source event.

### Relevant lineage

- First reconciled runtime checkpoint: `5b7744acc78a1a8508e5a954a4f5b2161db7a8d8`
- Final reconciled runtime checkpoint: `7cc1ccb9eb09857f945dab2ea992b2809d8b50f1`
- Rebased stable-host checkpoint: `636321dcd9f204eae08f5e9cfc567ab1b2ac5c1d`
- Initial reconciliation authority: `26009037b55c158a0606e84bf69202b165e59057`
- Final pre-event runtime authority: `3c2cc5efd320157ba67d888240f195344c015be7`
- Pre-event main authority: `3f3d8eaeec4859099a3710155df8067577ca27fe`
- Final canonical and deployment receipts: pending publication/deployment.

### Rollback / migration

- No existing collector data migration is required; the private store begins with no configured sources or accepted training material.
- Rollback restores the preceding stable deployment and the pre-event `runtime` authority. Immutable snapshot artifacts, if later created by an operator, remain preserved unless separately and explicitly removed.

## Server v2.3.72 — 2026-09-12

### Triggering evidence

- The adult Ice Dragon wallpaper was finally rendering, but remained visibly blurred/pixelated on the mobile viewport.
- A user-initiated Vercel redeploy did not improve the image, ruling out deployment propagation as the quality bottleneck.
- Runtime inspection showed `ice-dragon-art-loader-v13.js` still fetched `adult-180x320.jpg.b64` and stretched it across `.messages` with `background-size: cover`.
- The runtime asset tree already contained six ordered `adult-864x1536.part000.b64` through `part005.b64` source chunks, and the first chunk's JPEG header identifies the intended 864×1536 dimensions.

### Full-resolution wallpaper path

- Added `web/themes/ice-dragon/ice-dragon-art-loader-v14.js`.
- Preserved the verified v13 ownership model: `.messages` remains the single adult wallpaper owner; companion hydration remains independent; single-flight deduplication remains intact.
- Adult hydration now fetches all six 864×1536 Base64 chunks concurrently, joins them in numeric order, normalizes the complete payload once, creates the same Blob URL, and runs the browser decode probe before painting.
- Added diagnostics for `adult-part-fetch-start`, `adult-parts-complete`, normalized payload length, decoded dimensions, and final paint state.
- Added a resolution guard so an unexpectedly low-resolution decoded adult asset fails loudly instead of silently reintroducing the same visual regression.
- `runtime_pages/manifest.json` advanced from manifest v6 to v7 and now injects the unique `ice-dragon-art-loader-v14.js` URL, avoiding the stale fixed-asset URL problem discovered earlier.

### Concurrency reconciliation

- Transaction baseline was Server `2.3.71` / Chat `1.4.65`.
- Immediately before version assignment, both authoritative version files were re-read and remained Server `2.3.71` / Chat `1.4.65`.
- This event therefore advanced to Server `2.3.72` / Chat `1.4.66`.

### Verification / deployment state

- Runtime source changed only on `runtime`.
- **Production deployment:** not required for this runtime-hot fix; the user's preceding redeploy already demonstrated deployment was not the image-quality bottleneck.
- **Server restart:** not required.
- Repository acceptance: manifest v7 points at v14; the six 864×1536 chunks remain the v14 adult source.
- Browser acceptance: Theme Logs should report `adult-parts-complete`, `adult-decode-ok 864x1536`, and `adult-painted`; the target Android viewport should show materially sharper adult artwork than the 180×320 path.

### Relevant lineage

- v14 full-resolution hydrator: `7f82590e30ae6b6da77e3407b739a05c1df32b51`
- Manifest v7 activation: `3c1fce86ce392618e2eff15db26d914faa2c48bc`
- Server version authority: `32ff3c525c0c6471b6bed129414e8ce21d0b9a02`
- Chat version authority: `7074153de81d57d7d4af063b02239cfb5e5a1b8f`
- Release record: `docs/releases/server-2.3.72-ice-dragon-full-resolution-wallpaper.md`
