# §wyrlz Adaptive Task Effort — v182 isolated candidate

**Status:** EXPERIMENTAL; OFF BY DEFAULT. Not deployed; no trained model weights.

## Purpose
Recognize task scale independently of prompt length:
- Tier 1 INSTANT: greeting/atomic low-risk request
- Tier 2 FOCUSED: isolated explanation, transformation or small code edit
- Tier 3 STRUCTURED: research, diagnosis, preservation and targeted tests
- Tier 4 DEEP: cross-module, persistent state, auth or other impactful boundaries
- Tier 5 CRITICAL: production/destructive operations or live migrations

Tiers are advisory. Original user intent, ownership, test evidence, tool permissions and approvals remain separately authoritative.

## Implementation
- hf_space/task_effort.py is a pure, deterministic first-hop classifier with bounded reason codes, tier, verification, priority and authorization hints; it does not perform or permit actions.
- hf_space/model_router.py performs existing Brain programming-intent evaluation first. Only SWRLZ_ADAPTIVE_EFFORT=1/true/yes enables the additional plan event and model-payload hint; default is OFF.
- hf_space/qwen_coder_engine.py and hf_space/lfm2_700m_engine.py optionally append one bounded effort policy to the model system context; repair context assembly preserves it.
- No extra GGUF/model calls; no changes to token budgets, model choice, online retrieval, source acceptance, user-approved release or existing repair evaluator.
- hf_space/station.py preserves bounded plan metadata in the active session camera/status, excluding raw prompts, private profile content and credentials.
- No operational queue changes. Workstation short/simple-first scheduling with aging/anti-starvation remains a future separately-owned change.

## Evaluation
- test_task_effort_v182.py: 20 seed scenarios and uppercase/whitespace metamorphic checks.
- test_task_effort_adversarial_v182.py: 37 risk/scope floor-ceiling cases. First classifier missed 21; corrected local copy passed all 37.
- test_task_effort_routing_v182.py: stubbed on/off, coder-routing and payload/privileged-action invariants.
- verify-task-effort-v182.yml: syntax and isolated offline tests only. No model downloads, secrets or deployment.

PUBLIC FIXTURE PASS is **not** an unbiased accuracy measure or evidence of improved Qwen/700M output. These heuristics can misclassify implicit dependencies, follow-ups and novel wording.

## Promotion gates
1. Terminal successful exact-SHA isolated CI and existing project programming/Chat/online/music regression gates.
2. No behavior changes or overhead when feature flag OFF.
3. Independent unseen workload benchmark, high-consequence false-negative weight, output correctness, response length/cost, tool usage, latency and context truncation.
4. Actual hosted Qwen coder and 700M requests, corrections and verified output receipts, including songs, API signatures, multi-file integration and failure repair.
5. User-authorized guarded Hugging Face deployment with recorded source/revision/rollback, then new live verification.
6. Weight adaptation only after a separate model-specific train/held-out/evaluator/provenance procedure; documents and runtime hints do not change weights.

## Next maturity increments (NOT IMPLEMENTED HERE)
- Replan after architecture discovery from actual source files, dependency edges, independent subtasks and observed failure receipts, without hiding original requirements.
- Station/Workstation priority arbitration: low-cost tasks first when feasible, with aging so expensive jobs cannot starve.
- Bounded tool selection and independently validated two-gate acceptance: technical validity AND original intent/negative-constraint validity.
- Explicit measurement of unchanged repair attempts, regression-causing attempts and false confidence.
- Train/evaluate Qwen, LFM2-700M and future specialists as separate models; never claim any one model can handle every request flawlessly.

**Truth boundary:** complexity classification is not completed work; source tests are not production behavior; shorter answers are not better when they omit requested content.
