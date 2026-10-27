# Runtime capacity observations

**Deployment status (2026-10-27):** the implementation described here is in deployed source `f925e2012ed7ece820e3272700bc6619846c2085`. Runtime/model acceptance remains scoped by [the current checkpoint](entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md); dated preparation claims below are historical.

`GET /api/hf/runtime-capacity` reports a small, read-only snapshot of the visible cgroup v2 memory and CPU controller values. It does not load a model, retrieve account data, create a session or change runtime configuration. Responses use `Cache-Control: no-store`.

The response schema is `swrlz-runtime-capacity-v1`. Memory includes `limitBytes`, `currentBytes` and `peakBytes`, with a state for each: `measured`, `unlimited` or `unavailable`. Only the limit can be `unlimited`; usage remains a measured number or unknown. CPU includes `quotaMicros`, `periodMicros`, `limitCores` and `state`; fractional CPU limits are quota divided by period. `max` means the visible controller does not set a limit, not that physical capacity is infinite. Unknown or malformed values become `null` with `unavailable` state. Top-level `source` is `cgroup-v2` when at least one value is observed, otherwise `unavailable`.

The helper reads only `memory.max`, `memory.current`, `memory.peak` and `cpu.max`, at most 512 bytes each. Parser input and output are bounded. Missing files, permission errors, malformed values and non-ASCII data do not expose error details. No environment variables, process names, host paths, credentials, model paths, account identifiers or user data appear in the response.

These observations describe the visible controller scope. They do not measure host RAM, GPU/VRAM, hidden ancestor constraints, future peaks or memory needed by a proposed model. Individual counters are read sequentially rather than as an atomic snapshot. A current-memory value is not a model-fit or safe-headroom verdict. Model selection, weight identity, context/output budgets and paid hardware settings remain unchanged.

This endpoint supports evidence gathering before the owner's proposed larger-model choice. Actual hosted capacity remains unknown until this source is deployed and the live endpoint is queried. Local parser/HTTP tests do not establish Hugging Face capacity or approve a larger default.

Verification: `python hf_space/test_runtime_capacity.py` covers numeric/fractional limits, `max`, zero usage, malformed and missing input, partial observations, bounded file reads, the narrow public HTTP shape, no account/model access, no session cookie and GET-only behavior. The helper's parser is pure; generated code and model weights are not executed by these tests.
