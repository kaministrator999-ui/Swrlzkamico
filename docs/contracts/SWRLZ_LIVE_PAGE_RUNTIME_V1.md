# SWRLZ Live Page Runtime v1

Current server boundary: **2.1.15**

## Source of truth

Durable page source lives on the non-deploying `dev` branch. Updating `dev` does not trigger Vercel deployment.

Core mappings:

- `web/admin.html` -> `/api/admin`
- `web/chat.html` -> `/api/chat`
- `web/chat_enhancements.css` -> `/api/chat/assets/enhancements.css`
- `web/chat_enhancements.js` -> `/api/chat/assets/enhancements.js`
- `runtime_pages/index.html` -> `/live/`
- `runtime_pages/pages/<path>` -> `/live/pages/<path>`

Additional supported files under `runtime_pages/pages/` are published directly under `/live/pages/`.

## Live read boundary

Server 2.1.13 moved normal live reads away from instance-local `/tmp` and onto GitHub-backed resolution.

For each supported live page/asset request, the server resolves the current source from GitHub `dev`, using only a short bounded in-instance cache and a bundled fallback for core assets. The response includes source/branch/path receipts.

Therefore the normal page-update flow is:

`edit GitHub dev -> refresh live URL -> receive current dev source`

A Vercel server redeploy is not required for ordinary supported page/UI changes.

## Runtime mutation boundary

`/api/pages` remains the authenticated Page Manager. Runtime copies under `/tmp/swrlz-admin` still support:

- explicit `dev` -> runtime synchronization;
- runtime read/edit/save;
- optional runtime -> `dev` push-back;
- GitHub write-capability configuration/status;
- page/source/runtime/live-URL receipts.

These mutation tools are no longer required for normal live reads. `/tmp` remains ephemeral and instance-local and must never be treated as the durable page source of truth.

## GitHub write token

Push-back requires a fine-grained GitHub token with Contents write permission for `kaministrator999-ui/Swrlzkamico`. Precedence:

1. `/tmp/swrlz-admin/runtime/github-content-token.txt`
2. `SWRLZ_GITHUB_CONTENT_TOKEN`
3. `SWRLZ_GITHUB_TOKEN`

The Page Manager reports configured/not-configured state but never returns the raw secret.

## Deployment discipline

Stable backend changes still require deliberate `main` deployment. This includes Python/API routes, authentication/session semantics, middleware, inference plumbing, and deployment configuration.

Normal HTML/CSS/JS/page-source work belongs on `dev` and is consumed live by the deployed server without promotion or redeployment.

## Acceptance receipt

The live-source path was proven by changing Chat UI versions on `dev` while the deployed server version remained unchanged. Browser refreshes advanced the Chat UI without `/api/pages` sync and without a Vercel server redeploy.
