# v224 — §wyrlz mobile GitHub nested folder navigation

**Date:** 2026-10-12. **State:** exact source CI PASS; guarded production Chat Space release PASS; runtime lineage CAS verified. Signed-in Android browser acceptance still pending.

## User-driven issue
The user requested the complete collapsible mobile repository explorer and persistent in-thread GitHub questions, then asked to continue. Review of the freshly published v223 source found a concrete mismatch: its JavaScript parser required a leading slash on all `GitHub directory:` headings, while the actual server emits relative paths for subfolders (`docs`, `hf_space`, `docs/engineering`). This meant opening a subdirectory via a Chat command could fall back to raw Markdown instead of the interactive viewer.

## Correction
Exact published v223 `45cbeb928f9064025907f84213ac43931242fd70` → v224 `2873e1a161d0a79b0156e22fbbda3b02a4f2a451`, [PR #128](https://github.com/kaministrator999-ui/Swrlzkamico/pull/128) draft. `chat/§wyrlz/assets/github-explorer-v223.js` now recognizes both `/` and validated relative folder names, rejects unsafe path segments and malformed lines, and exposes its pure parser for deterministic tests. New `tests/test_github_directory_parser_v224.mjs` tests root, one-level and deeper nested paths, Unicode names, partial responses and invalid headings. Three CI definitions were updated to enforce this test.

## Exact verification
- [GitHub account #38309058077](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38309058077): SUCCESS.
- [HF Candidate Offline #38309089420](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38309089420): SUCCESS.
- [Mobile Integrity #38309089352](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38309089352): SUCCESS.
All source checks ran at exact commit `2873e1a161d0a79b0156e22fbbda3b02a4f2a451`.

## Existing Space publication
The governed `kamiloki/Swyrlz` request was committed at `b6caa1f85b63132370de00949de7062b7591a07f`; [HF deployment #38309288881](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38309288881) SUCCESS. New Space revision `3a841e1f996e695e94c085ae8a4ffb3be1d51589`; rollback `f21de3bf1f56090b3db343c9347561f49ba415a9`. Checkpoint artifacts: release `11773493630`, rollback `11773348933`, prior snapshot `11773259267`. Release receipt `DEPLOYED_UNVERIFIED`, `knownGood=false`.

Runtime `1ecfd399709c950a2c0df7761f2f7b7a093adb63`: Repository Work **1.0.165**, Server Runtime **2.3.377**, Web Chat **1.5.111**. Read-only GitHub Stage 1 remains mandatory; model weights, LALM Engine and dedicated §E engine are unchanged.

## Real acceptance remaining
Authenticate to the existing Chat Space with Google and linked GitHub, open root, then `docs`, then `docs/engineering`, check cards remain interactive. Inspect source snippets, sortable metadata, commit-history dates, and in-thread follow-ups. Check a write command remains denied. Automation does not prove actual signed-in mobile behavior. Avoid announcing live UI success without that session evidence.
