# §wyrlz Hot Runtime Update Guide

**READ THIS BEFORE MODIFYING CHAT, PAGES, THE LALM, OR SERVER RUNTIME.**

## One rule

**`runtime` is the live application source of truth. `main` is stable loader/infrastructure.**

Normal application changes are:

**edit `runtime` → bump the overall Server version → bump every affected module version → update the roadmap/release record → commit → reload/request → verify → NO VERCEL DEPLOY → NO SERVER RESTART.**

## Mandatory version + roadmap contract

Every server-side development event that changes the runtime is a new **overall Server version**, even when the change is tiny or the attempt fails.

The Server version is the chronological umbrella release/event number. Each affected module gets its own module-version bump underneath it.

Example:

```text
Server v5.5.6

Chat v5.5.5
- Sidebar fix.

LALM v5.5.4
- No change.
```

If only LALM is changed on the next event:

```text
Server v5.5.7

LALM v5.5.5
- Inference fix.
```

A failed attempt is still recorded and still increments the Server version. The next fix is another Server version and another affected-module version bump.

For every versioned server update:

1. Determine the current Server version.
2. Determine the current version of every affected module.
3. Fetch each target file from the current source-of-truth branch before editing.
4. Make the smallest targeted change.
5. Increment the overall Server version.
6. Increment every module version that actually changed.
7. Update every canonical in-code/version-source location for those module versions.
8. Update any UI or status surface that owns/displays those versions.
9. Do **not** duplicate module versions as unrelated hardcoded values in other modules.
10. When one module displays another module's version, fetch/read the owning module's authoritative status/version source automatically.
11. Update the server roadmap/release record with the new Server version and all affected module versions, including failures and verification state.
12. Commit the code and roadmap/version records to `runtime`.
13. Reload/request the affected live route(s).
14. Verify live behavior, returned version values, and displayed version values.
15. Verify no legacy injector/loader is overriding the runtime asset.
16. Only then declare the update complete.

## Version ownership

- **Server:** canonical runtime Server version is owned by `api/index.py` (`VERSION`) and exposed through the control-plane status endpoints.
- **Chat:** canonical Chat version is owned by `web/chat_version.js` (`CHAT_VERSION`).
- **LALM UI:** canonical LALM UI version is owned by the LALM control-plane status source and exposed as `/api/lalm/status` `uiVersion`.
- **LALM engine:** engine/hot-runtime revisions are owned by the active LALM runtime source (`runtime_hot/r39_engine.py`). These are separate from the LALM UI version and must also be bumped when that runtime itself changes.

## Automatic cross-module version display

A module must not require manual edits to another module merely because it displays that module's version.

For example, Chat must retrieve Server/LALM versions from their authoritative status endpoints rather than carrying stale copies. Current Chat version rendering retrieves:

- `/api/server/status` → `version`
- `/api/lalm/status` → `uiVersion`

This makes a LALM version bump automatically visible in Chat without changing Chat's own version merely to mirror LALM.

## NO REDEPLOY: edit `runtime`

Use `runtime` for:

- `web/chat.html` — Chat UI/page
- `web/chat_*.js` — Chat behavior, stream UI, enhancements, version display
- `web/chat_*.css` — Chat styling
- `web/server.html`, `web/lalm.html`, and other runtime-owned pages
- `runtime_pages/manifest.json` — add/remove/change routes
- runtime assets under `web/` or `runtime_pages/`
- runtime-loadable LALM/inference code, including R39 runtime source

### Exact hotfix procedure

1. **Fetch the current file from `runtime` before editing.**
2. Make the **smallest targeted change** possible.
3. Apply the required Server/module version bumps.
4. Update the roadmap/release record.
5. Commit the change to `runtime`.
6. Reload/request the affected live route.
7. Verify the live response/headers/version/behavior is from `runtime`.
8. If incorrect, make another versioned runtime fix; do not silently overwrite the previous event.

### Especially for Chat

If asked for a version bump, text change, footer change, CSS tweak, stream UI change, or other small Chat modification:

- change only the owning runtime file;
- bump Chat and the overall Server version;
- update the roadmap;
- do **not** rewrite the entire `web/chat.html` unless the HTML itself is the requested change;
- do **not** add a competing hardcoded version/injector in `main`;
- preserve the existing complete Chat page.

## REDEPLOY: edit `main`

Only change `main` when the stable deployed boundary itself must change, including:

- Python API routes or middleware
- authentication/session/security boundaries
- runtime loader/source-resolution logic
- runtime hydration/sync mechanism
- deployment/build configuration (`vercel.json`, build/runtime configuration)
- new bundled dependencies or stable server capabilities
- a capability the current runtime loader cannot serve

A `main` change requires a Vercel deployment.

## Restart/cold-start rule

GitHub `runtime` is durable. `/tmp`, memory caches, loaded Python module objects, and Vercel instance state are disposable. A restart/cold start must recreate active runtime state from the durable `runtime` source automatically.

Never treat `/tmp` as the permanent source of truth.

## Page lifecycle

### Add a page

1. Create the page on `runtime`.
2. Add its route to `runtime_pages/manifest.json`.
3. Bump the Server version.
4. Bump the page/module version if that page owns a version.
5. Update the roadmap.
6. Commit.
7. Request the new route and verify.

### Remove a page

1. Remove its route from `runtime_pages/manifest.json`.
2. Delete the obsolete page file if no longer needed.
3. Bump the Server version.
4. Update the roadmap and lineage record.
5. Commit.
6. Request the route and verify it is no longer served.

### Update page JS/CSS

Edit the runtime-owned asset directly, bump the affected module and Server versions, update the roadmap, commit, reload, verify. No deploy/restart.

## LALM/R39

Runtime-loadable inference/LALM modules belong to the runtime source tree. A LALM update must bump:

- the overall Server version;
- the affected LALM UI/module version where applicable;
- the LALM engine/hot revision when inference runtime code changes;
- every canonical version source where the changed version is owned.

Other modules that display LALM information must obtain the current LALM version from the authoritative status source rather than copying a stale literal.

Changing LALM internals does **not** require changing the Chat version unless user-facing Chat behavior/protocol itself changes.

## Verification checklist

Before declaring a hotfix complete:

- [ ] Current target file fetched first.
- [ ] Current Server/module versions established.
- [ ] Smallest possible file change made.
- [ ] Server version incremented.
- [ ] Every affected module version incremented.
- [ ] Canonical in-code version sources updated.
- [ ] Cross-module version displays resolve authoritative values automatically.
- [ ] Roadmap/release record updated.
- [ ] Change committed to `runtime`.
- [ ] No Vercel deployment created for the runtime-only change.
- [ ] Live request serves current `runtime` source rather than bundled fallback.
- [ ] Browser behavior/version reflects the change.
- [ ] No legacy injector/loader overrides the runtime asset.

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

Version ownership flows outward from each module's source/status.
Cross-module displays query the owner; they do not copy its version.

main = stable infrastructure → deploy when changed
runtime = live app source   → hotfix without deploy
```

**Bottom line:**

> **Any server runtime change = new Server version + affected module version(s) + roadmap entry + commit + reload + verification.**
>
> **Chat/page/JS/CSS/stream/LALM change → `runtime` → smallest edit → version/roadmap update → commit → reload → verify → no deploy.**
>
> **Loader/API/middleware/auth/deployment infrastructure change → `main` → deploy.**
