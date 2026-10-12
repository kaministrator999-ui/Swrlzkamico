# v222 — Natural GitHub file reads without forcing extensions

**Status:** source and offline CI passed; guarded existing Hugging Face Space publication completed; signed-in real user acceptance unverified.

## Requested behavior
The user can ask for `config`, `app`, or a natural repo-scoped file reference without supplying an extension. Search the selected repository's complete GitHub tree at its verified default-branch commit. Read a uniquely identified file and include full path plus source SHA. If several files share the requested basename/stem across folders or extensions, list their real paths and request a selection without reading any. If the index is incomplete, do not claim uniqueness.

## Source
Exact v221 baseline `f05900407818be66e276360da427b8b0bebb461e` → v222 candidate `a2f9b8005230d9189a4a0caa36fc59b2a551647d`. [Review PR #125](https://github.com/kaministrator999-ui/Swrlzkamico/pull/125) (draft). Existing `hf_space/github_connection.py` remains the single authenticated tool router for this read-only capability, with extended `hf_space/test_github_staged_read_v221.py` fixture tests. No write escalation, model weights or private archive changes.

## Verification
[GitHub account CI #38294669968](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38294669968) and [HF offline #38294706198](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38294706198) successful. [Existing Chat Space guarded deployment #38294911145](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38294911145) successful; deployed revision `da98762c9a42ed4a70203a78320fac0b820675d9`, rollback `84f48b3a3bf1546a44c64d83d2d2fd984af6a7df`. Artifacts: release checkpoint `11767981664`, rollback `11767836673`. Receipt `DEPLOYED_UNVERIFIED`, `knownGood=false`.

## Versions and next
Runtime `ecd4a101f78d3171b7ce863636dadb8e4a0a49f4`: Repository Work **1.0.163**, Server Runtime **2.3.375**. Others unchanged. Live signed-in tests should confirm auto-matching and collision choices. GitHub writes remain blocked (Stage 1). Separate next tier only after reading accepted.
