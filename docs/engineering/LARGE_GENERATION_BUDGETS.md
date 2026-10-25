# Bounded large code and document generation

Checkpoint: [editor project completion](entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md).
State: source candidate; actual long-form native/hosted behavior is recorded separately.

The owner requested substantially more response room for 700M and substantial code/document projects. Both native model engines now use a bounded 32,768-token runtime context. Shared request policy reserves output before optional history fitting:

| Request | Output allowance |
| --- | ---: |
| Ordinary conversation or code | 4,096 tokens |
| Editor or multi-file project; explicit 1,000–1,999-word response | 8,192 tokens |
| Explicit large/comprehensive code project, long document/report, at least 2,000 words or at least 5 pages | 16,384 tokens |

These are decode allowances, not required output lengths or proof of quality. The current user's concise/brief/small-fix instruction overrides a carried large-project request for prose. A complete-source edit still reserves the actual canonical source token size plus 1,024 tokens of headroom, up to 16,384. Source larger than that complete-delivery bound is rejected explicitly; concise wording cannot starve the full-file delivery. Existing narrow identity, exact-step, internal GitHub plan/candidate and lyric-shape response modes retain their special caps. Incidental mentions of a large topic do not alone request a large output. Long source explanations can use the larger tier instead of the ordinary short verified-file answer path.

Both pinned GGUF metadata headers were read directly, without executing their generated content: LFM2-700M declares `lfm2.context_length=128000`; Qwen2.5-Coder 7B declares `qwen2.context_length=131072`. The runtime 32K window stays below both declarations; this does not establish useful generation at their maximum windows. The existing 32 GiB environment memory bound is unchanged. A larger runtime window can increase KV-cache memory and prompt latency.

The mandatory current request, canonical source under repair, and latest imported source under editing remain intact. Raw imported HTML does not need a stored artifact ID to become mandatory editing context; the application still cannot invent an artifact identity or overwrite an unrelated artifact. If required input plus requested output cannot fit, the engine reports the context limit rather than silently deleting source. Optional history can be removed first. Context telemetry records `responseBudgetTier`, requested output reservation, input size and omitted optional history.

The shared delivery policy requires implemented behavior rather than pseudocode, TODO/empty handlers or comments standing in for code, unless the user explicitly requested a scaffold/pseudocode/placeholders. Large work is not silently abbreviated: if a whole scope exceeds one delivery, the model must identify the completed scope and remaining work. A stage contains complete files or a complete document section. This is a model instruction and source validation boundary, not an automatic multi-stage executor. The application packages actual persisted files, not promised future files. No automatic continuation or whole-project completion is implied.

Observed model `finish_reason=length` remains an explicit `OUTPUT_TOKEN_LIMIT` failure. A larger response tier cannot turn truncated source into a completed artifact. Existing source gates and independent runtime evaluation remain separate.

Verification: `hf_space/test_large_generation_budget.py` exercises request sizing, ordinary/short overrides, real engine-loop reservations, retained special caps, optional-history fitting, length-stop failure and raw imported-source protection. `hf_space/test_generation_completion_budget.py` preserves the earlier completion/ZIP/source-fidelity regressions with updated project/context expectations. Deterministic model doubles establish policy/control flow only; actual model output is recorded separately.

A real pinned native 700M budget trial (`native-700m-large-r1`, seed42, one CPU affinity) loaded 32K context and requested 8,192 output tokens for the explicit 1,200-word ocean-current explanation. It produced 855 tokenizer-measured output tokens, then upstream `finish_reason=stop` after 216.7s. The response was 630 words by a simple word-pattern count, so it did **not** satisfy the 1,200-word request. This proves the larger allowance reaches the real model and exceeds its former 768-token cap; it does not prove exact length compliance or improved content quality. Peak observed process RSS was about 1.6 GiB while a separate Qwen heading trial ran concurrently. The receipt preserves per-file source hashes; later literal-heading feedback changes are not retroactively tested by this non-coding smoke.
