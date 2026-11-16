# §C non-code output budget — streamed answer preservation

Date: 2026-11-15 US Central.
Workstream: Chat/LALM generation finalization, not Forge or code-artifact acceptance.
Incident: an ordinary lyric-generation follow-up ended in `Generation failed: OUTPUTTOKENLIMIT`.

## Source evidence

The read-only live source audit (GitHub Actions run 43795941595, exact Space revision `1e6e232b281b9a87d18e7248a143ee7740c55273`) located the common engine tail in both `lfm2_700m_engine.py` and `qwen_coder_engine.py`. When the last native attempt ended with `finishReason=length`, engines emitted `FAILED/OUTPUT_TOKEN_LIMIT` even after streaming content. Station then raised on the `FAILED` event and its exception path could append a separate failure message instead of the visible assistant reply.

## Scoped change

- Preserve text that has actually been emitted for non-code answers; never emit it a second time.
- Convert length exhaustion for ordinary non-code answers to a recorded `INCOMPLETE` / `OUTPUT_LIMIT_PAUSED` / `COMPLETED(PARTIAL)` lifecycle, not a hard `FAILED`.
- A buffered candidate must pass its existing acceptance check before it can be displayed. A rejected, never-displayed buffered lyric candidate is not leaked; return a short plain-language incomplete result instead.
- Preserve `codingTask` and source-edit `OUTPUT_TOKEN_LIMIT` rejection so truncated HTML, code or unverified source artifacts are not mistakenly accepted.
- Do not claim a length-terminated answer is complete. The current change preserves text and a truthful partial state, not unlimited native generation or automatic multi-part lyric completion.
- Do not change model weights, context window, native CPU thread counts, authentication, Google account state, source-retrieval copyright gates or Forge.
- Patch exact current Hugging Face Space engine files in place with immutable source-sha and version/contents checks. Never redeploy an old repository `hf_space/` bundle over current live changes.

## Execution

The patch recipe lives at `scripts/hf_chat_noncode_output_budget_v1.py`. Tests:
`tests/test_hf_chat_noncode_output_budget_v1.py`, validated by
`.github/workflows/hf-chat-noncode-output-budget-preflight.yml`.

The existing canonical HF request chain supports a narrowly gated
`CHANGE_SCOPE=noncode-output-limit-recovery-v1`, which selects
`hotfix-output-budget` mode. The canonical reusable workflow now runs an
exact two-file source-snapshot/CAS update rather than its old full-folder
upload *only in that mode*. All other modes and default full deployments
retain their previous path. The predeploy engine snapshot is retained as a
GitHub Actions artifact. If readback mismatches and the patch revision is
still current, the repair routine restores the previous exact two file bytes.

## Verification levels

- Static/source preflight: required and automated. The live snapshot may advance, so the patch refuses to publish if its exact anchors no longer match.
- Publication: only the canonical `main:.deploy/HF_SPACE_REQUEST.txt` request can authorize the scoped production release.
- Live lyric acceptance: not proven by static tests; test a real generation with a length stop and inspect resulting saved message, status and absence of the extra `Generation failed` bubble.
- If validation or deployment fails, retain the exact failed run and source/version receipts. Do not label the change live from a code commit alone.

## Published production receipt

- GitHub source integration: [PR #431](https://github.com/kaministrator999-ui/Swrlzkamico/pull/431), merge commit `a4af52d3d2290c7efda3cd78176acb9016c4c29b`.
- Canonical authorized request: `main:.deploy/HF_SPACE_REQUEST.txt`, request commit `694dc13214c3920e99871303990dd6e9a5f5f502`, `CHANGE_SCOPE=noncode-output-limit-recovery-v1`.
- Governed Space release: [Actions run 43797780182](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43797780182), success. Source SHA and six trust-boundary unit tests verified in deploy job. Prior exact two engine files archived before upload.
- Published previous Space revision: `1e6e232b281b9a87d18e7248a143ee7740c55273`.
- New Space revision: `70e0a4fc6b179cda6f465c77b59c1eba4b36626e`, two-file byte-for-byte readback successful.
- Scope verification: original general full-Space `prepare` deploy job was skipped; only scoped two-engine fix published. No model weights, context size, original song-source evidence or native editor changes.
- Acceptance distinction: published source and unit-based length handling verified; specific user lyric thread/browser behavior under an actual limit remains to be observed. Do not claim a finished song from a length stop or automatic same-turn continuation. 
