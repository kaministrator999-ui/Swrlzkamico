# §C existing-project coding output limit: bounded continuation (2026-11-13)

## Reported regression

User's existing single-file HTML page received a follow-up instruction, "Now improve the page". The live §C reply failed with `Generation failed: OUTPUT_TOKEN_LIMIT` after the earlier 16,384-token context / 8,192-token page-output expansion. This is **generation output exhaustion**, distinct from the earlier 4,944-input-versus-3,968-available context failure.

## Root cause

The live source `qwen_coder_engine.py` used `_swrlz_code_candidate_preview` to stream provisional code until the native finish reason was `length`, then used the existing candidate validation/retry gate. A code segment with `finishReason=length` is rightly rejected by `completion_validation`; however, a valid project edit that simply needed more generation tokens could be discarded rather than being resumed from its existing prefix.

## Minimal production change

- Target: `kamiloki/Swyrlz` Hugging Face Space, **one production file changed**: `qwen_coder_engine.py`.
- Space source before: `15adc2c14b74bc95de7b48f075d387fe0e1fbac6`.
- Space source after: `68690bdc3fea79684ef1d5228381025e063102d3`.
- Native 9B model, weight hashes, 16 effective cores, 18 decode/batch threads, 16K KV context, account data, project files, profile and §E remained unchanged.
- Existing project edits are recognized by source under edit, artifact continuation/edit metadata, or a grounded previous assistant code fence. New-project requests and casual chat retain their original behavior.

For eligible existing-project code, if native generation ends with `length`, the engine holds the existing candidate bytes and requests only the missing suffix with a compact tail-based continuation prompt. This avoids reinserting all 16K of original context on every segment. Exact suffix/prefix overlap is removed conservatively. Up to four model generation segments can contribute to one candidate: the initial reserved output allowance plus at most three 4,096-token extensions, bounded individually by the same existing KV window. The current provisional-code pane updates throughout the attempt. No provisional data is persisted as completed output.

**Validation is not relaxed.** The last native segment must end normally and the assembled candidate must still pass the unchanged structural and language/source-preservation checks. A candidate that still ends with `length` after all bounded segments remains `REJECT`; final acceptance is never fabricated. Existing attempts/retries, stopping, and failures still apply.

## Evidence and release receipts

- Read-only preflight: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43530851001
  - Python AST/source anchors checked.
  - Four deterministic generator checks covered output limit without continuation, successful segment assembly, repeated-suffix handling, and exhaustion after four segments. The final native `stop` requirement was preserved.
- Live guarded deployment: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43531005689
  - Exact prior `qwen_coder_engine.py` stored as an Actions artifact with SHA-256 before editing. Publish used parent-commit verification; exact-source rollback available if acceptance failed.
  - Live source SHA verified. Resident Qwen3.5-9B confirmed ready with 16 CPU quota and 18 threads.
  - Anonymous production HTML test: terminal `COMPLETE`, draft first visible at **39.08 seconds**, final accepted output at **120.81 seconds**, 3,252 HTML characters, complete HTML present.
  - Release kept source revision `68690bdc3fea79684ef1d5228381025e063102d3`.

## Verification scope

The **forced output-limit continuation branch** was exercised with deterministic model doubles, not by a naturally length-stopped real model during the live HTML acceptance run. The production HTML acceptance validated normal coding behavior and draft/final streaming after the code change. The user's exact preexisting HTML thread was not read or recreated. A real-world retry of that thread is still needed to verify the originally failing long continuation and any output-quality differences.

## Next engineering rung

For long-lived projects, a source-backed file/revision store and per-file patch/test protocol remain higher-value than endlessly expanding the context window. The current fix lets a single project edit span multiple output segments; it does not establish automatic persistence of arbitrary project work beyond §C's existing chat/project services.
