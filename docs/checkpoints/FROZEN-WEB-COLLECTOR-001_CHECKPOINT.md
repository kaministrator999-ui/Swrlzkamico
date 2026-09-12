# Checkpoint FROZEN-WEB-COLLECTOR-001: Browser-operated frozen web snapshots

Mode: IMPLEMENT
Lifecycle state: DOCUMENTATION_SYNCED; publication/build/runtime gates pending
Status: source implementation verified and deployment explicitly approved

## Objective

Create a professional browser interface and a bounded, durable server pipeline that can collect public web material into frozen searchable snapshots and separately prepare rights-reviewed training material for the §wyrlz LALM. Install the stable authenticated host once on Vercel while keeping compatible page and collector-engine updates live from the `runtime` branch without subsequent server redeployment.

## Success criteria

- `/collector` provides complete operator controls and evidence views.
- Collection is resumable from durable state and bounded by explicit policies.
- Frozen search evidence is immutable and remains separate from training decisions.
- Training acceptance requires an explicit rights/provenance confirmation.
- SSRF, redirects, robots, MIME, bytes, time, domains, politeness, and pressure limits are enforced.
- Private Vercel Blob, not `/tmp`, owns durable collector state.
- Stable authentication and runtime-source compatibility are verified.
- The approved production workflow provisions storage, deploys once, and verifies the public page/readiness/auth boundary.
- Later compatible collector changes are loaded from `runtime` without redeployment.

## Confirmed facts

- Repository: `kaministrator999-ui/Swrlzkamico`.
- Production project: `swrlzkamico-o3nu` at `https://swrlzkamico-o3nu.vercel.app`.
- Vercel project ID: `prj_dGgleDMgkOQ57wULKlDH5fcYj9Yp`.
- Vercel team ID: `team_E4y2LpTSFo9UxTErO9aw6HW1`.
- `vercel.json` disables Git deployment.
- Production deployment is triggered only by an approved workflow dispatch or a `main` push changing `.deploy/REQUEST.txt` with its approval fields.
- The user explicitly approved the bounded stable-host deployment and private Blob provisioning, then directed work to continue.
- `docs/governance/SWRLZ_CONSTITUTION.md` is absent from the current repository. Project-start, hotfix, version-evolution, accepted contracts, current implementation, and direct evidence were therefore used in the next available authority order; no absent constitutional text was invented.

## Requirements

- Use the server through a live browser.
- Preserve the stable-loader/runtime-source architecture.
- Allow compatible page and engine updates without redeploying the server.
- Save progress continuously so recovery does not depend on transient workspace state.
- Preserve source lineage and concurrent work.
- Do not start collection or approve training as part of deployment.

## Assumptions

- Private Vercel Blob remains available to this project and within the operator's accepted plan/usage boundary.
- The existing Admin token remains the correct authorization boundary for this operator-only surface.
- API schema 1 and state schema 1 remain compatible for runtime-hot revisions; an incompatible future change crosses the stable deployment gate.

## Sources of truth inspected

- `SWRLZ_PROJECT_START.md`
- `SWRLZ_HOTFIX_RULES.md`
- `SWRLZ_VERSION_MODULE_EVOLUTION.md`
- `SWRLZ_SERVER_ROADMAP.md`
- `vercel.json`
- `.github/workflows/manual-vercel-production.yml`
- runtime `VERSION.txt` and affected `versions/*.txt` authorities
- current `main` and `runtime` branch heads
- supplied `SWRLZ_Frozen_Web_Snapshot_Collector_Design.docx`
- implemented stable host, runtime engine, browser console, manifests, and focused verification scripts

## Source lineage and concurrency

The implementation began from:

- main `99b56cf63b305aae13728195a7277aa1758fadad`;
- runtime `e47741237a3f79651af09c8ea5bd2d430c94bc38`;
- Server `2.3.58`, Chat `1.4.52`, Deployment Control `1.0.1`.

At the first release-boundary revalidation, current authority had advanced to:

- main `4a070f5d5cc8aba67ef0575d8567b2f0f9813f7a`;
- runtime `26009037b55c158a0606e84bf69202b165e59057`;
- Server `2.3.67`, Chat `1.4.61`, Deployment Control `1.0.1`.

At the final commit boundary, runtime advanced again to `349ebf5f8e2d8c6927d131905ec595145a9816b0`, Server `2.3.69`, and Chat `1.4.62`. Planned Server `2.3.59` and `2.3.68` identities were discarded. Collector work was reconciled again, preserving the concurrent Ice Dragon and RMCCA changes, and reassigned to Server `2.3.70`.

Recovery checkpoints:

- original stable checkpoints: `e3c7e51f5a36017e253108cd8555f8daab60dd17`, `f2a8106c8d3328d0918edd1f4ed58781cd3a7577`;
- original runtime checkpoints through `9cf836bda3792f5cd4fd2b02452d2196e4749af6`;
- reconciled stable checkpoint: `636321dcd9f204eae08f5e9cfc567ab1b2ac5c1d`;
- first reconciled runtime checkpoint: `5b7744acc78a1a8508e5a954a4f5b2161db7a8d8`;
- final reconciled runtime checkpoint: `852a27207a89554ff8c37b5ed3b149b1d5b66a21`.

Three transient workspace pruning/reset events occurred during the checkpoint. Functional code was recovered from the GitHub checkpoints each time. The documentation draft not yet published during the latest pruning event was reconstructed from source evidence rather than represented as previously saved.

## Files and areas changed

### Stable `main`

- `api/collector_host.py`
- `api/index.py`
- `requirements.txt`
- `scripts/verify_collector_host.py`
- `.github/workflows/manual-vercel-production.yml`
- project-start/hotfix/version rules, roadmap, README, contract, release, engineering, and checkpoint records

### Live `runtime`

- `runtime_hot/web_snapshot_collector.py`
- `web/collector.html`
- `runtime_pages/manifest.json`
- `runtime_pages/index.html`
- `requirements.txt`
- `VERSION.txt`
- `versions/server-runtime.txt`
- `versions/frozen-web-collector.txt`
- `versions/deployment-control.txt`
- `scripts/verify_web_snapshot_collector.py`
- `scripts/verify_collector_console.mjs`
- runtime README, hot-update guide, roadmap, and release record

## Implementation summary

- Added a stable, authenticated, size-bounded runtime-module host with fixed `runtime` source selection, source/version SHA receipts, API schema checks, cache-busted refresh, atomic disposable code caching, and last-known-good behavior.
- Added a private-Blob-backed collector state machine with source registry, priorities/policies, explicit budgets, durable checkpoints, and configure/start/pause/continue/step/seal actions.
- Added canonicalization, public-network validation, redirect/robots/politeness enforcement, text extraction, raw-HTML discard, content-hash deduplication, URL revision history, quality/privacy scoring, chunking, provenance, and immutable artifacts.
- Added lexical frozen-snapshot search and document/manifest inspection.
- Added a separate training-candidate queue with explicit accept/reject review and mandatory rights/provenance confirmation for acceptance.
- Added the professional responsive browser console with overview, source, search, frontier, training, snapshot, and safety views.
- Added private Blob provisioning and post-deployment acceptance checks to the existing manual Vercel workflow.

## Documentation impact set

- Categories: AUTHORITY / INDEX; CHECKPOINT / DELIVERY RECEIPT; CHANGELOG / RELEASE NOTE; CONTRACT / PROTOCOL / SCHEMA; CAPABILITY / SETTINGS; UI / UX; REPOSITORY / CI; ROADMAP / MILESTONE; PROVENANCE / LINEAGE; HANDOFF.
- Documents updated: project-start module examples, hotfix ownership, version-evolution registry, both branch READMEs, runtime hot-update guide, both roadmaps, collector V1 contract, release records, engineering log, and this checkpoint receipt.
- Architecture documents intentionally unchanged: the established stable-host/runtime-source architecture is extended rather than replaced; the collector contract records the new boundary.
- Migration documents intentionally unchanged: no pre-existing collector state exists to migrate.
- Package/checksum: not applicable to this repository-backed web release. Canonical Git commit/tree identities and Vercel deployment evidence replace a source ZIP pair.
- Documentation gate: pending final publication/live-evidence append at this stage.

## Verification

### Source checks completed

- Python compilation of stable host and runtime collector: pass.
- `scripts/verify_collector_host.py`: pass.
- `scripts/verify_web_snapshot_collector.py`: pass.
- `scripts/verify_collector_console.mjs`: pass with 91 unique element IDs.
- Runtime page manifest JSON parsing: pass.
- Production workflow YAML parsing: pass.

The focused runtime suite verifies Blob API v12 headers, truthful unconfigured storage state, loopback/private SSRF rejection, external redirect boundaries, destination robots checkpointing, shallow/deep source policy, start/pause/continue lifecycle, state checkpointing, search, deterministic seal retry, immutable frozen documents across training review, rights confirmation, separate accepted/rejected corpora, and storage preflight before immutable writes.

### Build evidence

- Status: `BUILD NOT RUN` at documentation stage.
- Workflow/run: approved production workflow pending.
- Artifact: pending Vercel deployment.
- Evidence pending: build/deploy result, production deployment identity, readiness output, and post-deploy error scan.

### Runtime evidence

- Local simulated runtime: focused engine/host/console checks pass.
- Public production page/API: `RUNTIME NOT TESTED` until the stable host is deployed.
- Browser acceptance: pending public HTTPS deployment; the controlled cloud browser rejects local/private preview origins, and no bypass was attempted.

## Security and authority preservation

- Recognition is not authorization; every operational route remains Admin authenticated.
- The public readiness route is deliberately bounded and credential-free.
- Robots compliance cannot be disabled.
- Frozen evidence does not authorize training.
- The user remains the authority for source selection, collection lifecycle, sealing, and training review.
- No silent local-to-remote fallback or unrelated LALM modification was introduced.
- The Truth Firewall remains unaffected; no obedience-only or automatic-training path was added.

## Known limitations

- V1 advances bounded batches through browser/API actions rather than a permanent background daemon.
- Search is lexical preparation, not semantic/vector retrieval.
- A currently loaded worker refreshes compatible runtime code on its bounded refresh interval; cold workers reconstruct from GitHub `runtime`.
- Production verification depends on private Blob credentials being injected by the approved Vercel workflow.
- Live operator actions require the existing Admin token; that credential is not stored in source or checkpoint documentation.

## Exclusions

- No source was registered on behalf of the operator.
- No crawl or broad internet snapshot was initiated.
- No snapshot was sealed.
- No training material was accepted or applied to the LALM.
- No Chat, RMCCA, Ice Dragon, Android, or unrelated server behavior was changed.
- No destructive/cleanup operation was performed on existing Blob data.

## Current disposition

Source and documentation are prepared on reconciled release branches and recoverable GitHub checkpoints. The next gate is a final remote authority re-read, canonical publication, the already approved one-time production deployment, and live browser/API verification. Final commit, workflow, deployment, and browser receipts will be appended after they actually exist.

## Approval required to continue

- Waiting for: NOT APPLICABLE; the user already explicitly approved the bounded production deployment and private Blob provisioning and directed continuation.
- Approval authorizes: canonical publication of this collector checkpoint, one production workflow trigger through `.deploy/REQUEST.txt`, idempotent private collector Blob provisioning/connection, and live verification.
- Approval does not authorize: initiating a crawl, registering third-party sources, accepting training material, deleting existing data, or unrelated repository/deployment changes.
- Expected result: live `/collector` control room with authenticated operations and future compatible runtime updates that require no server redeployment.
- Exact approval phrase: already received as `Approved`, followed by `continue`.
