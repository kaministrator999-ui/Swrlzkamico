# v223 — §wyrlz interactive GitHub repository workspace

**Date:** 2026-10-12 · **Status:** source/CI/guarded Chat deployment completed. **Live authenticated acceptance pending**.

## Delivered
Mobile-first collapsible and fullscreen repository explorer, on-demand pinned GitHub tree statistics, verified file/folder byte counts, recursive counts, path search, local filter/sort, syntax-highlighted read-only source, safe copy-path/code, path-specific Git commit history dates, bounded branch differences, and same-thread repo+branch+directory+file+SHA conversational continuity. Selecting folders or files updates only the Google-account-owned native chat thread metadata, not GitHub. Subsequent common repository follow-ups can implicitly invoke Stage 1 tools. Read-only GitHub gates, no-OAuth-escalation and explicit denial of write families remain intact.

**Honest limits:** Git blob byte size is not repository-on-disk storage; history's first visible path commit is not a reliable OS creation date; directory trees over 20,000 or GitHub-truncated entries fail closed; global last-changed sort is limited to 24 entries when verified dates can all be loaded; comparison shows at most 30 paths and 10k characters of patch each. Arbitrary freeform code architecture explanation still depends on actual model comprehension and isn't guaranteed by file listings.

## Source and CI
Candidate `feature/github-explorer-ui-v223@45cbeb928f9064025907f84213ac43931242fd70`, [review PR #126](https://github.com/kaministrator999-ui/Swrlzkamico/pull/126) from published v222 source. Full [GitHub Account CI #38306401439](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38306401439), [HF Offline #38306406712](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38306406712) and [Mobile Integrity #38306406730](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38306406730) all passed at candidate SHA. Tests: `hf_space/test_github_explorer_v223.py`, historical Stage 1 read-only test suite, account ownership, thread context mutation, and staged mobile JS syntax. Prior CI failures corrected.

## Published release
Canonical unchanged target `kamiloki/Swyrlz`, approved request commit `ef15c43de4e723971b758ca61d68d0326fa30950`, nonce `2026-10-12-v223-repository-explorer-context-metadata-001`. [Guarded deploy #38306635047](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38306635047) passed, new Space revision `f21de3bf1f56090b3db343c9347561f49ba415a9`, rollback `da98762c9a42ed4a70203a78320fac0b820675d9`. Artifacts: release `11772084350`, rollback `11771954741`, previous-reference `11772024679`. Receipt `DEPLOYED_UNVERIFIED`, `knownGood=false`.

Atomic `runtime@c54c2753ea39809205ccb78a4beabeb959dcdca8`: Repository Work **1.0.164**, Server Runtime **2.3.376**, Web Chat **1.5.110**. Other module authorities unchanged. Separate §E game engine untouched.

## Live acceptance still open
On connected Google owner account open `/chat/§wyrlz`, ask `@GitHub files`; confirm interactive collapsible display, refresh metadata, folder breadcrumbs, total/recursive sizes, source viewer, Git path commits, and compare. Ask "how many files are there?" then "and directories?" after browsing a folder; refresh the same chat and verify context. Check writes remain denied. Automated CI does not constitute authenticated browser testing.
