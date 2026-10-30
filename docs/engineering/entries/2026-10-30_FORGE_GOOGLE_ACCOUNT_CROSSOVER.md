# §E ↔ embedded Chat Google crossover — focused repair candidate (2026-10-30)

**Stage:** SOURCE_CANDIDATE / NOT_DEPLOYED / OWNER_DEVICE_PENDING.

**User goal:** A Google login connected through the §E host must produce a verified authenticated session and matching account inside its embedded Chat interface without a second Chat login. The popup's explicit Connect action still establishes the scoped cross-origin grant.

**Root source:** The Chat-origin embed broker cleared the entire Google account for *every* HTTP 401 from a broad API allowlist, including unrelated GitHub/tool permissions. It also announced a connected account immediately after pairing without first checking the normal Chat /api/account/me result. A pre-login asynchronous account refresh could overwrite the later connected Chat display.

**Changed Chat source only:** `chat/§wyrlz/assets/forge-embed-v1.js` recognizes actual invalid/revoked embed session errors, captures token/epoch per request to ignore stale responses, checks `/api/account/me` for the exact paired principal before announcing connected state, and clears expired sessions. `chat/§wyrlz/index.html` serializes account refresh results so old anonymous refreshes cannot overwrite newer verified sign-in. Scoped bearer token stays Chat-origin-only in RAM. The §E host and project data remain unchanged.

**Controlled regression:** `node tests/forge_google_account_crossover_v1.mjs` verifies pair→real account status, Chat login-change notification, unrelated 401 preservation, legitimate session revocation, cookie-free bearer and no cross-origin token leakage. Actual Google OAuth, hosted deployment and physical Android/Quest browser behavior require separate acceptance.

**Publication boundary:** Do not deploy until this exact Chat candidate passes release preflight and version/roadmap governance. The separate §E DEPLOY_REQUEST.json is not part of this Chat-only correction.
