# §wyrlz Programming LALM Runtime Architecture — TARGET STATE + IMPLEMENTATION TRUTH

**Role:** canonical specification for how §wyrlz's architecture curriculum becomes executable programming behavior while preserving one primary cognitive authority.

**Current implementation state:** **Phase 1 is runtime scaffolded and authenticated-route verified; production behavior is live-proven through v71, while LALM `2.1.85` / R39 `v73` is source-complete and published with fresh-worker/user-turn activation pending.** v69 live-verified proportional lightweight-programming context compaction. v70 owns coding-terminal/repair hardening. v71 made terminal-source diagnostics collision-proof and a real authenticated turn proved both first and repair candidates were failing in lower inference after exactly two decode steps. v72 added bounded lower-failure detail diagnostics without changing response semantics. v73 repairs the source-visible inherited v55 n-gram NumPy namespace fault at that exact two-token threshold. One successful authenticated post-v73 runnable-code turn remains the current completion acceptance. Repository/tool execution, full architecture acceptance, coder-model delegation, and model training remain later states.

---

## 1. Core design decision

§wyrlz keeps **one primary LALM as the project/cognitive authority**.

```text
USER
  ↓
§WYRLZ PRIMARY LALM
  ├─ conversation + intent
  ├─ programming task routing
  ├─ architecture reasoning
  ├─ project constraints
  ├─ coding-plan ownership
  ├─ acceptance / repair reasoning
  └─ user-facing explanation
        ↓
PROGRAMMING SPECIALIZATION
  ├─ current Phase 1: same-model programming context
  └─ future optional coder model: subordinate proposal engine only
        ↓
SERVER / TOOLS
  ├─ Git/files
  ├─ tests/builds
  ├─ cameras/logs
  ├─ version authority
  └─ permitted external actions
```

A future coding model may become highly specialized at patch/test/refactor generation, but it must not become a second independent authority for user intent, conversation truth, project architecture policy, deployment permission, canonical state, version authority, final acceptance, or user-facing product decisions.

---

## 2. Hidden architecture grammar

Programming work should internally follow:

```text
understand desired outcome
→ distinguish requirements from implementation assumptions
→ determine coding/project context
→ inspect architecture when an existing project is involved
→ identify authority + state/readers/writers/lifecycle
→ find related or competing work
→ choose reuse / extend / consolidate / migrate+retire / new
→ implement through the intended owner
→ verify behavior + ownership + activation truth
```

The user does not need every internal classification. Surface architecture when it changes a tradeoff, responsibility, risk, or verification boundary.

For user-owned projects, apply this grammar proportionally rather than copying §wyrlz's internal repository structure.

---

## 3. Phase 1 implementation lineage

R39 `v66` introduced executable programming-mode routing. Later lineage hardens the same primary cognitive owner rather than replacing it:

- **v67** repaired the pinned v65→v61 source lineage;
- **v68** repaired the inherited canonical `_latest_user_text` namespace boundary;
- **v69** compacted redundant Brain-owned policy context for standalone lightweight coding and repaired bounded prompt-render diagnostics;
- **v70** preserved v69 while hardening coding completion/repair around malformed bare opening fences;
- **v71** preserved v70 response semantics while making coding-terminal camera identity collision-proof across the exec-based inherited namespace;
- **v72** preserved all response semantics and added bounded failure category / Python exception type / short sanitized detail at the first/repair candidate boundary;
- **v73** preserves v72 and repairs the inherited v55 n-gram sampler's missing NumPy global at the exact 2→3 generated-token transition.

Current source authority is LALM `2.1.85`, revision `2.1.85-hot-ngram-numpy-namespace-repair-v73`.

### A. Coding-task classifier

The active lineage compiles bounded routing state including:

```text
codingTask
projectContext = none / new / existing
changeClass = explain / create / feature / fix / refactor / migrate / deploy / review
architectureDepth = lightweight / normal / deep
architectureReconciliation
diagnostics
projectCoaching
toolEvidenceRequired
source = current-turn / conversation-bridge
inherited
implementationTruth = runtime-scaffolded
```

This metadata routes cognition; it does not replace semantic reasoning.

### B. Conversational programming inheritance

Short continuation turns such as `keep going`, `go ahead`, or `let's do this` may inherit programming mode from the nearest relevant user task. The bridge is conservative: it examines a bounded recent user window, stops at newer substantive unrelated work, honors explicit stop/cancel language, and represents inherited state as bounded metadata rather than copied hidden reasoning.

### C. Programming context compiler

Programming mode adds bounded system context to a **copy of the generation payload history**. It does not rewrite canonical persisted dialogue.

For existing-project changes it directs the LALM to inspect project evidence before inventing owners, identify state/readers/writers/lifecycle and related implementations, prefer **reuse → extend canonical owner → consolidate/refactor → migrate+retire → genuinely new structure**, and preserve ambiguity when evidence is insufficient.

For new user projects it applies proportional architecture: start with the smallest useful structure justified by current scale/risk, add stronger ownership/tests/observability/version/deployment boundaries only when warranted, and respect the user's choice to simplify optional architecture.

For lightweight standalone coding it avoids repository ceremony. For fix/debug work it follows **inspect evidence first → add bounded instrumentation only if needed → repair**.

### D. Proportional lightweight-programming context — v69

The first authenticated lightweight programming turn showed the classifier routed correctly but the copied generation payload accumulated nine Brain-owned policy records totaling about 16.8k characters, producing a 3,839-token prefill for a tiny coding request.

v69 compacts only recognized §wyrlz-owned internal policies when:

```text
programming active
+ projectContext = none
+ architectureDepth = lightweight
```

Unknown system authority and user/assistant dialogue are preserved. Non-lightweight programming requests remain unchanged.

Live authenticated evidence proved:

- policy records `9 → 1`;
- internal policy characters `16,774 → ~364–467` across the accepted tests;
- bounded rendered prompt roughly `444–466` tokens;
- actual inference prefill roughly `656–678` tokens instead of `3,839`;
- old bounded-render `NameError` removed;
- no reconnect dependency in the decisive failure tests.

This proves context proportionality, not fast raw inference; native prefill throughput remained roughly 10–11 tokens/s.

### E. Coding completion + bounded repair — v70

The compacted coding turn passed prefill but generated only an opening Python fence before failing. The inherited v27 requirement owner detected `runnable-code` and invoked its one bounded repair.

v70 extends that existing repair owner:

- empty/bare `python`/`py` fences retain `complete-code` and requested-explanation gaps;
- a repair following a bare opening Python fence removes that incomplete assistant prefix from repair-history conditioning;
- repair guidance continues inside the already-visible fence, emits executable code, closes the fence once, then supplies the requested explanation;
- lightweight programming policy explicitly forbids ending after only an opening language fence.

Hydration testing proved the pre-v70 gap checker already considered a bare opening fence incomplete, so semantic completion was not the source of the two-token terminal.

### F. Terminal-camera contract namespace — v71

v70 cameras lived in an exec-based inherited namespace and initially used generic `_CONTRACT`, which older nested layers could replace. v71 establishes unique `r39-v71-coding-terminal-camera-contract-v1`, restores it after inherited hydration, recomputes/fail-closes the v70 self-test, and preserves generation semantics.

Authenticated request `web:mu5zycye:4201205958924473599` then proved both first and repair candidates terminated:

```text
terminalType = FAILED
terminalReasonClass = inference-failed
deltaEvents = 2
deltaChars = 9
maxDecodeStep = 2
sawDegenerationGuard = false
bareOpeningFence = true
completeCodeGap = true
requestedExplanationGap = true
```

This ruled out EOS acceptance, completion-gap loss, degeneration, Chat transport, and fence-repair routing as the terminal source.

### G. Lower inference failure detail — v72

v71 intentionally collapsed the underlying base-generator exception to `inference-failed`, while the base generator already produced a bounded error category and Python exception message. v72 wraps the existing v27 candidate boundary and records only:

- terminal category;
- Python exception type;
- short sanitized detail preview.

It logs no prompt, response body, secret, or hidden reasoning and leaves candidate events unchanged. v72 is a diagnostic layer, not another semantic repair owner. v73 preserves it so any lower failure that survives remains diagnosable.

### H. Inherited n-gram NumPy namespace repair — v73

Source inspection exposed an exact causal match for the two-token failure. v55's `_ngram_guarded_sample` behaves as follows:

```text
history length 0 → delegate to prior sampler
history length 1 → delegate to prior sampler
history length 2 → enter n-gram branch → first `np.argpartition(...)`
```

v55 imported `urllib.request` and `re`, but not `numpy as np`. Because the hot lineage is assembled through nested `exec(..., globals(), globals())`, the sampler resolves that bare global dynamically and could reach a namespace without `np` exactly when attempting token three.

v73 repairs that compatibility boundary at the current edge:

- imports NumPy;
- restores `np` after the entire inherited v72 chain hydrates;
- preserves the v55 sampler as semantic owner rather than rewriting its policy;
- fail-closes if `_ngram_guarded_sample` is unavailable;
- runs a hydration self-test that calls the sampler with a two-token history, forcing the exact previously failing branch.

This is source/static verified and published. Fresh-worker hydration plus one authenticated coding completion remains required before the repair is called live verified.

### I. Permission boundary

Programming mode is cognitive routing only. It does **not** grant permission to write files, invoke tools, deploy, spend money/credits, bypass server policy, or bypass approval requirements. Operational authority remains with the server/tool layer and project contracts.

### J. Programming cameras

Programming turns emit bounded routing facts such as project context, change class, architecture depth, inheritance state, architecture-reconciliation requirement, diagnostics/coaching flags, tool-evidence requirement, and implementation-truth state.

v69 adds bounded context/prefill evidence; v70/v71 add reliable candidate-terminal/fence evidence; v72 adds bounded lower-failure detail; v73 emits activation evidence for the namespace repair. These cameras intentionally avoid prompt/response text and private chain-of-thought unless an existing explicit Chat transcript camera separately owns visible user content.

### K. Deterministic routing self-test

The inherited programming suite covers seven generalized behavior classes:

1. non-programming question stays out of programming mode;
2. code explanation remains lightweight;
3. existing-project feature requires architecture reconciliation/evidence;
4. existing-project bug activates diagnostic behavior;
5. simple new webpage uses lightweight project coaching;
6. cross-cutting migration gets deep architecture treatment;
7. conversational continuation correctly inherits the prior coding task.

The lineage reports this suite **7/7**. This is routing/scaffold evaluation, not the later full Phase 2 architecture-acceptance suite.

---

## 4. Runtime lineage and activation

Relevant programming lineage:

```text
v17 canonical engine implementation
  ↓ module-owned implementation namespace (_impl)
conversation / planning lineage
  ↓
v61 context-focus lineage
  ↓
v65 inherited namespace lineage
  ↓
v66 programming-mode scaffold
  ↓
v67 pinned-source lineage repair
  ↓
v68 canonical _latest_user_text namespace bridge
  ↓
v69 lightweight context compaction + bounded render repair
  ↓
v70 coding terminal + v27 bounded-repair hardening
  ↓
v71 coding-terminal camera-contract namespace repair
  ↓
v72 bounded coding-inference failure-detail camera
  ↓
v73 inherited v55 n-gram NumPy namespace repair
  ↓
runtime_hot/r39_engine.py
```

### Activation truth

Current state:

- **source complete:** yes, through v73;
- **runtime scaffolded:** yes;
- **live worker hydration:** verified through v71; v73 fresh-worker hydration pending;
- **live startup/runtime readiness:** previously verified through v71; v73 pending;
- **authenticated programming-route entry:** yes;
- **programming routing acceptance:** `7/7` inherited;
- **v69 lightweight context compaction:** live user-turn verified;
- **v70 semantic/repair self-test:** live hydration verified;
- **v71 terminal-camera contract:** live hydration and real candidate evidence verified;
- **v72 diagnostic contract:** source/static verified and preserved, not independently required for acceptance after source diagnosis;
- **v73 two-token threshold self-test:** source/static verified; fresh-worker execution pending;
- **successful authenticated post-v73 runnable-code completion:** pending;
- **tool-integrated programming execution:** no;
- **full deterministic architecture acceptance:** no;
- **learned/trained programming specialization:** no.

Do not bypass Chat authentication or manufacture an end-to-end success simply to close acceptance. A normal authenticated lightweight coding turn is the correct live acceptance surface.

---

## 5. What Phase 1 does not yet implement

The following remain later work:

- automatic repository architecture-radius traversal from tool evidence;
- structured authority-map compilation from actual files/routes/state;
- responsibility/synonym/readers/writers/lifecycle search planning executed through tools;
- overlap classification A-H as explicit runtime state;
- architecture integration-decision object grounded in repository evidence;
- programming obligation ledger across long coding missions;
- repository/tool action planner and patch/test loop;
- architecture-aware patch acceptance evaluator;
- full generalized architecture regression suite;
- live-verified end-to-end programming missions proving tool use + architecture acceptance;
- dedicated coder-model delegation contract in runtime;
- a separate coding model;
- coding-specific fine-tuned/trained weights.

Phase 1 establishes the cognitive/routing/generation foundation before those mechanisms are layered on top.

---

## 6. When programming architecture activates

### Lightweight coding

Examples: explain syntax, write a standalone function, show an algorithm. Use lightweight programming reasoning and proportional context; do not force repository architecture scanning.

### Existing-project coding

Examples: feature, regression, persistence/auth change, refactor, integration. Activate architecture reconciliation and require real project evidence before inventing ownership.

### New user project

Activate proportional architecture coaching. Start small and grow structure with responsibility and risk.

### High-impact/cross-cutting work

Use deeper architecture treatment for migrations, deployment, auth/security, persistent state, multi-module protocols, or several interacting authorities.

---

## 7. Same-model-first strategy

Strengthen the **same primary LALM** before adding another model because that preserves one interpretation of user intent, one conversation/project context, one architecture authority, simpler evaluation/debugging, lower routing overhead, and less model-vs-model architecture drift.

```text
§wyrlz LALM = architect / lead engineer / conversational brain
programming mode = programming cortex
future coder model = specialist engineer
server/tools = hands + operational authority
```

---

## 8. Future coder specialist boundary

If benchmarking later justifies a dedicated coding model, the primary LALM supplies a bounded contract such as:

```text
TASK
ARCHITECTURE OWNER
ALLOWED CHANGE BOUNDARY
RELEVANT SOURCE/EVIDENCE
EXPLICIT CONSTRAINTS
REQUIRED TESTS
DO-NOT-CHANGE SURFACES
OUTPUT FORMAT
```

The specialist may return patches, affected files, assumptions, tests, migration concerns, and conflicts. It must not independently own user intent, conversation truth, architecture policy, deployment permission, canonical state, version authority, final acceptance, or user-facing product decisions. The primary LALM may reject or repair specialist proposals.

---

## 9. Implementation roadmap

### Phase 0 — curriculum/governance foundation

**Status: established.** Project Start, architecture reconciliation/coaching, project-wide cameras/logs, response standard, version evolution, roadmap/release discipline.

### Phase 1 — same-LALM programming mode

**Status:** routing and proportional context are live verified; coding-terminal diagnosis reached a source-complete v73 causal repair. **Final acceptance remains one successful authenticated post-v73 runnable-code + explanation turn.**

### Phase 2 — obligation + architecture acceptance

**Next capability target only after Phase 1 coding completion acceptance.** Add programming obligation tracking, repository-evidence/overlap state, integration decisions, completion requirements, and a generalized architecture acceptance suite.

### Phase 3 — repository/tool execution loop

Connect LALM planning to repository search/read/write/test/log operations through server authority while preserving deployment/permission gates.

### Phase 4 — richer user-project adaptation

Expand project-scale/risk detection and architecture coaching into structured adaptive state/evaluation.

### Phase 5 — optional coder specialist

Benchmark whether a specialized coding model materially improves quality, latency, or local resource use. Add only as a subordinate specialist if measured benefits justify complexity.

### Phase 6 — training/fine-tuning if justified

After enough high-quality generalized traces/evals exist, consider training/fine-tuning programming behavior. Do not train first and define architecture afterward.

---

## 10. Implementation-truth ladder

Programming capability claims use these states literally:

1. **Documented** — desired rule/architecture exists in canonical engineering documentation.
2. **Runtime scaffolded** — executable runtime state/behavior exists but may not be operationally integrated or fully accepted.
3. **Tool-integrated** — runtime can execute the relevant repository/tool loop through operational authority.
4. **Deterministically evaluated** — generalized acceptance cases exercise capability reproducibly.
5. **Live verified** — production/user-turn evidence proves the relevant path executed successfully.
6. **Learned/trained** — capability is materially represented in trained/fine-tuned model behavior rather than runtime prompting/scaffolding alone.

Do not collapse these states. A published/hydrated wrapper is not automatically a successful coding answer, and a documented future coder boundary is not a deployed specialist model.

---

## Bottom line

**§wyrlz keeps one primary cognitive authority. Phase 1 currently reaches source authority LALM 2.1.85 / R39 v73: authenticated programming routing and v69 proportional context are live verified; v70/v71 isolated the coding failure below semantic repair; v72 preserves bounded lower-failure diagnostics; and v73 repairs the exact inherited v55 NumPy namespace fault that activates at the two-token history threshold. v73 still requires fresh-worker plus authenticated runnable-code acceptance before it is called live verified. Phase 2 begins only after that boundary closes; repository/tool execution and any future coder model remain later, explicitly separate implementation states.**