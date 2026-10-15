# v262 — General GitHub CREATE_FILE: source, dotfiles, binary

Date: 2026-10-15

## User request
Extend the now-live §wyrlz GitHub connection beyond creating only `.txt` files: support the file formats that GitHub can store, including programming languages, configuration, data, documents and binary files. Retain real work receipts and safeguards.

## Owner and security model
- Use the existing signed-in Google account's encrypted OAuth connection, the actual GitHub-granted scopes, current repository selection, GitHub push role and default branch.
- First general-creation tier is restricted to the two verified public owner repos `kaministrator999-ui/Swrlzing-core` and `kaministrator999-ui/Swrlzkamico`. Not a claim of permission to arbitrary GitHub repositories or private repositories.
- Explicit two-phase `prepare → preview → confirm`, including actual selected repo, branch, path, byte length and SHA-256. Proposals are single-use and expire after 300 seconds; a different account cannot consume another user's ticket. Nothing executes solely from a model output, file content, or stale approval.
- GitHub Contents API PUT creates **one new file only**, with no existing-blob SHA supplied. GET checks before preparation, before PUT, and after PUT. Success requires the exact remote bytes and checksum; overwrite/update/delete/branch/PR/workflow dispatch remain outside this action.
- Existing narrow direct `test .txt` action and its no-manual-form behavior remain intact.

## File support
- Paths can be nested and Unicode NFC; extensionless names (e.g., `LICENSE`), dotfiles (`.gitignore`), Markdown, source code and JSON work with UTF-8 typed content, including an intentionally empty file.
- Binary mode transmits local uploaded bytes without text conversion, e.g. `assets/dragon.png`, `documents/report.pdf`, and compiled data.
- First adapter limit: **1,000,000 bytes per file**, deliberately below the GitHub Contents API 1 MiB reliable base64 readback threshold. This is not the maximum file size that GitHub itself supports. Larger files and Git LFS require a separately designed, tested route.
- Exact GitHub provider permission for protected workflow paths may require an additional `workflow` OAuth scope. The adapter does not broaden scopes behind the owner's back.

## Chat and presentation
- The server classifies the current user's general file-creation request as `GITHUB_GENERAL_CREATE_FILE_APPROVAL_REQUIRED` rather than a programming artifact or unapproved write.
- Chat opens an accessible file review for path + text/code or local binary upload, optionally prefilled only from explicit user-provided details.
- After an approved verified write, the same bounded GitHub work-statistics widget reports bytes, text line count where meaningful and provider-derived commit insertions/deletions where available. Unknown statistics remain absent.

## Proof before publication
- `hf_space/test_github_general_create_v262.py`: Unicode/dotfiles/nesting, byte-for-byte PNG, empty files, wrong-account/repo, replay, cancel, invalid paths, size and owner scope.
- `hf_space/test_github_general_http_v262.py`: actual HTTP prepare-confirm, cross-origin denial.
- `hf_space/test_github_general_work_summary_v262.py`: provenance-safe binary/source metrics and optional GitHub commit diff.
- `tests/test_github_general_create_v262.mjs`: mobile modal and no write before explicit confirmation.
- All previous Chat, model, editor, GitHub and mobile candidate CI gates remain required.
- Deploy only through the existing guarded Hugging Face Space request and record exact source, Space revision, rollback and signed-in Android acceptance separately.

## Unfinished capabilities
This tier does not claim to create files beyond 1,000,000 bytes, private/third-party repository writes, Git LFS, direct automatic writes from model-generated prose, or arbitrary GitHub repository mutations. The AI can prepare a request and user can supply/approve exact bytes; model-generated source drafting for an underspecified task is a separate inference-and-review capability.
