# §wyrlz Server Roadmap

## Current release

**Server v2.3.80**

**Status: Google OAuth browser-authority regression repaired in runtime source.**

Google sign-in now preserves an already configured browser OAuth Web Client ID and uses the server-provided client ID only to seed browsers that have no local OAuth client configuration. This repairs the regression where the server bridge overwrote a previously working browser client ID while work was being done to make Google sign-in available across browsers.

### Module state

- **Server runtime v2.3.80** — Google OAuth browser authority repair.
- **Chat v1.4.72** — preserves browser-proven Google client configuration.
- **Google Account v1.0.7** — browser client ID precedence + server fallback seeding.
- **Frozen Web Collector v1.0.0** — unchanged.
- **Deployment Control v1.0.2** — unchanged.
- **Web Frontend v1.0.0**, **LALM engine v2.1.30**, **LALM UI v1.0.0** — unchanged.

## Server v2.3.80 — 2026-09-12

### Google OAuth browser authority repair

- Google sign-in had previously worked in Chrome.
- During work to make the same flow available in Edge, `web/chat_google_server_config.js` began treating the server-reported Google client ID as an unconditional replacement authority.
- Chat and the isolated Google login page intentionally share the `swrlzGoogleLoginTestClientId` browser key, so the bridge could replace the already working browser OAuth client ID.
- Existing browser OAuth configuration now has precedence.
- The server-provided Google client ID is used only when the browser has no configured client ID.
- Server-side Google credential verification and signed session issuance remain unchanged.
- Diagnostic events now distinguish `browser` authority from `server-seed` authority.
- User explicitly approved this deployment-capable runtime repair.
- Release record: `docs/releases/server-2.3.80-google-oauth-browser-authority-repair.md`.

## Prior releases

The complete prior release history remains preserved in `docs/releases/` and Git history. The preceding current release was Server v2.3.79 / Chat v1.4.71 / Google Account v1.0.6.
