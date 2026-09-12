# Server 2.3.80 — Google OAuth browser authority repair

Date: 2026-09-12
Branch: `runtime`

## Versions
- Server Runtime: 2.3.80
- Web Chat: 1.4.72
- Google Account Architecture: 1.0.7

## Triggering evidence
Google sign-in had previously worked in Chrome. During work to make the same flow available in Edge, the runtime server-config bridge began mirroring the server-reported Google client ID into the shared browser-local compatibility key. The bridge overwrote an already configured browser client ID whenever it differed from the server fallback. After that change, both Chrome and Edge reached Google but failed with `Error 401: invalid_client` and `no registered origin`.

## Root cause
`web/chat_google_server_config.js` treated the server client ID as an unconditional replacement authority rather than a bootstrap fallback. The isolated Google login page and Chat intentionally share `swrlzGoogleLoginTestClientId`, so the bridge could replace the client configuration that had already proven valid in the browser.

## Repair
- Existing browser OAuth client configuration now has precedence.
- The server-provided Google client ID is used only to seed a browser when `swrlzGoogleLoginTestClientId` is absent.
- Existing browser configuration is never overwritten by the server fallback.
- Google server-side credential verification remains unchanged and authoritative after Google issues a credential.
- Configuration events now identify `browser` versus `server-seed` authority for diagnostics.

## Acceptance
1. A browser that already has the known-good client ID retains it across Chat reloads.
2. Opening Chat no longer replaces that value with the server fallback.
3. Google Identity Services initializes using the preserved browser value.
4. A fresh browser with no local value can still receive the server client ID as an initial seed.
5. Google credentials continue through `/api/account/google` for server verification and session issuance.

## Deployment
The user explicitly approved the runtime repair and its deployment-capable GitHub action. No separate manual Vercel deployment is requested by this release.
