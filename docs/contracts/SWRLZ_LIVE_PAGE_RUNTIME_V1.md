# SWRLZ Live Page Runtime v1

Server 2.1.8 separates durable page source from the stable Vercel deployment.

## Source of truth

Durable page source lives on the non-deploying `dev` branch. Updating `dev` does not trigger Vercel deployment.

Core mappings:

- `web/admin.html` -> runtime Admin page -> `/api/admin`
- `web/chat.html` -> runtime Chat page -> `/api/chat`
- `web/chat_enhancements.css` -> runtime Chat CSS
- `web/chat_enhancements.js` -> runtime Chat JS
- `runtime_pages/index.html` -> runtime launchpad -> `/live/`

Additional files under `runtime_pages/pages/` are discovered automatically and published under `/live/pages/`.

## Runtime boundary

Runtime copies are instance-local and live under `/tmp/swrlz-admin`. They can be edited while the server is running. `/api/pages` is the authenticated page manager.

The manager supports:

- sync `dev` -> runtime;
- read/edit/save the runtime copy;
- optional push runtime -> `dev`;
- runtime GitHub write-token configuration without exposing the token back to the browser;
- listing current page source/runtime/live URL receipts.

`/tmp` remains ephemeral. GitHub `dev` is the durable boundary.

## GitHub write token

Push-back requires a fine-grained GitHub token with Contents write permission for `kaministrator999-ui/Swrlzkamico`. Precedence:

1. `/tmp/swrlz-admin/runtime/github-content-token.txt`
2. `SWRLZ_GITHUB_CONTENT_TOKEN`
3. `SWRLZ_GITHUB_TOKEN`

The runtime token can be set from `/api/pages` using the Admin token. Secret values are never read back.

## Deployment discipline

Stable server/auth/API/security changes still require `main` deployment. Page/UI and approved hot inference changes belong on `dev` and are synced into the running instance. This keeps UI iteration from redeploying the server.
