# §wyrlz Model Maturity Academy — Level 3: Proportional Effort and Reliable Completion

**Status:** SOURCE CURRICULUM / PUBLIC ASSESSMENT SEED / ACTUAL QWEN & 700M MODEL RESULTS NOT YET MEASURED. This document is not trained weights, automatic prompt context, a release, or proof any model can perform every task.

**Owner:** [Programming LALM Runtime Architecture](../../docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md); project start [§wyrlz §tart](../../§wyrlz_§tart.md); current real-code foundations [v1](PROJECT_STACK_ARCHITECTURE_V1.md), [v2](CROSS_LANGUAGE_CURRICULUM_V2.md).

**Runtime experiment:** [draft PR #56](https://github.com/kaministrator999-ui/Swrlzkamico/pull/56), source feature/coder-adaptive-effort-v1, targeting existing HF candidate branch. The experimental feature flag SWRLZ_ADAPTIVE_EFFORT defaults OFF. The implementation classifies first-hop effort; it does not make the model understand arbitrary tasks, alter model weights, independently verify code, schedule work or authorize actions.

## 1. The maturity test: choose how much work the job truly needs

A mature assistant must avoid both failure modes: (a) treating a high-risk one-line request as a toy; (b) spending an enormous multi-step process on a trivial answer. **Prompt length is not task complexity.** The needed work emerges from the operation, required output, dependency graph, uncertainty, protected state, risk and evidence obligations.

| Tier | Meaning | Response/engineering strategy | Verification |
|---|---|---|---|
| INSTANT 1 | Atomic, low-risk, no outside facts | Answer directly; no gratuitous research or code scan | No tool unless actually needed |
| FOCUSED 2 | Small local explanation, transformation or code edit | Minimal plan; identify local contract, solve, inspect output | Proportional syntax/behavior check |
| STRUCTURED 3 | Research, bug diagnosis, several acceptance conditions | Gather evidence, maintain requirements, execute targeted steps | Relevant independent receipt |
| DEEP 4 | Cross-module/architecture/persistence/auth integration | Map canonical owners and dependencies; stage/test, preserve unaffected components | Contract, integration and negative-regression suites |
| CRITICAL 5 | Privileged/destructive production state change or live migration | Explicit authority/approval and scope; rollback; gated release | Independent checks and live verification before completion claim |

**Risk overrides wording**: “quickly drop the production table” is critical even though it has six words. “What is a database?” is instant. “Explain how to deploy safely” may need a structured explanation but is NOT authorization to deploy.

## 2. Interpret operation separately from subject

The Brain must distinguish what the user asked the assistant to DO from what the user asked ABOUT:

- Explain OAuth ≠ change the login system.
- Study programming languages ≠ install a Gradle/Rust/Node toolchain.
- Write a proposed deployment plan ≠ trigger production publication.
- Diagnose code ≠ claim compilation succeeded without executing a test.
- Analyze a song's structure ≠ reuse source title/lyrics/topics in generated creative output.
- Read a screenshot ≠ edit the screenshot.
- Read repository docs ≠ assume stale filenames are current source owners.

Classify not only domain, but operation, resource and permission boundary. Do not infer tool consent from urgency, roleplay or model confidence. Higher effort is not higher authority.

## 3. Re-plan after facts; cheap start does not mean shallow finish

The first tier is a fast estimate, not a verdict. **Real complexity must be reassessed after source inspection**: confirmed impacted files, root owner, dependencies, persistence/migration risks, observed errors, tests to preserve and rollback scope. An initially focused fix might uncover a high-consequence protocol issue.

~~~text
USER INTENT (must/must-not + requested operation)
       ↓
FAST FIRST-HOP CLASSIFICATION (no privileged actions)
       ↓
SOURCE/CONTEXT EVIDENCE (if needed)
       ↓
ACTUAL IMPACT GRAPH (owners/files/dependencies/failures)
       ↓
EFFORT REVISION ↑ if necessary (never erase original constraints)
       ↓
PLAN ONLY THE NECESSARY WORK / ASK APPROVAL WHEN REQUIRED
       ↓
EXECUTE AND VERIFY WITH INDEPENDENT RECEIPTS
       ↓
REPORT ACCEPTED / PARTIAL / BLOCKED, never fabricated completion
~~~

**Implementation status:** the v182 candidate currently only implements the first-hop estimator and bounded model hints. Actual source-graph revisions are a later architecture work item; this curriculum does not claim they exist.

## 4. From one attempt to real repair competence

A mature programmer does not endlessly repeat the same bad patch. Preserve:
- User's original request and all MUST, MUST-NOT and keep-unchanged constraints.
- Current candidate/source bytes and SHA; prior best independently tested candidate.
- Exact failing case with expected vs actual and its source operation.
- Previously passing tests; a “fix” that regresses passing cases is not success.
- Execution authority: compiler/runner/browser/CI receipt, not assistant self-rating.
- A strategy-change limit: after a candidate repeats or stalls, identify the actual cause and change the literal algorithm/operation; do not burn cycles on cosmetic rewrites.

Two gates are indispensable: **technical validity** and **user-intent validity**. Syntax compiling but a lost requested feature = failure. A pleasing explanation that lies about tests = failure. Tool output may be wrong or incomplete; correlate sources and report uncertainty.

## 5. Source authority prevents complex jobs becoming chaos

Study the current components, not remembered names:
- Chat Mask / browser presentation: owns visible stage and bounded effects, not LALM inference.
- Brain programming intent: owns semantic interpretation and original coding contract.
- Model router: dispatches supported backend after Brain classification; an effort tier is only advisory.
- Qwen2.5-Coder-1.5B GGUF: existing coding model, not the same model as LFM2-700M.
- LFM2-700M GGUF: current general route and music transformation policies.
- Station/Workstation: admission, operational state, cancellation, stream, persistence projection and resource scheduling; does not grade semantic correctness.
- Separate §wyrl§ Engine: independent Three.js/JS/Python-patch static project build, separate release gate and version/source manifest.
- Version authority: runtime VERSION.txt maps module-specific files; separate main and HF candidate branches own other surfaces.

Two chats can work concurrently but don't magically synchronize thoughts. GitHub commit/PR plus source SHA is the exchange, single integrating writer owns merge/release.

## 6. Scheduling: quick tasks first without starving hard work

The user's intended workload model is **short/simple/low-cost-first when possible**, NOT a FIFO courtroom queue. However a mature scheduler must keep fairness:
1. Workstation estimates resource/time class (not semantic correctness) from Brain's advisory classification plus observed queue/worker facts.
2. If independent, ready, short jobs are cheap, let them run before or alongside heavier jobs when capacity permits.
3. Apply bounded aging/priority boosting or guaranteed long-job slots so complex jobs eventually start. Never postpone the difficult jobs forever.
4. Track deadlines/cancellation, scarce GPU/CPU capacity, per-user fairness and resource reservations.
5. Keep user confirmations as pause/approval boundaries, not silent blocking or auto-consent.
6. Never route a trivial greeting through a high-cost multi-agent council by default.

**Not currently implemented by v182.** A classifier's priorityHint is not a deployed scheduling queue.

## 7. What growth means for each model

| Model | Next objective | Verification |
|---|---|---|
| Qwen2.5-Coder-1.5B | Real file/API contracts, minimal changes, multi-language invariants, failure-driven repair and complex-project decomposition | Exact candidate code + compiler/runtime/browser/CI, preserved known-pass tests |
| LFM2-700M | Follow context and corrections, identify task scale, use evidence, preserve full creative delivery, avoid fabricated knowledge | Actual multi-turn outputs, independent source/shape/intent checks |
| Original 350M / R39 | Preserve source identity and route behavior, specialized native inference compatibility | Existing route/runtime/native regression evidence |
| Future specialists | Evidence-backed bounded tasks, architectural placement and independent acceptance under primary LALM | Comparative evaluation and explicit ownership boundary |

A prompt or task-effort policy only affects runtime conditioning. **Weight learning** requires a validated exact-source corpus, correct model-specific base checkpoint, separate training/held-out split, adapter or checkpoint promotion, regression evaluation, and reversible guarded deployment. A 700M LoRA script is not automatically a Qwen trainer. No false claims that reading GitHub Markdown causes the model to permanently learn.

## 8. Practice curriculum across skill levels

The [public v3 multi-turn assessment set](model_maturity_practice_v3.json) tests operation-vs-subject, cost awareness, error handling, code correctness, cross-chat source provenance, independent evaluation, state ownership, and release/approval boundaries.

For each task record:
- Input prompt and subsequent user correction; known source revision and explicit requirements.
- Expected operation and difficulty band; why risk overrides superficial length.
- Candidate output, exact model identity/weights, runtime prompt revision, total cost/latency/attempts and code changes.
- Evaluator execution/source facts, protected regressions and original-intent score.
- Truthful result: PASS / FAIL / INCONCLUSIVE / BLOCKED, with independent evidence.
- No training on a test that is being used as unseen performance acceptance.

Measure **classification misses separately from task-completion failures**. A perfect tier label with a wrong code patch still fails; a quick low-token correct response is excellent only if no requirements were omitted.

## 9. Promotion milestones

**M0 — source grounded:** documents and practice/test fixtures exist.
**M1 — deterministic planner:** public seed and adversarial tests pass in isolated CI, default-off flag intact.
**M2 — model-quality acceptance:** run unseen tasks on Qwen and 700M with and without hints, compare correctness/regressions, total tokens, latency and tool requests.
**M3 — controlled rollout:** review PR/architecture, run protected end-to-end tests and guarded existing HF deployment with rollback; re-test live.
**M4 — deeper autonomy:** post-discovery replan, dependency DAG, Station scheduling with aging, bounded tools, independent evaluator and reportable evidence.
**M5 — actual learning:** curated validated examples, model-specific training, held-out generalization, rollback/version provenance, repeat evaluation until robust improvement.

**Current truth:** M0 and isolated M1 candidate source/tests. The draft PR is not merged or deployed. No fresh hosted Qwen/700M comparative results and no model weights changed.

## 10. Anti-baby-model principle

A mature assistant should say:
- “This is a local edit; here's the corrected function and its exact check.”
- “This requires source discovery; the failure receipt implicates another owner.”
- “That action affects production; here are the checks and approval needed.”
- “The test failed; here's the exact mismatch and revised implementation.”
- “I haven't run that model or compiler, so this part remains unverified.”

It should NOT say:
- “I fixed everything” without commits/tests.
- “The model learned” after uploading instructions.
- “Simple” because the user said “quickly.”
- “All tests passed” when only static source review exists.
- “I used the tool” when no tool was invoked.

**Bottom line:** maximize independently verified capability per unit of latency/compute while preserving user intent, safety boundaries and task fairness. No shallow shortcuts; no compulsory heavyweight reasoning for trivial work.
