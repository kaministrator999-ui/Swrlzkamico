# v221 — §wyrlz GitHub Stage 1: repository reading first

**Date:** 2026-10-12 · **State:** guarded source/CI/Space release completed; authenticated owner acceptance pending.

## Supported now
Read GitHub only: selected repository source listing, bounded exact-file reads, and canonical §tart startup documents. Stage 1 is enforced server-side across Chat commands, model-proposed actions, OAuth write escalation, stale approvals, write preflight and low-level GitHub issue/ref requests. Tokens may have grants beyond the stage; those do not enable locked operations.

## Locked
New files, edits, deletions, PRs, branches, issues, engine coding writes, workflow mutations and deployment. They require a future separately tested capability tier and explicit approval. Older mutation test fixtures run under a deliberate test-only legacy stage to preserve historical regressions, not active deployment functionality.

## Source and verification
- Candidate: `feature/github-staged-read-only-v221@f05900407818be66e276360da427b8b0bebb461e`, [draft PR #124](https://github.com/kaministrator999-ui/Swrlzkamico/pull/124), from v220 exact published source.
- First account CI [#38288751625](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38288751625) failed: denied-write preflight incorrectly hid still-allowed reading. Fixed.
- Corrected account CI [#38288886639](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38288886639) and HF offline [#38288893042](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38288893042) both succeeded.
- Existing Space deploy [#38289121426](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38289121426) succeeded; Space `84f48b3a3bf1546a44c64d83d2d2fd984af6a7df`, rollback `85c521293bda1a796ad3db20e7b9fd2c83bcbe7f`, checkpoint `11765040567`. `DEPLOYED_UNVERIFIED`; `knownGood=false`.
- Runtime registration `33c1aa65dd8dce94bb1541738f20e0c61525a86b`: Server 2.3.374; Repository Work 1.0.162. Other module versions unchanged.

## Acceptance
Authenticate in existing §wyrlz Chat, select repo, read root/known subfolder/existing file and canonical §tart. Confirm denied creation/edit/confirmation/workflow attempts do not write. Source/CI success does not prove Android UI or actual 700M comprehension; test these before activating Stage 2.
