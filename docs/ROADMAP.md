# §wyrlz Server Roadmap

## Current release

**Server v2.3.26**

This event corrects the mobile Chat viewport so the composer stays pinned to the usable bottom edge instead of leaving browser-dependent dead space underneath it.

### Module state

- **Server runtime v2.3.26** — current server development lineage.
- **Chat v1.4.22** — mobile viewport/composer-bottom correction.
- **LALM engine v2.1.21** — unchanged.
- **LALM UI v1.0.0** — unchanged.
- **Google Account architecture v1.0.4** — unchanged.
- **Deployment Control v1.0.0** — unchanged.

## Server v2.3.26 — 2026-09-11

### Mobile Chat viewport correction

- User browser evidence showed a large empty region below the Chat composer on Android even though the visible browser viewport extended farther down.
- The correction is owned by Web Chat and applies to mobile layouts regardless of whether Default or Ice Dragon is selected.
- Added a final runtime CSS layer that pins the mobile Chat app to the viewport edges and lets the workspace fill that pinned container rather than relying on a browser-dependent `100dvh` result for the app shell.
- The composer remains the final grid row, so the correction removes the dead lower region without moving it through a negative-margin or theme-specific hack.
- Existing message scrolling, sidebar behavior, theme selection, account behavior, streaming, LALM behavior, and stable infrastructure were intentionally left unchanged.
- `runtime_pages/manifest.json` now loads the viewport correction after the normal Chat and Ice Dragon styles so it wins only for the mobile layout properties it owns.

### Verification / deployment state

- `web/chat_mobile_viewport_fix.css` added on `runtime`.
- `runtime_pages/manifest.json` updated on `runtime` to load the correction for `/chat`.
- `versions/server-runtime.txt` advanced to `2.3.26`.
- `versions/web-chat.txt` advanced to `1.4.22`.
- **Production deployment:** NONE requested; this is a runtime-only Chat update.
- **Server restart:** NONE requested.
- **Verification:** source and live-asset verification pending immediately after commit; browser visual acceptance remains the final check for the exact Android viewport shown by the user.

### Relevant lineage

- Mobile viewport correction: `42f5fa6b402367c6b0b753607fbb77bd64279eaf`
- Runtime manifest wiring: `b36267dcfa10a49945f54506863322ac2cb41d74`
- Server version authority: `1ad54e46315dd28c0f96bf29e47b7c9bf8fab605`
- Chat version authority: `0af4dbcf530d0e1aa94d61cbf4ba0e1a22101fa0`

## Server v2.3.25 — 2026-09-11

### Ice Dragon Chat theme pack

- Added a complete Ice Dragon theme package under the runtime-owned Web Chat surface, including local CSS, JavaScript controller, dragon sigil artwork, and ice-shard artwork.
- Added a compact Chat theme selector with `Default` and `❄ Ice Dragon` choices.
- Default remains the first-load behavior; Ice Dragon is opt-in and the user's explicit theme choice persists locally across reloads.
- The theme covers the existing sidebar, top bar, conversation bubbles, composer, send controls, enhancement toolbar, evidence panels, modals, scrollbars, mobile layout, and reduced-motion preference without replacing the Chat page.
- Preserved the mobile sidebar rule: when the sidebar opens, the workspace may dim but the sidebar itself remains bright and undimmed.
- Wired the theme through `runtime_pages/manifest.json`, so the existing runtime source loader injects the theme CSS and controller after the normal Chat assets. No stable loader or API change was required.
- `VERSION.txt` routing was unchanged because Ice Dragon is part of the existing Web Chat module rather than a new independently versioned subsystem.

### Process correction / failure lineage

- The first implementation pass began before the required project-start documents were read and briefly placed duplicate theme files on `main`.
- After `SWRLZ_PROJECT_START.md`, `SWRLZ_HOTFIX_RULES.md`, `SWRLZ_VERSION_MODULE_EVOLUTION.md`, the active runtime roadmap, `VERSION.txt`, and the affected version authorities were read, ownership was corrected to the `runtime` branch.
- The misplaced `main` theme files were removed and the bundled `web/chat_account.js` bootstrap was restored to its prior contents, leaving no competing main-owned Chat theme path.
- Git-triggered deployment is disabled in the repository configuration, and no Vercel deployment or restart was requested or required for this correction.

### Verification / deployment state

- `runtime_pages/manifest.json` lists the Ice Dragon stylesheet and controller in the `/chat` route asset chain.
- `versions/server-runtime.txt` advanced to `2.3.25`.
- `versions/web-chat.txt` advanced to `1.4.21`.
- Live `/chat` verification returned HTTP 200 with `x-swrlz-live-source: github-runtime`, `x-swrlz-live-branch: runtime`, and `x-swrlz-live-path: web/chat.html`.
- The live HTML contains both the Ice Dragon stylesheet and controller injections after the existing Chat assets.
- The live Ice Dragon CSS and JavaScript asset URLs each returned HTTP 200 and identified their source as the `runtime` branch through the existing live-source loader.
- **Production deployment:** NONE requested; this is a runtime-only Chat update.
- **Server restart:** NONE requested.
- **Verification:** PASSED for runtime source selection, asset injection, and live theme asset delivery. Browser-visible theme selection remains user-controlled by the injected `Default` / `❄ Ice Dragon` selector.

### Relevant lineage

- Runtime controller: `5627b54d8d7e44aeb3be79ae6cbf1f71f5a33cb5`
- Runtime theme styles: `0047c77944b3b6f82b7d477ef32ba4a06c4e56fd`
- Runtime sigil asset: `19715b9e048c252c60756dcdc72591b3202c75f7`
- Runtime shard asset: `669fc0380697b515330a13c545928e3bc31cec66`
- Runtime manifest wiring: `c2b0c0e80fa424d5cbcc0274b1f6f9a714ab5859`
- Server version authority: `c625390e263bf71d16596b12830a951b796044c6`
- Chat version authority: `1756544c5cdf2f1e205bcd4fdb754be70048311a`

## Server v2.3.24 — 2026-09-11

### Pipelined prefill / next-turn race behavior

- Runtime evidence from LALM v2.1.20 showed the checkpoint design working: a later same-thread response reused 39 tokens and prefetched only 9, then the next response reused 77 and again prefetched only 9.
- Generated assistant tokens already advance the same recurrent/KV state needed by the next turn, so v2.1.21 now treats that generation work as future prefill work instead of throwing the state away until a later post-response pass.
- During generation, safe assistant-output checkpoints are published periodically when canonical retokenization proves the generated state is an exact prompt prefix.
- Before the `COMPLETE` event is exposed, the final assistant-open state is published as an immutable checkpoint. A user who sends the next message immediately can resume from that state even if speculative warmup has not finished.
- After generation, a daemon warmup continues independently. It first advances through the assistant-close marker and then through the fixed next-user role scaffold, publishing each exact-prefix state as it becomes available.
- The next request **never waits** for that speculative work. It selects the longest exact-prefix checkpoint that exists at request time and prefills only the remaining suffix plus the new user content.
- This creates the intended race: if postwarm finishes first, the next request begins from the next-user-open checkpoint; if the user responds first, the request begins from the assistant-open or assistant-closed checkpoint already available and performs only the missing suffix itself.
- Mutable generation state is never handed directly to another request. Checkpoints clone state before publication, preserving isolation between active generation and later requests.
- Context checkpoint capacity increased from four to six per thread to preserve prompt, live assistant, terminal assistant, assistant-close, and next-user-open boundaries without immediately evicting useful fallbacks.
- Prefix mismatch, edited history, worker replacement, expiry, or safety-bound overflow still falls back to correct prefill rather than trusting stale speculative state.

### Verification / deployment state

- `runtime_hot/r39_engine.py` advanced to LALM v2.1.21 on the `runtime` branch.
- `versions/lalm-engine.txt` advanced to `2.1.21`.
- `versions/server-runtime.txt` advanced to `2.3.24`.
- **Chat version:** unchanged because Chat code did not change.
- **Production deployment:** NONE requested; this is a runtime-hot LALM update.
- **Server restart:** NONE requested.
- Acceptance receipt: inspect the next same-thread camera log for checkpoint kinds/reuse counts and verify that a rapid next message can start without waiting for speculative postwarm completion.

## Server v2.3.23 — 2026-09-11

### Prefill evidence that triggered this work

- The captured conversation log showed that the first short request required 21 fresh prompt tokens and took about 6.38 seconds of prefill.
- The next request correctly reused those 21 tokens, but still had to prefill 27 additional tokens and took about 8.43 seconds before decoding. This proved the v2.1.19 cache was working, but it only preserved the previous prompt boundary; it did not preserve enough of the assistant answer/closed-turn boundary for the following user turn.
- Individual prefetched tokens were generally around 0.30 seconds each in that sample, making reduction of newly-prefilled tokens the highest-value immediate optimization.

### LALM v2.1.20 behavior

- Conversation cache entries now keep several exact-prefix checkpoints per thread instead of replacing the thread with only one cached prefix.
- Resume chooses the **longest exact matching checkpoint**, so a newer checkpoint can be used when valid while an older safe checkpoint remains available as fallback.
- After a response has already completed for the user, the engine opportunistically closes the assistant turn and stores that completed-turn checkpoint when the generated token sequence matches the canonical conversation prefix. This means the next user message can usually reuse the previous assistant answer rather than prefilling that answer again.
- The post-response checkpoint only processes the small assistant-closing suffix after the terminal response has already been emitted; it does not replay the whole answer merely to create a cache entry.
- Frequently reused invariant model tensors are resolved once into a fast local structure instead of repeatedly passing through tensor-cache lookup paths during every token.
- Recently used token-embedding rows now use a bounded in-memory row cache.
- Attention history arithmetic was moved toward vectorized NumPy operations while keeping the same recurrent/KV semantics.
- Prefill progress telemetry is quieter: it reports useful milestones rather than sending a browser/status event after every single prefetched token. This reduces diagnostic/UI overhead without hiding the final timing receipt.
- Prefix mismatch, edited history, expired cache, worker replacement, or safety-limit overflow still falls back to correct full prefill rather than using stale state.

### Expected observable result

For a normal continuing conversation, the next-turn receipt should move from behavior resembling:

`reused 21, prefetched 27`

toward a substantially larger reused prefix with only the new user-turn wrapper/content requiring prefill, when the assistant-close checkpoint can be established on that worker.

The per-new-token time should also be compared against the previous roughly 0.30-second sample; the static-tensor/token-row fast paths are intended to reduce that number, while the checkpoint change primarily reduces **how many** such tokens are required.

### Verification / deployment state

- `runtime_hot/r39_engine.py` updated on the `runtime` branch and syntax-validated before commit.
- `versions/lalm-engine.txt` advanced to `2.1.20`.
- `versions/server-runtime.txt` advanced to `2.3.23`.
- **Chat version:** unchanged because Chat behavior did not change.
- **Production deployment:** NONE requested for this runtime-hot LALM event.
- **Server restart:** NONE requested.
- Runtime measurement remains the acceptance gate: compare the next two or more messages in one thread and inspect `reused`, `prefetched`, prefill time, and per-token timing.

## Server v2.3.22 — 2026-09-11

### Whole-conversation camera visibility correction

- User verification showed the camera source existed but no camera control appeared in the mobile top bar.
- The root cause was ownership of the shared stream-follow initialization guard: one enhancement script initialized first, causing the later stream-focus file to exit before reaching its camera installer.
- The whole-conversation camera was moved onto an independent Chat script path so it no longer depends on which script owns stream-follow.
- The top-bar camera opens the current thread's complete log with copy, refresh, export, and close controls.
- Chat advanced to `v1.4.20`.
- No deployment or restart was required.

## Server v2.3.21 — 2026-09-11

### Whole-conversation camera logging

- Added the first whole-thread camera viewer for conversation messages, response-generation/activity traces, raw message state, and raw thread state.
- Added copy, refresh, and full-log export controls.
- Chat advanced to `v1.4.19`.
- No deployment or restart was required.

## Server v2.3.20 — 2026-09-11

### Per-response diagnostic controls

- Added camera, copy, and full-log export controls to assistant Activity logs.
- Preserved the standalone stream-camera export as an additional diagnostic route.
- Chat advanced to `v1.4.18`.
- No deployment or restart was required.

## Server v2.3.19 — 2026-09-10

### Manual deployment control and Chat boot presentation

- Added a manual-only production deployment workflow and deployment request gate while keeping ordinary Git pushes non-deploying.
- Corrected the Chat refresh flash where the base interface briefly appeared before the current enhancement layer finished installing.
- The first manual deployment attempt stopped safely before deployment because the required Vercel credential was not yet configured at that moment.

## Server v2.3.18 — 2026-09-10

### Streaming follow, account-scoped state, and first incremental prefill

- Verified the actual live Chat script chain and corrected earlier incomplete assumptions about which stream-focus asset was active.
- Added one-owner protection for stream-follow logic.
- Made generation scrolling line-aware: follow new lines, unlock when the user scrolls away, and re-lock when the user returns to the generated tail.
- Bound Chat history/preferences to the selected Google-account namespace on that browser.
- LALM `v2.1.19` introduced bounded exact-prefix conversation-state reuse with a 20-minute TTL and 2048-token safety bound.
- No production deployment was requested for the runtime-hot changes.

## Server v2.3.17 — 2026-09-10 — inspection correction preserved

- An incomplete static inspection initially suggested the stream-focus asset was not active.
- Live-page inspection corrected that conclusion.
- The correction was preserved in lineage rather than rewriting the earlier attempt.

## Server v2.3.16 — 2026-09-10

- Introduced account-selected local Chat history/preferences.
- Introduced the first exact-prefix recurrent-state reuse for same-thread LALM continuation.
- Introduced the first line-aware response-follow implementation.

## Server v2.3.15 — 2026-09-10

- Moved Google Identity architecture directly into Chat rather than embedding/linking the isolated Google test page.
- Kept Google configuration/credential material out of visible Chat settings.
- Added signed-in account identity plus functional Profile, Data & privacy, Personalization, and Security sections.

## Server v2.3.14 — 2026-09-10 — failed attempt preserved

- First direct Google-in-Chat implementation contained a JavaScript loader syntax error.
- The failed version remains part of lineage; v2.3.15 corrected it.

## Server v2.3.13 — 2026-09-10

- Added the first Chat account dock and Account settings gear.
- The initial iframe-based Google test-page reuse produced an empty-looking login host and was later replaced.

## Server v2.3.12 — 2026-09-10

- Corrected the `runtime` branch deployment configuration so runtime Git commits no longer create Vercel preview deployments.
- Follow-up commits verified zero new deployment events.

## Server v2.3.11 — 2026-09-10

- Restored recently verified LALM-ready state immediately on Chat refresh while checking status again in the background.
- Reduced readiness polling frequency.

## Server v2.3.10 — 2026-09-10

- Incremented only the Server runtime authority as a live propagation test.
- Chat correctly displayed the changed Server version without a Chat code change or deployment.

## Server v2.3.9 — 2026-09-10

### Version authority architecture

- Replaced duplicated version strings with per-module version authority files under `versions/`.
- `VERSION.txt` became the module-authority router.
- Chat resolves displayed Server/Chat/Stream/LALM versions from their owning module authorities.
- Added version authorities for Server runtime/UI, Web Chat, stream contract, LALM UI/engine, Admin Web, Google Account architecture, and APK structures.

## Earlier release lineage

The complete pre-2.3.9 lineage and the full-detail text of later historical revisions remain preserved in Git history. The active roadmap intentionally describes outcomes in observable project language rather than duplicating implementation statements line-for-line.

## Mandatory roadmap/version law

Every server development event gets a new overall Server runtime authority when project state changes, including failed attempts.

Every module actually changed gets its own version increment. A module that did not change keeps its version.

`VERSION.txt` is the module-authority router. It maps stable module IDs to their own `versions/<module-id>.txt` files and does not duplicate their values.

Consumers fetch the owning module authority when they need a version for display or update comparison. They do not maintain another module's version manually.

Every event records what changed, affected module versions, failed attempts where applicable, verification state, deployment/restart state, and relevant lineage.