# §wyrlz Programming LALM Runtime Architecture — TARGET STATE + IMPLEMENTATION TRUTH

**Role:** canonical specification for how §wyrlz's architecture curriculum becomes executable programming behavior while preserving one primary cognitive authority.

**Current implementation state:** **Phase 1 is runtime scaffolded, authenticated-route verified, and live-hydrated through LALM `2.1.82` / R39 `v70`.** The programming classifier/context compiler has been exercised by real authenticated Chat turns. v69 live-verified proportional lightweight-programming context compaction; v70 live-hydrates coding-terminal/repair hardening after that first compacted coding turn exposed a separate post-prefill completion defect. One successful authenticated post-v70 runnable-code turn remains the final current completion acceptance. Repository/tool execution, full architecture acceptance, coder-model delegation, and model training remain later states.

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

A future coding model may become highly specialized at patch/test/refactor generation, but it must not become a second independent authority for user intent, project architecture, deployment permission, version state, or final acceptance.

---

## 2. Hidden architecture grammar

Internally, programming work should follow this operating grammar:

```text
understand desired outcome
→ distinguish requirements from implementation assumptions
→ determine coding/project context
→ inspect existing architecture when an existing project is involved
→ identify authority + state/readers/writers/lifecycle
→ find related or competing work
→ choose reuse / extend / consolidate / migrate+retire / new structure
→ implement through the intended owner
→ verify behavior + ownership + activation truth
```

The user does **not** need to see every internal architecture map or classification. Surface the important architectural consequence when it improves understanding or affects a tradeoff.

For user-owned projects, apply the same principles proportionally rather than copying §wyrlz's internal repository structure.

---

## 3. Phase 1 implementation — v66 preserved through v70

R39 `v66` introduced the first executable programming runtime scaffold. Later lineage hardened the same owner rather than replacing it:

- **v67** repaired the pinned v65→v61 source lineage;
- **v68** repaired the inherited canonical `_latest_user_text` namespace boundary;
- **v69** compacted redundant Brain-owned policy context for standalone lightweight coding and repaired the bounded prompt-render diagnostic namespace;
- **v70** preserves v69 while hardening coding terminal/repair behavior around malformed bare opening code fences.

The current active authority is LALM `2.1.82`, revision `2.1.82-hot-coding-terminal-repair-v70`.

### A. Coding-task classifier

The active LALM compiles bounded routing state including:

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

This is routing/context metadata, not a replacement for semantic reasoning.

### B. Conversational programming inheritance

Short continuation/acceptance turns such as `keep going`, `go ahead`, or `let's do this` can inherit programming mode from the nearest relevant user task.

The bridge is conservative:

- it only looks through a bounded recent user window;
- it stops rather than tunneling through a newer substantive unrelated task;
- explicit stop/cancel language suppresses the programming continuation;
- inherited source is represented as bounded routing metadata rather than copied hidden reasoning.

### C. Programming context compiler

When programming mode is active, the runtime adds bounded system context to a **copy of the generation payload history**. It does not rewrite canonical persisted conversation history.

For an existing-project change, the context directs the primary LALM to:

- separate desired outcome from implementation assumptions;
- inspect available project/repository evidence before inventing owners or structure;
- identify current authority, relevant state, readers/writers/lifecycle, and related implementations;
- prefer **reuse → extend canonical owner → consolidate/refactor → migrate+retire → genuinely new structure**;
- avoid fabricating architecture when evidence is missing or ownership remains ambiguous.

For a new user project it directs the model to:

- choose the smallest useful structure justified by current scale/risk;
- add stronger ownership/state/tests/observability/version/deployment boundaries only when complexity warrants them;
- respect the user's explicit decision to simplify optional architecture;
- explain material tradeoffs without repeatedly pressuring the user.

For lightweight standalone coding/explanation it avoids forcing repository ceremony. For fix/debug work it directs the LALM toward **inspect evidence first → add bounded instrumentation only if needed → repair**.

### D. Proportional lightweight-programming context — v69

The first authenticated lightweight programming acceptance turn showed that the programming classifier routed correctly but the copied generation payload accumulated nine Brain-owned policy records totaling about 16.8k characters. This produced a 3,839-token prefill for a tiny standalone coding request.

v69 preserves canonical Chat dialogue while compacting only recognized §wyrlz-owned internal policies when:

```text
programming active
+ projectContext = none
+ architectureDepth = lightweight
```

It replaces that redundant stack with one bounded lightweight-programming marker. Unknown system authority is preserved, user/assistant dialogue is preserved exactly, and non-lightweight programming requests remain unchanged.

Live authenticated v69 evidence proved:

- policy records: `9 → 1`;
- internal policy characters: `16,774 → 364`;
- bounded rendered prompt: `444` tokens;
- actual inference prefill: `656` tokens rather than the earlier `3,839` baseline;
- no old bounded-render `NameError`;
- zero reconnects on the decisive test.

This is **live-verified context proportionality**, not a claim that local inference throughput itself is fast; the observed native prefill still ran around 10–11 tokens/s.

### E. Coding completion + bounded repair — v70

The decisive v69 coding turn passed prefill, then exposed a separate defect: the first candidate terminated after roughly two decode steps with only an opening Python-fence fragment. The inherited v27 requirement owner correctly detected `runnable-code` and invoked its one bounded repair, but its repair conditioning included the incomplete assistant fence and the second pass produced another opening fragment instead of runnable code.

v70 extends the **existing v27 repair owner** rather than adding another repair subsystem:

- coding responses that are empty or only a bare opening `python`/`py` fence retain `complete-code` and, when requested, `requested-explanation` completion gaps;
- if v27 repairs a `runnable-code` failure whose first candidate is only an opening Python fence, that incomplete assistant prefix is removed from repair-history conditioning;
- the repair is told to continue inside the already-visible fence, emit executable code instead of another opener, close the existing fence once, then provide the requested explanation;
- the compact v69 lightweight policy also explicitly forbids ending after only an opening language fence.

A live v70 hydration self-test established an important diagnosis: the inherited pre-v70 gap checker already returned `complete-code` + `requested-explanation` for the bare fence. Therefore the original early terminal was **not** caused by the completion-gap helper considering the fence complete. The lower terminal source remains to be classified by the next real turn.

v70 adds a bounded `coding-candidate-terminal` camera at the existing v27 first/repair candidate boundary. It records pass kind, terminal type/reason class, delta count/character count, maximum observed decode step, degeneration-guard observation, fence count/bare-fence state, and gap booleans. It does **not** log response text or hidden reasoning. A second bounded `coding-fence-repair-normalized` event records activation of the repair normalization.

### F. Permission boundary

Programming mode is cognitive routing only. It does **not** grant permission to write files, invoke tools, deploy, spend money/credits, bypass server policy, or bypass user approval requirements.

Operational authority remains with the server/tool layer and the project's explicit approval contracts.

### G. Programming cameras

Active programming turns emit bounded `programming-mode` facts such as project context, change class, architecture depth, inheritance state, architecture-reconciliation requirement, diagnostic/coaching flags, tool-evidence requirement, and implementation-truth state.

v69/v70 add bounded performance/terminal evidence for their respective ownership boundaries. These events intentionally avoid prompt/response text and private chain-of-thought.

### H. Deterministic routing self-test

The inherited programming suite covers seven generalized behavior classes:

1. non-programming question stays out of programming mode;
2. code explanation remains lightweight;
3. existing-project feature requires architecture reconciliation/evidence;
4. existing-project bug activates diagnostic behavior;
5. simple new webpage uses lightweight project coaching;
6. cross-cutting migration gets deep architecture treatment;
7. conversational `let's do this` correctly inherits the prior coding task.

The active lineage still reports this suite **7/7**. This is a routing/scaffold evaluation, not the later full Phase 2 architecture-acceptance suite.

---

## 4. Runtime lineage and activation

Current published lineage relevant to programming mode:

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
v69 lightweight-programming context compaction + bounded render repair
  ↓
v70 coding-terminal + v27 bounded-repair hardening
  ↓
runtime_hot/r39_engine.py
```

### v68 namespace repair

The canonical `_latest_user_text` helper belongs to the v17 implementation loaded as `_impl`. v68 bridges the historical bare name directly to that owner; it does not create another parser.

### v69 context/render repair

v69 compacts only recognized internal policies for standalone lightweight coding, restores the bounded render counter's canonical model accessor, and keeps the legacy raw prompt-token trace retired.

### v70 terminal/repair hardening

v70 preserves the v69 lineage and extends dynamic completion/repair boundaries already owned by the inherited generator and v27 repair layer. It adds fail-closed hydration checks for the required inherited contracts and bounded terminal classification for the remaining early-terminal question.

### Activation truth

Current state:

- **source complete:** yes, through v70;
- **runtime scaffolded:** yes;
- **live worker hydration:** yes, through v70;
- **live startup/runtime readiness:** yes;
- **authenticated programming-route entry:** yes;
- **programming routing acceptance:** `7/7` inherited and active;
- **v69 lightweight context compaction:** live user-turn verified;
- **v70 coding-terminal deterministic self-test:** live hydration verified;
- **successful authenticated post-v70 runnable-code completion:** pending;
- **tool-integrated programming execution:** no;
- **full deterministic architecture acceptance:** no;
- **learned/trained programming specialization:** no.

Production `/api/lalm/status` reports `hotServerVersion=2.1.82`, revision `2.1.82-hot-coding-terminal-repair-v70`, `oneTokenReady=true`, `interactiveReady=true`, v69 preservation/compaction flags, v70 coding-terminal/repair flags, and a fully green v70 self-test.

The next normal authenticated lightweight coding turn is the correct final acceptance surface for v70. Do not bypass Chat auth or manufacture a synthetic end-to-end success merely to close the checklist.

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

Phase 1 intentionally establishes the cognitive/routing/generation foundation before those mechanisms are layered on top.

---

## 6. When programming architecture activates

### Lightweight coding

Examples: explain syntax, write a standalone function, show an algorithm.

Use lightweight programming reasoning and v69 proportional context. Do not force a repository architecture scan.

### Existing-project coding

Examples: feature, regression, persistence/auth change, refactor, integration.

Activate architecture reconciliation and require real project evidence before inventing ownership.

### New user project

Activate proportional architecture coaching. Start small; grow structure with responsibility and risk.

### High-impact/cross-cutting work

Use deeper architecture treatment for migrations, deployment, auth/security, persistent state, multi-module protocols, or several interacting authorities.

---

## 7. Same-model-first strategy

The next programming capabilities should continue to strengthen the **same primary LALM** before adding another model.

Why:

- one interpretation of user intent;
- one conversation/project context;
- one architecture authority;
- easier evaluation and debugging;
- less routing/resource overhead;
- no model-vs-model architecture drift.

```text
§wyrlz LALM = architect / lead engineer / conversational brain
programming mode = programming cortex
future coder model = specialist engineer
server/tools = hands + operational authority
```

---

## 8. Future coder specialist boundary

If benchmarking later justifies a dedicated coding model, the primary LALM supplies a bounded coding contract such as:

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

The specialist returns proposals/evidence such as patches, affected files, assumptions, tests, migration concerns, and possible conflicts.

It must **not** independently own user intent, conversation truth, project architecture policy, deployment permission, canonical state, version authority, final acceptance, or user-facing product decisions.

The primary LALM can reject or repair a specialist proposal that violates the architecture contract.

---

## 9. Implementation roadmap

### Phase 0 — curriculum/governance foundation

**Status: established.**

Project Start, architecture reconciliation/coaching, project-wide cameras/logs, response standard, version evolution, roadmap/release discipline.

### Phase 1 — same-LALM programming mode

**Status: runtime scaffolded and live-hydrated through LALM `2.1.82` / R39 `v70`; authenticated routing + v69 context optimization verified; final v70 coding-completion acceptance pending.**

Implemented coding-task routing, new/existing/lightweight context, architecture depth, programming continuation inheritance, bounded programming context injection, proportional new-project policy, diagnostic policy, cameras, and routing self-tests. v68 hardened inherited namespace activation. v69 made lightweight programming context proportional and live-proved the compaction path. v70 hardens the existing coding completion/repair path and adds the missing bounded terminal-source camera.

**Remaining Phase 1 acceptance:** run a normal authenticated standalone coding request under v70 and verify terminal behavior. Success means runnable code + requested explanation complete. If a candidate still terminates early, the v70 terminal camera must classify the lower source and the normalized v27 repair must either recover or provide the precise next defect boundary.

### Phase 2 — obligation + architecture acceptance

**Next capability target after the remaining v70 coding-completion acceptance.**

Add programming obligation tracking, repository-evidence/overlap state, integration decisions, completion requirements, and a generalized architecture acceptance suite.

### Phase 3 — repository/tool execution loop

Connect LALM planning to repository search/read/write/test/log operations through server authority while preserving deployment/permission gates.

### Phase 4 — richer user-project adaptation

Expand project-scale/risk detection and architecture coaching into structured adaptive state/evaluation.

### Phase 5 — optional coder specialist

Benchmark whether a specialized coding model materially improves quality, latency, or local resource usage. Add only as a subordinate specialist if measured benefits justify the complexity.

### Phase 6 — training/fine-tuning if justified

After enough high-quality generalized traces/evals exist, consider training/fine-tuning the programming behavior. Do not train first and define the architecture afterward.

---

## 10. Implementation-truth ladder

Programming capability claims should use these states literally:

1. **Documented** — the desired rule/architecture exists in canonical engineering documentation.
2. **Runtime scaffolded** — executable runtime state/behavior exists, but may not yet be connected to operational tools or fully accepted.
3. **Tool-integrated** — the runtime can execute the relevant repository/tool loop through operational authority.
4. **Deterministically evaluated** — generalized acceptance cases exercise the capability reproducibly.
5. **Live verified** — production/user-turn evidence proves the relevant path actually executed successfully.
6. **Learned/trained** — the capability is materially represented in trained/fine-tuned model behavior rather than only runtime prompting/scaffolding.

Do not collapse these states. In particular, a live-hydrated wrapper is not automatically a successful end-to-end coding answer, and a documented future coder boundary is not a deployed specialist model.

---

## Bottom line

**§wyrlz keeps one primary cognitive authority. Phase 1 now reaches LALM 2.1.82 / R39 v70: authenticated programming routing is proven, v69 proportional lightweight context is live verified, and v70 is live-hydrated with deterministic coding-terminal/repair hardening. One successful authenticated post-v70 runnable-code turn remains the current completion acceptance. Phase 2 begins only after that boundary is closed; repository/tool execution and any future coder model remain later, explicitly separate implementation states.**
