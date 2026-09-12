# §wyrlz Server Roadmap

## Current release

**Server v2.3.92 — Frozen Web Collector 1.0.6**

**Status: authenticated state and storage access verified; configuration form repair published for live acceptance.**

The response-limit field now accepts the exact saved byte limit after conversion to MiB, fixing a native browser validation error that blocked saving current settings. Engine, stored data, and schema remain unchanged. Compatible runtime updates require no server redeployment.

- Server Runtime 2.3.92; Collector 1.0.6.
- Deployment Control 1.0.3, Chat 1.4.77, Web Frontend 1.0.3, Google Account 1.0.8, LALM engine 2.1.30 unchanged.

## Server v2.3.92 — 2026-09-12

Fixed the response-size field's step mismatch and aligned its MiB bounds with the server's byte limits. Authenticated state retrieval and private Blob listing passed before the repair. A browser save/reload will verify the corrected form and durable write. No crawl or training action was started. See [event receipt](releases/server-2.3.92-collector-configuration-save.md).

## Server v2.3.91 — 2026-09-12

Installs pinned uv before future Vercel builds, verifies compatible current Collector API/state schema 1 instead of a fixed 1.0.0, and checks saved HTML without a pipefail hazard. Collector suite, revision-continuity regression, and workflow validation pass. No production collection or training operation was initiated. See [current event receipt](releases/server-2.3.91-collector-deployment-recovery.md).

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

## Publication, workflow, and live-page evidence — 2026-09-12

- Lifecycle: **BLOCKED — deployment credential required**; source publication and focused verification are complete.
- Canonical runtime source: `aabe9d94f5461750ad013206c62a410f4d7dc893` (tree `0bbc113bacabac87c1672a0c9e57a85328332f77`).
- Canonical stable source: `329f4222b6ed159f472f29b093aa789accc76263` (tree `57d85e02c3fa32f568b0a2abdc24115fce4ef2a6`).
- Approved trigger: `eedda9a3777c3d97da866673317a155cb745ca48`, submitted at `2026-09-12T17:24:12.116Z`. Its `SOURCE_REF` pins the stable source commit above.
- Workflow: [Manual Vercel Production Deploy, run 34708124306](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/34708124306).
- Authorization job `103591797259`: **success**.
- Deploy job `103591825615`: **failure** at **Verify deployment token exists**, `2026-09-12T17:24:40Z`. The runner received an empty `VERCEL_TOKEN` and reported that the repository secret is required.
- CLI installation, environment pull, private Blob provisioning, build, deployment, and workflow production acceptance checks were all **skipped**. No collector deployment was created by this attempt.
- Vercel still reports preceding production deployment `dpl_Gjsx9ttTfqazCfQYWtRrbgzSPb3q`, `READY`, built from `3f3d8eaeec4859099a3710155df8067577ca27fe`.
- Live page verified at [Collector overview](https://swrlzkamico-o3nu.vercel.app/collector#overview): correct title, rendered sidebar/control room, budget cards, and administrator connection prompt. Visual inspection confirms the desktop layout renders correctly.
- The page honestly reports **Collector host unavailable**. Both `/api/collector/readiness` and `/api/collector/status` return **404** on the preceding deployment. Production authentication and Blob operations therefore remain **unverified**; the local focused tests remain passing.
- Collector engine and stable host tests pass; console contract passes with 91 unique IDs; workflow YAML and all nine shell blocks parse. Local/remote release tree IDs match exactly.
- No source registration, collection, sealing, training acceptance, or data deletion occurred.

### Exact recovery step — historical, superseded

**Do not execute this historical step. The live recovery verification below records the installed host and current state.**

Configure a valid Vercel deployment credential for the existing team/project as the GitHub Actions secret `VERCEL_TOKEN` in `kaministrator999-ui/Swrlzkamico` (repository secret or the workflow's `production` environment). Enter credentials only in the provider's secure settings, never in chat or tracked files.

Then re-run the failed deploy job in workflow run `34708124306`. The retained successful authorization output pins source `329f4222b6ed159f472f29b093aa789accc76263`; the same approved collector installation is still pending. Do not alter deployment settings or start a crawl as a workaround. After the job succeeds, verify readiness/storage/auth responses and browser operation, then append the actual deployment ID and result here.

Approval is already on record for this bounded installation; the remaining prerequisite is credential configuration. This receipt records new evidence for the same Server 2.3.79 event and does not introduce another source change or version event.

## Live recovery verification — 2026-09-12

This evidence supersedes the original missing-token recovery instructions. The collector host is already deployed. **Do not rerun the original deployment to install it again.**

- After the user saved the deployment token, run [34708124306](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/34708124306), attempt 2, deploy job `103597917306` passed token validation, Vercel access, and private Blob provisioning. The private `swrlz-collector-o3nu` store was created in `iad1` and connected to production at `2026-09-12T18:10:38Z`.
- That attempt stopped before deployment because Vercel CLI 59.16.0 required `uv`, which the runner lacked. The original missing-token failure remains preserved above.
- Independent production deployments subsequently installed the host. The currently verified production deployment is `dpl_3jK3gqEmX4dRNvPQSng2ywp5vhYq`, READY, stable source `ecad83c84b4a28d945190213ac28041d396b6638`. This continuation did not create another deployment.
- At `2026-09-12T22:26:58Z`, public `/api/collector/readiness` returned HTTP 200, `ready:true`, Collector `1.0.5`, API/state schema 1, configured private Vercel Blob, and `ephemeralTmpUsedAsAuthority:false`.
- The live host reports `github-runtime`, branch `runtime`, source `runtime_hot/web_snapshot_collector.py`, source SHA-256 `c8ae6439a93cdba0c365fea8e6e72b62d0b5cc4fecb52a5884d06d540377b1b1`, and `deploymentRequiredForRuntimeChanges:false`.
- Anonymous `/api/collector/status` returned HTTP 401. The browser at [Collector overview](https://swrlzkamico-o3nu.vercel.app/collector#overview) rendered the expected console, showed `1.0.5 · private storage ready`, and requested the existing SWRLZ admin token.
- The Vercel error query for the two collector API routes found no errors from `2026-09-12T22:26:00Z` through this check.
- Current Collector 1.0.5 passes the complete deterministic collector suite. An additional isolated check verified that Start new carries revision 7 into the next snapshot, saves revision 8 without a usable ETag, and rejects a stale prior revision. These checks did not access production state.
- **Verification limit:** readiness proves module loading and storage configuration; it does not prove authenticated Blob reads/writes or a complete production collection run. This session still requires secure administrator sign-in for that acceptance check.
- No source registration, collection, sealing, training acceptance, or data deletion was performed by this continuation.

Server 2.3.91 / Deployment Control 1.0.3 repairs the manual workflow for future explicitly approved deployments. It installs pinned uv before building, accepts compatible versioned API/state schema 1 runtime modules instead of requiring Collector 1.0.0, and checks the saved HTML without an early-closing curl/grep pipeline. Its receipt now accurately calls the storage check a configuration check. Workflow YAML/shell syntax and positive/negative readiness fixtures pass. The repaired workflow was not dispatched because production already has the host.
