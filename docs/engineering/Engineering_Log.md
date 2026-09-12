# SWRLZ Engineering Log

## 2026-09-12 — FROZEN-WEB-COLLECTOR-001

### Objective

Install one stable authenticated host and create a runtime-owned browser interface/engine for bounded, resumable frozen web snapshots, searchable evidence, and separately rights-reviewed training preparation.

### Source lineage

- Initial main/runtime baselines: `99b56cf63b305aae13728195a7277aa1758fadad` / `e47741237a3f79651af09c8ea5bd2d430c94bc38`.
- First pre-release concurrency baselines: main `4a070f5d5cc8aba67ef0575d8567b2f0f9813f7a`; runtime `26009037b55c158a0606e84bf69202b165e59057`.
- Final pre-release runtime baseline: `3c2cc5efd320157ba67d888240f195344c015be7` at Server `2.3.78` / Chat `1.4.71`.
- Reconciled checkpoints: stable `636321dcd9f204eae08f5e9cfc567ab1b2ac5c1d`; first runtime `5b7744acc78a1a8508e5a954a4f5b2161db7a8d8`; final runtime `7cc1ccb9eb09857f945dab2ea992b2809d8b50f1`.
- Planned Server 2.3.59 and 2.3.68 identities were discarded after concurrent authority advances; this event is Server 2.3.79.

### Facts

- `runtime` owns compatible collector engine and page updates.
- `main` owns the authentication/loader/compatibility boundary.
- Git deployment is disabled; `.deploy/REQUEST.txt` or explicit approved workflow dispatch is the production trigger.
- The user approved the bounded stable deployment and private Blob provisioning.
- The repository has no `docs/governance/SWRLZ_CONSTITUTION.md`; this absence is recorded rather than filled with assumed rules.

### Requirements

- Use private Vercel Blob for mutable control state and immutable evidence; never `/tmp` as authority.
- Use a fixed strict API/state schema contract at the stable host.
- Preserve source provenance, canonical URLs, content hashes, revision history, immutable manifests, and explicit training review.
- Enforce public-network-only fetching, verified TLS, redirect revalidation, mandatory robots compliance, politeness, MIME/byte/time/domain/storage budgets, and pressure stops.
- Keep deployment itself inert: no source registration, crawl, seal, or training acceptance.

### Engineering changes

- `SOURCE IMPLEMENTED`: stable collector host, private-storage deployment gate, runtime engine, `/collector` console, route manifest, module authority, tests, and operational documentation.
- Server authority prepared for `2.3.79`.
- Frozen Web Collector authority created at `1.0.0`.
- Deployment Control prepared for `1.0.2`.
- Chat `1.4.71` and LALM Engine `2.1.30` remain unchanged.

### Verification performed

- `STATIC VERIFICATION PASS`: runtime engine lifecycle/security/storage/sealing/training suite.
- `STATIC VERIFICATION PASS`: console contract with 91 unique IDs, safe rendering, session-only authorization, route/action bindings, and runtime manifest ownership.
- `STATIC VERIFICATION PASS`: stable-host module contract, readiness redaction, Admin rejection, body limits, dispatch, and source receipts.
- `STATIC VERIFICATION PASS`: runtime manifest JSON and deployment workflow YAML parsing.

### Runtime evidence

- `BUILD NOT RUN` at this entry stage.
- `RUNTIME NOT TESTED` on public production until the approved workflow completes.
- A post-deployment entry will record the actual run, deployment, readiness, authentication, browser, and log evidence.

### Known issues

- Cloud browser policy blocks local/private preview origins, so visual verification must use the public HTTPS deployment.
- Private Blob credentials must be present after workflow provisioning; the workflow fails closed if they are not.

### Exclusions

- No crawl, source registration, snapshot seal, training acceptance, data deletion, or unrelated module change.

### Follow-up

Publication and the approved trigger are complete. Configure the missing GitHub Actions `VERCEL_TOKEN`, re-run the failed deploy job in run 34708124306, verify the browser → API → Blob → response story, and append actual deployment evidence.

## Final continuation reconciliation

A further workspace-maintenance pruning removed the transient checkout. Recovered source from stable checkpoint `6861aedc32249fd7b5bdafc480f0e020238cf5d3` and runtime checkpoint `7cc1ccb9eb09857f945dab2ea992b2809d8b50f1`. Reconciled with current main `3f3d8eaeec4859099a3710155df8067577ca27fe` and runtime `3c2cc5efd320157ba67d888240f195344c015be7` (Server 2.3.78, Chat 1.4.71, LALM 2.1.30, Deployment Control 1.0.1). The unassigned collector 2.3.70 candidate was discarded; publication is Server 2.3.79, Collector 1.0.0, Deployment Control 1.0.2. The existing Google deployment request is preserved until the distinct approved collector trigger. No collection or training operation is part of deployment.

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
