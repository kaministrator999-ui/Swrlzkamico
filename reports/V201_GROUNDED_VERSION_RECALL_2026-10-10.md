# v201 — Grounded version recall from verified Google-owned GitHub thread context

**Release status:** Source verified; account/persistence/version-recall CI SUCCESS; HF offline candidate CI SUCCESS; guarded existing Hugging Face Space publication SUCCESS. **Actual mobile v201 response and post-v201 restart persistence still require user acceptance.** No model weights were changed.

## User-observed failure
In the live v200 Chat screenshots (2026-10-10, 08:42 local), the v199 content-first renderer visibly removed the nested Response costume for the startup report and displayed a usable source version table. The same Google-owned thread then received “Can you tell me the versions again.” The model produced the right module/version topic but verbose duplicate details and wrong provenance, percent-encoded the §tart filename, called the source commit an unverified “initial commit,” and invented a separate “vending machine project” with releases by mixing in an earlier rap prompt. This is a documented *inference output* failure, not a failure to retrieve those module values.

## Architecture and implementation
- Source parent: prior guarded released v200 `feature/lyric-eight-bar-intent-validator-v200` SHA `7f4ba0e9e9ce8910cfd21ad47d8d04c2ad6eea49`.
- Isolated v201 candidate: `feature/grounded-version-recall-v201` SHA `ffb9a9777f878b911b01e2a18c003f7123b43ce2`; [draft PR #87](https://github.com/kaministrator999-ui/Swrlzkamico/pull/87) (stacked on published feature lineage, not merged to main).
- `hf_space/project_thread_memory.py`: general `short_version_recall(prompt)` discriminator and `source_version_recap(source,prompt)`. Exact short recap questions alone get a read-only Markdown table generated from safe, deduplicated module/version pairs in the *already verified* Google-scoped GitHub snapshot. No hardcoded §wyrlz version values, no invented history or reference file name, no freeform user-history mixing, no new storage or API call. Missing/invalid/unrelated snapshot falls back.
- `hf_space/station.py`: attaches recap only after verified Google-account identity and current authenticated Chat thread project snapshot.
- `hf_space/model_router.py`: yields bounded STATUS + DELTA + COMPLETED before the model for this factual-recall path; wider questions about comparison, provenance, releases, creation, explanation and coding retain ordinary inference.
- `hf_space/test_project_version_recall_v201.py`: broad positive/negative recall forms, 16-register-style values, deduplication, invalid/fake sources, no lyrical topic contamination, no fabricated initial commit, bypass-on-qualified evidence, full model fallback on complex prompts, owner-gate static assertions.
- `.github/workflows/verify-github-account-v1.yml`: branch-specific Python/owner/regression tests.
- `.github/workflows/hf-candidate-validation.yml`: branch-specific offline packaging checks.

## Verification
1. First feature-branch CI run [#38057294501](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38057294501) correctly failed on “List the module versions again”; broadened the article+module phrase grammar and reran.
2. Final exact source [GitHub Account CI #38057484069](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38057484069): SUCCESS.
3. Final exact source [HF Candidate Offline Validation #38057484008](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38057484008): SUCCESS.
4. [Guarded HF deployment request #38057588722](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38057588722): COMPLETED/SUCCESS. Existing `kamiloki/Swyrlz`, new Space revision `dfd7986e5a84bd2097342cb12003dfecc82dfc9d`, prior rollback revision `548f3868d54474c013e01ffd604f44f70b1a0829`. Exact selected source `ffb9a9777f878b911b01e2a18c003f7123b43ce2`, request nonce `2026-10-10-v201-grounded-version-recall-001`, main request commit `43ad4e66f86c752e1a06ff589104628c08de8d07`. No Vercel or replacement Space.

## Version lineage
- Repository Work **1.0.137 → 1.0.138** (runtime file commit `9b0c774abc55f76bc27cc592e6bfcd4c5d143454`)
- LALM Engine **2.1.179 → 2.1.180** (`1253d8cc18f35ef782728656f9d78f03566963d9`)
- Server Runtime **2.3.351 → 2.3.352** (`001de623320373d112312151881b25705df5ca6a`)
- Web Chat **1.5.95** unchanged; v199 mobile layout remains the published renderer; v200 lyric validation unchanged. `runtime:VERSION.txt` still owns routing.

## Pending live acceptance
In the *same authenticated Google-owned Chat thread* with a prior GitHub §tart report, refresh after v201 deployment and ask “Can you tell me the versions again?” Expect one source-bound module/version table, no source hash or invented history, no repeat, no “vending machine project”, and a short snapshot-vs-live disclaimer. Verify existing messages persist across restart and ordinary code/lyrics remain unchanged. Comparisons / introducing-commit questions should still use inference and abstain when source history has not been checked. CI verifies code path/structure only, not mobile end-to-end user experience.
