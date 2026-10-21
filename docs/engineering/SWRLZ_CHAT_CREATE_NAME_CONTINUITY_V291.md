# §wyrlz Chat v291 — GitHub create-collision filename continuity

## User-observed regression, 2026-10-20

The connected testbed `kaministrator999-ui/Swrlzing-core` had a **real verified owner-approved creation** of `write-lab/created-by-swyrlz.txt`, commit `fcf1087d1b58ebee786f2f2bd5890c91e793bc8d`, containing exactly `§wyrlz owner-approved create test`. A subsequent instruction to create that same path correctly produced `FILE_ALREADY_EXISTS`, but §wyrlz then treated the follow-up **"Name it swyrlz1 then"** as a coding request. Its generated `code.txt` and prose about an "updated GitHub repository" were **not** GitHub mutations; this is a verifiable intent-routing failure. It also left the existing file untouched.

## Implementation

Code owners: `hf_space/github_conversation_actions_v264.py` and `hf_space/station.py`. The existing Stage-1 source/read allowlist and two narrowly granted owner writes remain unchanged.

If `create.prepare` confirms `FILE_ALREADY_EXISTS`, the Chat adapter independently checks a complete authenticated Git tree for the existing path. The thread/user-scoped bounded, expiring `need-new-name` continuation holds the original **requested content**, destination directory, selected repository and branch; it cannot authorize or perform a rename, overwrite or edit. A reply such as `Name it swyrlz1 then` is explicitly routed by Station to this adapter, not to the coding model. A relative extensionless name inherits the original directory and suffix, so the *new* proposed path is `write-lab/swyrlz1.txt`. A fresh `create.prepare` verifies destination absence and write permission. A separate **Yes/No** on the new path is always required, and only `create.confirm` may mutate GitHub and return a verified commit receipt. Existing source `write-lab/created-by-swyrlz.txt` remains byte-for-byte unchanged.

If the selected repository/branch changes, original collision is no longer verifiable, or the proposed new path already exists, the adapter refuses to make the write. The continuation expires after five minutes and is consumed by an unrelated user turn; a later Yes never authorizes a stale action. These are server-process-local transient states, not a model memory claim; after a restart, a user should submit a fresh complete create request.

## Verification

`hf_space/test_github_create_name_continuity_v291.py` checks the screenshot case, exact content preservation, second collision, no write before separate Yes, one-use approval, cancellation, wrong account, changed repository and Station routing. CI also runs the existing v262 general file-create and v263 rename regression suites. No live `Swrlzing-core` files were created or renamed by these tests.

## User acceptance

In a signed-in §wyrlz Chat thread with `Swrlzing-core` selected, request a new file at an intentionally existing path using an arbitrary **known, synthetic** test payload. §wyrlz should say it already exists and ask for a new name. Respond `Name it fresh-name then`, verify the displayed **new** destination path and exact payload, then choose Yes/No separately. Inspect the resulting actual commit and check original file is unchanged.

GitHub CI and deployment are separate from signed-in Android acceptance. Do not claim that generated code artifacts, a code block or a Chat statement alone represent a GitHub write.
