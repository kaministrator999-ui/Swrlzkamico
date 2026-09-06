# SWRLZ Runtime Web Workspace v1

Status: development branch contract for the next SERVER release.

## Purpose

Allow Admin-authenticated uploads under the running Vercel function's writable `/tmp` storage to become directly linkable web pages/assets without another server deployment.

## Public runtime web root

Filesystem root:

`/tmp/swrlz-admin/web`

Public URL root:

`/live/`

Routing is implemented inside the already-mounted chat sub-application so it executes in the same unified `api/index.py` runtime that owns the Admin workbench. Vercel rewrites `/live` and `/live/:path*` to `/api/chat/live...`.

Examples:

- `/tmp/swrlz-admin/web/chatv2/index.html` -> `/live/chatv2/`
- `/tmp/swrlz-admin/web/tools/tokenizer.html` -> `/live/tools/tokenizer.html`
- `/tmp/swrlz-admin/web/status/app.js` -> `/live/status/app.js`

Directories publish `index.html`. Requests are path-confined to the runtime web root; traversal and symlink escapes are rejected. Files are served with MIME detection and `Cache-Control: no-store` so edits can be refreshed immediately.

## Admin workflow

1. Open the Admin workbench and authenticate.
2. Navigate the file browser to `/tmp/swrlz-admin/web`.
3. Create the desired page directory.
4. Upload or edit `index.html` plus any CSS/JS/image assets.
5. Open the corresponding `/live/.../` URL.
6. Iterate by replacing/editing files in the same runtime instance. No Git commit or Vercel redeploy is required for those runtime edits.

`/tmp` is ephemeral and instance-local. Runtime pages are a hot workspace, not the durable source of truth. Finished assets should later be committed to GitHub.

## Chat page relocation

The bundled chat UI currently determines its API base from its path. A runtime-published copy should use an absolute chat API base:

`const API = "/api/chat";`

That lets a copied chat page run correctly from `/live/chatv2/`, `/live/chatv3/`, or another runtime web path.

## Runtime chat token override

The chat bridge now checks this runtime file first:

`/tmp/swrlz-admin/runtime/web-chat-token.txt`

If it contains a valid 16-512 character token, it overrides `SWRLZ_WEB_CHAT_TOKEN` for that runtime instance. If the file is absent or invalid, the environment variable remains the fallback.

This lets Admin set or rotate the temporary web chat token without redeploying. The token file is not under the public `/tmp/swrlz-admin/web` tree and must never be copied there.

## Deployment discipline

Active development uses branch `dev`. `vercel.json` contains:

```json
"git": {
  "deploymentEnabled": {
    "dev": false
  }
}
```

Therefore commits to `dev` do not automatically create Vercel deployments. Production remains on `main`; finished, verified work is promoted to `main` as a deliberate release step.

## Security boundary

- Only `/tmp/swrlz-admin/web` is publicly readable through `/live/*`.
- Admin/runtime/token files outside that subtree are not exposed by the live route.
- Path traversal and resolved-path escape are rejected.
- Runtime token override is read dynamically on each chat-auth check.
- `/tmp` lifetime remains controlled by Vercel and may disappear when the instance is recycled.
