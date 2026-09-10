# §wyrlz Hotfix Rules — READ THIS FIRST

**Purpose:** prevent unnecessary Vercel redeploys and accidental overwrites of the live Chat application while preserving complete Server/module version lineage.

## One rule

**`runtime` is the live application source of truth. `main` is stable loader/infrastructure.**

For normal Chat/page/LALM changes: **edit `runtime` → increment the overall Server version → increment every affected module version → update the roadmap/release record → commit → reload/request → verify. DO NOT DEPLOY. DO NOT RESTART.**

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
4. Make the smallest targeted change possible.
5. Increment the overall Server version.
6. Increment every module version that actually changed.
7. Update every canonical in-code/version-source location for those versions.
8. Update every module-owned UI/status surface that should show its own version.
9. Cross-module version displays must retrieve the owning module's authoritative version automatically; do not duplicate stale hardcoded versions.
10. Update the roadmap/release record with the Server version, affected module versions, changes, failures, and verification state.
11. Commit code + version records + roadmap to `runtime`.
12. Reload/request every affected route.
13. Verify live behavior, version responses, and visible version displays.
14. Verify no legacy injector/loader overrides the runtime asset.
15. Only then declare the update complete.

## Version ownership

- **Server:** `api/index.py` `VERSION`; exposed through `/api/server/status` as `version`.
- **Chat:** `web/chat_version.js` `CHAT_VERSION`.
- **LALM UI:** control-plane `LALM_UI_VERSION`; exposed through `/api/lalm/status` as `uiVersion`.
- **LALM engine:** active runtime revision fields in `runtime_hot/r39_engine.py`, including `HOT_SERVER_VERSION` and `HOT_REVISION`.

If another module needs to display one of these values, it must read the authoritative status/version source. It must not receive a second manually maintained copy.

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

### Hotfix procedure

1. **Fetch the current target file from `runtime` first.**
2. Make the **smallest targeted edit** possible.
3. Apply the required Server/module version bumps.
4. Update the roadmap/release record.
5. Commit it to `runtime`.
6. Reload/request the affected route.
7. Verify the live response/headers/version/behavior comes from `runtime`.
8. If wrong, make another versioned runtime fix; do not silently overwrite the previous event.

### NEVER do this for a hotfix

- Do not replace a whole page when one line/script needs changing.
- Do not inject a second hardcoded Chat version from `main`.
- Do not use `/tmp` as source of truth.
- Do not restart the server to expose ordinary runtime changes.
- Do not trigger Vercel deployment for ordinary runtime edits.
- Do not change `dev` when the task is a Chat/runtime hotfix; use `runtime`.
- Do not manually copy another module's version into a second module when an authoritative status endpoint can provide it.

## REDEPLOY required

Only change `main` and deploy when the **stable infrastructure boundary** must change, such as:

- Python API routes or middleware
- authentication/session/security boundaries
- runtime loader/source-resolution logic
- runtime hydration/sync mechanism
- deployment/build configuration (`vercel.json`, build/runtime configuration)
- a new bundled dependency or stable server capability
- a capability the existing runtime loader cannot serve

A `main` change requires a Vercel deployment because `main` is the stable deployed boundary.

## Restart/cold-start rule

GitHub `runtime` is durable. `/tmp`, memory caches, loaded Python module objects, and Vercel instance state are disposable. A restart must be able to recreate active runtime state from `runtime` automatically.

## Ownership

- **Chat UI/code:** `runtime`
- **Chat stream/UI enhancements:** `runtime`
- **Chat version display:** `runtime`
- **LALM/R39 runtime code:** `runtime`
- **Stable API/loader/security infrastructure:** `main`

Changing LALM internals does **not** require changing the Chat version unless user-facing Chat behavior/protocol changed.

## Versioning rule

If asked to bump the Chat version, change the runtime-owned version source only, bump the overall Server version, and update the roadmap. **Do not rewrite `web/chat.html` unless the HTML itself is the requested change. Preserve the complete existing page.**

## Verification checklist

Before saying a hotfix is done:

- [ ] Current target file was fetched first.
- [ ] Current Server/module versions established.
- [ ] Only intended runtime file(s) changed.
- [ ] Server version bumped.
- [ ] Every affected module version bumped.
- [ ] Canonical version sources updated.
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

Version ownership stays with each module.
Cross-module displays query the owning module's authoritative source.

main = stable infrastructure → deploy when changed
runtime = live app source   → hotfix without deploy
```

## Bottom line for future §wyrlz

> **Any server runtime change = new Server version + affected module version(s) + roadmap entry + commit + reload + verification.**
>
> **If the user asks to update Chat, a Chat page, page-owned JS/CSS, stream UI, or runtime LALM: work on `runtime`, make the smallest possible edit, version everything affected, update the roadmap, commit, reload, verify, and do not redeploy.**
>
> **If the loader/API/middleware/auth/deployment infrastructure must change: work on `main` and redeploy.**
