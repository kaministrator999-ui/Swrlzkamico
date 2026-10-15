# v258 · GitHub text file creation from conversation

**User-origin instruction:** `Swrlzing-core/write-action-tests/Testing.txt` asked us to stop requiring the awkward manually opened test button and recognize a user's GitHub file creation request in §wyrlz Chat.

## Implementation
- Stage 1 repository reading remains unchanged.
- The owner-approved v257 `CREATE_FILE` permission is the *only* write exception, and remains bound to `kaministrator999-ui/Swrlzing-core:main/write-action-tests/*.txt`.
- The existing authenticated server route produces `GITHUB_CREATE_TXT_APPROVAL_REQUIRED` only after the current user requests GitHub TXT creation. This is an explicit server-owned routing signal—not untrusted model output or a command embedded in a file.
- The Chat renderer projects that event to a client-side `swrlz:github-txt-proposal` signal with the matching request ID and originating user prompt.
- A compact human review panel opens *from the conversation*. The floating standalone **Test GitHub TXT creation** control is no longer injected.
- Filename and text are prefilled only when clearly present in the user's request; otherwise they stay blank for editing. It never invents the bytes to be committed.
- Only after the user presses **Prepare (no write)** and **Confirm GitHub creation** does the server attempt a create-only GitHub PUT, followed by byte-for-byte readback verification. Deny and scope checks remain authoritative on the server.

## Validation
- PR #182, `feature/chat-natural-txt-approval-v258`.
- Offline candidate test job: [GitHub Actions #38802469006](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38802469006), **SUCCESS**.
- Browser simulation: `node tests/test_github_chat_create_txt_v258.mjs`. Verifies server-signal-driven opening, explicit quote/filename prefill, no automatic write, one confirmation and absent guessed content.
- The simulation does not prove generalized LFM2-700M semantic reasoning. Richer ambiguous-language interpretation should be evaluated separately through real model tests, with all proposals still gated by user approval.

## Release and acceptance
Validate exact source commit, preserve the existing Hugging Face Space revision for rollback, deploy via guarded `.deploy/HF_SPACE_REQUEST.txt`, and observe logged-in mobile behavior after deployment. Ask for a text file directly in Chat, inspect prefill, approve an isolated new filename, and verify real GitHub readback. Never treat model-proposed words as approval.
