# §wyrlz Model Academy v4 — Evidence Changes the Difficulty

**Status:** TEACHING MATERIAL AND UNGRADED PUBLIC PRACTICE. Not model-weight training, actual hosted-model evaluation, active runtime context or a production release.

Prerequisites: [Project stack](PROJECT_STACK_ARCHITECTURE_V1.md), [language bridge](CROSS_LANGUAGE_CURRICULUM_V2.md), and [model maturity v3](MODEL_MATURITY_EFFORT_V3.md). The canonical Programming LALM Runtime Architecture remains policy owner. The v183 experimental source is reviewed separately as a stacked draft under [v182 PR #56](https://github.com/kaministrator999-ui/Swrlzkamico/pull/56).

## The core progression

Simple-first should mean the model begins cheaply, not that it refuses to recognize new complexity.

~~~text
USER GOAL
   → first-hop effort guess (prompt + canonical intent)
   → inspect evidence only as the task requires
   → verified files, owners, dependencies, failing tests, risks
   → escalate effort if actual evidence proves hidden difficulty
   → preserve original requested outcome and negative constraints
   → choose correct work/verification depth
   → independently check results and report evidence gaps
~~~

A one-line bug becomes deep when it affects persistent user state across several components. A ten-paragraph explanation can remain low-risk if it needs no tool, mutation or fresh source evidence. The model must update effort on new **trusted evidence**, not on user insistence or another model's confident assertion.

## Two separate authorities

**Brain** owns what a task means, original requirements, coding-intent semantics and a bounded *advisory* effort label. It does not own repository writes, scheduler ordering or production approval.

**Station/Workstation** owns operational acceptance, resource allocation, task lifecycle, cancellation, and trusted-source collection. The experimental v183 replan helper is a pure Python function: it neither collects real source files itself nor authenticates them. A future Workstation integration must establish that trust independently; do not set trusted=True from client/model JSON.

Independent compiler, runtime, browser, tests and release receipts—not the model's prose—establish technical completion. User-intent completeness is a distinct second gate.

## Evidence matters more than impressive explanations

Three paired examples:

- **Small:** Fix a function's typo. Source inspection confirms one local file, no dependent contracts. Continue focused, with a small relevant check; no mandatory 20-step task graph.
- **Hidden risk:** Fix a function's typo. Inspection reveals two component owners, five dependency edges and an authentication boundary. Escalate to deep, trace the actual API contract and verify end-to-end behavior.
- **Critical:** Ship a one-line change that deletes persisted user records. Escalate to critical; ask for proper authorization, rollback/data preservation plan and independent acceptance. The number of lines is irrelevant.

Unknown sources are not evidence that no dependencies exist. Say what remains unverified instead of guessing confidence or inventing a test result.

## Fast-and-fair scheduling

Effort classification and scheduling are not the same operation. When Workstation capacity permits, inexpensive independent ready work can move before long expensive jobs. **Aging and anti-starvation** must guarantee that large jobs eventually start. Queue design must consider GPU/CPU resource limits, user fairness, task ownership, cancellation, and deliberate approval pauses.

The v183 code does not implement or activate a queue. The priority hint is advisory; do not pretend processing order changed.

## Correctly measuring actual model progress

Evaluate Qwen2.5-Coder and LFM2-700M independently, with a matched **same-model/same-checkpoint/same-request** baseline versus candidate experiment. Before calling an improvement real:

1. Record exact request and correction, model/checkpoint revision, prompt/policy revision, and actual output hash.
2. Preserve independent test and original-user-intent evaluations. Neither compilation alone nor model self-ratings suffice.
3. Capture whether evidence is verified; absent test/response records stay UNSCORED, not FAIL and not PASS.
4. Compare correctness, regression rate, response completeness, tool calls, token/time cost, and high-risk misclassifications.
5. Keep genuinely unseen challenges away from training. Public exercises, including [24 v4 cases](model_maturity_discovery_v4.json), cannot serve as sealed holdout benchmarks after the model studies them.
6. Only deploy after protected regression gates and explicit production authority. Merely checking a doc into GitHub cannot teach GGUF weights.

The experimental [v183 evidence-and-pairing spec](https://github.com/kaministrator999-ui/Swrlzkamico/blob/feature/task-discovery-replan-v1/hf_space/MATURITY_V183_EVIDENCE.md) gives source schemas and offline comparison commands. Its comparison program reports **self-described** grader receipts, not cryptographically proven or independently audited acceptance. A reviewer must validate receipts against actual model outputs.

## What to practice next

The 24 tasks in [model_maturity_discovery_v4.json](model_maturity_discovery_v4.json) cover local fixes, impact graphs, auth/persistence, destructive operation boundaries, untrusted source labels, false types, queue fairness, two-gate completion, and independent evaluation. They are marked NOT_RUN to prevent classroom prompts being mistaken for measured Qwen/700M output.

Teach model decision-making, not arbitrary keyword associations:

- The right amount of work can change *upward* after discovery.
- Complex work must eventually complete, not be starved by endless trivial work.
- User corrections preserve original untouched constraints.
- A failed independent test is evidence; an explanation of success is not a passing result.
- A model can propose a plan, but cannot award itself tool permission or a release authorization.

**Long-term target:** verified capability and useful completions per compute unit, not maximum generated words or unsupported promises of handling every request.
