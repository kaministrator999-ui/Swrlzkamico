# §wyrlz Programming LALM Runtime Architecture — TARGET STATE + IMPLEMENTATION TRUTH

**Role:** canonical specification for how §wyrlz's architecture curriculum becomes executable programming behavior while preserving one primary cognitive authority.

**Current implementation state:** **Phase 1 runtime scaffolded and live-hydrated** through LALM `2.1.80` / R39 `v68`. The programming classifier/context compiler is deterministically exercised in the active lineage and startup warm is live verified. Repository/tool execution, full architecture acceptance, coder-model delegation, and model training remain separate later states. A full authenticated post-v68 user programming turn still awaits direct generation-camera evidence.

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

## 3. Phase 1 implementation — v66 preserved through v68

R39 `v66` introduced the first executable programming runtime scaffold. v67 repaired its inherited source lineage, and v68 repaired an inherited namespace boundary required by conversation-state/context-focus and programming routing. The current active authority is LALM `2.1.80`, revision `2.1.80-hot-v67-latest-user-namespace-repair-v68`.

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

When programming mode is active, the runtime adds a bounded system-context marker to a **copy of the generation payload history**. It does not rewrite canonical persisted conversation history.

For an existing-project change, the marker directs the primary LALM to:

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

### D. Permission boundary

Programming mode is cognitive routing only. It does **not** grant permission to write files, invoke tools, deploy, spend money/credits, bypass server policy, or bypass user approval requirements.

Operational authority remains with the server/tool layer and the project's explicit approval contracts.

### E. Programming camera

Active programming turns emit bounded `programming-mode` camera facts such as project context, change class, architecture depth, inheritance state, architecture-reconciliation requirement, diagnostic/coaching flags, tool-evidence requirement, and implementation-truth state.

The event does not intentionally log prompt/response text or private chain-of-thought.

### F. Deterministic routing self-test

The inherited programming suite covers seven generalized behavior classes:

1. non-programming question stays out of programming mode;
2. code explanation remains lightweight;
3. existing-project feature requires architecture reconciliation/evidence;
4. existing-project bug activates diagnostic behavior;
5. simple new webpage uses lightweight project coaching;
6. cross-cutting migration gets deep architecture treatment;
7. conversational `let's do this` correctly inherits the prior coding task.

Production v68 status reports this suite **7/7**. This is a routing/scaffold evaluation, not yet the full Phase 2 architecture-acceptance suite.

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
runtime_hot/r39_engine.py
```

### v67 lineage repair

v67 corrected a typo in the pinned v65 → v61 source commit. That restored the intended source chain but did not by itself restore every historical bare-global name expected by later wrappers.

### v68 namespace repair

The canonical `_latest_user_text` helper already belongs to the v17 implementation loaded as `_impl`. Later conversation-state/context-focus code still references the historical bare-global name. v68 therefore bridges:

```text
_latest_user_text = _impl._latest_user_text
```

This is compatibility plumbing, not a second parser. The canonical semantic owner remains `_impl._latest_user_text`.

v68 fails hydration closed if that owner is unavailable and runs a three-part namespace self-test over:

- canonical latest-user-text extraction;
- inherited conversation-state compilation;
- programming-task classification.

This prevents the exact class of defect from remaining latent until a user turn.

### Activation truth

Current state:

- **source complete:** yes;
- **runtime scaffolded:** yes;
- **live worker hydration:** yes;
- **live startup warm:** yes;
- **namespace self-test:** `3/3` live;
- **conversation acceptance:** `9/9` live status;
- **context-focus acceptance:** `5/5` live status;
- **programming routing acceptance:** `7/7` live status;
- **tool-integrated:** no;
- **full deterministic architecture acceptance:** no;
- **authenticated post-v68 programming generation directly observed:** not yet;
- **learned/trained:** no.

Production `/api/lalm/status` reports `hotServerVersion=2.1.80`, the v68 revision, `oneTokenReady=true`, and `interactiveReady=true`. A fresh production `/api/server/status` reports `lalm-startup-warm.ready=true` and `phase=server-start-complete`. Hot-load cameras independently show the canonical namespace bridge and conversation/programming probes passing.

No authenticated production Chat request has yet emitted a `v68-enter` generation camera after activation. The Chat POST boundary requires its private browser/admin credential; verification must not bypass that authority. Therefore this document distinguishes **live runtime/startup verification** from **full end-to-end user-turn verification**.

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

Phase 1 intentionally establishes the cognitive/routing foundation before those mechanisms are layered on top.

---

## 6. When programming architecture activates

### Lightweight coding

Examples: explain syntax, write a standalone function, show an algorithm.

Use lightweight programming reasoning. Do not force a repo architecture scan.

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

**Status: runtime scaffolded and live-hydrated through LALM 2.1.80 / R39 v68.**

Implemented coding-task routing, new/existing/lightweight context, architecture depth, programming continuation inheritance, bounded programming context injection, proportional new-project policy, diagnostic policy, cameras, and routing self-tests. v68 additionally hardens inherited namespace activation so conversation/programming state is exercised at hydration rather than failing on the first user turn.

**Remaining Phase 1 acceptance:** observe a normal authenticated post-v68 programming generation and confirm `v68-enter` + `programming-mode` + terminal generation evidence without namespace exceptions.

### Phase 2 — obligation + architecture acceptance

**Next capability target after the remaining end-to-end Phase 1 acceptance.**

Add programming obligation tracking, repository-evidence/overlap state, integration decisions, completion requirements, and a generalized architecture acceptance suite.

### Phase 3 — repository/tool execution loop

Connect LALM planning to repository search/read/write/test/log operations through server authority while preserving deployment/permission gates.

### Phase 4 — richer user-project adaptation

Expand project-scale/risk detection and architecture coaching into structured adaptive state/evaluation.

### Phase 5 — optional coder specialist

Benchmark whether a specialized coding model materially improves quality, latency, or local resource usage. Add only as a subordinate specialist if measured benefits justify the complexity.

### Phase 6 — training/fine-tuning if justified

After enough high-quality generalized traces/evals exist, consider training/fine-tuning the programming behavior. Do not train first and define the architecture afterward.
