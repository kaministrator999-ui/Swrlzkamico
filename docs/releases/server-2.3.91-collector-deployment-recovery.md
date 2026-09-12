# Server 2.3.91 — Collector deployment recovery and live verification

Date: 2026-09-12
Checkpoint: `FROZEN-WEB-COLLECTOR-001`
Status: workflow source validated; live public host/UI/auth boundary verified; authenticated operator acceptance pending.

## Accomplishment

The collector is available on production and loads compatible engine/page updates from `runtime`. This event repairs the failed manual workflow and replaces obsolete missing-token status instructions with current deployment evidence.

## Version authority and lineage

- Baseline main: `349d8e85f9fe1ca6eef9eaed40357fda12a5beef`.
- Baseline runtime: `a8a215eab089eeea92a83879f3ca946a4657b8ec`.
- Server Runtime: `2.3.90` → `2.3.91`.
- Deployment Control: `1.0.2` → `1.0.3`.
- Collector `1.0.5`, Chat `1.4.77`, Web Frontend `1.0.3`, Google Account `1.0.8`, and LALM engine `2.1.30` retain their source and authority.
- Current authority was read at entry and re-read before version assignment. The runtime router and affected authorities were unchanged.
- The failed Collector 1.0.1/1.0.2 attempts and subsequent 1.0.3/1.0.4/1.0.5 repairs belong to intervening release history and are preserved; this event does not overwrite them.

## Change and deployment boundary

Only the manual workflow, Server/Deployment Control authorities, and documentation change. No collector engine, interface, Google auth, Chat, LALM, state schema, or stable API source changes.

Current `vercel.json` disables Git deployments. The only repository workflow triggers on explicit dispatch or a main push affecting `.deploy/REQUEST.txt`; this event does not change that request file or dispatch a workflow. **Deployment: NONE. Restart: NONE.**

The pinned setup action follows [Astral's official GitHub Actions integration](https://docs.astral.sh/uv/guides/integration/github/). The exact `uv`-missing failure is retained in the Actions job receipt below.

## Verification and rollback

The existing collector suite and focused new-snapshot revision regression pass against the canonical 1.0.5 source. Workflow YAML, every shell block, uv/build order, and readiness acceptance/rejection fixtures pass. These are source checks, not a new production build.

Rollback can revert this workflow/documentation/version event through a new governed versioned correction. No durable state migration or data deletion is involved. Do not roll back unrelated runtime or Google-auth work to restore the obsolete deployment baseline.

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
