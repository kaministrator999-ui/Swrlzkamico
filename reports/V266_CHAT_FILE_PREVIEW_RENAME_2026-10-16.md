# v266 — latest Chat export (64): GitHub file preview and rename continuity

Date: 2026-10-16 (America/Chicago)
Scope: §wyrlz AI Chat only. Owner supplied mobile screenshots and most recent conversation in export (64). No unrelated historical threads were used to identify regressions.

## Observed
- A verified GitHub file read correctly located `write-action-tests/Testing.txt` at `a03a600eab16fc653a3c8b8184e803feccf9b66a`, Git blob `defcc454e4340b7bf5a6a3b0b8fee2b5b7d3cf56`, but the Chat message displayed an oversized literal URL and long raw hashes.
- The unmodified plaintext file appeared in a `text` fenced preview that horizontally scrolled on Android rather than wrapping.
- Natural followups `Can you rename that file for me` and `Can you rename it too testing.txt` were classified as programming tasks (`CODER_AUTO_ROUTE`) and rejected with `no-code-candidate`, reusing the previous GitHub source response rather than asking a destination or preparing a rename.
- None of these messages changed the GitHub file.

## Scoped correction
1. `chat/§wyrlz/index.html`: verified GitHub file response preamble is displayed in the existing compact provenance/source card. Details collapse full commit and blob hashes; a verified GitHub link is available. The card is rendered only when signed-in server-persisted repository context, file path, source SHA and provider URL exactly match, rather than trusting arbitrary assistant prose. The `text`, `txt` and `plaintext` fenced previews wrap using CSS without changing underlying source bytes or regular programming-code scrolling. Copy and Download still use original raw bytes.
2. `hf_space/github_conversation_actions_v264.py`: verified same-thread `lastFile` takes priority, with current authorized Git-tree revalidation; bare rename questions ask for the new filename and store a short-lived account/thread-scoped destination request. A follow-up new filename or `rename it too name.txt` moves to an existing one-time confirmation proposal only. No mutation is authorized by a question, clarification or destination.
3. `hf_space/station.py`: `need-destination` is handled by the file action route rather than sent to the coding model.
4. Regression tests: export (64) utterances, case-only rename preparation, missing destination, mismatch no-write paths, plain text wrapping, lyric-reader compatibility and safe provider card contract.

## Source / validation
- [PR #198](https://github.com/kaministrator999-ui/Swrlzkamico/pull/198), merged source `510362e50fd9db9f8f325855d72e3d8eb5f1011a`.
- Candidate head `06f37fde912e6f37c60ce1091c8a74bba8c7790a`, tree `0951c7a309b48fc19729c51f1dbc36696a335d3c`. Merged Git tree matches exactly.
- [HF Candidate Offline Validation #38949111598](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38949111598): COMPLETED / SUCCESS.
- [Mobile Lyric Reader Integrity #38949111580](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38949111580): COMPLETED / SUCCESS.
- Initial mobile CI was red because the old exact four-argument source assertion omitted the new optional verified context; the test was updated to assert both preserved lyric hint and verified context. Failure history remains in GitHub.

## Deployment / acceptance
A guarded release of the existing `kamiloki/Swyrlz` Space should be issued only for the validated merged source; the trigger is not success until the workflow terminates and captures the new Space revision and rollback. Signed-in Android behavior should then be tested separately: file card, mobile wrapping, missing rename destination, destination follow-up, confirm/decline and case-only rename. No production rename has been performed during engineering.