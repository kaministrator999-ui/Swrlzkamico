# v263 — GitHub atomic file rename release

Date: 2026-10-15
Space: `kamiloki/Swyrlz`

## User request and implementation
Add renaming of existing GitHub files to §wyrlz Chat without losing the file's contents or exposing an unapproved delete/edit pathway.

- Renames a **single file**, optionally moving it between folders, using one new Git tree and commit. The destination points to the exact existing Git blob SHA and Git mode; the old path is removed in the same commit.
- The user sees an exact review of the current selected owner repo, default branch, source, destination, original blob/size/mode, and pinned branch HEAD before confirming. Approval is one-time and expires.
- The server rechecks linked Google user, existing GitHub OAuth grant, live repository push role, selected repo, default branch and HEAD. A non-forced ref update protects against races; existing destination files and directory/submodule sources are rejected.
- After the rename commit, server checks the new HEAD, verifies the source path is gone, and verifies the destination points to the original SHA/mode. It returns a verified Chat work receipt with source/destination and commit links.
- Restricted to the two selected public owner repositories `kaministrator999-ui/Swrlzing-core` or `kaministrator999-ui/Swrlzkamico`. Directory-wide moves and unrelated GitHub writes remain locked. Renaming a workflow path requires the provider's separate workflow grant.
- Unlike the v262 create upload action, this operation does not re-upload data, so it is not limited to its 1,000,000-byte input limit. Repository tree enumeration must be complete, or the action is blocked.

## CI and deployment evidence
- [PR #189](https://github.com/kaministrator999-ui/Swrlzkamico/pull/189): **MERGED**.
- Exact merged source: `80bab274b8f7b7f05de1681539343debe86430f4`.
- Offline candidate [Actions #38826436165](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38826436165): **SUCCESS**.
- Mobile integrity [Actions #38826436146](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38826436146): **SUCCESS**.
- Protected Hugging Face deploy [Actions #38826561291](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38826561291): **SUCCESS**.
- New Space revision: `8c2627d58bf0b11ceec947830a5811238fecef1a`.
- Rollback revision: `c3e42c8a4b7384ec17375864ed70af707be89b5f`.
- Deployment state: **DEPLOYED_UNVERIFIED**; signed-in owner rename has not yet been demonstrated live. A successful upload proves deployment, not successful real-user write acceptance.
- Version registry: repository-work `1.0.202`, server-runtime `2.3.414`, web-chat `1.5.145`.

## Signed-in acceptance
With a disposable test file selected in §wyrlz Chat, ask `Rename write-action-tests/my-test.txt to write-action-tests/my-renamed-test.txt in the GitHub repo`. Only use files actually present and intentionally disposable. Confirm proposal. Verify GitHub contains exactly one rename commit, the old path is absent, the new path points to the same blob SHA/mode and the Chat work receipt is accurate.
