# §wyrlz Server Roadmap

## Current release

**Server v2.3.23**

This event improves LALM conversation prefill so a continuing thread can reuse more of the previous turn and spend less work rebuilding context before response generation.

### Module state

- **Server runtime v2.3.23** — current server development lineage.
- **Chat v1.4.20** — unchanged in this event.
- **LALM engine v2.1.20** / revision `2.1.20-hot-boundary-v11-prefill-checkpoints` — prefill reuse and prefill fast-path update.
- **LALM UI v1.0.0** — unchanged.
- **Google Account architecture v1.0.4** — unchanged.
- **Deployment Control v1.0.0** — unchanged.

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
