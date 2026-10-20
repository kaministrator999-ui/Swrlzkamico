# §wyrlz Chat v289 — Selected GitHub repository readiness

This capability is part of the §wyrlz Chat server in `Swrlzkamico`. It classifies whatever repository is connected by the signed-in user's verified Google/GitHub session. It does **not** rely on the author's development repository, infer content from archives or make any GitHub edits.

## Locations

- Pure SHA-pinned classifier: `hf_space/github_repo_readiness_v289.py`
- Existing account-scoped read route: `hf_space/github_connection.py`
- Explicit natural-language classifier: `hf_space/github_read_inference_v235.py`
- Offline deterministic acceptance: `hf_space/test_github_repo_readiness_v289.py`
- Scoped CI: `.github/workflows/chat-repo-readiness-v289.yml`

## How it appears

After selecting a GitHub repository inside §wyrlz Chat:
- Ask `@GitHub readiness` or `Is my GitHub repo empty?` to receive a verified classification and immediate next actions.
- Browse root using `@GitHub files` to see the **existing native GitHub explorer**, plus a concise read-only state line; no replacement UI.
- Classification distinguishes empty, onboarding-only, archive/fixtures, test-data-only, documentation/data, source, source-with-fixtures and mixed source testbeds.
- A repository with exact marker files `docs/SCENARIO_MATRIX.md` and `write-lab/README.md` is eligible for mixed-source-testbed guidance (only after its complete Git tree verifies the files).

## Boundaries

The classifier uses **file path metadata only** from a complete, verified Git tree pinned to the authorized selected repo and branch. Source content, ZIP payloads, runtime health and CI execution are not inspected. Results make no claims about deployment, user-confirmed write permission or OAuth scope; the isolated owner-confirmed create/rename routes continue to check those separately. Root explorer remains unaffected if readiness metadata cannot be verified. No user-provided path, model output or repository text authorizes GitHub mutations.

The deliberately populated `Swrlzing-core` is a testbed, not an empty repo anymore; the genuine empty-state case is validated with synthetic zero-file trees.
