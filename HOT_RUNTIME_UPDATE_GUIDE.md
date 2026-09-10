# §wyrlz Hot Runtime Update Guide

**READ THIS BEFORE MODIFYING CHAT, PAGES, OR THE LALM.**

## One rule

**`runtime` is the live application source of truth. `main` is stable loader/infrastructure.**

Normal application changes are:

**edit `runtime` → commit → reload/request → verify → NO VERCEL DEPLOY → NO SERVER RESTART.**

Canonical rules are also kept on `main` in `SWRLZ_HOTFIX_RULES.md` so a new §wyrlz chat has a single obvious place to start.

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
3. Commit the change to `runtime`.
4. Reload/request the affected live route.
5. Verify the live response/headers/version/behavior is from `runtime`.
6. If incorrect, revert the runtime commit or make another small runtime-only fix.

### Especially for Chat

If asked for a version bump, text change, footer change, CSS tweak, stream UI change, or other small Chat modification:

- change only the owning runtime file;
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
3. Commit.
4. Request the new route.

### Remove a page

1. Remove its route from `runtime_pages/manifest.json`.
2. Delete the obsolete page file if no longer needed.
3. Commit.
4. Request the route and verify it is no longer served.

### Update page JS/CSS

Edit the runtime-owned asset directly, commit, reload, verify. No deploy/restart.

## LALM/R39

Runtime-loadable inference/LALM modules belong to the runtime source tree. The hot-runtime mechanism should reload changed source by revision/signature. Changing LALM internals does not require changing the Chat version unless user-facing Chat behavior/protocol changes.

## Verification checklist

Before declaring a hotfix complete:

- [ ] Current target file fetched first.
- [ ] Smallest possible file change made.
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

main = stable infrastructure → deploy when changed
runtime = live app source   → hotfix without deploy
```

**Bottom line:**

> **Chat/page/JS/CSS/stream/LALM change → `runtime` → smallest edit → commit → reload → verify → no deploy.**
>
> **Loader/API/middleware/auth/deployment infrastructure change → `main` → deploy.**
