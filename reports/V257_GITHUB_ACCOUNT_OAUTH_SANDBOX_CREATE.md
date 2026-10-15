# v257 · Owner-approved GitHub TXT creation via existing connected account

Date: 2026-10-15

## Original observed defect
Owner signed into §wyrlz Chat and selected `kaministrator999-ui/Swrlzing-core`, but natural-language `Can you make a txt file in the repo for me` was interpreted as programming, rejected by a `no-code-candidate` gate, and surfaced an irrelevant GitHub startup retrieval failure. Connected GitHub was Stage 1 read-only; the original OAuth flow requested `read:user` and explicitly blocked write scope escalation.

## Architecture correction
- Use the **actual v254 Space deployment source** `b44d9f19dfcc1c168fb71f4d05ed92ec0c7a6206`, not a stale laboratory branch missing encrypted account history and connected GitHub source browsing.
- Retain the existing `github_connection.py` Google-account session, Fernet encrypted per-account GitHub OAuth token, durable Redis record, chosen repo, scope, and repository-reading commands.
- Allow only OAuth `public-write` upgrade within the verified owner's selected public `Swrlzing-core` repository. Reuse an existing `public_repo`/ `repo` grant if present; otherwise surface a one-time GitHub consent redirect. Never treat GitHub owner role or successful read as sufficient write authorization.
- All other Stage 1 GitHub mutations stay locked. Specifically no edits, overwrites, deletes, issues, PRs, branches, workflow creation/dispatch, engine mutations or deployments.
- New sandbox API: `/api/github/sandbox/write-status`, `prepare-create-txt`, `confirm-create-txt`; owner+scope+role+same-origin checks, five-minute one-use approval, fixed `main:write-action-tests/` destination, 4 KiB UTF-8 limit, no SHA on GitHub PUT and verified read-back before success.
- The 700M conversational request produces an approval proposal, not generated code, an automatic repository mutation or a GitHub startup action.

## Offline acceptance
- [GitHub Actions #38787188570](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38787188570) validates the earlier intermediate source; v257 final source is separately checked by the candidate CI run associated with PR #181.
- Legacy Stage 1 read/write-denial cases, GitHub explorer, mobile Chat, archive, Chat model contracts, authenticated sandbox HTTP and create-only regressions remain required.
- At the production request stage record the **exact final source SHA**, predeployment rollback checkpoint, terminal Hugging Face workflow result, deployed HF revision, and live user acceptance separately.

## Owner-facing behavior
Open Chat's **Test GitHub TXT creation**. If the existing GitHub token grants public write, the test form is immediately enabled with no extra login. If only read access was granted, Chat offers GitHub's ordinary OAuth consent screen for `public_repo`; it never requests a GitHub personal-access token. Review the exact proposed filename and contents, confirm explicitly, then verify the resulting file URL/commit.

## Truth boundaries
Source change, tests and deployment cannot prove the user's OAuth grant, actual Android UI acceptance, or that a live file was written. The owner must inspect the consent page and authorize it if required. No token is stored in Chat plaintext/browser storage or printed in logs.
