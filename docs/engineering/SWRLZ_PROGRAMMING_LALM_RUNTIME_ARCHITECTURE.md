# §wyrlz Programming LALM Runtime Architecture — TARGET STATE + IMPLEMENTATION TRUTH

**Role:** canonical specification for how §wyrlz's architecture-reconciliation curriculum should become executable programming behavior inside the LALM/runtime over time.

**Purpose:** separate what is already documented/governed from what is actually implemented in the active LALM, define the intended coding architecture, and prevent a future coding model from becoming a second competing cognitive authority.

This document is deliberately explicit about **current implementation status**. Architecture curriculum, runtime behavior, and model specialization are different things and must not be conflated.

---

## 1. Core design decision

§wyrlz should have **one primary cognitive authority**.

The preferred architecture is:

```text
USER
  ↓
§WYRLZ PRIMARY LALM
  ├─ conversation / intent / context
  ├─ architecture reasoning
  ├─ project constraint interpretation
  ├─ coding-plan ownership
  ├─ acceptance / repair reasoning
  └─ user-facing explanation
        ↓
PROGRAMMING SPECIALIZATION
  ├─ repository discovery
  ├─ architecture-map construction
  ├─ code synthesis / patch proposal
  ├─ test generation
  ├─ refactor proposal
  └─ code-focused evaluation
        ↓
SERVER / TOOL EXECUTION
  ├─ Git/files
  ├─ tests/builds
  ├─ logs/cameras
  ├─ version authority
  └─ permitted external actions
```

The programming specialization may initially use the **same LALM/model** with a coding-specific context/compiler/tool workflow.

A dedicated coding model may be added later, but if it exists it is a **subordinate specialist**, not another project brain.

---

## 2. Why one primary LALM should remain the authority

The same system needs to understand all of these at once:

- what the user actually wants;
- what the current conversation refers to;
- what the project already contains;
- which architecture owns the change;
- which user preferences are optional vs required constraints;
- what can safely be changed;
- how the result should be explained to the user.

Splitting those responsibilities between two co-equal models would recreate the exact duplicate-authority problem the architecture curriculum is designed to prevent.

Bad target:

```text
GENERAL LALM decides architecture A
CODING MODEL independently decides architecture B
SERVER receives both
```

Preferred target:

```text
PRIMARY LALM owns task + architecture contract
        ↓
CODING SPECIALIST receives bounded coding brief
        ↓
returns patch/test/refactor proposals + evidence
        ↓
PRIMARY LALM evaluates against architecture + user intent
        ↓
SERVER executes approved/permitted operations
```

---

## 3. Current implementation truth

### Already established as engineering/curriculum contracts

The repository already defines:

- `SWRLZ_PROJECT_START.md` — project-work router/orchestrator;
- `SWRLZ_HOTFIX_RULES.md` — runtime/main mutation and deployment boundary;
- `SWRLZ_VERSION_MODULE_EVOLUTION.md` — Server/module evolution, version authority, concurrency, and release lineage;
- `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md` — architecture discovery/reconciliation method;
- `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md` — proportional architecture teaching/adaptation for user-owned projects;
- `SWRLZ_CHAT_CAMERA_LOGS.md` — automatic project-wide evidence/camera workflow;
- `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md` — readable project-work reporting;
- `SWRLZ_SERVER_ROADMAP.md` — durable release/progress memory.

These documents define the **desired engineering behavior** and provide a curriculum that can be converted into runtime/model behavior.

### Already present in the active LALM lineage

The active R39/v65 lineage includes general conversation/runtime capabilities such as:

- conversation-state/context-focus behavior inherited from v61;
- response planning and response-contract behavior;
- continuation/bridge-turn behavior;
- bounded structured cameras/loader diagnostics;
- hot-loader lineage and cold-load namespace validation.

These are useful foundations, but they are **not yet a complete programming architecture engine**.

### Not yet implemented as a dedicated executable programming subsystem

As of this specification, there is no proven dedicated runtime component that performs all of the following automatically inside R39:

- explicit coding-task mode detection;
- automatic architecture-radius traversal from repository evidence;
- authority-map compilation as structured model context;
- responsibility/synonym/readers/writers/lifecycle repository search planning;
- overlap classification A-H as a runtime state machine;
- architecture integration decision object;
- programming obligation ledger across multi-step coding work;
- coding-specific tool plan/patch loop owned by the LALM;
- architecture-aware patch acceptance evaluator;
- user-project architecture scaling decision engine;
- structured architecture teaching decision tied to project scale;
- dedicated programming/coder model delegation contract;
- dedicated coding regression/evaluation suite proving those behaviors;
- coding-specific trained/fine-tuned model weights.

Therefore these behaviors must currently be described as **documented target/curriculum**, not as fully implemented LALM runtime behavior.

---

## 4. Hidden architecture vs visible user experience

Internally, §wyrlz should use the architecture curriculum as an **operating grammar**.

The user does not need to see every authority map, search radius, lifecycle trace, or overlap classification.

Internal behavior:

```text
understand outcome
→ inspect existing architecture
→ find authority
→ trace readers/writers/lifecycle
→ classify overlap
→ choose integration path
→ implement
→ verify architecture + behavior
```

User-facing behavior:

```text
understand goal
→ propose/build a sensible structure
→ briefly explain important architecture choices when useful
→ adapt if user wants simpler structure
→ preserve correctness/source-of-truth constraints
```

The architecture may be mostly invisible when it is functioning normally, but §wyrlz should be able to explain it when the user asks or when a tradeoff matters.

---

## 5. When the programming architecture should activate

The LALM should not apply the full repository-development protocol to every mention of code.

### Lightweight coding

Examples:

- explain a syntax error;
- write a small standalone function;
- show an algorithm example;
- answer a programming concept question.

Use normal coding reasoning. No full architecture traversal is necessary unless the request affects an existing project/repository.

### Existing-project coding

Examples:

- add a feature to an application;
- fix a regression;
- change persistence/state;
- modify authentication;
- alter deployment behavior;
- add an AI/tool subsystem;
- refactor code with existing consumers.

Activate architecture reconciliation before mutation.

### New user project

Use the Architecture Coaching Guide.

Start with proportional structure, then increase architectural rigor as project complexity/risk grows.

### High-impact/cross-cutting change

Use the deepest programming workflow, including:

- ownership/authority map;
- state/readers/writers/lifecycle trace;
- tests/acceptance;
- observability;
- migration/rollback where needed;
- version/release/deployment boundaries.

---

## 6. Same-model-first strategy

The first implementation should improve the **same primary LALM** for programming rather than immediately creating another model.

Recommended first-stage components:

### A. Coding task classifier

Produces bounded facts such as:

```text
codingTask = true/false
projectContext = none/new/existing
changeClass = explain/create/fix/feature/refactor/migrate/deploy
architectureDepth = lightweight/normal/deep
```

This is routing metadata, not a replacement for semantic reasoning.

### B. Programming context compiler

Convert project evidence into compact structured context:

```text
userOutcome
explicitConstraints
canonicalOwners
affectedModules
stateAuthorities
readersWriters
lifecyclePaths
relatedExistingWork
versionAuthorities
deploymentBoundary
verificationRequirements
```

Do not dump the entire repository into the prompt.

### C. Architecture reconciliation planner

Implements the documented integration ladder:

```text
reuse
→ extend
→ consolidate/refactor
→ migrate+retire
→ new structure
```

### D. Programming obligation ledger

Track what the request requires across long coding missions:

- requested behaviors;
- explicit exclusions;
- architecture constraints;
- tests/verification;
- migration tasks;
- documentation/version/roadmap duties.

This reduces partial implementations where code is changed but verification or cleanup is forgotten.

### E. Tool/action planner

The LALM determines what evidence/actions are needed; the server executes permitted repository/test/log operations.

### F. Architecture acceptance evaluator

Before completion, verify:

- requested behavior works;
- canonical owner was used;
- no unintended duplicate writer/owner remains;
- existing behavior was not regressed;
- source/runtime activation truth is stated correctly;
- required release/version records are complete.

---

## 7. Optional future coding model

A dedicated coding model can be useful later for:

- faster local code generation;
- code-token efficiency;
- repository-scale completion;
- syntax/library specialization;
- patch generation;
- test generation;
- refactor alternatives;
- running on hardware where a smaller coding-specialized model is cheaper than the general LALM.

But the interface must preserve one cognitive authority.

### Coder specialist input

The primary LALM supplies a bounded contract such as:

```text
TASK
ARCHITECTURE OWNER
ALLOWED CHANGE BOUNDARY
CURRENT RELEVANT SOURCE
EXPLICIT CONSTRAINTS
REQUIRED TESTS
DO-NOT-CHANGE SURFACES
OUTPUT FORMAT
```

### Coder specialist output

The coding model returns proposals/evidence such as:

```text
patch proposal
files affected
assumptions
test proposal
migration concerns
possible conflicts
```

### What the coder specialist must NOT own

It must not independently own:

- user intent;
- conversation truth;
- project architecture policy;
- deployment permission;
- canonical project state;
- version authority;
- final acceptance;
- user-facing product decisions.

The primary LALM may reject or repair a coder proposal that violates the architecture contract.

---

## 8. Why not create a separate coding brain immediately

A separate coding model introduces real complexity:

- two context windows that can disagree;
- duplicated project memory;
- architecture drift between models;
- additional local RAM/VRAM/storage requirements;
- model-routing latency;
- another evaluation surface;
- harder diagnosis when the generated patch is wrong;
- risk that the coding model optimizes locally while breaking cross-project architecture.

Until the primary LALM has a stable programming contract and eval suite, a second model would make it harder to know whether failures come from architecture reasoning, delegation, prompt translation, coding quality, or tool execution.

Therefore:

> **Build the programming cognition contract in the primary LALM first. Add a coding specialist later only when measured code-generation quality/performance justifies it.**

---

## 9. User-project design behavior

When §wyrlz helps a user build something new, it should use the same underlying architecture grammar but adapt it to the project's scale.

Example progression:

```text
simple webpage
→ clear files + one state owner + basic run instructions

interactive app
→ module boundaries + API/state ownership + error visibility

persistent/deployed app
→ auth/data contracts + tests + logs + deployment boundary

large/long-lived system
→ explicit authority maps + versioning + release lineage + migrations + observability
```

The user may reject optional structure.

The LALM should explain the consequence and simplify cleanly rather than forcing §wyrlz's internal repository rules onto another project.

Architecture should be applied **when responsibility/complexity justifies it**, not merely because the request contains code.

---

## 10. Programming architecture evaluation plan

Before claiming the programming architecture is implemented, build deterministic acceptance cases covering at least:

1. existing feature under a different name is reused instead of duplicated;
2. two writers to the same state are detected;
3. stale documentation does not override current authority;
4. fallback is not treated as a second primary;
5. a small new project stays small;
6. a growing project receives stronger boundaries at the right transition;
7. user rejects optional architecture and it is removed coherently;
8. user rejects a correctness-critical constraint and the LALM explains the consequence rather than silently breaking integrity;
9. multi-part coding task completes code + tests + cleanup + version/roadmap obligations;
10. coder-specialist proposal that violates architecture is rejected;
11. ambiguous repository ownership triggers more inspection instead of invented architecture;
12. live/source mismatch is reported truthfully.

Do not use private raw transcripts as regression fixtures. Generalize behavior classes.

---

## 11. Implementation roadmap

### Phase 0 — curriculum/governance foundation

**Status: substantially established in documentation.**

Includes Project Start, architecture reconciliation, architecture coaching, cameras/logging, response reporting, version evolution, and roadmap discipline.

### Phase 1 — same-LALM programming mode

Implement coding-task routing + programming context compiler + architecture state fields inside the active LALM lineage.

### Phase 2 — obligation + architecture acceptance

Add programming obligation tracking, overlap/integration state, completion requirements, and deterministic tests.

### Phase 3 — repository/tool execution loop

Connect the LALM planning contract to repository search/read/write/test/log tools through server authority, while preserving permissions/deployment gates.

### Phase 4 — user-project architecture adaptation

Make project-scale detection and architecture coaching runtime behavior rather than documentation-only guidance.

### Phase 5 — optional coder specialist

Benchmark whether a specialized coding model materially improves quality, latency, or local resource use.

Only add it if it passes the subordinate-specialist contract and measurable evaluation.

### Phase 6 — training/fine-tuning if justified

After enough high-quality generalized programming traces/evals exist, consider model training/fine-tuning around architecture-aware programming behavior.

Do not train first and define the architecture afterward.

---

## 12. Definition of implementation truth

Do not say “the programming architecture is implemented” merely because this document exists.

Use explicit states:

### Documented

The behavior is specified in project contracts/curriculum.

### Runtime scaffolded

The active LALM has structured routing/state/context for the behavior.

### Tool-integrated

The behavior controls repository/test/log operations through the server/tool layer.

### Deterministically evaluated

Generalized acceptance suites prove the expected architecture behavior.

### Live verified

Actual project work demonstrates the architecture path executing correctly.

### Learned/trained

The model itself has been trained/fine-tuned for the behavior, rather than relying primarily on runtime instruction/context.

These states must not be collapsed into one claim.

---

## 13. Recommended model decision

**Near term:** improve the existing §wyrlz LALM for both general conversation and programming by adding a programming mode/context/compiler/evaluation layer.

**Later:** optionally add a purpose-built coding model as a subordinate specialist if benchmarks show a clear advantage.

This gives §wyrlz one coherent brain with specialized capability instead of multiple models independently deciding what the project means.

A useful mental model is:

```text
§wyrlz LALM = architect / lead engineer / conversational brain
coding specialization = programming cortex
optional coder model = specialist engineer
server/tools = hands + operational authority
```

The specialist may be extremely capable at writing code. It still works from the architecture contract supplied by the primary LALM.

---

## Bottom line

**The architecture curriculum is intended to become §wyrlz's internal programming operating grammar and also the foundation for how it designs user projects. Today that grammar is much more complete in documentation than in executable R39 programming code. Build the same primary LALM into an architecture-aware programming orchestrator first. Add a separate coding model later only as a subordinate proposal engine when measured benefits justify the extra complexity. Keep user intent, project architecture, canonical state, permissions, and final acceptance under one primary LALM authority.**