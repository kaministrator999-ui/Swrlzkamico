# §wyrlz Server Roadmap

## Current release

**Server v2.3.17**

This corrective runtime event wires the line-aware streaming-follow implementation into the JavaScript asset that Chat actually hot-loads, while retaining the account-scoped state and incremental LALM prefill work established in Server v2.3.16.

### Module state

- **Server runtime v2.3.17** — current runtime development lineage.
- **Chat v1.4.15** — account-selected browser history/settings plus actively hot-loaded line-aware, user-interruptible streaming follow.
- **Google Account architecture v1.0.4** — unchanged from v2.3.16; Google subject selects isolated Chat-history and preference namespaces on the device.
- **LALM UI v1.0.0** — unchanged.
- **LALM engine v2.1.19** / revision `2.1.19-hot-boundary-v10-thread-prefill-cache` — unchanged from v2.3.16; bounded per-thread recurrent-state reuse for incremental conversation prefill.

## Server v2.3.17 — 2026-09-10

### Correction

- Review of the active Chat middleware showed that `/api/chat` injects `/api/chat/assets/enhancements.js`; `web/chat_stream_focus.js` exists in the runtime source set but is not currently injected by that middleware.
- The first Server v2.3.16 scroll implementation therefore existed in source but was not guaranteed to execute in the active Chat page. That path is preserved rather than rewritten out of history.
- The same line-aware follow logic is now installed directly by `web/chat_enhancements.js`, the hot-loaded Chat enhancement asset.
- The active implementation now:
  - does not move the viewport on status events or every token;
  - measures assistant-bubble growth and moves only after approximately one new rendered line appears;
  - centers the newest generated line near the middle of the Chat viewport while follow is locked;
  - disables smooth animation for programmatic streaming steps to avoid cumulative jitter;
  - unlocks follow on manual wheel/touch/pointer navigation;
  - re-locks only when the user brings the generated tail back into the generation focus band;
  - suppresses completion-time forced-bottom scrolling after the user has intentionally navigated away.
- `loadState` and `saveState` are both now rebound to the active Google-account namespace layer, so the original cross-tab storage listener cannot accidentally reload the legacy global namespace while a Google account is active.

### Verification state

- `api/chat_extensions.py` confirms the active Chat page injects `/api/chat/assets/enhancements.js`.
- `web/chat_enhancements.js` now contains both account-scoped state selection and the runtime streaming-follow controller.
- `versions/server-runtime.txt` reports `2.3.17`.
- `versions/web-chat.txt` reports `1.4.15`.
- Google Account architecture remains `1.0.4`.
- LALM engine remains `2.1.19` / `2.1.19-hot-boundary-v10-thread-prefill-cache`.
- **Production deployment:** NONE requested.
- **Server restart:** NONE.
- **Manual Vercel deployment:** NONE.
- The newest Vercel deployment remains the older Server v2.3.11 runtime deployment; no deployment was created by the v2.3.16/v2.3.17 runtime-branch updates.
- Browser reload and live stream receipts remain the final runtime verification gate.

## Server v2.3.16 — 2026-09-10 — CORRECTION LINEAGE PRESERVED

### Accomplishment

- Chat history is no longer one undifferentiated browser-local namespace. The signed-in Google account's stable `subject` claim selects a separate local history namespace, and switching accounts reloads the corresponding namespace.
- Existing pre-account Chat history is migrated once into the first signed-in account namespace so the current user's existing threads are not discarded. Later account switches do not clone another account's history.
- Profile/personalization settings now use the same account-selected namespace model instead of one global preference key.
- Sign-in and sign-out persist the namespace being left before changing identity, then load the namespace belonging to the identity being entered.
- Google credential tokens and hidden OAuth client configuration remain outside Chat history and account preference storage.
- This release deliberately distinguishes **account-selected local persistence** from **durable cross-device cloud sync**. Google currently selects which browser namespace to load; true cross-device persistence still requires server-side Google-token verification plus a durable account datastore. Ephemeral Vercel instance storage is not used as fake persistence.
- The hot R39 engine now keeps a bounded per-thread prefill cache containing the exact token prefix, recurrent/KV/short-convolution state, and terminal prefill logits.
- On a continuing conversation, the engine reuses the cached state only when the previously prefetched token sequence is an exact prefix of the newly rendered prompt. It then prefills only the appended context.
- Prefix mismatch, worker restart, missing thread identity, cache expiry, or safety-bound overflow falls back to the existing full-prefill path rather than trusting stale state.
- Conversation context caching is bounded to two recent entries, 20-minute TTL, and 2048 cached prompt tokens per entry to avoid unbounded KV-memory growth.
- Engine status receipts report cache hits as `reused N` plus `new M` tokens, making the optimization externally observable rather than inferred from latency alone.

### Scroll-wiring issue discovered during verification

- The initial line-aware streaming-follow implementation was written to `web/chat_stream_focus.js`.
- Inspection of the active middleware then showed that the current Chat response injects `web/chat_enhancements.js`, not `web/chat_stream_focus.js`.
- The scroll algorithm itself was retained, but Server v2.3.17 / Chat v1.4.15 moved the active controller into the actually served enhancement layer.

### Module versions established in this event

- Server runtime `2.3.16`.
- Chat `1.4.14`.
- Google Account architecture `1.0.4`.
- LALM engine `2.1.19` / `2.1.19-hot-boundary-v10-thread-prefill-cache`.

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

- Incremented only the canonical Server runtime authority to verify Chat could dynamically display `v2.3.10` without changing Chat code.

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
