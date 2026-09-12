# §wyrlz Server Roadmap

## Current release

**Server v2.3.68**

This event improves the visual quality of the now-working Ice Dragon adult wallpaper while deliberately preserving the rendering path that was proven in Server v2.3.66.

### Module state

- **Server runtime v2.3.68** — current server development lineage.
- **Chat v1.4.62** — Ice Dragon wallpaper quality pass.
- **LALM engine v2.1.26** — unchanged.
- **LALM UI v1.0.0** — unchanged.
- **Google Account architecture v1.0.4** — unchanged.
- **Deployment Control v1.0.0** — unchanged.

## Server v2.3.68 — 2026-09-12

### Ice Dragon adult wallpaper quality pass

- User browser verification confirmed the adult Ice Dragon wallpaper finally rendered correctly, but the recovered 180×320 JPEG derivative was visibly over-compressed when stretched across the mobile Chat chamber.
- Re-encoded the exact intended adult Ice Dragon artwork into the existing `web/themes/ice-dragon/assets/adult-180x320.jpg.b64` slot at substantially higher JPEG quality.
- Preserved the verified v13 asset hydrator, direct `.messages` wallpaper ownership, theme selector behavior, companion icon behavior, and all existing CSS/DOM ownership.
- No new wallpaper mechanism, pseudo-element owner, image loader, or runtime route was added.

### Concurrency reconciliation

- Before version assignment, the authoritative version files were re-read.
- They had concurrently advanced to Server `2.3.67` / Chat `1.4.61` for unrelated RMCCA work.
- This wallpaper-quality event therefore advances from those authorities to Server `2.3.68` / Chat `1.4.62` rather than overwriting concurrent lineage.

### Verification / deployment state

- Replacement payload is valid Base64 and locally decodes as JPEG before commit.
- Rendering architecture is unchanged from the browser-verified working path.
- `versions/server-runtime.txt` advanced from `2.3.67` to `2.3.68`.
- `versions/web-chat.txt` advanced from `1.4.61` to `1.4.62`.
- **Production deployment:** NONE requested; runtime-hot asset update only.
- **Server restart:** NONE requested.
- Final acceptance is visual: verify reduced blockiness/compression artifacts on the target Android viewport.

### Relevant lineage

- Wallpaper quality asset: `23595d179bad58e0370749d2dc42fdeb6f4e7220`
- Server version authority: `277f8648d54e77a846c31d8063ef25b09f552ea3`
- Chat version authority: `61411018d8a722df55e8a5e01bee66e22dd9fd14`
- Release record: `docs/releases/server-2.3.68-ice-dragon-wallpaper-quality.md`

## Server v2.3.67 — 2026-09-11/12

### Recursive Multi-Domain Cognitive Clock Architecture integration

- Added the formal RMCCA architecture specification at `docs/architecture/RMCCA.md`.
- Integrated a stable RMCCA cognitive response policy into the canonical Chat-to-LALM context layer. The policy teaches progressive structure decoding, scope preservation, local correction/revision, simultaneous multi-domain activation, domain salience, resolution depth, contextual reference frames, user-established synthesis order, and response-topology selection.
- Identity questions are taught as contextual conversational acts that should receive a natural identity answer rather than a bare unexplained label.
- Casual conversation is taught as participation rather than meta-description of the act itself.
- Added RMCCA camera telemetry that records structural roles, active domains, qualitative salience, resolution depth, reference frame, response topology, and synthesis order alongside canonical/display context evidence.
- RMCCA camera planning is diagnostic only and does not dynamically rewrite the prompt each turn, preserving a stable prefix for conversation-cache/checkpoint reuse.

### Concurrency reconciliation

- The event began from Server `2.3.65` / Chat `1.4.59`.
- Immediately before version assignment, the authorities were re-read and had advanced concurrently to Server `2.3.66` / Chat `1.4.60` for the Ice Dragon adult-wallpaper repair.
- The originally planned version numbers were discarded and the RMCCA event was reassigned to Server `2.3.67` / Chat `1.4.61` from the newest authority.

### Verification / deployment state

- `versions/server-runtime.txt` advanced from `2.3.66` to `2.3.67`.
- `versions/web-chat.txt` advanced from `1.4.60` to `1.4.61`.
- LALM engine remains `2.1.26` because the R39 engine source itself was not modified.
- **Production deployment:** NONE requested; runtime-only Chat/model-policy update.
- **Server restart:** NONE requested.
- Acceptance remains camera-driven: verify natural identity framing, natural social participation, multi-domain RMCCA metadata, and stable checkpoint reuse in the next conversation log.

### Relevant lineage

- RMCCA cognitive policy: `984f783165f96326d58a90293a3fb7ffa8d21397`
- RMCCA camera integration: `c5a1689953a60e42c581151fa867312f9ef84e5d`
- RMCCA architecture document: `22017bbdc32e27a003e4c023ba83438d1bae3f48`
- Server version authority: `7743a48186e333b8356f99389e91a24897c63d75`
- Chat version authority: `2457c2cec2a676cd12bc6dd6e887b0b9b81708bb`
- Release record: `docs/releases/server-2.3.67-rmcca-integration.md`

## Server v2.3.66 — 2026-09-11/12

### Ice Dragon adult wallpaper source repair

- Exported theme diagnostics proved the v13 single-flight hydrator was active and correctly collapsing repeated boot triggers, while the adult wallpaper still failed because the source payload normalized to 7713 significant Base64 characters — an impossible `4n+1` length.
- Recovered the exact intended Ice Dragon wallpaper from project/user Library source artwork `32841.png` (864×1536).
- Rebuilt the artwork at the existing 180×320 theme aspect ratio as a valid JPEG and Base64-encoded the verified result.
- Replaced `web/themes/ice-dragon/assets/adult-180x320.jpg.b64` with the rebuilt payload; the existing v13 loader remains the runtime owner because its concurrency and diagnostics behavior were already verified.
- The live runtime asset path now returns the rebuilt payload directly from the `runtime` branch with `no-store` caching.

### Failure lineage preserved

- An intermediate replacement commit accidentally wrote a placeholder string into the adult payload path.
- The mistake was detected immediately and corrected by the next commit before acceptance; both commits remain in Git history.

### Verification / deployment state

- Local source recovery: exact 864×1536 artwork confirmed from Library.
- Rebuilt JPEG: 180×320, valid Base64 length divisible by four, local decode verified before commit.
- Live asset request: HTTP 200 from `github-runtime`, branch `runtime`, path `web/themes/ice-dragon/assets/adult-180x320.jpg.b64`.
- `versions/server-runtime.txt` advanced from `2.3.65` to `2.3.66`.
- `versions/web-chat.txt` advanced from `1.4.59` to `1.4.60`.
- **Production deployment:** NONE requested; runtime-only asset repair.
- **Server restart:** NONE requested.
- Browser acceptance gate: theme diagnostics should now show `adult-decode-ok` followed by `adult-painted`.

### Relevant lineage

- Intermediate placeholder write: `4b0ff408f68e5f2ade8c2005e255837a8c8f1014`
- Correct rebuilt adult payload: `08f9af180e8714a935a8a57c27624c0794d443ed`
- Server version authority: `6626332198a7ce61a4d4f67c79a98c2fd95a200b`
- Chat version authority: `ea16fe9fd0b6d23d9018dd21b639edbcb95adc4c`
- Release record: `docs/releases/server-2.3.66.md`

### Roadmap continuity note

Detailed intermediate release records from Server v2.3.29 through v2.3.65 remain preserved under `docs/releases/` and Git history. This active roadmap is re-anchored here to the current authoritative module versions rather than pretending the previously stale v2.3.28 header was current.

## Server v2.3.28 — 2026-09-11

### Responsive Chat geometry + response presentation

- User screenshots showed normal Android browser mode appearing oversized and clipping the right side of Chat, while Chrome desktop-site mode exposed a different proportion problem across sidebar, workspace, message cards, and composer.
- Added a final runtime responsive-polish stylesheet that constrains all major Chat surfaces to their actual container width and prevents long code/text from forcing horizontal page overflow.
- Mobile mode now keeps the app, workspace, top bar, message stack, composer, route control, theme selector inside the visual viewport while preserving internal horizontal scrolling for code blocks only.
- Desktop-site mode on phone-sized desktop CSS viewports now uses a compact desktop sidebar and bounded message/composer widths instead of inheriting full desktop proportions that crowd the workspace.
- Assistant response cards now have a more intentional layered card surface, softer radius, cleaner code-block spacing, and improved overflow handling without changing response semantics or LALM output.
- Existing Ice Dragon selection, account state, camera controls, stream behavior, message storage, and LALM behavior were intentionally left unchanged.

### Verification / deployment state

- `web/chat_responsive_polish.css` added on `runtime`.
- `runtime_pages/manifest.json` now loads responsive polish after the existing viewport correction so it owns only final geometry/presentation overrides.
- `versions/server-runtime.txt` advanced from `2.3.27` to `2.3.28`.
- `versions/web-chat.txt` advanced from `1.4.23` to `1.4.24`.
- **Production deployment:** NONE requested; runtime-only Chat update.
- **Server restart:** NONE requested.
- **Verification:** live source/asset verification follows this record; exact Android visual acceptance remains screenshot-driven.

### Relevant lineage

- Responsive polish stylesheet: `913960884b9a169cf1941884f219baf4b36e0f56`
- Runtime manifest wiring: `0b225f264327b8f62c4fc877696d4f946aefd069`
- Server version authority: `0e0c71013986e78976ddd2eea7919689db9e4d6e`
- Chat version authority: `10cc10c970ae5c8f37df83f9ee5b0820c350472`

## Server v2.3.27 — 2026-09-11

### Authoritative LALM engine version display

- Chat's version footer was corrected to resolve and display the authoritative `LALM_ENGINE` module version instead of the LALM UI version.
- Chat advanced to `v1.4.23`; Server runtime advanced to `v2.3.27`.
- The change remained runtime-only and did not alter LALM inference behavior.
- **Production deployment:** NONE.
- **Server restart:** NONE.

### Relevant lineage

- Chat version-display correction: `c0e4a17a49500966f687d124b87974bc6d6c2997`
- Chat version authority: `d60c84d98d32a44d4580bcfdfab5b850f60d41e1`
- Server version authority: `8d695b695b9b58ec55620f08bfdfe234204d1839`

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