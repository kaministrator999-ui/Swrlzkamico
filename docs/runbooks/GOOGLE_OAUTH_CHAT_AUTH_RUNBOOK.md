# §wyrlz Google OAuth + Chat Authentication Runbook

**Purpose:** Permanent architecture, diagnosis, recovery, and regression-prevention guide for Google sign-in in §wyrlz Web Chat.

**Read this before changing Google account/authentication behavior.** This document exists because a working Chrome login was broken while extending compatibility to Edge, and the final failure required tracing Google Cloud configuration, stable backend authority, browser-local state, runtime boot order, and live Vercel source delivery together.

---

## 1. Canonical production identity

### Canonical Google OAuth Web Client ID

```text
1083208613166-bj7isingvbv5dcns9ldtru8cjfj993mc.apps.googleusercontent.com
```

This is the Web OAuth client that was verified working on the canonical §wyrlz production origin.

### Retired / known-bad client ID

```text
1083208613166-59am0s2p1v4vpoc04klr3iinh0oph1en.apps.googleusercontent.com
```

This ID was introduced as a fallback during Google account work and caused Google Identity Services to return `401 invalid_client` / `no registered origin` in the browser. It must be treated as retired. Browser or server state containing this exact ID should be migrated to the canonical client ID.

### Canonical production origin

```text
https://swrlzkamico-o3nu.vercel.app
```

Google OAuth JavaScript-origin checks are origin-exact. If authentication is attempted from another Vercel alias, preview hostname, custom domain, or localhost origin, that origin must be independently authorized in the Google Web OAuth client before it can be expected to work.

### Primary Chat URL

```text
https://swrlzkamico-o3nu.vercel.app/api/chat
```

---

## 2. Source-of-truth map

| Concern | Authority / source |
|---|---|
| Stable Google client authority and server-side ID-token audience verification | `main/api/google_account.py` |
| Live browser/server Google configuration bridge | `runtime/web/chat_google_server_config.js` |
| Chat account UI and Google Identity Services initialization | `runtime/web/chat_enhancements.js` |
| Google recovery/control page | `runtime/runtime_pages/pages/google-login-test.html` |
| Live stable account diagnostic endpoint | `/api/account/status` |
| Stable token verification endpoint | `/api/account/google` |
| Logout/session endpoint | `/api/account/logout` |
| Google Account module version | `runtime/versions/google-account.txt` |
| Web Chat module version | `runtime/versions/web-chat.txt` |
| Overall Server runtime version | `runtime/versions/server-runtime.txt` |

Do not infer the active OAuth client from browser appearance alone. Query `/api/account/status` and inspect live runtime source when diagnosing.

---

## 3. Normal authentication flow

The intended flow is:

```text
Browser opens /api/chat
        ↓
runtime Chat assets load from GitHub runtime
        ↓
chat_google_server_config.js establishes/repairs browser OAuth client authority
        ↓
chat_enhancements.js initializes Google Identity Services with that client ID
        ↓
Google issues an ID credential for the same Web client audience
        ↓
Chat posts credential to /api/account/google
        ↓
main/api/google_account.py verifies the token against the canonical client audience
        ↓
server issues signed HttpOnly §wyrlz account session
        ↓
Chat stores only safe account display claims in session-scoped browser state
        ↓
account-specific browser Chat namespace becomes active
```

The browser-side Google button appearing is not proof that server verification will succeed. The complete proof is:

```text
GIS initializes successfully
+ Google credential is issued
+ /api/account/google accepts it
+ account UI reflects signed-in identity
```

---

## 4. Browser storage involved

### OAuth Web Client ID

```text
localStorage key: swrlzGoogleLoginTestClientId
```

This key is shared by the Chat Google bridge and the recovery page.

Current rule:

- empty value → seed canonical server/client authority;
- exact retired `...59am0s...` value → repair to canonical `...bj7ising...` immediately;
- any other non-retired browser-proven value → preserve it rather than silently overwriting it.

### Safe signed-in display claims

```text
sessionStorage key: swrlzGoogleLoginTestClaims
```

These are presentation/account-scoping claims, not a durable authentication credential. Server-side session verification remains authoritative.

### Account-scoped Chat/history namespaces

`chat_enhancements.js` can derive account-specific browser-local namespaces from the Google subject. This means different signed-in Google accounts may show different local thread counts/history on the same device.

Do not interpret different thread counts across Chrome/Edge or signed-in identities as an OAuth failure without separately checking authentication state.

---

## 5. Critical boot-order rule

This was the final hidden regression in the 2026-09-12 incident.

The Chat page loads runtime scripts in this relevant order:

```text
chat_enhancements.js
chat_google_server_config.js
```

`chat_enhancements.js` registers account/UI startup on `DOMContentLoaded` and its `bootGoogle()` reads:

```text
localStorage['swrlzGoogleLoginTestClientId']
```

If the Google bridge waits until its own `DOMContentLoaded` callback to repair a bad client ID, the enhancement listener can run first and initialize Google Identity Services using stale browser state.

Therefore `chat_google_server_config.js` must perform browser client seeding/retired-ID repair **synchronously while the script is parsed**, before its asynchronous `/api/account/status` reconciliation.

Regression guard:

```text
repair browser OAuth authority synchronously
BEFORE
account UI initializes Google Identity Services
```

Do not move this repair later in the lifecycle unless the script load order is deliberately redesigned and verified.

---

## 6. Stable backend authority rule

`main/api/google_account.py` owns the audience used for server-side Google ID-token verification.

The canonical default is:

```text
1083208613166-bj7isingvbv5dcns9ldtru8cjfj993mc.apps.googleusercontent.com
```

The stable backend must not advertise or verify against the retired `...59am0s...` client.

If `SWRLZ_GOOGLE_CLIENT_ID` is used as a deployment environment override, it must be checked against the canonical Web OAuth client. A stale environment value can override otherwise-correct source code unless the stable boundary explicitly migrates/rejects known-retired values.

The browser and server must agree on audience:

```text
Google GIS client_id
        =
Google token aud
        =
server google_client_id()
```

If these differ, Google may reject initialization or the §wyrlz server will reject the issued credential.

---

## 7. Diagnostic ladder — follow this order

When Google sign-in fails, do not immediately edit code or Google Cloud. Collect evidence in this order.

### Step 1 — capture the exact browser error

Common signatures:

- `Error 401: invalid_client`
- `no registered origin`
- Google button never appears
- Google credential is issued but §wyrlz says server verification failed
- login works in one browser but not another

Different signatures point to different layers.

### Step 2 — capture the exact browser origin

Read the full address bar origin, not just the project name.

Canonical expected origin:

```text
https://swrlzkamico-o3nu.vercel.app
```

A path such as `/api/chat` does not change the OAuth origin. A different hostname does.

### Step 3 — query live stable account status

Request:

```text
GET https://swrlzkamico-o3nu.vercel.app/api/account/status
```

Verify at minimum:

```json
{
  "ok": true,
  "authConfigured": true,
  "googleClientId": "1083208613166-bj7isingvbv5dcns9ldtru8cjfj993mc.apps.googleusercontent.com"
}
```

If the endpoint reports the retired client, the problem is still at the stable backend/deployment/environment authority layer. Do not blame browser cache first.

### Step 4 — inspect the live runtime Google bridge

Request:

```text
/live/assets/chat_google_server_config.js
```

Verify production is actually serving current `runtime` source and that synchronous repair exists before account UI initialization.

### Step 5 — inspect browser-local OAuth authority

Check:

```text
localStorage['swrlzGoogleLoginTestClientId']
```

Expected canonical value:

```text
1083208613166-bj7isingvbv5dcns9ldtru8cjfj993mc.apps.googleusercontent.com
```

If it contains the retired value, the current bridge should repair it on page load. If it contains another deliberate non-retired value, preserve it until there is evidence it is wrong.

### Step 6 — check boot order, not just final localStorage

A browser may show the canonical value *after* page load while Google was already initialized with the stale value earlier in the same boot.

If the browser remains blocked despite correct final localStorage and correct `/api/account/status`, inspect whether `bootGoogle()` initialized before the repair occurred.

This exact condition caused the final persistent failure in the 2026-09-12 incident.

### Step 7 — use the recovery page

Recovery/control page:

```text
/live/pages/google-login-test.html
```

Use it to:

- seed/repair the canonical browser Web Client ID;
- initialize Google Identity Services in isolation;
- verify the issued credential against `/api/account/google`;
- separate Chat-UI problems from OAuth/server problems.

If this page is 404/503, verify `runtime/runtime_pages/pages/google-login-test.html` exists and is reachable through the live runtime loader before drawing conclusions about Google itself.

### Step 8 — only then inspect Google Cloud

If the canonical client is being used and Google still reports `no registered origin`, verify the exact current origin is listed in the OAuth Web client's Authorized JavaScript origins.

Do not rotate client IDs or create new credentials merely because a browser reports a generic login failure.

---

## 8. Failure-signature matrix

| Symptom | Most likely layer | First evidence to check |
|---|---|---|
| `401 invalid_client` + `no registered origin` | wrong client ID or unauthorized origin | exact origin + `/api/account/status` client ID |
| Works in Chrome, fails in Edge | browser-local state or origin/boot differences | exact origin + localStorage client ID |
| Worked in Chrome, then Chrome also breaks after compatibility change | shared/fallback regression | recent runtime bridge changes + localStorage |
| Google chooser/button works but §wyrlz rejects login | backend audience/session verification | `/api/account/google`, `google_account.py`, active client ID |
| `/api/account/status` reports old client after source fix | production deployment/environment stale | active Vercel deployment + environment override |
| localStorage becomes correct but same tab still shows Google 401 | GIS initialized before repair | boot-order race; close/reopen tab and inspect runtime order |
| recovery page unavailable | runtime page delivery | runtime file existence + `/live/pages/...` response |
| different Chat history after login | account namespace switch, not auth failure | signed-in subject/account and namespace behavior |

---

## 9. 2026-09-12 incident timeline

### Initial working state

Google sign-in was already working in Chrome on the canonical §wyrlz production site. Google Cloud Web OAuth configuration already existed.

### Compatibility work begins

Work was performed to make the Google account experience function consistently in Edge as well.

### Regression 1 — wrong fallback client became authority

The server/runtime architecture began advertising/forcing:

```text
1083208613166-59am0s2p1v4vpoc04klr3iinh0oph1en.apps.googleusercontent.com
```

The runtime bridge used the same localStorage key as the previously working test/login flow and overwrote the browser-proven client ID.

Result:

```text
Edge still blocked
Chrome, previously working, became blocked too
Google error: 401 invalid_client / no registered origin
```

### Regression 2 — browser preservation stopped future damage but preserved already-poisoned state

The bridge was changed to stop overwriting an existing browser client ID with the server fallback.

That was directionally correct but insufficient: browsers already containing the retired client now preserved the poisoned value.

### Recovery-path discovery

The isolated Google login test page that could have repaired browser state existed on `main` but was missing from `runtime`, causing the live recovery path to fail.

The page was restored to:

```text
runtime/runtime_pages/pages/google-login-test.html
```

### Root cause found in stable backend

`main/api/google_account.py` contained the retired OAuth client as its fallback/audience authority.

The correct working Web OAuth client was recovered from the user's Google Cloud configuration:

```text
1083208613166-bj7isingvbv5dcns9ldtru8cjfj993mc.apps.googleusercontent.com
```

Stable backend source was corrected and production was redeployed.

Post-deployment proof:

```text
/api/account/status
→ googleClientId = canonical ...bj7ising...
```

### Remaining failure — boot-order race

Even after the backend and final browser storage value were correct, Google still showed blocked login.

Inspection of live Chat source showed:

```text
chat_enhancements.js
loads before
chat_google_server_config.js
```

Both registered `DOMContentLoaded` behavior. The enhancement layer could read the old value and initialize Google Identity Services before the later bridge callback repaired localStorage.

Thus a browser could end a page load with the *correct* stored value while the already-initialized Google client was still using the *wrong* value.

### Final correction

Server Runtime `2.3.81`, Web Chat `1.4.73`, Google Account `1.0.8` changed the bridge so empty/retired browser OAuth state is repaired synchronously at script parse time, before the Chat account footer initializes Google.

### Verification

User screenshots verified successful Google UI on both Chrome and Edge after the final runtime repair.

The incident's causal chain was:

```text
wrong fallback client
    ↓
browser localStorage poisoned
    ↓
stable backend audience also wrong
    ↓
canonical backend/client restored
    ↓
remaining boot-order race discovered
    ↓
synchronous pre-boot repair
    ↓
Chrome + Edge working
```

---

## 10. Recovery procedure

If this exact class of failure returns:

1. Do not change credentials immediately.
2. Confirm exact browser hostname/origin.
3. Query `/api/account/status` and confirm the canonical `...bj7ising...` client.
4. Fetch `/live/assets/chat_google_server_config.js` and confirm current runtime source is live.
5. Check `swrlzGoogleLoginTestClientId` in localStorage.
6. If it is the retired `...59am0s...` ID, reload/reopen Chat and verify synchronous migration occurs.
7. If a tab was already initialized using stale state, close the tab completely and reopen it after the repair is live.
8. Test `/live/pages/google-login-test.html` to isolate OAuth from the full Chat UI.
9. Verify `/api/account/google` accepts the credential.
10. Only if Google still reports an origin error with the canonical client, inspect Authorized JavaScript origins in Google Cloud.
11. Preserve evidence and add a new versioned incident/release record if code changes are required.

---

## 11. Regression guards

Future auth changes must preserve all of these invariants:

- One canonical production Web OAuth client authority.
- The retired `...59am0s...` client never becomes browser/server authority again.
- Browser OAuth repair happens before Google Identity Services initialization.
- Server token audience and browser GIS client ID agree.
- Runtime bridge does not silently overwrite an unrelated non-retired browser-proven client.
- `/api/account/status` exposes enough state to diagnose what production is actually using.
- Recovery page stays live and testable independently of Chat.
- Browser-local display claims never substitute for server authentication proof.
- A successful Google button render is not treated as end-to-end verification.
- Chrome and Edge should both be tested after auth architecture changes.

Recommended future hardening:

- Add an automated browser smoke test that asserts the client ID seen by GIS equals `/api/account/status.googleClientId`.
- Add an integration test for the retired-ID migration.
- Add a startup assertion/test that recovery occurs before account UI calls `google.accounts.id.initialize()`.
- Add an explicit `googleClientSource` diagnostic field (`environment`, `canonical-default`, etc.) if stable API evolution later warrants it.

---

## 12. Evidence-first rules for future §wyrlz

When this system fails again, §wyrlz should distinguish facts from hypotheses.

Good evidence:

```text
exact browser error
exact browser origin
live /api/account/status JSON
live served runtime JavaScript
current repository source + commit
current localStorage value
current script order
successful /api/account/google verification
Chrome + Edge screenshots after fix
```

Weak evidence that must not be treated as proof:

```text
"it worked before"
"Google Cloud should be configured"
"the code looks right in GitHub"
"localStorage is correct now"
"the Google button rendered"
"Vercel says Ready"
```

Each weak signal can coexist with a broken layer elsewhere.

---

## 13. Change-boundary reminder

Follow the project contracts before editing:

- browser/Chat/runtime bridge behavior → normally `runtime`;
- stable token verification/auth/session boundary → `main`;
- production stable changes require the Deployment Approval Gate when they will actually deploy;
- runtime and stable changes receive the appropriate version/release lineage when behavior changes;
- documentation-only updates do not justify arbitrary runtime/module version bumps unless they are part of a governed server development event.

Always read:

```text
SWRLZ_PROJECT_START.md
SWRLZ_HOTFIX_RULES.md
SWRLZ_VERSION_MODULE_EVOLUTION.md
SWRLZ_SERVER_ROADMAP.md
```

before substantial project work.

---

## Bottom line

The key lesson from this incident is that Google login is a **multi-authority flow**, not a single button:

```text
Google Cloud Web OAuth configuration
        +
exact browser origin
        +
stable backend audience authority
        +
browser-local client state
        +
runtime script order
        +
server credential verification/session issuance
```

A future §wyrlz should prove each rung in order before changing the next one. The 2026-09-12 regression was only fully resolved when the final boot-order race was identified after the client ID, deployment, and browser storage had already been corrected.