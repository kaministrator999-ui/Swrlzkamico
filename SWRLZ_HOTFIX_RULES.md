# §wyrlz Hotfix Rules — READ THIS FIRST

**Purpose:** prevent unnecessary Vercel redeploys and accidental overwrites of the live Chat application.

## One rule

**`runtime` is the live application source of truth. `main` is stable loader/infrastructure.**

For normal Chat/page/LALM changes: **edit `runtime` → commit → reload/request → verify. DO NOT DEPLOY. DO NOT RESTART.**

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
3. Commit it to `runtime`.
4. Reload/request the affected route.
5. Verify the live response/headers/version/behavior comes from `runtime`.
6. If wrong, revert the runtime commit or make another small runtime-only fix.

### NEVER do this for a hotfix

- Do not replace a whole page when one line/script needs changing.
- Do not inject a second hardcoded Chat version from `main`.
- Do not use `/tmp` as source of truth.
- Do not restart the server to expose ordinary runtime changes.
- Do not trigger Vercel deployment for ordinary runtime edits.
- Do not change `dev` when the task is a Chat/runtime hotfix; use `runtime`.

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

If asked to bump the Chat version, change the runtime-owned version source only. **Do not rewrite `web/chat.html` unless the HTML itself is the requested change. Preserve the complete existing page.**

## Verification checklist

Before saying a hotfix is done:

- [ ] Current target file was fetched first.
- [ ] Only intended runtime file(s) changed.
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

main = stable infrastructure → deploy when changed
runtime = live app source   → hotfix without deploy
```

## Bottom line for future §wyrlz

> **If the user asks to update Chat, a Chat page, page-owned JS/CSS, stream UI, or runtime LALM: work on `runtime`, make the smallest possible edit, commit, reload, verify, and do not redeploy.**

> **If the loader/API/middleware/auth/deployment infrastructure must change: work on `main` and redeploy.**
