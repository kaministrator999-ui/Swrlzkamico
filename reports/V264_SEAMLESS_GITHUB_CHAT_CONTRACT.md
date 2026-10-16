# v264 — Seamless GitHub Chat file actions

Purpose: remove per-tool modals from the §wyrlz Chat experience. Inspect real GitHub files before proposing mutations, answer inside Chat, and request conversational yes/no only for a verified bounded write.

## Rename or move
- The accepted user's Chat turn is the source of intent, never fetched content, model response prose or another thread's messages.
- Read the selected connected owner's real default-branch repository tree before proposing a rename.
- If the requested exact file does not exist, say so briefly, list up to three verified similar filenames if any, and stop. Never silently substitute a fuzzy match.
- If exact source and destination validate, use the existing atomic tree/commit preparer and return the exact source/destination in Chat. Require a next-turn explicit yes/no by the same Google account in the same thread within five minutes. A changed topic revokes the pending approval. Writes retain one-shot no-overwrite and branch HEAD checks.
- Confirmed renames return verified GitHub work receipts. Failed or unverifiable operations must never be presented as successful.

## Create
- Exact source/text file content and path supplied in Chat can be prepared for existing protected CREATE_FILE action.
- If content is missing, ask only what the file should contain; the next Chat message provides content, after which yes/no is required.
- Do not hallucinate code, silently invent file content or attempt a binary upload from an unavailable Chat attachment.
- Backend binary upload and existing creation endpoints remain available, but no modal controllers are injected in Chat.

## UI
- Keep a single conversational interaction. No v258/v262/v263 Chat popup JS, CSS or popup event dispatch.
- Human authority is explicit conversational confirmation, not a data-entry wizard.
- No source control writes on read-only checks or missing files.

## Tests
- Python regressions for verified misses, close suggestions, no mutation, create/rename preparation, explicit approval, decline, account/thread isolation, expiry and programming/meta-request classification.
- Node source-contract tests assert that server inference is used and no legacy popup integration remains.
- Existing v262/v263 preparer and HTTP integrity tests remain active in the release pipeline.

Limits: selected public owner GitHub repositories only, one file per operation, no overwrite, no arbitrary directory-wide renames or workflow privilege escalation. Live signed-in account acceptance remains separate from offline CI and deployment.
