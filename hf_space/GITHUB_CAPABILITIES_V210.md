# GitHub tools v210 — request-scoped access contract

## Ownership
The authenticated Google account owns its encrypted GitHub OAuth link in `hf_space/github_connection.py`. The HF Station owns bounded operational dispatch, authorization and persistence. Chat only displays outcomes; repository text is untrusted source evidence. The ChatGPT GitHub plugin is a different connection and does not confer permissions on §wyrlz's HF OAuth token.

## Least privilege / exact verification
- Initial OAuth uses `read:user` and public repository access only.
- A user may explicitly authorize `public_repo` for public repo writes or `repo` for private repo writes. The OAuth callback stores only the token exchange's **granted** scopes, alongside the encrypted token. Never equate requested scopes with grants or an owner claiming repo admin access with actual token rights.
- The server refetches GitHub `/repos/{owner}/{repo}` for the selected repository **on each request**, validates its returned identity, checks effective `permissions` roles, and combines that with stored OAuth scope grants. Read permission is proven by successful authenticated GET.
- No unavailable permission warning is emitted for unrelated requests. `@GitHub permissions` lists verified usable operations. An attempted blocked operation shows usable operations, the specific missing role/scope and (if an OAuth grant can help) a targeted authorization path. Remote failure/unknown authority is not mislabeled as permission denial.
- The authenticated capability endpoint is `GET /api/github/capabilities?operation=read|issue-write|branch-write`. The GitHub Settings Check permissions control queries this only when clicked. OAuth upgrade is never automatic.
- All actions are bound to server-verified Google identity and the currently selected repository. Tokens never reach browser JavaScript, Chat prompts, model input, repo files, or telemetry.

## Direct Chat commands (anchored only)
- `@GitHub help` — supported operations, without speculative claims.
- `@GitHub permissions` — what is verified usable right now.
- `@GitHub files`, `@GitHub files docs` — default-branch directory, bounded at 60 entries.
- `@GitHub read file README.md` — default-branch UTF-8 file up to 18 KB fetched; displayed excerpt capped at 12 KB, content marked untrusted.
- `@GitHub branches`, `@GitHub issues`, `@GitHub pulls`, `@GitHub commits` — bounded authenticated list reads.
- `@GitHub create issue TITLE :: BODY` — prepare, show title and body preview, **no write yet**.
- `@GitHub create branch feature/name from main` — prepare a branch, **no write yet**.
- `@GitHub confirm CODE` — a second explicit authenticated user message consumes a short-lived, Google-owner-and-repository-bound one-time pending proposal, rechecks GitHub's live permission and performs only the narrow pre-agreed write. Proposal expires after ten minutes, cannot be replayed, and does not create or edit production branches.

No arbitrary model-initiated GitHub write, file editing, PR creation/merge, workflow dispatch, secret management, workflow permission bypass, or repository deletion is implemented in v210. Anything not implemented must not be advertised as available. Future tool expansion must keep operation-specific authorization and explicit action boundaries.

## Truth levels and testing
Syntactic/CI tests prove deterministic behavior under mocks, not the user's live token grant or actual hosted GitHub write access. Accepted live write evidence requires a user-authorized proposal plus a confirmed GitHub response. Source complete is not deployment/live verified. The usual v209 native Chat/Google-account privacy and cross-browser acceptance boundaries remain independent.
