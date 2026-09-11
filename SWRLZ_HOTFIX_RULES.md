# §wyrlz Hotfix Rules — READ THIS FIRST

**Purpose:** prevent unnecessary Vercel redeploys and accidental overwrites of the live Chat application while preserving complete Server/module version lineage.

## One rule

**`runtime` is the live application source of truth. `main` is stable loader/infrastructure.**

For normal Chat/page/LALM changes: **edit `runtime` → increment the overall Server version → increment every affected module version → update the roadmap/release record → commit → reload/request → verify. DO NOT DEPLOY. DO NOT RESTART.**

## HARD STOP — Deployment Approval Gate

**No repository action that can cause deployment/redeployment may be performed without explicit user approval first.** This rule applies even when the requested work is documentation-only.

Before any mutation to a branch, file, configuration, merge target, workflow, or other repository state that could trigger deployment, the agent must STOP and tell the user:

- what exact branch/path/configuration/action causes deployment;
- why it causes deployment;
- whether deployment is architecturally required or merely automatically triggered by the deployment configuration;
- what deployed surface would be affected;
- whether the work can be performed through `runtime` without deployment;
- the exact repository action awaiting approval.

**The agent must obtain explicit user approval before performing that action.** If deployment behavior is uncertain, treat it as deployment-capable and stop. Never infer approval from a general request to fix, update, document, commit, merge, or architect.

A commit is not deployment authorization. A merge into `main` is not deployment authorization. Documentation changes are not exempt. The user may choose to perform the actual deployment manually.

## Mandatory Server + module versioning

Every server-side development event that changes runtime state is a new overall **Server version**, including a tiny change, a test-only version event, an unsuccessful attempt, or a failed fix.

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

For **every** runtime/server update:

1. Determine the current Server version.
2. Determine the current version of every affected module.
3. Fetch the current target file(s) from `runtime` before editing.
4. Determine whether any proposed repository action can cause deployment.
5. If deployment-capable, **STOP → explain the trigger/reason → obtain explicit user approval before mutation.**
6. Make the smallest targeted change possible.
7. Increment the overall Server version.
8. Increment every module version that actually changed.
9. Update every canonical in-code/version-source location for those versions.
10. Update every module-owned UI/status surface that should show its own version.
11. Cross-module version displays must retrieve the owning module's authoritative version automatically; do not duplicate stale hardcoded versions.
12. Update the roadmap/release record with the Server version, affected module versions, changes, failures, verification state, and deployment state.
13. Commit code + version records + roadmap to `runtime`, or use an explicitly approved deployment path when `main` is required.
14. Reload/request every affected route.
15. Verify live behavior, version responses, and visible version displays.
16. Verify no legacy injector/loader overrides the runtime asset.
17. Only then declare the update complete.

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
2. Make the **smallest targeted edit** possible.
3. Apply the required Server/module version bumps.
4. Update the affected module-owned version file(s) and `VERSION.txt` only when routing/registration changes.
5. Update the roadmap/release record.
6. Commit it to `runtime`.
7. Reload/request the affected route.
8. Verify the live response/headers/version/behavior comes from `runtime`.
9. If wrong, make another versioned runtime fix; do not silently overwrite the previous event.

### NEVER do this for a hotfix

- Do not replace a whole page when one line/script needs changing.
- Do not inject a second hardcoded Chat version from `main`.
- Do not use `/tmp` as source of truth.
- Do not restart the server to expose ordinary runtime changes.
- Do not trigger Vercel deployment for ordinary runtime edits.
- Do not change `dev` when the task is a Chat/runtime hotfix; use `runtime`.
- Do not manually copy another module's version into a second module when an authoritative version file/status source can provide it.
- Do not treat `VERSION.txt` as a duplicated ledger of module numbers; it routes to module-owned authorities.

## REDEPLOY required

Only change `main` and deploy when the **stable infrastructure boundary** must change, such as:

- Python API routes or middleware
- authentication/session/security boundaries
- runtime loader/source-resolution logic
- runtime hydration/sync mechanism
- deployment/build configuration (`vercel.json`, build/runtime configuration)
- a new bundled dependency or stable server capability
- a capability the existing runtime loader cannot serve

A `main` change requires a Vercel deployment because `main` is the stable deployed boundary. **However, the agent must pass the Deployment Approval Gate before making the `main` mutation that will cause the deployment.**

## Restart/cold-start rule

GitHub `runtime` is durable. `/tmp`, memory caches, loaded Python module objects, and Vercel instance state are disposable. A restart must be able to recreate active runtime state from `runtime` automatically.

## Ownership

- **Chat UI/code:** `runtime`
- **Chat stream/UI enhancements:** `runtime`
- **Chat version display:** `runtime`
- **LALM/R39 runtime code:** `runtime`
- **Module-owned version authorities:** `runtime` for runtime-owned modules
- **Stable API/loader/security infrastructure:** `main`

Changing LALM internals does **not** require changing the Chat version unless user-facing Chat behavior/protocol changed.

## Versioning rule

If asked to bump a module version, update that module's authoritative version file, bump the overall Server version when the event is server-governed, and update the roadmap. **Do not rewrite an unrelated page or module merely to carry the version number.** UI/status surfaces should derive the value from the authority.

## Verification checklist

Before saying a hotfix is done:

- [ ] Current target file was fetched first.
- [ ] Current Server/module versions established from authoritative sources.
- [ ] Deployment risk was evaluated before repository mutation.
- [ ] Explicit approval was obtained before any deployment-capable action.
- [ ] Only intended runtime file(s) changed.
- [ ] Server version bumped when required by the event contract.
- [ ] Every affected module version bumped.
- [ ] Affected module-owned version files updated.
- [ ] `VERSION.txt` routing updated only if module registration/ownership changed.
- [ ] Cross-module version displays resolve authoritative values automatically.
- [ ] Roadmap/release record updated.
- [ ] `runtime` contains the change.
- [ ] No Vercel deployment was created for the runtime-only change.
- [ ] Live request serves `runtime`, not bundled fallback.
- [ ] Browser behavior/page/version reflects the change.
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

main = stable infrastructure → deploy when changed + explicit approval
runtime = live app source   → hotfix without deploy
```

## Bottom line for future §wyrlz

> **Any server runtime change = new Server version + affected module version(s) + module-owned version authority update + roadmap entry + commit + reload + verification.**
>
> **If the user asks to update Chat, a Chat page, page-owned JS/CSS, stream UI, runtime LALM, or another runtime-owned module: work on `runtime`, make the smallest possible edit, version everything affected, update the owning `versions/*.txt` file(s), update the roadmap, commit, reload, verify, and do not redeploy.**
>
> **If the loader/API/middleware/auth/deployment infrastructure must change: explain the deployment trigger and requirement, obtain explicit user approval before the repository mutation, then work on `main` and redeploy/verify.**
