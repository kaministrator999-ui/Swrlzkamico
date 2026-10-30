# Google profile image and single-tab recovery preflight — Chat source candidate, 2026-10-30

**Owner screenshot:** §E v11.176 showed a circular generic “G” rather than the Google profile image, and its recovery code appeared only after the sign-in popup was opened. In an in-app browser without usable multiple tabs, the user could not return to copy the code.

**Chat-origin repair:** The canonical embedded broker now reports the authenticated user's existing Google profile image URL, after restricting to HTTPS under `googleusercontent.com`. Only the optional display URL and name are passed across the existing authenticated `account.status` channel; account session, ID token, Google ID and password remain Chat-origin-only. §E will display this image with a safe G fallback when no suitable image exists.

The pending recovery code remains **inside the original Chat iframe**. It is now presented as a selectable input and explicit Copy code control with guidance **before** opening Google. The §E host will provide a two-step ‘Prepare connection’ → ‘Continue to Google’ interaction: the first step sends the existing `account.signIn` RPC and displays the code; the second opens the original first-party Google login URL on a direct user gesture. The recovery code is not part of the URL or sent to the §E parent. Existing five-minute expiry, first-party Google identity check, PKCE challenge/verifier, host/channel binding, single-use exchange, and genuine logout continue unchanged.

**Limitation:** If a browser destroys the original §E tab entirely, the in-memory PKCE exchange can be interrupted even with a copied code. Actual single-tab Android WebView and Meta Quest behavior must be accepted on the device; Chrome remains the reliable same-browser fallback.

**Validation:** `node tests/test_forge_avatar_preflight_v1.mjs` checks trusted image URL filtering, original iframe copy UI, no proof sent to parent, and cleanup; existing backend and Chat candidate validation remain required. This is not a deployment receipt.
