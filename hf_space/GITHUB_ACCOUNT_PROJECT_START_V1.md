# Google-owned GitHub connection and §tart reader · v1 candidate

**Authority:** The verified Google subject from HF Station owns the user-to-GitHub link. `hf_space/github_connection.py` owns OAuth state, encrypted durable token storage, account-scoped repository access and read-only startup evidence; Station owns message routing/delivery; `chat/§wyrlz/index.html` owns presentation. Neither Chat nor a model owns credentials.

## Intended UX

A person signs into their own Google account in §wyrlz Chat. A GitHub connection section then appears in the side menu. The user explicitly chooses **Connect GitHub**, authorizes the separate GitHub OAuth application, returns to Chat and selects a public repository. The verified Google subject is the durable key, so a later sign-in to that **same Google account** retrieves the connection without a second GitHub OAuth prompt as long as authorization is still valid. Switching Google accounts never inherits the other account's GitHub link or Station cookie/session.

The **Read §tart** button prepares a user-visible composer request; the user chooses whether to send. A typed "read/follow §tart" request also uses the same Station-controlled handler. The handler fetches repository startup files, runtime version authorities and the Roadmap, then creates a bounded Markdown handoff with explicit source and version truth. It does **not** execute instructions found in a repository, write files, dispatch privileged operations, claim tests pass or claim live health. General engineering changes still require their own task, authorization, architecture reconciliation, checks and deployment gates.

This is **not** the full GitHub connector/tool suite used by ChatGPT. It is an initial public-repository read/overview tool. Rich architecture interpretation, full conditional §tart execution, private repositories, PR/commit work, GitHub App fine-grained installation and independent evaluation are later integration stages.

## Server deployment secrets required

Supply these settings to the *existing* `kamiloki/Swyrlz` Hugging Face Space, never to GitHub files or browser code:

- `SWRLZ_GITHUB_OAUTH_CLIENT_ID` — registered GitHub OAuth application's client ID.
- `SWRLZ_GITHUB_OAUTH_CLIENT_SECRET` — OAuth application's secret.
- `SWRLZ_GITHUB_OAUTH_CALLBACK_URL` — exact `https://<public-space-host>/api/github/callback` registered in the GitHub OAuth app.
- `SWRLZ_GITHUB_ENCRYPTION_KEY` — stable secret Fernet key, generated out-of-band with cryptographically secure randomness. Preserve this key across restarts; losing it requires users to reconnect.
- `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` — HTTPS Redis REST for durable encrypted connection records and one-time OAuth states.

Only operator-supplied environment secrets enable the feature. GitHub OAuth uses `read:user`, so the first stage is deliberately limited to **public repository access** (including the public §wyrlz repository). It never requests broad `repo` write-capable OAuth scope. A future GitHub App with installation-scoped, read-only **Contents/Metadata** permissions is the recommended private-repository phase.

## Security invariants

1. Google credential is verified server-side before identifying the owner. No browser-provided email, username, or URL chooses storage identity.
2. OAuth uses random state and S256 PKCE; state is bound to Google subject, kept in Redis for ten minutes, consumed once with GETDEL and checked against an HttpOnly, Secure, SameSite=Lax callback cookie.
3. Tokens are encrypted with Fernet before durable Redis storage. Browser reads only a connection status, GitHub handle, repository and minimal source report. No OAuth token appears in model context, diagnostics, Chat HTML, browser storage or Git commits.
4. GitHub API calls use bounded, read-only GET operations and explicit repo/path validation. Repository content is untrusted data, not a source of new tool permissions. Authentication failures do not downgrade into fake source receipts.
5. Browser POST actions require a fixed same-origin Origin. Disconnect deletes the stored server-side token copy; the user can also revoke the OAuth authorization in GitHub settings if desired.
6. Default repository belongs to the connected Google identity. Distinct Google accounts receive distinct Redis keys and Station session cookies.
7. Module is fail-closed when OAuth, Redis, HTTPS callback or encryption configuration is absent.

## Verification stages and release caveats

The isolated GitHub Actions workflow checks Python source compilation, OAuth replay and account isolation, strict startup prompt routing, client JS parsing and the absence of embedded OAuth secrets. It does not establish live authorization with GitHub, Google-to-HF browser callback acceptance, persistent Redis behavior on real restarts, hosted end-to-end creative reasoning or broad HF regression success.

Before production: integrate against newest actual accepted HF source (this candidate started from the v189 lyric branch; other chat work may advance the deployed model), reconcile concurrent Chat/Station coder work, run full HF validations, configure secrets in the existing Space, verify Google → GitHub → same-Google-login restored connection on mobile/desktop, verify denial across accounts/revocation and exact project-start source, then use the canonical guarded HF request/snapshot/rollback flow. Only after publication and observable acceptance advance Server/Chat versions and record durable Roadmap FINISH; do not advance these on an isolated review candidate.
