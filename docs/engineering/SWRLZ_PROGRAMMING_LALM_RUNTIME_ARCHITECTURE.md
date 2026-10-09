## Validated learning promotion pipeline

Runtime prompting and model learning are separate layers. The 700M must not rewrite its own weights from unverified conversation output.

The governed growth path is:

```text
coding task + canonical intent
→ student candidate
→ deterministic structural checks
→ independent compiler/runtime/test/browser evidence
→ accepted corrected candidate
→ normalized training example
→ held-out regression suite
→ LoRA/fine-tune candidate
→ independent regression comparison
→ promote model checkpoint only if acceptance improves without protected regressions
```

Only independently validated examples may enter the promoted training corpus. Generation completion, self-review, user praise, or an explanation that claims a fix are not sufficient labels. Failed candidates remain useful as contrastive/repair examples only when paired with the exact failure evidence and a separately validated corrected target.

Each promoted example should preserve: canonical contract ID, source/candidate lineage, original request, compact requirements, candidate revision, failure/evaluator evidence, corrected target, language/runtime, and acceptance results. Training data must exclude secrets, credentials, unrelated personal profile material, and bulky conversational prose that is not necessary to teach the programming relationship.

The runtime should prefer compact structured state over repeated policy prose. Weight training is a separate release event: changing prompts/contracts does not mean the 700M weights learned. A trained checkpoint/adapter must have its own provenance, dataset revision, evaluation receipt, and rollback path before it can replace the current model route.

# §wyrlz Programming LALM Runtime Architecture — TARGET STATE + IMPLEMENTATION TRUTH

**Role:** canonical specification for how §wyrlz's architecture curriculum becomes executable programming behavior while preserving one primary cognitive authority.

**Current implementation state:** **LALM `2.1.148` / v123 extends the live-verified v122 programming-repair lineage with a shared bounded response-cognition layer for ordinary and coding turns. Current-turn scope/grammar remains authoritative; deterministic metadata classifies standalone/topic-reset/continuation/correction/expansion/selection/confirmation/decline/creative-delegation/return-to-prior relationships plus response operation/detail/count/preserve constraints. v117-v122 programming repair, external-receipt, behavior-ledger, and execution-truth gates remain unchanged and authoritative. Static v123 verification covers broad conversational continuations plus the complete v117-v122 regression stack; live v123 activation is established only after guarded HF deployment and runtime acceptance. Historical lineage sections below remain useful archaeology and do not override the current module authority.**

---

### Response cognition — v123

v123 adds one shared Brain-owned response relationship compiler consumed by the HF 700M general-response engine and the Qwen coder response engine. It does not create a second semantic authority.

The classifier converts the current prompt + bounded canonical history into compact state describing:
- turn relationship (standalone/topic reset/continuation/correction/expansion/selection/confirmation/decline/creative delegation/return);
- requested operation;
- explicit-reference and nearest-turn anchor indices;
- compact/normal/expanded detail request;
- exact requested item count when stated numerically;
- output-only and preserve/do-not-change constraints.

Model-facing policy then applies relation-specific behavior: continue without restarting, correct by delta, expand without repeating, bind selections to the newest compatible option set, respect declines, choose delegated creative details, return to explicitly named prior subjects, and drop old constraints on explicit topic reset.

This layer improves conversational coherence while preserving the existing truth boundary: history supports the present request but never outranks it; programming intent remains the coding owner; external compiler/test/runtime receipts remain the behavioral authority for repairs.

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
  ├─ canonical conversation history
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
- **v73** preserved v72 and repaired the inherited v55 n-gram sampler's missing NumPy global at the exact 2→3 generated-token transition;
- **v74** preserves v73 inference/sampling and repairs proportional continuation routing for references to a recent coding artifact such as `that code`.

Current LALM authority is `2.1.86`, revision `2.1.86-hot-programming-artifact-continuation-v74`.

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
source = current-turn / conversation-bridge / conversation-artifact-bridge
inherited
artifactContinuation
implementationTruth = runtime-scaffolded
```

This metadata routes cognition; it does not replace semantic reasoning.

### B. Conversational programming inheritance

Short continuation turns such as `keep going`, `go ahead`, or `let's do this` may inherit programming mode from the nearest relevant user task. The bridge is conservative: it examines a bounded recent user window, stops at newer substantive unrelated work, honors explicit stop/cancel language, and represents inherited state as bounded metadata rather than copied hidden reasoning.

v74 extends this with **artifact-aware inheritance**. Deictic follow-ups such as `that code`, `this script`, or `the previous function` may anchor to the nearest recent assistant code artifact and its preceding programming task. A standalone artifact stays standalone/lightweight unless the user explicitly introduces an existing project/repository.

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

It logs no prompt, response body, secret, or hidden reasoning and leaves candidate events unchanged. v72 is a diagnostic layer, not another semantic repair owner. Later layers preserve it so any lower failure that survives remains diagnosable.

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

Authenticated request `web:mu621xd9:9391101464251047456` then crossed the former failure threshold, decoded 134 tokens / 509 characters through at least decode step 128, and completed runnable Python plus the requested explanation with zero completion gaps. v73 is therefore live/user-turn verified.

### I. Programming-artifact continuation routing — v74

The next same-thread request asked to `add a error catch to that code`. Canonical history unexpectedly arrived empty, so the older classifier had no code artifact and promoted the phrase `error catch` into existing-project/fix semantics. That triggered architecture reconciliation/tool evidence, prevented v69 lightweight compaction, and inflated the rendered prompt to 3,599 tokens before the function timed out during prefill.

v74 repairs the Brain-owned half without changing v73 generation/sampling:

- recognizes bounded code referents such as `that code`, `this script`, and `the previous function`;
- locates the nearest recent assistant code artifact and preceding programming task from supplied canonical history;
- inherits prior `projectContext` rather than inventing a project;
- keeps a standalone artifact `projectContext=none` / `architectureDepth=lightweight`;
- treats adding error handling as feature/hardening rather than proof of an existing broken project;
- preserves true `fix/debug/repair` semantics when explicitly requested;
- preserves explicit repository/project language as existing-project work.

v74's five-case hydration self-test is production verified and the hot entry reports LALM `2.1.86`. End-to-end deictic continuation still requires canonical history delivery from the Server.

### J. Canonical-history delivery + runtime-hot Server history policy — Server 2.3.256–2.3.257

The same failed continuation exposed the Server-owned half: the deployed stable writer used legacy Redis sorted-set names such as `messages`, while the canonical reader enumerated `message_index`. Durable messages existed but history reconstruction returned zero.

Server 2.3.256 added a bundled compatibility reader on `main` that merges current and legacy message indexes. Server 2.3.257 generalizes that read policy behind a **runtime-hot Server policy ABI** while preserving stable Server authority:

```text
stable auth + durable Redis records
        ↓
stable hot-loader ABI
        ↓
runtime_hot/chat_history_policy.py  (read-only)
        ↓
bounded canonical history
        ↓
v74 cognition
```

The hot policy may enumerate/filter already-authoritative Server records only. It cannot accept browser history as authority and does not own writes, authentication, turn lifecycle, or terminal commits. The stable loader validates the hot contract/self-test, re-bounds its output, and falls back to the bundled canonical reader on missing/invalid/failing runtime policy.

Runtime policy revision `1.0.0-runtime-history-compat-v1` passed six deterministic compatibility cases covering legacy recovery, order, dedupe, current-request exclusion, failed-turn exclusion, and bounded index counts. The stable loader seam is source-complete but needs one explicit production deployment. Once that seam is active, later history-policy-only improvements can ship from `runtime` without another Vercel deployment/restart.

### K. Permission boundary

Programming mode and runtime history reconstruction are cognitive/read-routing facilities only. They do **not** grant permission to write files, invoke tools, deploy, spend money/credits, bypass server policy, or bypass approval requirements. Operational authority remains with the server/tool layer and project contracts.

### L. Programming cameras

Programming turns emit bounded routing facts such as project context, change class, architecture depth, inheritance state, artifact-continuation state, architecture-reconciliation requirement, diagnostics/coaching flags, tool-evidence requirement, and implementation-truth state.

v69 adds bounded context/prefill evidence; v70/v71 add reliable candidate-terminal/fence evidence; v72 adds bounded lower-failure detail; v73 emits activation evidence for the namespace repair; v74 emits artifact-continuation routing state. Server 2.3.257 adds `SWRLZ_CHAT_HISTORY_POLICY` / `SWRLZ_CHAT_HISTORY_HOT` count-only history-source evidence. These cameras intentionally avoid prompt/response text and private chain-of-thought unless an existing explicit Chat transcript camera separately owns visible user content.

### M. Deterministic routing self-tests

The inherited programming suite covers seven generalized behavior classes:

1. non-programming question stays out of programming mode;
2. code explanation remains lightweight;
3. existing-project feature requires architecture reconciliation/evidence;
4. existing-project bug activates diagnostic behavior;
5. simple new webpage uses lightweight project coaching;
6. cross-cutting migration gets deep architecture treatment;
7. conversational continuation correctly inherits the prior coding task.

The lineage reports this suite **7/7**. v74 adds five artifact-continuation cases, and the runtime-hot history policy adds six deterministic canonical-history compatibility checks. These are routing/history-policy evaluations, not the later full Phase 2 architecture-acceptance suite.

---

### N. Offline Code Truth + web/UI engineering runtime — v91

v91 turns the documented evidence-first/offline web curriculum into executable runtime prompt policy for programming turns. It is injected only when the existing programming classifier is active and is deduplicated across inherited history.

The bounded policy requires artifact-first syntax/structure, symbol/scope/type/contract, control/data/state-flow, runtime-failure, repair, and re-verification reasoning. HTML/CSS/JavaScript work additionally covers DOM wiring, layout/overflow/stacking, responsive/mobile viewport behavior, accessibility/focus, interaction state, security/performance, and chat-specific invariants such as composer clearance, pinned/code-container state preservation, streaming/final separation, auto-scroll ownership, roles/timestamps, and error/loading states.

Provider-specific current facts (for example Google, Hugging Face, OAuth, hosted SDK endpoints/scopes/versions) remain an explicit external-evidence boundary. Lack of internet does not block ordinary standalone webpage engineering; unknown provider facts must be marked unverified rather than invented.

v91 includes a hydration self-test for programming detection, single policy injection/deduplication, non-programming isolation, offline-first wording, syntax/structure + control/data/state coverage, chat UI invariants, provider boundary, and repair re-verification.

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
v74 programming-artifact continuation routing
  ↓
runtime_hot/r39_engine.py
```

Canonical-history support feeding that lineage is separately Server-owned:

```text
canonical Redis records
  ↓
Server 2.3.256 bundled legacy/current compatibility
  ↓
Server 2.3.257 stable hot-policy loader seam
  ↓
runtime_hot/chat_history_policy.py
```

### Activation truth

Current state:

- **LALM source complete:** yes, through v74;
- **runtime scaffolded:** yes;
- **live worker hydration:** verified through v74;
- **live startup/runtime readiness:** verified with v74 hot hydration;
- **authenticated programming-route entry:** yes;
- **programming routing acceptance:** `7/7` inherited;
- **v69 lightweight context compaction:** live user-turn verified;
- **v70 semantic/repair self-test:** live hydration verified;
- **v71 terminal-camera contract:** live hydration and real candidate evidence verified;
- **v72 diagnostic contract:** source/static verified and preserved;
- **v73 two-token threshold repair:** live/user-turn verified;
- **successful authenticated post-v73 runnable-code completion:** yes;
- **v74 artifact-continuation routing:** live hydration/self-test verified; authenticated fresh-thread first-hop continuation verified lightweight;
- **runtime-hot canonical-history policy:** live production verified on current + legacy indexes;
- **stable history-policy loader ABI:** production activated by the user-approved bootstrap deployment;
- **successful authenticated same-thread `that code` continuation through hot history policy:** yes for history delivery/anchor resolution; fresh-thread first-hop routing stayed lightweight, while an edit-of-edit provenance defect was exposed and superseded by v75;
- **v75 continuation provenance + runnable-edit semantic gates:** production hydrated; deterministic acceptance 5/5; fresh authenticated post-v75 user-turn acceptance pending;
- **tool-integrated programming execution:** no;
- **full deterministic architecture acceptance:** no;
- **learned/trained programming specialization:** no.

Do not bypass Chat authentication or manufacture an end-to-end success simply to close acceptance. A normal authenticated same-thread continuation after the stable loader deployment is the correct acceptance surface.

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



## Intent-grounded iterative development loop

Programming completion has two independent gates. Technical validity is necessary but not sufficient.

```text
USER INTENT
  → compile persistent intent contract
  → generate/modify candidate
  → Gate 1: build / execute / syntax-runtime validity
      FAIL → capture evidence → repair → retry
  → Gate 2: validate ORIGINAL user intent
      FAIL → identify failed requirement → repair → rebuild/retest
  → DONE only when technical validity + intent validity both pass
```

The intent contract persists across correction iterations and records explicit MUST, MUST-NOT, preservation/change-only boundaries, and acceptance evidence expectations. Every repair receives the original contract plus the newest failure evidence. A successful compile, zero exit code, or runtime start cannot by itself satisfy the request.

Repairs must not make Gate 1 pass by deleting, renaming, bypassing, or weakening the requested feature or unrelated compatibility surface. After every repair, the full original acceptance contract is rechecked alongside the newly failing case.

Ownership remains separated: the Brain/LALM reasons from the contract and produces candidates; an independent evaluator/test/tool surface supplies authoritative acceptance evidence when available; the Workstation only orchestrates routing/lifecycle/resources and carries the contract/evidence between stages.

**Current implementation tier:** the HF 700M Brain now compiles and injects a bounded persistent intent contract and applies the two-gate completion rule during generation. The Workstation carries that contract as lifecycle metadata. This tier does **not** yet provide an autonomous compiler/browser/repository tool executor or independent evaluator loop; executable receipts remain a later tool-integrated tier.


### Canonical intent ownership during repair

The original coding request owns the active intent contract for the lifetime of that repair exchange. Compiler output, stack traces, test failures, source excerpts, and later repair directions are separate evidence/delta channels and must not be reparsed as replacements for the canonical contract.

A receipt-driven repair binds three distinct inputs:

```text
CANONICAL ORIGINAL INTENT
+ PREVIOUS COMPLETE CANDIDATE
+ NEW FAILURE EVIDENCE / USER REPAIR DIRECTION
→ repaired complete candidate
→ re-check original contract + failing case
```

Diagnostic text may explain *why* Gate 1 failed, but cannot create new MUST/preserve requirements merely because a stack frame or broken source line contains words such as return, use, or pass. Repair output preserves the complete API/wrapper/signature unless the original request explicitly authorizes a fragment or interface change.

### User-returned compiler/runtime evidence bridge

Before autonomous execution tooling exists, the user can act as the external execution surface. When a user reply contains recognizable compiler, build, runtime, or test failure output after an assistant coding candidate, the Brain treats that reply as **Gate 1 failure evidence**, not as a new unrelated coding request.

The repair turn receives the failure evidence and must:
1. diagnose the concrete reported failure against the previous candidate;
2. produce corrected code, not merely explain the error;
3. preserve the original intent contract and unrelated interfaces/configuration;
4. re-check Gate 1 conceptually against the reported failure and Gate 2 against the original user requirements; and
5. avoid claiming successful execution until a real execution receipt exists.

The Workstation may carry this evidence with the job lifecycle but does not interpret or grade it. This bridge is deliberately compatible with the later independent evaluator: user-returned evidence and evaluator-returned evidence use the same conceptual repair path.


## Student → Teacher → Independent Evaluator boundary

The current 700M development loop treats the model as a **student**. Its generated answer is a candidate artifact, not an authoritative grade. Known-answer fixtures, deterministic tests, compiler/runtime/browser evidence, repository contracts, and engineering review determine whether the candidate actually passes.

Self-review remains useful: the model should trace its own work, compare it with requirements, and repair obvious misses before submission. That is **pre-submission review**, not independent acceptance. Model confidence or an explanation that says a requirement was satisfied is never, by itself, a verification receipt.

Corrections should teach reusable relationships — intent → requirements → implementation → observed behavior — rather than memorize one literal failed answer. The desired progression is:

```text
STUDENT
  → receives known-answer tasks and grounded corrections
  → learns reusable reasoning relationships
  → becomes a competent practitioner
  → may later operate as TEACHER for other agents/tasks
```

Teacher status does not collapse the evaluator boundary. A future teacher-capable LALM may explain, critique, propose tests, and teach another agent, but it must not be the sole authority grading its own work. Acceptance remains independently grounded in the strongest available evidence.

```text
PRODUCER / TEACHER
        ↓ candidate + self-review
INDEPENDENT EVALUATOR
        ↓ tests / runtime / browser / contracts / grounded review
ACCEPT / REPAIR
```

This separation is architectural, not merely pedagogical: generation/reasoning and authoritative acceptance have different owners.

### Workstation orchestration boundary

The Workstation is **not** a semantic evaluator and does not grade response content. It owns operational orchestration around a response:

```text
request accepted
→ identify/routable workload
→ queue/admit
→ select worker/engine
→ assign available compute budget
→ track start/progress/cancel/terminal lifecycle
→ receive result/stream terminal state
→ persist/project response state as owned
→ synchronize/deliver to the correct client/thread
```

The Workstation may decide **operational readiness** from transport/lifecycle facts: a job was admitted, a worker started, a stream is active, a terminal result arrived, persistence completed, cancellation occurred, or a response envelope is ready for delivery. It must not inspect semantic content and convert its own interpretation into a correctness grade.

Content correctness, pedagogical review, and acceptance belong outside Workstation scheduling. When an evaluation workflow is requested, the Workstation may route a candidate to an independent evaluator and transport the evaluator's result, but it does not become that evaluator.

```text
Brain/LALM → produces/reasons
Evaluator  → independently assesses when required
Workstation → delegates/schedules/resources/tracks/routes/delivers
Mask/Chat   → presents/synchronizes
```

Therefore response **ready** at the Workstation means operationally complete/available for its next routed stage, not semantically proven correct.

## 5A. Evidence-first code verification gate

Coding responses that analyze, debug, review, repair, or assert that code is correct MUST perform a verification pass before presenting a confident diagnosis or fix.

The gate is language-agnostic and proportional to the task. For small snippets it should be cheap; for project work it composes with architecture reconciliation and tool evidence.

Minimum verification obligations when applicable:

1. **Identifier/symbol consistency** — compare declarations, references, scope, spelling, shadowing, imports/exports, callable names, and entrypoints. An undeclared or mismatched identifier must outrank speculative style/API criticism.
2. **Syntax/API validity** — do not label valid language/library usage as erroneous without evidence. If proposing a correction, the replacement must differ materially from the alleged defect and must itself be valid.
3. **Control/data-flow trace** — follow the relevant execution path far enough to identify where failure actually occurs, including event handlers, conditionals, state mutation, return values, async boundaries, and error paths.
4. **Runtime-failure prediction** — when the code would raise/throw/fail at runtime, identify the likely concrete failure class/message when reasonably inferable (for example an undeclared JavaScript identifier causing ReferenceError).
5. **Claim-to-code alignment** — every statement such as “this works,” “this increments,” “this handler is wrong,” or “this is the main issue” must be supported by the supplied code or execution evidence. Do not describe a behavior as functioning merely because the prose pattern is familiar.
6. **Fix verification** — mentally or deterministically re-run the repaired path and confirm the proposed change addresses the identified cause without introducing a new mismatch. Avoid no-op fixes where the “corrected” code is materially identical to the original.
7. **Uncertainty discipline** — if evidence is insufficient, say what is uncertain instead of manufacturing a plausible bug.

For bug-finding requests, prefer this order:

```text
parse structure
→ build declaration/reference map
→ check syntax and API usage
→ trace the failing path
→ identify concrete defect
→ verify proposed repair
→ explain
```

For general code explanation/review requests, do not automatically claim the snippet is fully functional unless the verification pass supports that conclusion. If an obvious correctness defect is discovered while explaining code, surface it even when the user did not explicitly ask for debugging.

### Offline-first coding diagnosis contract

Programming diagnosis MUST work without internet access. External research is not a prerequisite for ordinary code correctness analysis.

Use this evidence order by default:

```text
supplied/local artifact
→ parse + symbol/scope/type/structure checks
→ control/data-flow simulation
→ local compiler/linter/test/runtime evidence when available
→ repository-local contracts/docs/examples when relevant
→ answer or repair
```

Rules:

- Treat the code/artifact under inspection as primary evidence for claims about its own behavior.
- Build lightweight internal maps of declarations/references, imports/exports, functions/callers, state mutations, branches, async boundaries, and entrypoints as proportional to the task.
- Prefer deterministic local evidence (parser/compiler/linter/tests/runtime logs) over model confidence whenever that evidence is available.
- Use repository-local documentation, dependency manifests, lockfiles, type definitions, vendored source, tests, and existing examples to resolve framework/library behavior before assuming outside lookup is necessary.
- Distinguish **artifact truth** from **external dependency truth**. The model may diagnose artifact-internal defects offline. If correctness depends on an unknown/current external API fact that cannot be established locally, mark that narrow fact unverified rather than inventing it.
- Do not weaken an otherwise supported local diagnosis merely because internet access is absent.
- Do not fabricate documentation, API signatures, versions, or runtime results.
- When no execution tool exists, perform bounded execution simulation and label runtime-specific conclusions according to the available evidence.

Internet/research capability, when added later, is an optional escalation layer for unresolved external facts; it must not replace local code reasoning or become the default first step.

## 5B. Local web/UI engineering competence profile

The programming cortex should be capable of designing, explaining, debugging, and repairing substantial HTML/CSS/JavaScript interfaces without internet access when the requested behavior depends only on browser-platform capabilities and locally supplied/project evidence.

### Core webpage construction

For local webpage work, reason across the page as a system rather than emitting visually plausible markup only:

1. **Semantic HTML and document structure** — correct hierarchy, landmarks, forms, buttons, labels, lists, headings, metadata, and native elements where appropriate.
2. **CSS layout** — normal flow, flexbox, grid, positioning, stacking contexts, overflow, intrinsic sizing, min/max constraints, viewport units, safe areas, and container behavior.
3. **Responsive design** — mobile-first constraints, narrow/wide layouts, wrapping, touch targets, keyboard appearance, dynamic viewport height, orientation changes, and content that remains reachable at zoomed or constrained sizes.
4. **Interaction/state** — event handlers, toggles, collapsible regions, menus, dialogs, tabs, selections, pinned content, editable content, state transitions, persistence boundaries, and disabled/loading/error states.
5. **DOM integrity** — IDs, selectors, references, creation/removal, event ownership, mutation ordering, focus targets, and relationships between markup and JavaScript.
6. **Accessibility** — keyboard operability, focus visibility/management, labels, semantic roles, ARIA only when needed, reduced-motion considerations, readable contrast assumptions, and screen-reader-relevant state.
7. **Visual hierarchy** — spacing, typography, density, grouping, emphasis, component consistency, readable code/content, and deliberate rather than accidental decoration.
8. **Robustness** — long text, long code lines, empty states, large histories, repeated components, resizing, scrolling, overflow, missing optional data, and malformed/user-generated content.
9. **Performance** — avoid unnecessary DOM churn, duplicate listeners, unbounded expensive work on scroll/input, layout thrashing, and gratuitous animation work.
10. **Security boundaries** — distinguish text from trusted HTML, avoid unsafe injection patterns, validate/sanitize untrusted content at appropriate boundaries, and do not expose secrets in client code.

### Chat-interface specialization

When designing chat interfaces, explicitly model these interacting regions and invariants when applicable:

- application shell/header/navigation;
- scrollable conversation viewport;
- user/assistant/system/tool role presentation;
- message content and markdown/code rendering;
- code containers with wrapping/horizontal-scroll/copy behavior;
- pinned content that may expand/collapse without resetting unrelated state;
- composer whose collapsed/expanded height changes the usable conversation viewport;
- bottom clearance so the last message remains fully readable above the composer;
- auto-scroll behavior that does not fight a user who intentionally scrolled upward;
- streaming/generating/status presentation without duplicating finalized content;
- timestamps and message metadata;
- loading, retry, error, empty, disconnected, and disabled states;
- mobile keyboard, safe-area, touch, and dynamic viewport behavior;
- preservation of component state across ordinary scrolling/re-rendering.

A visually attractive first render is not sufficient acceptance. The model should mentally test layout and interaction invariants across representative states such as: short/long messages, code blocks, pinned expanded/collapsed, composer expanded/collapsed, narrow viewport, long conversation, streaming response, error state, and user scrolled away from bottom.

### Webpage generation verification loop

Prefer this offline loop for generated pages:

```text
extract requirements + invariants
→ design component/region structure
→ generate HTML/CSS/JS
→ validate syntax/DOM references
→ trace interactions and state transitions
→ inspect layout/scroll/overflow constraints
→ inspect responsive + accessibility behavior
→ inspect security/performance hazards
→ repair defects
→ re-run relevant invariants
→ return the page/code
```

Do not equate syntactically valid HTML with a correct interface. Conversely, do not invent defects merely to appear thorough; findings must be supported by code, browser-platform rules, local project contracts, or execution evidence.

### External-service boundary

Separate ordinary browser/UI engineering from provider-specific integration. Google APIs, Hugging Face services, OAuth providers, hosted SDKs, rapidly changing third-party frameworks, and similar external systems may require current authoritative documentation or locally pinned provider contracts.

Without verified external evidence, the model may still design the integration boundary, UI states, adapters, configuration shape, mock implementation, and failure handling, but MUST label uncertain provider-specific endpoints, scopes, SDK calls, authentication requirements, quotas, or version behavior as unverified rather than inventing them.

External lookup is therefore an escalation for **provider truth**, not a prerequisite for designing a strong standalone webpage.

### Web/UI regression curriculum

Deterministic evaluation should grow beyond identifier mistakes and include small and project-scale cases for:

- invalid and valid syntax discrimination;
- broken DOM selector/reference wiring;
- malformed HTML structure;
- CSS overflow/clipping and stacking-context defects;
- fixed/sticky/composer overlap with scrollable content;
- state reset caused by re-render/reconstruction;
- duplicate event listeners;
- incorrect toggle/collapse behavior;
- async loading/streaming state bugs;
- mobile viewport and keyboard-sensitive layout;
- inaccessible interactive elements/focus traps;
- unsafe HTML injection;
- responsive layout breakpoints and long-content stress;
- no-op fixes and fabricated bugs;
- valid pages containing no planted defect, where acceptance requires not hallucinating one.

Evaluation examples should vary names, structure, styling, framework/no-framework form, and defect location so the model learns transferable web-engineering behavior rather than memorizing one chat page or one coding pattern.

### Regression class: fabricated-bug / missed-symbol defect

The deterministic programming evaluation suite should include adversarial small snippets where:

- one identifier is declared under one name and referenced under another;
- the surrounding event/API usage is valid;
- the prompt may initially ask only for explanation, then later ask to find the error;
- a poor model can easily hallucinate an API misuse while missing the actual symbol defect.

Acceptance requires the model to identify the concrete symbol mismatch, avoid falsely condemning valid API usage, and avoid proposing a no-op “fix.” This regression class should be represented across multiple languages/frameworks rather than overfitting to one HTML/JavaScript example.

### Repository-grounded coder language/dependency/Chat/Forge curriculum

The first source-verified **Qwen coder project curriculum** lives at [`training/coder/PROJECT_STACK_ARCHITECTURE_V1.md`](../../training/coder/PROJECT_STACK_ARCHITECTURE_V1.md). Its [12 public practice exercises](../../training/coder/project_stack_architecture_v1.json) cover actual Python, JavaScript, HTML/CSS, C/NumPy, Three.js, JSON and build/configuration sources; Hugging Face vs root dependency boundaries; `Mask → Station → Brain/model → Station → Mask`; the separate `§wyrl§ Engine` source-manifest/patch/render/edit/save lifecycle; and GitHub concurrency, version and release isolation.

**Training truth / activation:** these are authored **reference lessons and UNGRADED evaluations**, not a new module authority, successful held-out benchmarks, a runtime prompt injection, a LoRA adapter, or changed Qwen/700M model weights. A GitHub-connected programming session may fetch and study the pack on project work; the hosted Qwen backend does **not automatically load this file**. Any future selective model-context loading must be bounded and architecture-reconciled with `hf_space/brain_programming.py` and `hf_space/qwen_coder_engine.py`, with programming-intent gating and context-budget regression. Weight training requires a separately established **coder-model** training/evaluation/provenance pipeline; the existing `training/700m/train_lora.py` is **not** a Qwen trainer.

**Source hierarchy:** this architecture document remains policy owner; the curriculum cites branch-specific actual code. The Forge router `§tart_§E.md` remains the release/engine authority, and `§wyrlz_§tart.md` remains the AI Chat/LALM startup router. Never infer live Forge v9.4 or new model competence from a source inventory.

## 6. When programming architecture activates

### Lightweight coding

Examples: explain syntax, write a standalone function, show an algorithm, or modify a recent standalone code artifact. Use lightweight programming reasoning and proportional context; do not force repository architecture scanning.

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

**Status:** core generation/routing/history foundation is live verified through v75. Runnable-code completion acceptance passed under v73; Server 2.3.257's hot history-policy seam is production active and authenticated turns proved both current-index and legacy-index recovery. v75 is live hydrated and deterministically passes multi-hop provenance + runnable-edit semantics. The remaining Phase 1 checkpoint is a fresh authenticated post-v75 continuation proving those new semantic gates on a real user turn.

### Phase 2 — obligation + architecture acceptance

**Next capability target after the remaining v75 user-turn semantic checkpoint closes.** Add programming obligation tracking, repository-evidence/overlap state, integration decisions, completion requirements, and a generalized architecture acceptance suite.

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

Do not collapse these states. A published/hydrated wrapper is not automatically a successful coding answer, a runtime-hot history policy is not live until its stable loader ABI is active, and a documented future coder boundary is not a deployed specialist model.

---

## Bottom line

**§wyrlz keeps one primary cognitive authority. LALM 2.1.87 / R39 v75 is the active programming edge: v69 proportional context is live verified; v70/v71 isolated semantic-vs-inference failure correctly; v72 preserves bounded diagnostics; v73 repaired the exact two-token NumPy namespace failure; v74 established proportional first-hop artifact continuation; and v75 preserves provenance across edit chains while adding runnable-edit semantic gates for callable names, entrypoints, and unrequested retry behavior. Server 2.3.257's read-only runtime-hot history-policy seam is production active and authenticated turns have proved both current-index and legacy-index recovery. The remaining Phase 1 checkpoint is a fresh authenticated post-v75 continuation; repository/tool execution and any future coder model remain later, explicitly separate implementation states.**