# v263: GitHub file rename implementation

Scope: Rename one existing file in the selected connected GitHub repository. This release uses a Git tree update and one commit rather than separate create/delete commits.

Safeguards:
- Use signed-in Google account, connected GitHub OAuth and verified repository role.
- Require user review of source and destination and explicit confirmation.
- Reject destinations that already exist, missing source files and outdated branch revisions.
- Preserve original Git blob SHA and mode (no file re-upload).
- Verify the new branch commit, absence of the original path and matching destination blob.
- Respect workflow path permissions. Directory renames and unrelated repository mutations remain unavailable.

Validation: Python engine/HTTP and Node Chat/UI regression tests. Deployment via existing Hugging Face guarded request.

Mobile acceptance remains required: make a permitted rename, confirm one commit with preserved blob SHA and source-path removal.
