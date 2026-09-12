# §wyrlz Hotfix Rules — READ THIS FIRST

**Purpose:** prevent unnecessary Vercel redeploys and accidental overwrites of the live Chat application while preserving complete Server/module version lineage.

## One rule

**`runtime` is the live application source of truth. `main` is stable loader/infrastructure. Deployment capability is determined by the current deployment configuration/workflows, not by branch name alone.**

For normal Chat/page/LALM changes: **edit `runtime` → capture authoritative versions → make the smallest change → revalidate authoritative versions → increment the overall Server version → increment every affected module version → update the roadmap/release record → commit → reload/request → verify. DO NOT DEPLOY. DO NOT RESTART.**

## HARD STOP — Deployment Approval Gate

**No repository action that can actually cause deployment/redeployment may be performed without explicit user approval first.** This rule applies to code, documentation, configuration, merges, workflows, and explicit deployment actions.

Before any mutation to a branch, file, configuration, merge target, workflow, or other repository state that could trigger deployment, the agent must STOP and tell the user:

- what exact branch/path/configuration/action causes deployment;
- why it causes deployment;
- whether deployment is architecturally required or merely automatically triggered by the deployment configuration;
- what deployed surface would be affected;
- whether the work can be performed through `runtime` without deployment;
- the exact repository action awaiting approval.

**The agent must obtain explicit user approval before performing that action.** If deployment behavior is uncertain, treat it as deployment-capable and stop. Never infer approval from a general request to fix, update, document, commit, merge, or architect.

### Deployment capability determination

Before invoking the gate, inspect the current deployment configuration and relevant workflows.

- A commit to `main` is **not inherently a deployment**.
- A documentation change is **not inherently deployment-capable**.
- If Git-based deployment is disabled and no workflow or other automation deploys the proposed mutation, the commit may proceed without deployment approval.
- If a later configuration change makes the branch/path deployment-watched, the gate applies again immediately.
- An explicit deployment command/action always requires explicit approval unless the user has already approved that exact deployment-producing action.

The currently verified baseline uses Vercel configuration with Git deployment disabled; future §wyrlz instances must still re-check current configuration rather than assuming that remains true forever.

A commit is not deployment authorization. A merge into a deployment-watched branch is not deployment authorization. The user may choose to perform the actual deployment manually.

## Mandatory Server + module versioning

Every server-side development event that changes runtime or governed project state is a new overall **Server version**, including a tiny change, a test-only version event, an unsuccessful attempt, or a failed fix.

The Server version is the umbrella chronological release/event number. Module versions record the lineage of the components actually changed underneath that Server version.

Example:

```text
Server v5.5.6

Chat v5.5.5
- Sidebar fix.

LALM v5.5.4
- No change.
```

If the next change is only LALM:

```text
Server v5.5.7

LALM v5.5.5
- Inference fix.
```

If an attempt fails, record the failure as its own Server version. The subsequent fix is another Server version.

## Mandatory update workflow

For **every** runtime/server-governed update:

1. Determine the current Server version.
2. Determine the current version of every affected module.
3. Record the authoritative version values and file/blob SHAs as the event baseline.
4. Fetch the current target file(s) from the authoritative branch before editing.
5. Determine from current configuration/workflows whether any proposed repository action can actually cause deployment.
6. If deployment-capable, **STOP → explain the trigger/reason → obtain explicit user approval before mutation.**
7. Make the smallest targeted change possible.
8. **Immediately before assigning versions or committing, re-read `VERSION.txt` and every affected authoritative `versions/<module-id>.txt` file.**
9. Compare that state to the event baseline. If anything relevant changed, assume another instance/process advanced the project and reconcile from the newest authority before continuing.
10. Increment the overall Server version from the newest authoritative state.
11. Increment every module version that actually changed.
12. Update every canonical in-code/version-source location for those versions.
13. Update every module-owned UI/status surface that should show its own version.
14. Cross-module version displays must retrieve the owning module's authoritative version automatically; do not duplicate stale hardcoded versions.
15. Update the roadmap/release record with the Server version, affected module versions, changes, failures, verification state, and deployment state.
16. Commit code + version records + roadmap on the correct branch/path.
17. Use repository SHA/precondition checks where available so concurrent writes fail instead of overwriting newer state.
18. Re-read the authoritative version files after mutation/commit and verify they match the versions assigned to the event.
19. Reload/request every affected route when applicable.
20. Verify live behavior, version responses, visible version displays, and source lineage.
21. Verify no legacy injector/loader overrides the runtime asset.
22. Only then declare the update complete.

## Version ownership

- **Repository version router:** `VERSION.txt`; it identifies the authoritative version file for each module and must not become a second manually maintained copy of every module's version value.
- **Server runtime:** `versions/server-runtime.txt`.
- **Server UI:** `versions/server-ui.txt`.
- **Chat:** `versions/web-chat.txt`.
- **Stream contract:** `versions/stream-contract.txt`.
- **LALM UI:** `versions/lalm-ui.txt`.
- **LALM engine:** `versions/lalm-engine.txt`.
- **Admin web:** `versions/admin-web.txt`.
- **Google account architecture:** `versions/google-account.txt`.
- **Android client APK:** `versions/client-apk.txt`.
- **Android server APK:** `versions/server-apk.txt`.
- **Frozen Web Snapshot Collector:** `versions/frozen-web-collector.txt`.
- **Deployment control:** `versions/deployment-control.txt`.

Existing API/status/code constants may expose or consume these values, but the **module-owned version file is the version identity authority**. Cross-module consumers must fetch the owning module's authority, directly or through a status/API surface derived from it. They must not maintain duplicate version literals.

If a new independently evolvable structure is introduced, it must receive a stable module ID, its own `versions/<module-id>.txt`, and an entry in `VERSION.txt` in the same development event.

If the real current version of an existing artifact has not been verified, use an explicit unassigned/unknown state rather than inventing a version.

## NO REDEPLOY required

These belong on `runtime`:

- `web/chat.html` — Chat page/UI
- `web/chat_*.js` — Chat behavior, stream UI, enhancements, version display
- `web/chat_*.css` — Chat styling
- `web/server.html`, `web/lalm.html`, and other runtime-owned pages
- `runtime_pages/manifest.json` — add/remove/change runtime routes
- runtime assets under `web/` or `runtime_pages/`
- runtime-loadable LALM/inference code, including active R39 runtime source
- normal Chat behavior already supported by the stable loader
- runtime-owned `VERSION.txt` and `versions/*.txt` authority changes when the existing loader already serves them

### Hotfix procedure

1. **Fetch the current target file from `runtime` first.**
2. Capture current Server/module authorities and SHAs.
3. Make the **smallest targeted edit** possible.
4. Re-read the affected authorities immediately before version assignment/commit.
5. If they changed, reconcile first; never use stale planned version numbers.
6. Apply the required Server/module version bumps.
7. Update the affected module-owned version file(s) and `VERSION.txt` only when routing/registration changes.
8. Update the roadmap/release record.
9. Commit it to `runtime`.
10. Re-read the authorities to verify the committed versions.
11. Reload/request the affected route.
12. Verify the live response/headers/version/behavior comes from `runtime`.
13. If wrong, make another versioned runtime fix; do not silently overwrite the previous event.

### NEVER do this for a hotfix

- Do not replace a whole page when one line/script needs changing.
- Do not inject a second hardcoded Chat version from `main`.
- Do not use `/tmp` as source of truth.
- Do not restart the server to expose ordinary runtime changes.
- Do not trigger Vercel deployment for ordinary runtime edits.
- Do not change `dev` when the task is a Chat/runtime hotfix; use `runtime`.
- Do not manually copy another module's version into a second module when an authoritative version file/status source can provide it.
- Do not treat `VERSION.txt` as a duplicated ledger of module numbers; it routes to module-owned authorities.
- Do not write a version that was planned from an earlier snapshot without revalidating the current authority first.

## REDEPLOY required

Stable infrastructure changes may require `main` plus a production deployment, including:

- Python API routes or middleware
- authentication/session/security boundaries
- runtime loader/source-resolution logic
- runtime hydration/sync mechanism
- deployment/build configuration (`vercel.json`, build/runtime configuration)
- a new bundled dependency or stable server capability
- a capability the existing runtime loader cannot serve

A `main` mutation and a deployment are separate concepts. Under manual-deployment configuration, `main` may be updated without deploying. If production behavior must change through an actual deployment action, **the agent must pass the Deployment Approval Gate before that deployment-producing action.**

## Restart/cold-start rule

GitHub `runtime` is durable. `/tmp`, memory caches, loaded Python module objects, and Vercel instance state are disposable. A restart must be able to recreate active runtime state from `runtime` automatically.

## Ownership

- **Chat UI/code:** `runtime`
- **Chat stream/UI enhancements:** `runtime`
- **Chat version display:** `runtime`
- **LALM/R39 runtime code:** `runtime`
- **Module-owned version authorities:** `runtime` for runtime-owned modules
- **Stable API/loader/security infrastructure:** `main`
- **Project engineering contract documents:** `main`, with deployment capability determined from current configuration rather than branch name alone

Changing LALM internals does **not** require changing the Chat version unless user-facing Chat behavior/protocol changed.

## Versioning rule

If asked to bump a module version, update that module's authoritative version file, bump the overall Server version when the event is server-governed, and update the roadmap. **Do not rewrite an unrelated page or module merely to carry the version number.** UI/status surfaces should derive the value from the authority.

## Verification checklist

Before saying a hotfix/update is done:

- [ ] Current target file was fetched first.
- [ ] Current Server/module versions established from authoritative sources.
- [ ] Baseline authority values/SHAs were captured.
- [ ] Deployment risk was evaluated from current configuration/workflows before repository mutation.
- [ ] Explicit approval was obtained before any action that can actually cause deployment.
- [ ] Only intended files changed.
- [ ] Authorities were re-read immediately before version assignment/commit.
- [ ] Any concurrent authority change was reconciled instead of overwritten.
- [ ] Server version bumped when required by the event contract.
- [ ] Every affected module version bumped.
- [ ] Affected module-owned version files updated.
- [ ] `VERSION.txt` routing updated only if module registration/ownership changed.
- [ ] Cross-module version displays resolve authoritative values automatically.
- [ ] Roadmap/release record updated.
- [ ] Post-commit authorities were re-read and matched the assigned event versions.
- [ ] No Vercel deployment was created when deployment was not required/approved.
- [ ] Live request serves `runtime`, not bundled fallback, when runtime behavior changed.
- [ ] Browser behavior/page/version reflects the change when applicable.
- [ ] No legacy injector/loader is overriding it.

## Architecture

```text
                 DURABLE
              GitHub runtime
                    │
          VERSION.txt (router)
                    │
           versions/*.txt owners
                    │
                    ▼
          stable runtime loader
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
         HTML      JS/CSS    LALM/R39
          │         │         │
          └─────────┼─────────┘
                    ▼
               live request
                    │
                    ▼
              current §wyrlz

Each independently evolving structure owns its version file.
Cross-module displays query the owning authority.

main    = stable infrastructure / engineering contract boundary
runtime = live app source / hot-update authority
DEPLOY  = separate production action when current configuration requires it
```

## Bottom line for future §wyrlz

> **Any server-governed update = capture current authority → smallest change → revalidate authority → reconcile concurrency if needed → new Server version + affected module version(s) + module-owned version authority update + roadmap entry + commit + post-commit authority verification + live verification when applicable.**
>
> **If the user asks to update Chat, a Chat page, page-owned JS/CSS, stream UI, runtime LALM, or another runtime-owned module: work on `runtime`, make the smallest possible edit, version everything affected, update the owning `versions/*.txt` file(s), update the roadmap, commit, reload, verify, and do not redeploy.**
>
> **If the loader/API/middleware/auth/deployment infrastructure must change: determine from current configuration what action actually causes deployment. Obtain explicit user approval before that deployment-producing action. A non-deploying documentation or `main` commit does not require fake deployment approval simply because it is on `main`.**
