# §wyrlz Server Roadmap

## Current release

**Server v2.3.72**

This event replaces the active Ice Dragon adult wallpaper's 180×320 source with the existing 864×1536 source payload while preserving the verified direct `.messages` paint path.

### Module state

- **Server runtime v2.3.72** — current server development lineage.
- **Chat v1.4.66** — Ice Dragon full-resolution adult wallpaper hydration.
- **LALM engine v2.1.26** — unchanged.
- **LALM UI v1.0.0** — unchanged.
- **Google Account architecture v1.0.4** — unchanged.
- **Deployment Control v1.0.0** — unchanged.

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

## Server v2.3.71 — 2026-09-12

### Triggering camera evidence

- A fresh `Hey 👋` turn was classified by the engine as `brief-social` but still generated `This is a friendly greeting. How can I assist you today?`, proving response framing remained meta-descriptive instead of participatory.
- The same camera reported `authority=unknown`, `envelope=none`, `first-send receipt=n/a`, and `RMCCA=not-captured`.
- Recovery then reported `canonicalEnvelopePreserved=false` after a server-instance change.
- Raw model capture concatenated output from the original generation and the recovery generation even though visible reconciliation correctly showed only one coherent answer, making the raw `modelText` unsafe as canonical future history.

### RMCCA social participation

- Advanced policy to `rmcca-cognitive-policy-v4-social-participation` and envelope to `swrlz-rmcca-context-v3`.
- Greeting/social topology now explicitly requires direct conversational participation: greet back, match conversational energy, and continue naturally.
- Meta-descriptions such as `This is a friendly greeting` are explicitly disallowed.
- Greeting cues now activate the social domain and conversational reference frame.

### Canonical transport hardening

- Canonical context preparation now degrades safely instead of silently disappearing when a diagnostic/history substep fails.
- Background transport validates that the outgoing payload owns the current canonical envelope and retries canonical preparation if needed.
- Canonical receipts are retained by request ID until terminal completion rather than being consumed too early.
- Camera transport metadata now records canonical preparation status/errors, envelope identity, request attempt, and generation branch identity.

### Recovery-safe canonical model text

- Every generation attempt receives a branch identity (`requestId:branch-N`).
- Recovery advances to a new branch and the camera resets raw capture at that branch boundary.
- Terminal `modelText` is now sourced only from the winning generation branch and marked `canonicalModelTextSource=winning-generation-branch`.
- This prevents pre-recovery partial output from being concatenated into canonical history after a regenerated response.

### Concurrency reconciliation

- Transaction baseline: Server `2.3.70` / Chat `1.4.64`.
- Immediately before version assignment both authorities were re-read and remained unchanged.
- The event therefore safely advanced to Server `2.3.71` / Chat `1.4.65` using the fresh authority SHAs.

### Verification / deployment state

- Runtime source changed only on `runtime`.
- LALM engine remains `2.1.26`; R39 inference source was not modified.
- **Production deployment:** NONE requested.
- **Server restart:** NONE requested.
- Browser acceptance remains camera-driven. A fresh greeting should report `cognitiveAuthority=chat_context_canonical`, envelope `swrlz-rmcca-context-v3`, topology `social-participation`, conversational frame, and natural greeting behavior. If recovery occurs, the same envelope should remain preserved and only one winning raw generation branch should become canonical history.

### Relevant lineage

- Canonical RMCCA v4: `6968b1489732df12609556d5a80e23305e9ff497`
- Recovery/canonical transport lineage: `623c4ece6b2595a796c51130d5cea8df8e8fa0cb`
- Branch-aware context camera: `70863beab2cd9ad2463a6568137dda3073e135d1`
- Server version authority: `0ef58926f166f1d5aee8aeb4560cf50244887e15`
- Chat version authority: `134bc2ef18c76739a779ccc9d223d7ae3cea75c0`
- Release record: `docs/releases/server-2.3.71-rmcca-social-recovery-lineage.md`

## Server v2.3.70 — 2026-09-12

### Identity framing stabilization

- Clean-thread acceptance showed that identity fact retrieval had improved: `What's your name?` returned the correct `§wyrlz` identity.
- The response still failed conversational framing because it emitted only the bare identity label rather than a natural first-person answer.
- RMCCA cognitive policy advanced to `rmcca-cognitive-policy-v3-natural-identity`.
- Identity-answer topology now explicitly requires a natural first-person contextual answer such as `I'm §wyrlz.` or an equivalent.
- Bare `§wyrlz` output is no longer the desired topology unless the user explicitly requests only the label/name.
- Identity detection now also recognizes variants such as `What should I call you?`.

### First-send cognitive camera receipt

- The same clean acceptance test showed `authority=unknown`, `envelope=none`, and `RMCCA=not-captured` even though there was no recovery attempt.
- Root cause was an observability timing gap: canonical request preparation could run before the assistant placeholder message existed, so message-local annotation had no target.
- `web/chat_context_canonical.js` now keeps a bounded request-ID keyed pending cognitive receipt before the request leaves Chat.
- The receipt carries cognitive authority, canonical envelope ID, directive ID, history provenance, prompt size, and RMCCA clock diagnostics.
- `web/chat_context_camera.js` now hydrates that pending receipt onto the matching assistant message on the first stream event and retries at terminal completion.
- Camera continuity telemetry now records whether a first-send receipt was attached.
- Canonical envelope advanced to `swrlz-rmcca-context-v2`.

### Concurrency reconciliation

- Work began from authoritative Server `2.3.69` / Chat `1.4.63`.
- Immediately before version assignment both authorities were re-read and remained unchanged.
- The event therefore safely advanced to Server `2.3.70` / Chat `1.4.64` using the fresh authority SHAs.

### Verification / deployment state

- `versions/server-runtime.txt` advanced from `2.3.69` to `2.3.70`.
- `versions/web-chat.txt` advanced from `1.4.63` to `1.4.64`.
- LALM engine remains `2.1.26`; R39 inference source was not modified.
- **Production deployment:** NONE requested; runtime-only Chat/model-context update.
- **Server restart:** NONE requested.
- Browser acceptance gate: a fresh identity request should return a natural contextual identity answer and the camera should report `cognitiveAuthority=chat_context_canonical`, `canonicalEnvelopeId=swrlz-rmcca-context-v2`, `firstSendReceiptAttached=true`, and RMCCA topology `identity-answer`.

### Relevant lineage

- Canonical RMCCA / identity framing: `53253034318d076c64a4cebd981a0ccfa07d21bc`
- First-send camera receipt bridge: `a66d2007d488e428926a4983799c6bf36e3c8ce2`
- Server version authority: `f1ac6dcc53fd6a9b9d61e134e6b93e28761a1e4d`
- Chat version authority: `7711a90a00c9690c3c1fb48c47941983663fc45f`
- Release record: `docs/releases/server-2.3.70-rmcca-first-send-receipts-identity-framing.md`

## Server v2.3.69 — 2026-09-12

### RMCCA single cognitive authority

- A fresh browser close/reopen still answered `What's your name?` with `I don't have a name. I'm an AI`, disproving the stale-tab-only explanation.
- `web/chat_context_canonical.js` became the single owner of model-facing response policy, canonical history, RMCCA diagnostics, and persisted cognitive request envelope.
- Background recovery stopped injecting its older competing response directive and instead preserves the canonical RMCCA request.
- The leading-`§wyrlz` display suppression path was removed so correctness belongs to model understanding/generation rather than presentation hiding.
- Recovery camera telemetry gained attempt count, original request start time, recovery elapsed time, and canonical-envelope preservation evidence.
- Server advanced to `2.3.69`; Chat advanced to `1.4.63`; LALM remained `2.1.26`.
- Release record: `docs/releases/server-2.3.69-rmcca-single-authority.md`.

## Server v2.3.68 — 2026-09-12

### Ice Dragon adult wallpaper quality pass

- Re-encoded the verified adult Ice Dragon artwork at substantially higher JPEG quality while preserving the already-working wallpaper hydrator and rendering path.
- Server advanced to `2.3.68`; Chat advanced to `1.4.62`; LALM unchanged.
- Release record: `docs/releases/server-2.3.68-ice-dragon-wallpaper-quality.md`.

## Server v2.3.67 — 2026-09-11/12

### Recursive Multi-Domain Cognitive Clock Architecture integration

- Added formal RMCCA architecture documentation.
- Integrated stable RMCCA response policy for progressive structure decoding, scope preservation, local revision, simultaneous multi-domain activation, domain salience, resolution depth, contextual reference frames, synthesis ordering, and response-topology selection.
- Added RMCCA camera telemetry.
- Concurrency reconciliation detected concurrent advancement from Server `2.3.65` / Chat `1.4.59` to `2.3.66` / `1.4.60`; this event correctly advanced to Server `2.3.67` / Chat `1.4.61`.
- Release record: `docs/releases/server-2.3.67-rmcca-integration.md`.

## Server v2.3.66 — 2026-09-11/12

### Ice Dragon adult wallpaper source repair

- Diagnostics identified an invalid Base64 adult-wallpaper payload.
- Recovered the intended artwork, rebuilt a valid JPEG/Base64 payload, and preserved the already-verified loader architecture.
- An intermediate placeholder write was detected and corrected; both commits remain in Git history.
- Server advanced to `2.3.66`; Chat advanced to `1.4.60`.
- Release record: `docs/releases/server-2.3.66.md`.

## Roadmap continuity

Detailed Server v2.3.29 through v2.3.65 records remain preserved under `docs/releases/` and Git history. Earlier Server v2.3.28 and prior roadmap history also remains preserved in Git history. This active roadmap intentionally keeps the current development frontier compact while every new server event must still be recorded here and in its release record.

## Mandatory roadmap/version law

Every server development event gets a new overall Server runtime authority when project state changes, including failed attempts.

Every module actually changed gets its own version increment. A module that did not change keeps its version.

`VERSION.txt` is the module-authority router. It maps stable module IDs to their own `versions/<module-id>.txt` files and does not duplicate their values.

Consumers fetch the owning module authority when they need a version for display or update comparison. They do not maintain another module's version manually.

Every event records what changed, affected module versions, failed attempts where applicable, verification state, deployment/restart state, and relevant lineage.

Before version assignment, the authoritative Server and affected-module version files must be re-read and compared to the transaction baseline. If either changed during work, planned version numbers are discarded, current state is reconciled, and the next valid versions are calculated from the newly current authorities. Roadmap updates must use the freshly re-read roadmap SHA and are part of the same guarded release transaction.
