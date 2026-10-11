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

## Explain access and consent to the user

- If no GitHub account is linked, explain that §wyrlz cannot obtain *authenticated* GitHub read or write permissions itself; the user must connect GitHub and approve the access presented by GitHub.
- If GitHub responds with 401/403/404 on the selected repository, state that effective read/write access is **unverified**. It might be a token, scope, repository identity/existence, or remote restriction issue. Do not categorically say a scope is missing without evidence.
- If a known public/private repository is readable and a requested write is blocked, show confirmed available operations and only the missing OAuth scope or repository role for **that requested write**. The suggested URL begins an interactive user-approved OAuth flow; it never grants scopes without consent.
- A permissions inspection reports current observations; it never silently requests or expands any permission.
- Public GitHub source that is intentionally public may be independently readable without authenticated repository grants. That does not give §wyrlz access to private files, account-owned features, or writing.

## v211 — model-guided read operations and visible inference progress

The core v210 permission/confirmation contract remains authoritative. v211 adds bounded conversational interpretation **within** that contract: the existing selected §wyrlz local model may suggest 1–3 read-only operations from a request such as "Can you show my repo issues and pull requests?" or "@GitHub ask check my repo permissions". Exact commands still select tools deterministically; exact write proposals and confirmations remain solely in the v210 server-owned authorization path.

- Planner receives a brief user request plus strict JSON tool-selection rules; no OAuth token, encrypted history, Google subject, raw private conversations, profile details, or arbitrary URLs are put into model context. Planner text is captured as untrusted proposed actions, **never displayed as internal reasoning**.
- Allowlist: permissions, files, branches, issues, pulls, commits, and a specific read-file/directory path only when explicitly present in the user's request. Up to three checks. No GitHub write, workflow dispatch, PR merge, branch deletion or scope upgrade can be model-selected. Invalid, missing, excessive or forbidden model output falls back to bounded deterministic read checks.
- Each proposed tool is independently checked using the existing Google-bound encrypted connection and live GitHub repo permission preflight. Failure leaves read unverified rather than inventing missing scopes; subsequent checks stop instead of continuing unverified. Direct user-typed write commands retain the existing one-time explicit approval requirement.
- Station emits actual ordered STATUS events: GITHUB_MODEL_PLAN_STARTED, GITHUB_MODEL_LOADING/GENERATING/PROGRESS (only when reported/produced), GITHUB_PLAN_READY, GITHUB_PERMISSION_CHECK, GITHUB_PERMISSION_VERIFIED (only after actual repo evidence), GITHUB_TOOL_STARTED, GITHUB_TOOL_COMPLETE or GITHUB_TOOL_FAILED, GITHUB_EVIDENCE_COMPLETE. The NDJSON stream and existing Chat progress trail render those events without invented percentages or simulated internal thought.
- Verified tool responses—not a model's unsupported reconstruction—provide the final evidence. Permission checks disclose the relevant missing permission only for a requested operation; a read does not ask for write. If no model exists, explain safe fallback via the plan status; never falsely label fallback as model inference.

The v211 work reuses the single account connection, Station lifecycle and existing Chat UI. It creates neither an AI identity fork nor a separate GitHub token store. Source/CI/release status must be reported separately; real signed-in Android observations are the last acceptance boundary.

## Truth levels and testing
Syntactic/CI tests prove deterministic behavior under mocks, not the user's live token grant or actual hosted GitHub write access. Accepted live write evidence requires a user-authorized proposal plus a confirmed GitHub response. Source complete is not deployment/live verified. The usual v209 native Chat/Google-account privacy and cross-browser acceptance boundaries remain independent.
