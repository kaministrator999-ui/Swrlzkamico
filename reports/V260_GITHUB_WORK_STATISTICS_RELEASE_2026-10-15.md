# v260 — GitHub work statistics and verified-receipt visualization

Date: 2026-10-15
Target: `kamiloki/Swyrlz` (existing Hugging Face §wyrlz Chat Space)

## User evidence verified from GitHub

Screenshot at 5:08 PM Central showed a direct Chat-created file. Public GitHub read and commit evidence independently confirmed:
- Repository: `kaministrator999-ui/Swrlzing-core`
- Branch: `main`
- File: `write-action-tests/chat-test-6bbae6acc5289bb8.txt`
- Exact commit: `d7d24c4629c62613744742e52ca9349716721e31`, 2026-10-15T22:08:53Z.
- Current file bytes: **189**. Lines: **3**. Commit diff: **1 file added**, **3 insertions**, **0 deletions**.
- Text confirms the expected preselected safe §wyrlz Chat testing content; current blob SHA `3b45f878ef3d00a58badb91aafa99d5be34fb141`.
- Verified sandbox listing had 3 distinct files at inspection time. This is a time-bound count, not a repository-wide total.

## Change

The canonical Chat uses a reusable `swrlz-widget-v1` / `github-work` structured summary card with a mobile-friendly layout for the repository, branch, file/commit links, exact-byte verification, bytes written, text lines, files created, plus real GitHub diff statistics when an exact commit SHA and matching added-file path are validated. Styling uses scoped `.github-work-*` classes and textContent; GitHub URLs are allowlisted.

The owner-authorized direct `CREATE_FILE` action streams and durably persists the widget on the Chat assistant message. The reviewed/confirmed `CREATE_FILE` dialog shows the same verified receipt. If optional provider diff retrieval fails, the widget displays *unavailable*, never invented additions/deletions. Existing Google-account GitHub OAuth checks, narrow path scope, create-only mutation and no-overwrite behavior remain unchanged. The display component can support future GitHub operations when they provide equivalently grounded structured data; no claim that all future operations are already instrumented.

## Tests, source, release, and rollback
- [PR #185](https://github.com/kaministrator999-ui/Swrlzkamico/pull/185) — merged.
- Deployed source: `c0d3b9805088f2fc804858fc9ed203999150359d`.
- Complete offline candidate CI [Actions #38815986465](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38815986465) — **SUCCESS**.
- Mobile integrity [Actions #38815986598](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38815986598) — **SUCCESS**.
- Guarded Hugging Face production deployment [Actions #38816193162](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38816193162) — **SUCCESS**.
- New HF Space revision: `bf5272aa205ac812b77f9690215716850c6e5199`.
- Prior HF Space rollback: `b3b4d43aabc8ba1b07b86504f75983869d0cf7ce`.
- Verification state: **DEPLOYED_UNVERIFIED**, pending signed-in mobile rendering acceptance.
- Version registry: repository-work `1.0.199`, server-runtime `2.3.411`, web-chat `1.5.142`.

## Remaining live acceptance

In the signed-in mobile §wyrlz Chat, issue another harmless test-file creation request (or confirm a pending sandbox creation). Check that the work summary is a proper card, that all displayed links target `Swrlzing-core`, that file bytes and line counts are accurate, that GitHub diff metrics appear only when available, and that refreshing the thread preserves the card. Verify the new commit and contents independently. The deployed source and offline CI do not prove the mobile visualization has already been observed live.
