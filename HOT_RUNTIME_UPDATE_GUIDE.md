# §wyrlz Hot Runtime Update Guide

## Purpose

`runtime` is the live application source of truth. The stable Vercel/server bootstrap serves runtime page files and runtime-owned assets without requiring a Vercel deployment or server restart.

## Update a page

1. Edit the page under `web/` or `runtime_pages/` on the `runtime` branch.
2. Commit/save the change.
3. Reload the page. The next request retrieves the current runtime source.

Examples:

- `web/chat.html` → Chat page
- `web/server.html` → Server page
- `web/lalm.html` → LALM page
- `runtime_pages/pages/*.html` → additional runtime pages

## Add a page

1. Create the HTML file on `runtime`.
2. Add its public route to `runtime_pages/manifest.json`.
3. Save/commit both changes.
4. Open the new route.

## Remove a page

Remove its route from `runtime_pages/manifest.json` and delete the page file if it is no longer needed. The stable bootstrap must not contain a second copy that can override the runtime route.

## Update page-owned JavaScript/CSS

Keep page behavior and styling on `runtime` whenever possible. Changes to HTML, JavaScript, CSS, stream UI, enhancement code, and page assets are runtime changes and should be served from the runtime branch.

## Update LALM / inference used by Chat

Runtime-loadable LALM/inference modules belong under the runtime hot-runtime source tree. The server should reload the changed module by runtime revision/signature rather than requiring process restart. Durable source files live in GitHub `runtime`; `/tmp` is only a disposable execution/cache layer.

## Durability rule

Never treat `/tmp`, a Vercel instance filesystem, browser cache, or a running Python module object as the source of truth. Those are caches/execution state only. A server restart may destroy them; the runtime branch must recreate the active state automatically.

## No-deploy rule

Do **not** create a Vercel deployment for ordinary runtime application changes. A deployment is only required when changing the stable bootstrap/infrastructure that is responsible for loading the runtime source.

## Verification

A healthy hot-runtime response should identify:

- source branch: `runtime`
- source: runtime/GitHub rather than bundled fallback
- cache policy: no-store or a very short bounded fetch cache
- current runtime revision

The visible page version must be owned by the runtime application itself, never hardcoded by the stable bootstrap.

## Architecture

```text
GitHub runtime branch
        │
        ▼
stable runtime loader
        │
        ├── HTML
        ├── CSS
        ├── browser JS
        ├── page assets
        └── runtime-loadable LALM/inference
        │
        ▼
Vercel request
        │
        ▼
current runtime source
```

This is the intended §wyrlz rule: **save to runtime → request/reload → new code is served; no deploy and no restart.**
