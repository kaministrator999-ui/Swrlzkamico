# §wyrlz Server Roadmap

## Current release

**Server v2.3.21**

This corrective Chat event promotes camera logging to the conversation level: one persistent camera button now opens the complete current thread log, including conversation messages, assistant activity/generation traces, raw thread state, and stream-camera events.

### Module state

- **Server runtime v2.3.21** — current server development lineage.
- **Chat v1.4.19** — adds a persistent whole-conversation camera control in the Chat top bar.
- **Deployment Control v1.0.0** — unchanged.
- **Google Account architecture v1.0.4** — unchanged.
- **LALM UI v1.0.0** — unchanged.
- **LALM engine v2.1.19** / revision `2.1.19-hot-boundary-v10-thread-prefill-cache` — unchanged in this event.

## Server v2.3.21 — 2026-09-11

### Whole-conversation camera logging

- Added one persistent `📷` control to the Chat top bar for the current conversation, which is the primary camera-log entry point requested for whole-thread diagnostics.
- Opening the conversation camera renders a single complete log snapshot containing every message in the current thread, rendered assistant activity/generation traces, raw per-message state, the raw thread state, and full stream-camera / response-generation events available in the browser session.
- The conversation camera includes `Copy whole log`, `Refresh`, `Export full log`, and `Close` controls.
- `Refresh` rebuilds the snapshot while the modal is open so an actively evolving thread can be recaptured without closing the camera.
- Existing per-message Activity-log camera/copy/export controls from Server v2.3.20 remain available as secondary diagnostics; the conversation-level camera is now the main control.

### Verification / deployment state

- `web/chat_stream_focus.js` is updated on the `runtime` branch.
- **Production deployment:** NONE required.
- **Server restart:** NONE.
- **Manual Vercel deployment:** NONE for this runtime-hot Chat change.

## Server v2.3.20 — 2026-09-11

### Activity-log camera and export controls

- Every assistant Activity log receives an inline `📷` camera control, a `Copy` control, and an `Export full log` control.
- The camera opens a dedicated log viewer containing the selected response text, rendered activity/generation trace, and the raw message state used by Chat.
- `Copy box` copies the complete selected log snapshot rather than only the visible summary label.
- `Export full log` downloads the current conversation as a text log containing every stored message, each rendered activity trace available in the current DOM, the raw thread state, and the complete browser stream-camera / response-generation event log.
- The existing standalone stream-camera export remains available; this event adds the same diagnostic capability directly where each assistant log is inspected.
- Controls stop event propagation so clicking Camera/Copy/Export does not accidentally toggle the `<details>` activity log open or closed.
- The viewer and controls include responsive mobile layout behavior.

### Verification / deployment state

- `web/chat_stream_focus.js` was updated on the `runtime` branch and then fetched from the live Vercel `/live/assets/chat_stream_focus.js` route.
- Live response headers identify `x-swrlz-live-branch: runtime` and `x-swrlz-live-source: github-runtime`, confirming the new Chat log controls propagated through the hot runtime path.
- **Production deployment:** NONE.
- **Server restart:** NONE.
- **Manual Vercel deployment:** NONE for this Chat update.

## Server v2.3.19 — 2026-09-10

### Manual deployment control

- Added `.github/workflows/manual-vercel-production.yml` on `main`.
- Normal Git pushes remain non-deploying because Vercel Git deployments stay disabled.
- Production deployment is now an explicit workflow action only.
- Added `.deploy/REQUEST.txt` as the assistant-controlled trigger. It must remain unapproved unless the user has explicitly authorized a production deployment.
- Registered the new `deployment-control` module in `VERSION.txt` with authority `versions/deployment-control.txt` at `v1.0.0`.
- The first approved workflow request correctly entered the authorization/deploy pipeline but stopped safely because the repository does not currently have the required `VERCEL_TOKEN` secret. No production deployment occurred from that failed run.

### Chat refresh flash correction

- Inspection confirmed the server returns the Chat shell and injects runtime enhancement CSS in `<head>` plus enhancement JavaScript at the end of `<body>`.
- The visible "old Chat then snap to new Chat" effect was not a second page replacing the first; it was the base shell becoming visible before enhancement JavaScript finished installing the current runtime UI structures.
- `web/chat_enhancements.css` now keeps the Chat body hidden until the enhancement layer has created the current account dock marker (`#swrlzAccountDock`). Because the enhancement stylesheet is loaded from `<head>`, the browser waits to reveal the interface until the current runtime UI is assembled.
- The live production enhancement CSS was fetched after the runtime commit and confirmed to contain the boot-gating rule with `X-SWRLZ-Chat-UI-Source: runtime-override`.

### Deployment / verification state

- Runtime Chat correction: **Deployment NONE**; live runtime CSS verified.
- Main deployment-control workflow files: committed without automatic Vercel deployment.
- Approved manual production deployment attempt: **FAILED SAFELY before Vercel CLI execution** because `VERCEL_TOKEN` is not configured in GitHub Actions secrets.
- Stable per-worker hot-engine refresh infrastructure remains committed on `main` but is not production-active until a successful approved manual production deployment occurs.

## Server v2.3.18 — 2026-09-10

### Correction and live verification

- Live `/api/chat` inspection proved the deployed runtime page currently loads `chat_enhancements.js`, `chat_stream_focus.js`, and the other runtime Chat scripts from the `runtime` branch. This supersedes the incomplete Server v2.3.17 conclusion that `chat_stream_focus.js` was not active.
- The streaming-follow controller now uses a shared global single-install guard in both possible entry paths. Whichever runtime script initializes the controller first owns it; the later copy exits without double-wrapping `render`, `scheduleRender`, or `consumeEvent`.
- The live `chat_stream_focus.js` asset was fetched from the production Vercel URL and confirmed to be sourced from branch `runtime` with the corrected controller code.
- Line-follow behavior now moves the viewport only after approximately one newly rendered response line, not on every token/status event.
- While locked, the newest generated line is positioned near the middle of the Chat viewport with smooth scrolling and browser overflow anchoring disabled for programmatic generation steps to reduce jitter.
- Manual wheel, touch, or pointer navigation unlocks automatic follow. Follow re-locks only when the user brings the generated tail back into the central generation band.
- Completion-time forced scrolling remains suppressed when the user intentionally scrolled away during generation.
- Account-scoped Chat state also rebinds both `loadState` and `saveState`, preventing the base page's legacy storage listener from reloading the old global namespace while a Google account is active.

### Account-data boundary

- Google identity currently selects a separate browser-local Chat-history and preference namespace using the signed-in account's stable Google subject claim.
- Existing pre-account history migrates once into the first signed-in namespace; subsequent accounts receive their own independent namespace rather than inheriting another account's data.
- Google credential tokens and hidden OAuth client configuration are not written into Chat history or preferences.
- This is **account-selected local persistence**, not durable cross-device cloud persistence. The current Vercel runtime does not pretend ephemeral instance-local files are an account database. True cross-device account history remains gated on server-side Google verification plus a durable persistent datastore.

### Incremental LALM prefill

- The hot R39 engine keeps a bounded per-thread cache containing the exact previously-prefilled token prefix, recurrent/KV/short-convolution state, and terminal prefill logits.
- A continuing request reuses that state only when the cached token sequence is an exact prefix of the newly rendered prompt. Only newly appended context is then prefetched/prefilled.
- Prefix mismatch, cache expiry, worker restart, missing thread identity, or safety-bound overflow falls back to full prefill instead of trusting stale state.
- Context reuse is bounded to two recent entries, a 20-minute TTL, and 2048 cached prompt tokens per entry to avoid unbounded KV-memory growth.
- Engine status receipts expose reuse explicitly with `reused N` and `new M` token counts.

### Verification state

- `web/chat_enhancements.js` contains account namespace selection and a guarded streaming-follow installer.
- `web/chat_stream_focus.js` contains the same single-owner guard and the active line-aware generation-follow controller.
- Live Vercel fetches confirmed both the current Chat page script chain and the current `chat_stream_focus.js` runtime asset.
- `runtime_hot/r39_engine.py` advertises incremental conversation prefill and exposes its bounded context-cache status.
- `versions/server-runtime.txt` reports `2.3.18`.
- `versions/web-chat.txt` reports `1.4.16`.
- `versions/google-account.txt` reports `1.0.4`.
- `versions/lalm-engine.txt` reports `2.1.19` / `2.1.19-hot-boundary-v10-thread-prefill-cache`.
- **Production deployment:** NONE requested.
- **Server restart:** NONE.
- **Manual Vercel deployment:** NONE.
- The newest actual Vercel deployment remains the older Server v2.3.11 runtime deployment; these later changes are being consumed through the established hot-runtime branch path.

## Server v2.3.17 — 2026-09-10 — INCOMPLETE INSPECTION CORRECTED

### Attempt

- Static inspection of `api/chat_extensions.py` showed explicit injection of the enhancement asset and did not show the complete live runtime script chain.
- Based on that incomplete path inspection, the line-follow controller was also installed from `chat_enhancements.js` so the active Chat page would definitely receive the feature.

### Correction lineage

- A subsequent fetch of the actual live `/api/chat` HTML showed that the runtime page also loads `/live/assets/chat_stream_focus.js` through the broader live-runtime layer.
- The earlier conclusion that the stream-focus asset was inactive was therefore incorrect, not a project failure.
- Server v2.3.18 keeps both paths safe by giving them one shared single-install guard and verifies the live asset directly.

### Versions in this event

- Server runtime `2.3.17`.
- Chat `1.4.15`.
- Google Account architecture remained `1.0.4`.
- LALM engine remained `2.1.19`.

## Server v2.3.16 — 2026-09-10

### Accomplishment

- Chat history changed from one undifferentiated browser-local namespace to a namespace selected by the signed-in Google account's stable `subject` claim.
- Existing pre-account Chat history migrates once into the first signed-in account namespace so current threads are not discarded. Later account switches do not clone another account's history.
- Profile and personalization settings use the same account-selected namespace model.
- Sign-in and sign-out persist the namespace being left before changing identity, then load the namespace belonging to the identity being entered.
- Google credential tokens and hidden OAuth client configuration remain outside Chat history and account preference storage.
- The hot R39 engine introduced bounded exact-prefix recurrent-state reuse so normal same-thread continuation can prefill only newly appended context.
- The first line-aware scroll implementation was also created in this event; later events corrected and verified how the live runtime loads it.

### Module versions established

- Server runtime `2.3.16`.
- Chat `1.4.14`.
- Google Account architecture `1.0.4`.
- LALM engine `2.1.19` / `2.1.19-hot-boundary-v10-thread-prefill-cache`.

## Server v2.3.15 — 2026-09-10

### Accomplishment

- Removed Chat's dependency on `/live/pages/google-login-test.html` and removed the iframe/cropped-page architecture that produced the empty rounded box in the sidebar.
- Chat now loads Google Identity Services directly and uses the existing browser-stored Google Web Client configuration internally. The client configuration is consumed silently and is not displayed in the sidebar or Account settings UI.
- The sidebar renders the real Google sign-in button directly in the footer.
- A successful sign-in stores only safe account claims: name, email, verification state, picture, subject, issuer, and expiration metadata. The raw Google credential token is not retained in the Account settings UI.
- The signed-in account identity is display-only rather than another Account settings trigger.
- The centered gear is the dedicated Account settings entry point.
- Account settings gained functional Profile, Data & privacy, Personalization, and Security sections.
- Server-side Google ID-token verification remains a future stable-auth boundary; this release intentionally does not treat browser-decoded identity claims as server-verified authentication.

## Server v2.3.14 — 2026-09-10 — FAILED ATTEMPT PRESERVED

### Attempt

- First direct-in-Chat Google Identity implementation removed the page/iframe dependency and introduced the intended Account settings structure.

### Failure / correction lineage

- The first JavaScript write contained a syntax error in the Google Identity script-loader error callback.
- The incorrect attempt is preserved as Server `v2.3.14`, Chat `v1.4.12`, and Google Account architecture `v1.0.2`.
- Server `v2.3.15` / Chat `v1.4.13` / Google Account `v1.0.3` corrected it.

## Server v2.3.13 — 2026-09-10

### Accomplishment

- Introduced the first Chat sidebar account dock and Account settings gear.
- Attempted to reuse the isolated Google login page through a cropped iframe.
- Added the initial settings menu shell.

### Failure discovered by browser verification

- The sidebar showed an empty rounded Google host instead of the actual sign-in button.
- The deeper design issue was using the isolated test page as a UI dependency instead of moving its proven Google Identity architecture directly into Chat.

## Server v2.3.12 — 2026-09-10

### Accomplishment

- Corrected the `runtime` branch's own `vercel.json` so Git pushes from that branch no longer request Vercel Git deployments.
- Follow-up runtime commits produced no new Vercel deployments, verifying the correction.

### Deployment state

- **Production deployment:** NONE.
- **Server restart:** NONE.
- **Manual Vercel deployment:** NONE.
- Git-triggered deployment suppression is configured on both `main` and `runtime`.

## Server v2.3.11 — 2026-09-10

### Accomplishment

- Chat no longer has to visibly fall back to a yellow/pending state on every refresh when that same browser tab has already verified the LALM as ready moments earlier.
- A recent verified-ready state is restored immediately from session state while `/api/lalm/status` is checked in the background.
- Status polling was reduced from every 15 seconds to every 60 seconds.

## Server v2.3.10 — 2026-09-10

### Purpose

- Incremented only the canonical Server runtime authority to verify Chat could dynamically display `v2.3.10` without changing Chat code.

## Server v2.3.9 — 2026-09-10

### Architecture established

- Replaced the single value-bearing root `VERSION.txt` with an index mapping stable module IDs to independent canonical files under `versions/`.
- Added dedicated version authorities for Server runtime, Server UI, Web Chat, stream contract, LALM UI, LALM engine, Admin Web, Google Account architecture, Client APK, and Server APK.
- Chat resolves displayed Server runtime / Chat / Stream / LALM versions from the corresponding per-module files.
- Unverified APK versions remain `UNASSIGNED` instead of being fabricated.

## Earlier release lineage

The complete pre-2.3.9 lineage remains preserved in repository history. Server v2.3.8 and earlier established the initial shared registry, synchronized Chat/LALM status presentation, browser loading-loop corrections, runtime hot-update boundaries, and the mandatory roadmap/version law.

## Mandatory roadmap/version law

Every server development event gets a new overall Server runtime authority when project state changes, including failed attempts.

Every module actually changed gets its own version increment. A module that did not change keeps its version.

`VERSION.txt` is the module-authority router. It maps stable module IDs to their own `versions/<module-id>.txt` files and does not duplicate their values.

Consumers fetch the owning module authority when they need a version for display or update comparison. They do not maintain another module's version manually.

Every event records what changed, affected module versions, failed attempts where applicable, verification state, deployment/restart state, and relevant lineage.