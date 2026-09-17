# §wyrlz Programming LALM Runtime Architecture — TARGET STATE + IMPLEMENTATION TRUTH

**Role:** canonical specification for how §wyrlz's architecture curriculum becomes executable programming behavior while preserving one primary cognitive authority.

**Current implementation state:** **Phase 1 runtime scaffolded** in LALM `2.1.77` / R39 `v66`. Repository/tool execution, full architecture acceptance, coder-model delegation, live activation proof, and model training remain separate later states.

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

## 3. Phase 1 implementation — R39 v66

LALM `2.1.77`, revision `2.1.77-hot-programming-mode-context-v66`, introduces the first executable programming runtime scaffold.

### A. Coding-task classifier

The active LALM now compiles bounded routing state including:

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
- the inherited source is represented as bounded routing metadata rather than copied hidden reasoning.

### C. Programming context compiler

When programming mode is active, v66 adds a bounded system-context marker to a **copy of the generation payload history**. It does not rewrite canonical persisted conversation history.

The marker tells the primary LALM to apply the architecture grammar appropriate to the classified task.

For an existing-project change it instructs the model to:

- separate desired outcome from implementation assumptions;
- inspect available project/repository evidence before inventing owners or structure;
- identify current authority, relevant state, readers/writers/lifecycle, and related implementations;
- prefer **reuse → extend canonical owner → consolidate/refactor → migrate+retire → genuinely new structure**;
- avoid fabricating architecture when evidence is missing or ownership remains ambiguous.

For a new user project it instructs the model to:

- choose the smallest useful structure justified by current scale/risk;
- add stronger ownership/state/tests/observability/version/deployment boundaries only when complexity warrants them;
- respect the user's explicit decision to simplify optional architecture;
- explain material tradeoffs without repeatedly pressuring the user.

For lightweight standalone coding/explanation it explicitly avoids forcing repository ceremony.

For fix/debug work it directs the LALM toward **inspect evidence first → add bounded instrumentation only if needed → repair**.

### D. Permission boundary

Programming mode is cognitive routing only.

Its context explicitly does **not** grant permission to:

- write files;
- invoke tools;
- deploy;
- spend money/credits;
- bypass server policy;
- bypass user approval requirements.

Operational authority remains with the server/tool layer and the project's explicit approval contracts.

### E. Programming camera

Active programming turns emit a bounded `programming-mode` camera event with routing facts such as:

- project context;
- change class;
- architecture depth;
- inheritance state;
- architecture-reconciliation requirement;
- diagnostic/coaching flags;
- tool-evidence requirement;
- implementation-truth state.

The event does not intentionally log prompt/response text or private chain-of-thought.

### F. Deterministic routing self-test

v66 includes a bounded in-engine self-test covering generalized behavior classes:

1. non-programming question stays out of programming mode;
2. code explanation remains lightweight;
3. existing-project feature requires architecture reconciliation/evidence;
4. existing-project bug activates diagnostic behavior;
5. simple new webpage uses lightweight project coaching;
6. cross-cutting migration gets deep architecture treatment;
7. conversational `let's do this` correctly inherits the prior coding task.

The source was also locally syntax-compiled before publication. This is a **routing/scaffold evaluation**, not yet the full Phase 2 architecture-acceptance suite.

---

## 4. Runtime lineage and activation

Current published lineage:

```text
R39 v65
  ↓ immutable source inheritance
R39 v66 source
  ↓
runtime_hot/r39_engine.py hot entrypoint
  ↓
runtime_hot/manifest.json revision identity
```

v66 source is published immutably through the runtime commit recorded in the Server `2.3.234` release lineage. The hot entrypoint and hot manifest both identify the v66 target/revision.

### Activation truth

Current state for this event:

- **source complete:** yes;
- **local syntax/static classifier self-test:** yes;
- **runtime scaffolded in published hot source:** yes;
- **tool-integrated:** no;
- **full deterministic architecture acceptance:** no;
- **live worker hydration verified:** not yet — the checked production log window contained no R39 hot-entry records at all;
- **learned/trained:** no.

Do not collapse these states into “fully implemented coding model.”

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

A useful mental model remains:

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

It must **not** independently own:

- user intent;
- conversation truth;
- project architecture policy;
- deployment permission;
- canonical state;
- version authority;
- final acceptance;
- user-facing product decisions.

The primary LALM can reject or repair a specialist proposal that violates the architecture contract.

---

## 9. Implementation roadmap

### Phase 0 — curriculum/governance foundation

**Status: established.**

Project Start, architecture reconciliation/coaching, project-wide cameras/logs, response standard, version evolution, roadmap/release discipline.

### Phase 1 — same-LALM programming mode

**Status: runtime scaffolded in LALM 2.1.77 / R39 v66.**

Implemented coding-task routing, new/existing/lightweight context, architecture depth, programming continuation inheritance, bounded programming context injection, proportional new-project policy, diagnostic policy, cameras, and routing self-tests.

Live activation remains separately verifiable.

### Phase 2 — obligation + architecture acceptance

**Next target.**

Add programming obligation tracking, repository-evidence/overlap state, integration decisions, completion requirements, and a generalized architecture acceptance suite.

### Phase 3 — repository/tool execution loop

Connect LALM planning to repository search/read/write/test/log operations through server authority while preserving deployment/permission gates.

### Phase 4 — richer user-project adaptation

Expand project-scale/risk detection and architecture coaching beyond the initial v66 routing prompt into structured adaptive state/evaluation.

### Phase 5 — optional coder specialist

Benchmark whether a specialized coding model materially improves quality, latency, or local resource usage. Add only as a subordinate specialist if measured benefits justify the complexity.

### Phase 6 — training/fine-tuning if justified

After enough high-quality generalized traces/evals exist, consider training/fine-tuning the programming behavior. Do not train first and define the architecture afterward.

---

## 10. Implementation-truth ladder

Use these labels literally:

**Documented** → behavior exists as curriculum/specification.  
**Runtime scaffolded** → active/published LALM source has structured routing/state/context.  
**Tool-integrated** → that state controls repository/test/log operations through server tools.  
**Deterministically evaluated** → generalized architecture acceptance suites pass.  
**Live verified** → real project work demonstrates the path executing correctly.  
**Learned/trained** → model weights were actually trained/fine-tuned for the behavior.

A later state does not erase the need to state earlier evidence precisely.

---

## Bottom line

**§wyrlz now has the first executable programming cortex inside the same primary LALM: v66 can recognize programming work, distinguish lightweight/new/existing project contexts, carry coding intent through short continuation turns, and inject the proportional architecture operating grammar into generation. It is deliberately still only `runtime scaffolded`: repository/tool execution, obligation tracking, full architecture acceptance, live hydration proof, coder-model delegation, and training remain separate future milestones. Keep the primary LALM as architect/authority; add a coder specialist later only if measured value justifies it.**
