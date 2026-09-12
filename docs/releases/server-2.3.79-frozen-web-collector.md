# Server 2.3.79 — Frozen Web Snapshot Collector

- Date: 2026-09-12
- Original lifecycle at first attempt: BLOCKED — deployment credential required (superseded by the live recovery receipt below)
- Production status at source publication: deployment approved and pending

## Versions

- Server Runtime: `2.3.79`
- Frozen Web Collector: `1.0.0`
- Deployment Control: `1.0.2`
- Web Chat: `1.4.71` unchanged
- LALM Engine: `2.1.30` unchanged

## Result

This release adds an authenticated browser-operated pipeline for creating bounded, durable, searchable frozen web snapshots. The operator registers sources, controls collection budgets and lifecycle, reviews evidence, seals immutable manifests, and separately decides whether qualified material may enter a reviewed training corpus.

The stable deployment hosts authentication and a fixed module contract. The interface and compatible collector engine remain owned by the `runtime` branch, so later compatible updates can be loaded live without another Vercel deployment.

## Safety and authority

- Private Vercel Blob owns durable state and immutable artifacts; `/tmp` is not authoritative.
- Robots compliance is mandatory and fail-closed.
- Only public HTTP/S destinations on safe ports are permitted; DNS results and every redirect are revalidated.
- TLS hostname verification is preserved while the connection is pinned to a validated address.
- Content types, bytes, redirects, domains, pages, documents, runtime, storage, and crawl rate are bounded.
- Raw HTML is discarded after extraction.
- Frozen search evidence is distinct from reviewed training data.
- Training acceptance requires explicit rights/provenance confirmation.

## Verification

`STATIC VERIFICATION PASS`

- `scripts/verify_web_snapshot_collector.py`
- `scripts/verify_collector_console.mjs`
- stable-host verification on the reconciled `main` candidate
- deployment workflow YAML parsing

`BUILD NOT RUN` and `RUNTIME NOT TESTED` refer only to the production deployment at the time this source record was authored. Deployment and live-browser evidence are recorded after the approved workflow completes.

## Lineage

- Initial runtime reconciliation: `26009037b55c158a0606e84bf69202b165e59057`
- Final runtime baseline: `3c2cc5efd320157ba67d888240f195344c015be7`
- Main baseline: `4a070f5d5cc8aba67ef0575d8567b2f0f9813f7a`
- First reconciled runtime checkpoint: `5b7744acc78a1a8508e5a954a4f5b2161db7a8d8`
- Final reconciled runtime checkpoint: `7cc1ccb9eb09857f945dab2ea992b2809d8b50f1`
- Rebased stable checkpoint: `636321dcd9f204eae08f5e9cfc567ab1b2ac5c1d`

No crawl, snapshot sealing, or training acceptance was performed as part of deployment.

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
