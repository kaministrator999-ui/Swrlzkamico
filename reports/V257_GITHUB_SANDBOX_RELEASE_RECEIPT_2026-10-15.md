# v257 · Existing GitHub OAuth → narrow TXT sandbox creation

**Date:** 2026-10-15
**Target:** existing Hugging Face Space `kamiloki/Swyrlz`
**Scope:** user-approved `CREATE_FILE` for new UTF-8 `.txt` files in `kaministrator999-ui/Swrlzing-core:main/write-action-tests/` only.

## Source and release receipt
- Source baseline: exact previously deployed v254 commit `b44d9f19dfcc1c168fb71f4d05ed92ec0c7a6206`.
- Owner-approved design and implementation: [PR #181](https://github.com/kaministrator999-ui/Swrlzkamico/pull/181), merged into `integration/live-source-v254-sandbox-v257`.
- Deployed source commit: `f79c968b63a1a8f2ff009945d9206990f84fae07`.
- Full offline candidate validation: [Actions #38787434368](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38787434368) — **SUCCESS**.
- Canonical guarded deployment: [Actions #38787595714](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38787595714) — **SUCCESS**.
- Exact new Space revision: `6d2f4dd8fa92b9d185c000c5ae6c104928169d01`.
- Predeployment rollback Space revision: `81a0c8cd951cea860ba6dba8d58ec849dee657ca`.
- Workflow checkpoint: **`DEPLOYED_UNVERIFIED`**, `knownGood=false` until signed-in Android live acceptance.
- Version registry `runtime:versions/`: repository-work `1.0.196`, server-runtime `2.3.408`, web-chat `1.5.139`. No unrelated engine/inference module bumped.

## Security and behavior
Existing encrypted OAuth record is reused. A one-time public GitHub OAuth write grant (`public_repo`) is offered only when the linked account currently grants read-only. The owner login, exact selected repo, current repo push role, user-confirmed filename and content, server-side one-time ticket, no-SHA GitHub create PUT, and byte-for-byte read-back are mandatory. Other GitHub command mutation classes remain locked. A natural-language request to make a repo text file now proposes the confirmation UI rather than generating code.

## Outstanding acceptance
The owner should load `https://kamiloki-swyrlz.hf.space/chat/%C2%A7wyrlz`, confirm the GitHub connection remains linked to `Swrlzing-core`, open **Test GitHub TXT creation**, and inspect the write grant. If the saved OAuth grant is read-only, approve the requested GitHub public-repository permission in GitHub's own OAuth consent screen. Then create a uniquely named test `.txt`, confirm explicitly, and check commit/file read-back. This source/workflow receipt is not itself a live-file-creation claim. No real sandbox file was created by the deployment workflow.
