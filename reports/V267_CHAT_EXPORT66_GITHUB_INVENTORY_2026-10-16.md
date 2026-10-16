# v267 — Chat export (66): filename clarification, source-versus-inventory and mobile display

Date: 2026-10-16. Owner evidence: six mobile screenshots and **only the most recent** conversation of 44 in `swrlz-dragon-chat (66).json`.

## Observed failure and true boundaries

- `What files are in the GitHub repo` and `What are the files in the repo` returned the full source-analysis prose, despite the immediate user intent being a file inventory.
- `Can you locate the test file in the repo`, `The test.txt file`, and `The testing.txt file` fell into `PROGRAMMING_INTENT / CODER_AUTO_ROUTE`, re-emitted the same report and unnecessarily spent 16–17 seconds generating unrelated code.
- GitHub evidence itself was valid: `kaministrator999-ui/Swrlzing-core`, `main`, source `a03a600eab16fc653a3c8b8184e803feccf9b66a`, six unique files with five inspected UTF-8 source entries. The sixth is not silently claimed to have been inspected.
- Exact `test.txt` and `Testing.txt` are **different requested filenames**. Never manufacture a match; the existing verified unique-filename resolver must determine existence and case. No repository file was changed.

## Scoped source changes

1. `hf_space/github_read_inference_v235.py`: verified root directory is a valid context even when its path is empty; simple repo-file questions select recursive inventory, descriptive test-file location selects path search, and bare exact nominal filenames select read-only file lookup. General chatter and GitHub write intent remain excluded.
2. `hf_space/github_connection.py`: direct read-only inventory/search/file intents are handled before generic source-specialist/coder inference, still under authenticated GitHub read permissions; recursive inventory context is retained only when actual branch/repository/revision match the provider and current read access.
3. `hf_space/station.py`: latest thread context is passed into the file-intent classifier before programming fallback, without changing mutation capability or owner approvals.
4. `chat/§wyrlz/index.html`: compact, mobile-friendly source-report / recursive / directory inventory card, true file links to revision-bound GitHub paths, inspected-vs-total coverage, provenance expanded only on request. Raw report is retained for Copy/export and available under a reversible details panel; paths are validated before link construction. No changed behavior to the code and lyric panels.
5. New regression `tests/test_github_inventory_mobile_v267.mjs` and scoped `hf_space/test_github_read_inference_v235.py` expectations are included in `.github/workflows/hf-candidate-validation.yml`.

## Recorded failures, CI and release truth

- Initial CI passed old suites but **did not execute** new v267 tests. The action was updated to run them.
- A follow-up CI then exposed an overescaped Python regex in the read-only dispatch; repaired on the same narrow branch, retaining the failed CI receipt.
- [PR #199](https://github.com/kaministrator999-ui/Swrlzkamico/pull/199) merged at `8222c5976b87b61d70b19d4c655b5c0819479065`. This merge has the **exact** CI candidate tree `15bd0257e40cfdad6847dffe3ea28fb205fb50ba` of `974dd776c23ed11774046527199ea5ed359dd25a`.
- [HF Candidate Offline Validation #38952006721](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38952006721): SUCCESS, including the new v267 tests. [Mobile Lyric Integrity #38952006690](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38952006690): SUCCESS.
- A guarded existing-Space release and signed-in Android acceptance must be separately checked. No production change is presumed solely from source/CI.

## Terminal guarded release
- Existing `kamiloki/Swyrlz` Space [guarded workflow #38952283104](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38952283104): **COMPLETED/SUCCESS**.
- Approved source `8222c5976b87b61d70b19d4c655b5c0819479065`; merged/validated Git tree `15bd0257e40cfdad6847dffe3ea28fb205fb50ba`.
- Previous Space revision `281e412110f766f50904c1400056651b95262f21` retained in predeploy reference artifact `12068479516` and rollback checkpoint `12068719344`.
- Published Space revision `e85674b2ba536abc75c9a52d3c7050cc6c6dcf6a`; immutable release checkpoint `12069252636`.
- Runtime registry reconciled to Repository Work `1.0.206`; Server Runtime `2.3.418`; Web Chat `1.5.149`; no unrelated versions changed.
- **Truth:** SOURCE + scoped offline CI + guarded publication verified. **DEPLOYED_UNVERIFIED** for signed-in Android file listing and filename conversation behavior. A real on-device visual test remains needed; no GitHub write was performed.
