# Chat/AI v293 — GitHub Read-Tool Planning and Model Reasoning

**Date:** 2026-10-21
**Owner request:** Analyze GitHub tooling, model reasoning, their uses, and implement improvements under the `§§§§` Chat/AI scope.
**GitHub source authority:** `integration/chat-github-read-reasoning-v293` at `e90b2f395589da8cbfb0315a5c1db9f70e2afcb4`.
**Source review:** [PR #286](https://github.com/kaministrator999-ui/Swrlzkamico/pull/286), merged after offline tests.
**Release request:** `main:.deploy/HF_SPACE_REQUEST.txt`, request commit `b17c5322fca16dca502d85687250d38cbc911261`; target existing Space `kamiloki/Swyrlz`. The request is **not** proof of completed deployment or live behavior.

## Architecture and findings

- `hf_space/github_connection.py` is the canonical Station owner for OAuth-gated GitHub tools and read execution. `github_read_inference_v235.py` owns deterministic path/context reads; `github_workflows_v212.py` owns workflow read mechanisms; `brain_programming.py` continues to own programming intent. No second GitHub agent was created.
- Stage-1 routing prevented a natural-language request for existing safe issue/PR reads from reaching the already-implemented bounded model planner. The request was incorrectly called locked, even though checked read handlers existed.
- Some model-planned numeric target validation used substring checks, potentially confusing PR/issue 7 with 17. Model output was never a valid permission grant.

## Implemented and tested

1. Stage 1 now permits authenticated, **read-only** issue, pull request, commit and workflow/run checks, besides existing file/source reads.
2. Natural-language inspection can use the existing bounded model planner when multiple checks are useful; single clear checks prefer deterministic routing to avoid needless inference.
3. Candidate tools are mapped through a strict Stage-1 category/command allowlist, then independently checked by the existing Station GitHub access gate. Unsupported model output fails closed to bounded deterministic read selection. No prompt, secrets or hidden reasoning are used as permission.
4. Model-selected issue/PR identifiers must match complete user-named numbers; partial-number matches are rejected.
5. Multi-check Chat responses finish with a **single terminal event** rather than terminating after the first check.
6. Extended `hf_space/test_github_model_progress_v211.py` with Stage-1 read, fallback, malformed-plan, target-precision, non-mutation and completion regressions; `.github/workflows/hf-candidate-validation.yml` now executes them.

**Validation receipts:** [HF Candidate Offline Validation #39629222988](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39629222988) SUCCESS; [Chat v289 Repository Readiness #39629222608](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39629222608) SUCCESS on tested head `e88b0f96126f8181ea229e883436c00a79009edd`. The merged candidate has the identical Git tree `c05d4e420602ba95b06ec18617030c97700573c2`.

## Deliberate unchanged boundaries

- Model weights/Qwen/R39 weights unchanged; this is **tool-routing reasoning**, not training or a measured general IQ gain.
- GitHub write permission, branch/issue/PR mutations, workflow dispatch, confirmation authority, OAuth scopes, secrets, account identity and source provenance stay with existing server-owned gates.
- Chat UI/frontend, Forge Engine/§e, engine Space and engine versions unchanged.
- Concurrent source/feature branches are not merged by name and cannot silently override an immutable validated source SHA.

## Remaining release truth

The guarded Chat Space request was submitted after the exact source-tree/CI check. A final GitHub request/workflow result, Hugging Face revision, live behavior and owner handset acceptance must be observed before saying **deployed/live verified**. Repository Work advancement can record this completed source/governance tier; Server Runtime changes require a confirmed actual deployed Server release. No model weights should be bumped.
