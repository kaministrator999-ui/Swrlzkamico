# v265 — Chat GitHub named-file read and contextual rename repair

Date: 2026-10-15 (America/Chicago)
Scope: §wyrlz AI Chat only; latest conversation in owner export (63); independent older threads excluded.
Runtime: existing Hugging Face Space `kamiloki/Swyrlz`.

## Observed latest-thread failures
1. A user asked if a file named `testing.txt` was visible in their selected GitHub repository. The reply twice reported an unhelpful GitHub 404 despite a verified directory context.
2. The immediately subsequent request to rename “that file” to `testing1.txt` was not recognized as a GitHub file operation. It entered programming inference and returned HTTP 500.
3. Independent authenticated repository inspection established the actual case-sensitive file `write-action-tests/Testing.txt`; no file was renamed during diagnosis.

## Minimal canonical source correction
- `hf_space/github_read_inference_v235.py`: deterministic singular named-file read intent now invokes the authenticated, SHA-pinned repository filename resolver, instead of the generic fallback.
- `hf_space/github_conversation_actions_v264.py`: recognize an explicit same-thread “rename that file” follow-up only with a verified repository/branch/revision context and a recent user-named filename; inspect the current owner-authorized Git tree, require a unique case-sensitive blob, then present full actual source/destination paths.
- `hf_space/station.py`: carry the bounded verified thread context and latest history to the existing Chat file-action handler, bypassing coding generation only for an applicable operation.
- Existing preview, one-time yes/no owner authorization, immutable Git blob and mode, no overwrite, repo/branch matching, and no-write-before-confirm restrictions remain.

## Validation and ownership
- Scoped candidate: [PR #195](https://github.com/kaministrator999-ui/Swrlzkamico/pull/195).
- Exact merged candidate source: `617b6445fa93c7e41f393b745aff5bfe579d5b46`.
- The initial candidate CI uncovered an invalid multiline insertion; a second attempt identified a stale static-test signature; a third attempt identified whitespace sensitivity in that test. Each was corrected with a new commit; no failed attempts were erased.
- Final head offline HF CI [#38847988939](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38847988939) reported SUCCESS.
- Verify merged source tree and guarded HF release separately before considering this feature active.
- No production rename was executed on the owner's test file and no signed-in live rename acceptance was established by source/CI.

## Post-release signed-in acceptance
1. Browse the sandbox directory and ask “Can you see the testing.txt file?”; expected: one verified case-preserving file answer, not generic 404.
2. Ask “And you rename that file for me to testing1.txt”; expected: verified existing `Testing.txt` to new destination preview, with explicit yes/no and no mutation before confirmation.
3. Test denial, mismatched context, ambiguous same-named paths, branch movement and expired confirmation.
4. Compare the committed rename blob/mode against the original after approval only. Owner hands-on acceptance remains distinct from workflow publication.
