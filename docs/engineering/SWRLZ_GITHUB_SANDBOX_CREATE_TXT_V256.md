# §wyrlz Chat GitHub sandbox CREATE_FILE — v256 candidate

## Boundary
The only supported mutation is **creating a new UTF-8 `.txt` file** under `kaministrator999-ui/Swrlzing-core:main/write-action-tests/`. Existing files are rejected. There is no edit, delete, branch, PR, merge or deployment action. The model cannot invoke this endpoint by generating text. The human uses the bounded Chat test panel.

## Operator prerequisites (not included in Git)

Set in the protected server environment, NEVER in user messages, public source, browser JavaScript or diagnostics:
- `SWRLZ_SANDBOX_WRITE_ENABLED=true` — defaults off.
- `SWRLZ_SANDBOX_WRITE_GOOGLE_SUB=<Google OAuth subject of authorized repo owner>` — not an email or nickname.
- `SWRLZ_SANDBOX_WRITE_GITHUB_TOKEN=<GitHub fine-grained token>` — grant only Contents **Read and write** for `Swrlzing-core`, with minimum needed permission and expiration; do not give access to `Swrlzkamico` or other repositories.

The Google ID token is verified by the existing signed-in session endpoint. API requests require same-origin HTTPS. Never share or commit credentials.

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
