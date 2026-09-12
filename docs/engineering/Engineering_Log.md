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

Re-read remote authorities, publish `runtime` and `main` with stale-write protection, trigger the one approved production request, verify the full browser → API → Blob → response story, and append actual evidence.

## Final continuation reconciliation

A further workspace-maintenance pruning removed the transient checkout. Recovered source from stable checkpoint `6861aedc32249fd7b5bdafc480f0e020238cf5d3` and runtime checkpoint `7cc1ccb9eb09857f945dab2ea992b2809d8b50f1`. Reconciled with current main `3f3d8eaeec4859099a3710155df8067577ca27fe` and runtime `3c2cc5efd320157ba67d888240f195344c015be7` (Server 2.3.78, Chat 1.4.71, LALM 2.1.30, Deployment Control 1.0.1). The unassigned collector 2.3.70 candidate was discarded; publication is Server 2.3.79, Collector 1.0.0, Deployment Control 1.0.2. The existing Google deployment request is preserved until the distinct approved collector trigger. No collection or training operation is part of deployment.
