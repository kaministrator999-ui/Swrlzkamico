# §wyrlz Chat GitHub sandbox CREATE_FILE — v256 candidate

## Boundary
The only supported mutation is **creating a new UTF-8 `.txt` file** under `kaministrator999-ui/Swrlzing-core:main/write-action-tests/`. Existing files are rejected. There is no edit, delete, branch, PR, merge or deployment action. The model can propose the action and describe the approval UI, but cannot execute it by generating text. The human uses the bounded Chat test panel.

## Account-scoped GitHub OAuth reuse (v257)

The sandbox uses the *existing signed-in Google-account GitHub connection* encrypted in Upstash Redis, not a new GitHub personal-access token. It preserves the original `swrlz:github:account:<SHA-256(Google user ID)>` key format and Fernet-encrypted record (`owner`, `token`, `githubId`, `login`, `repo`, `scopes`, `connectedAt`). Tokens are never sent to the browser, inference model, client logs, or repository.

The original connection's hosting configuration is still required on the **server**: `SWRLZ_GITHUB_OAUTH_CLIENT_ID`, `SWRLZ_GITHUB_OAUTH_CLIENT_SECRET`, `SWRLZ_GITHUB_OAUTH_CALLBACK_URL`, `SWRLZ_GITHUB_ENCRYPTION_KEY`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`. These are existing connection settings, not a new sandbox token or separate owner allowlist. Server must preserve the original Google-account authority and encrypted records. Missing secrets/storage means the action fails closed.

For the **public** `kaministrator999-ui/Swrlzing-core`, prepare checks all of:
1. Verified Google account and its existing encrypted GitHub connection;
2. Selected repository exactly `kaministrator999-ui/Swrlzing-core`;
3. Verified stored GitHub login `kaministrator999-ui` from an earlier successful `/user` OAuth identity check;
4. **Actual granted** `public_repo` or `repo` OAuth scope, not merely the requested scope or repo ownership;
5. Live GitHub repository identity, public visibility, and `push` / `maintain` / `admin` role.

If the stored token grants only `read:user`, the existing GitHub OAuth app offers an **explicit one-time** `public-write` upgrade (`read:user public_repo`) through GitHub's consent page. Current read login and chosen repo remain linked to the same Google account. No manual PAT paste is required. A denied, interrupted, stale, or insufficient upgrade does not authorize a write. The action scope is still only `CREATE_FILE` in `write-action-tests/*.txt`.

Note: `public_repo` is a broad GitHub OAuth **provider grant** even though §wyrlz's application-level executor is narrowly confined to this sandbox. If that provider scope is considered too broad, use a separately bounded GitHub App installation credential in a later reviewed iteration instead of misrepresenting OAuth granularity.

## UI protocol
1. Sign into §wyrlz Chat with the allowlisted account.
2. Open **Test GitHub TXT creation**.
3. Enter a new filename and up to 4096 bytes of text.
4. Press **Prepare (no write)**. The server checks existence and returns a five-minute session-bound one-time ticket and exact preview.
5. Review the path and content. Press **Confirm GitHub creation**. Only then does the server issue PUT without SHA (GitHub Contents API requires SHA to update an existing file).
6. Server reads the file back and verifies exact bytes and SHA-256. Only a successful response with commit SHA and verified URL counts as confirmed.
7. A duplicate, expired token, account mismatch, rejected origin, auth failure or ambiguous GitHub response is not reported as success. If read-back fails after PUT, inspect the remote file before retrying; creation may have occurred.

## Important limitations
- This is a *manual, user-approved test capability*, not proof that LFM2-700M semantically parsed a creation request.
- The process-local approval store does not persist across server restart; missing tickets fail closed.
- Enabling requires operator-managed credentials; this development PR does not configure secrets.
- No production acceptance until CI is green, the actual HF deployment is checked, and the signed-in browser write test returns a verified read-back receipt.
- Independent unit test: `python -m unittest discover -s hf_space -p test_github_sandbox_create_txt_v256.py -v`.
