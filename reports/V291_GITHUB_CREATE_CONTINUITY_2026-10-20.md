# v291 — GitHub creation-intent continuity and verified follow-ups

Date: 2026-10-20
Owner evidence: Chat export `swrlz-dragon-chat (89).json`, examined locally (never committed).

## Real incident
- Request: create `write-lab/created-by-swyrlz.txt` in connected `kaministrator999-ui/Swrlzing-core`, with exact owner-approved contents.
- The file already existed (from an earlier signed-in, owner-confirmed GitHub create verified by commit `fcf1087d1b58ebee786f2f2bd5890c91e793bc8d`).
- New create failed with `FILE_ALREADY_EXISTS` (proper safety outcome).
- Owner: `Name it swyrlz1 then`.
- Old router misclassified that short continuation as model text generation. The generated response claimed a GitHub rename/create despite no provider receipt.
- Follow-up question was sent to the coding model; it returned `The new file was created.` under `CANDIDATE_REJECTED`. GitHub `main` did not contain `write-lab/swyrlz1.txt`.

## Patch
- `hf_space/github_conversation_actions_v264.py`: recover an unfinished CREATE_FILE from the current thread's *server-marked* `GITHUB_CHAT_FILE_CHECK` conflict. Model assertions alone cannot establish a create or recovery.
- Recognize `Name it X then` and equivalent short corrections, retaining the requested directory, extension, and exact original bytes. Route to the existing owner-bound, no-overwrite `create.prepare`, followed by separate affirmative approval, commit, and provider readback.
- A later verified CREATE_FILE receipt or explicit cancellation ends recovery; an independent existing-file rename does not silently replace the unfinished create.
- A question about whether the claimed creation happened checks the live selected repository's exact tree, reports absence or presence with attribution limits, and never treats a model claim as commit evidence.
- `hf_space/station.py`: route these same-thread continuations and questions through the GitHub action handler *before* generic inference. Different account/thread history cannot silently authorize a write.
- `hf_space/test_github_create_continuity_v291.py`: owner-incident regression cases, invalid path, session isolation, explicit rename/new create distinctness, unverified claim checking, and trusted receipt test.
- `.github/workflows/hf-candidate-validation.yml`: mandatory regression suite.

## Validation
- HF Candidate Offline Validation: [GitHub Actions #39505957748](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39505957748) — SUCCESS.
- Rich Chat Widgets isolated acceptance: [GitHub Actions #39505957778](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39505957778) — SUCCESS.
- Source PR: [#281](https://github.com/kaministrator999-ui/Swrlzkamico/pull/281).

## Deployment and operational acceptance
GitHub CI passing and merging source do **not** establish Hugging Face Space publication. The owner-approved guarded deployment is still required; use the existing Manual Hugging Face Space Deploy workflow with snapshot, protected approvals, and rollback. After deploying, repeat the real signed-in three-turn scenario using a unique disposable filename and verify one create only after approval, with exact content, commit, correct target path, original file untouched, and no false success for verification questions.

**State at report creation:** source PR validated, deployment not yet verified. Do not mark production or signed-in acceptance complete on CI evidence alone.
