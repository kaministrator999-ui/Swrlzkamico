# §wyrlz Server Roadmap

## Current release

**Server v2.3.15**

This runtime event replaces the incomplete page/iframe Google-login bridge with direct Google Identity Services integration inside Chat and completes the first functional Account settings submenus.

### Module state

- **Server runtime v2.3.15** — current runtime development lineage.
- **Chat v1.4.13** — direct Google sign-in button, separated account identity/settings controls, and functional account settings UI.
- **Google Account architecture v1.0.3** — Google Identity Services now initializes directly inside Chat from the existing hidden browser-stored client configuration.
- **LALM UI v1.0.0** — unchanged.
- **LALM engine v2.1.18** / revision `2.1.18-hot-boundary-v9-effective-receipt` — unchanged.

## Server v2.3.15 — 2026-09-10

### Accomplishment

- Removed Chat's dependency on `/live/pages/google-login-test.html` and removed the iframe/cropped-page architecture that produced the empty rounded box in the sidebar.
- Chat now loads Google Identity Services directly and uses the existing browser-stored Google Web Client configuration internally. The client configuration is consumed silently and is not displayed in the sidebar or Account settings UI.
- The sidebar now renders the real Google sign-in button directly in the footer.
- A successful sign-in stores only the safe account claims already used by the isolated test flow: name, email, verification state, picture, subject, issuer, and expiration metadata. The raw Google credential token is not retained in the Account settings UI.
- The signed-in account identity is now display-only rather than another Account settings trigger.
- The centered gear is the dedicated Account settings entry point.
- Filled the Account settings sections with working local controls:
  - **Profile** — account identity display, optional display/preferred names, Google-name preference.
  - **Data & privacy** — explicit current storage behavior and local preference clearing.
  - **Personalization** — response-depth and preferred-name preferences stored locally.
  - **Security** — sign-in state, email verification state, session expiry, hidden-credential statement, and sign-out.
- Server-side Google ID-token verification remains a future stable-auth boundary; this release intentionally does not pretend browser-decoded identity claims are server-verified authentication.

### Verification state

- `web/chat_enhancements.js` no longer contains a Google login page URL or iframe bridge.
- `web/chat_enhancements.css` no longer depends on the cropped Google-page iframe and now styles the direct button and populated settings sections.
- `versions/server-runtime.txt` reports `2.3.15`.
- `versions/web-chat.txt` reports `1.4.13`.
- `versions/google-account.txt` reports `1.0.3`.
- **Production deployment:** NONE requested.
- **Server restart:** NONE.
- **Manual Vercel deployment:** NONE.
- User-side browser reload is the final visual/sign-in verification gate.

## Server v2.3.14 — 2026-09-10 — FAILED ATTEMPT PRESERVED

### Attempt

- First direct-in-Chat Google Identity implementation removed the page/iframe dependency and introduced the intended Account settings structure.

### Failure / correction lineage

- The first JavaScript write contained a syntax error in the Google Identity script-loader error callback.
- The incorrect attempt was not rewritten out of history. It is preserved as Server `v2.3.14`, Chat `v1.4.12`, and Google Account architecture `v1.0.2`.
- Server `v2.3.15` / Chat `v1.4.13` / Google Account `v1.0.3` is the corrective event.

## Server v2.3.13 — 2026-09-10

### Accomplishment

- Introduced the first Chat sidebar account dock and Account settings gear.
- Attempted to reuse the isolated Google login page through a cropped iframe.
- Added the initial settings menu shell.

### Failure discovered by browser verification

- The sidebar showed an empty rounded Google host instead of the actual sign-in button.
- The account/login area and Account settings behavior were insufficiently separated.
- Settings submenu contents were placeholder descriptions rather than functional controls.
- The deeper design issue was using the isolated test page as a UI dependency instead of moving its proven Google Identity architecture directly into Chat.

## Server v2.3.12 — 2026-09-10

### Accomplishment

- Corrected the `runtime` branch's own `vercel.json` so Git pushes from that branch no longer request Vercel Git deployments.
- The root cause was branch-local configuration drift: `main/vercel.json` had been changed to `git.deploymentEnabled=false`, but `runtime/vercel.json` still contained a branch map that did not disable `runtime` itself.
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

### Verification evidence

- Live `/api/lalm/status` reported `interactiveReady: true` and `warmModelResident: true` with the runtime override/native backend active.
- Vercel deployment history later showed the runtime commits for this event generated Preview deployments; Server v2.3.12 corrected that deployment-control issue.

## Server v2.3.10 — 2026-09-10

### Purpose

- Incremented only the canonical Server runtime version authority to verify Chat could dynamically display `v2.3.10` without changing Chat code.

### Verification state

- User-side verification confirmed Chat dynamically displayed Server runtime `v2.3.10`.
- The version-authority architecture worked correctly.

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
