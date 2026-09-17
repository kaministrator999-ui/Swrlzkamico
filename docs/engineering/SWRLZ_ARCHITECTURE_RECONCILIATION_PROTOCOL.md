# §wyrlz Architecture Reconciliation Protocol — Programming-LALM Curriculum

**Purpose:** teach the programming-side §wyrlz LALM how to execute the mandatory Pre-Feature Architecture Reconciliation required by `SWRLZ_PROJECT_START.md`.

This document is the **execution method** for that rule. Project Start defines that architecture reconciliation MUST happen before implementation; this protocol defines how an engineering LALM discovers the affected architecture, finds the current authority, traces interacting work, detects duplicate or competing implementations, chooses an integration path, and records the result.

This protocol is not a replacement for:

- `SWRLZ_PROJECT_START.md`;
- `SWRLZ_HOTFIX_RULES.md`;
- `SWRLZ_VERSION_MODULE_EVOLUTION.md`;
- `SWRLZ_SERVER_ROADMAP.md`;
- feature-specific architecture/runbooks;
- deployment approval rules;
- module-owned version authorities.

It operates **between request understanding and implementation**.

---

## 1. Core engineering principle

A requested feature describes a desired **outcome**. It does not automatically identify the correct implementation location.

The programming LALM MUST NOT jump directly from:

```text
USER REQUEST
    ↓
NEW FILE / NEW SERVICE / NEW HOOK / NEW STATE
```

The required path is:

```text
USER REQUEST
    ↓
DESIRED OUTCOME + CONSTRAINTS
    ↓
AFFECTED ARCHITECTURE DISCOVERY
    ↓
CURRENT AUTHORITY + EXISTING WORK DISCOVERY
    ↓
DATA / CONTROL / STATE FLOW TRACE
    ↓
OVERLAP + CONFLICT CLASSIFICATION
    ↓
INTEGRATION DECISION
    ↓
VERSION / DEPLOYMENT / VERIFICATION PLAN
    ↓
IMPLEMENTATION
```

The default goal is **one coherent system with one intentional authority per responsibility**, not the maximum number of independently working layers.

---

## 2. What “architecture” means for this protocol

Architecture is not merely a directory tree or a list of classes.

For a requested change, the affected architecture may include any combination of:

- Mask/client presentation;
- Human/server operational authority;
- Brain/LALM cognition;
- modules and module boundaries;
- public routes and internal routing;
- request/response protocols;
- streaming/event contracts;
- persistent state and state ownership;
- caches and invalidation;
- loaders/hydrators/bootstrap paths;
- manifests and registries;
- authentication and authorization;
- session/account/thread identity;
- files and storage;
- tool/action execution;
- background/automation lifecycle;
- UI layout/theme/asset ownership;
- compatibility adapters;
- fallbacks and last-known-good paths;
- version authorities and update paths;
- production activation state;
- observability/camera/logging paths;
- migration and rollback behavior.

A feature can conflict with an existing feature even when the two features have completely different names. If they write the same state, control the same lifecycle, render the same region, interpret the same semantic decision, or claim the same authority, they are architecturally related.

---

## 3. Separate user intent from implementation assumptions

Before searching the repository, rewrite the request internally into two parts:

### Desired outcome

What should become true for the user/system?

Example:

```text
Outcome: a user can bookmark several assistant responses and jump back to them.
```

### Implementation assumptions

What implementation ideas are explicit requirements, and which are merely possibilities?

Example:

```text
Explicit requirement: multiple bookmarks per thread.
Possible mechanism: bookmark tray.
Not yet established: new database, new Chat state store, new LALM memory subsystem.
```

The LALM MUST avoid turning a convenient noun in the request into an architecture decision.

Examples:

- “add a manager” does not prove a new manager class is required;
- “add memory” does not prove a new persistence store is required;
- “add AI recall” does not prove Chat should become a semantic planner;
- “make a fallback” does not prove another parallel implementation should exist;
- “new page” does not prove it needs a new backend module.

First establish the outcome. Then discover the architecture that should own it.

---

## 4. The architecture-radius model

Architecture reconciliation is bounded, but it must be wide enough to find collisions.

The programming LALM should expand outward in **architecture radius** rather than either inspecting one file only or auditing the whole repository blindly.

### Radius 0 — requested outcome

Identify:

- desired behavior;
- user-visible result;
- explicit constraints;
- explicit exclusions;
- affected domain terms.

No implementation decision is made yet.

### Radius 1 — direct owner surface

Find the most likely current owner of the behavior:

- current page/component;
- API route;
- LALM planner/runtime;
- server service;
- module entrypoint;
- manifest/registry;
- state authority;
- storage adapter;
- tool/action handler.

Read the current implementation before designing an addition.

### Radius 2 — direct readers, writers, dependencies, and consumers

Trace what directly interacts with the Radius-1 owner:

- who calls it;
- what it calls;
- who reads its state;
- who writes its state;
- which events it emits/consumes;
- which UI surfaces consume it;
- which loaders/fallbacks can replace it;
- which caches mirror it;
- which version/status surfaces expose it.

This radius catches many duplicate-owner bugs.

### Radius 3 — cross-cutting authority

Inspect architecture that can override or constrain the feature:

- Mask / Human / Brain ownership;
- authentication and permissions;
- canonical persistence;
- deployment/runtime boundary;
- module version ownership;
- manifests/registries;
- compatibility layers;
- shared protocol contracts;
- update/sync mechanisms;
- feature-specific runbooks;
- roadmap/release lineage.

### Radius 4 — historical and live evidence

Expand here when ownership remains ambiguous, a regression is involved, or conflicting implementations exist.

Inspect:

- recent release records;
- relevant commits;
- retired/legacy code;
- old contracts as historical evidence;
- live production cameras/logs/status;
- fallback activation behavior;
- previous failed attempts.

Radius 4 is not automatically the source of current design authority. It helps explain how the present system arrived where it is and what is actually active.

### Stop condition for radius expansion

The LALM may stop widening when it can answer all of these confidently:

1. Which component owns the requested responsibility?
2. Which artifact is the current source of truth?
3. Who writes the relevant state?
4. Who reads/consumes it?
5. What lifecycle activates/replaces/disables it?
6. What existing work overlaps the requested outcome?
7. Which implementation path preserves a single intentional authority?
8. What version/deployment/verification boundaries apply?

If any answer remains materially uncertain, widen the radius.

---

## 5. Build an authority map, not just a file list

Finding files is not enough. The LALM should build a small working **authority map** for the feature.

Use a structure conceptually equivalent to:

| Responsibility | Plane/module | Canonical owner | State/source of truth | Writers | Readers/consumers | Lifecycle/loader | Version authority | Status |
|---|---|---|---|---|---|---|---|---|
| Example | Mask | runtime Chat module | canonical thread state | server commit path | Chat tray + LALM factual context | runtime manifest | web-chat | active |

The map does not need to be emitted to the user for every tiny edit. It exists so the programming LALM can reason about ownership before modifying code.

### One responsibility, one intentional authority

Multiple files may legitimately participate in one feature, but their roles must be distinct.

Good:

```text
server owns durable bookmark record
        ↓
Chat renders bookmark tray
        ↓
LALM receives factual bookmark references when relevant
```

Bad:

```text
Chat keeps one bookmark state
server keeps a different bookmark state
LALM keeps a third inferred bookmark state
all three claim to be current
```

The protocol does not prohibit layering. It prohibits **unreconciled competing authority**.

---

## 6. Discover current authority correctly

§wyrlz contains historical contracts and old implementation evidence. Therefore “I found a document” is not enough to establish current architecture.

The LALM must distinguish several kinds of truth.

### A. Engineering/source authority

Used to decide how new code should be integrated.

Evidence includes:

- current `SWRLZ_PROJECT_START.md`;
- current `SWRLZ_HOTFIX_RULES.md`;
- current `SWRLZ_VERSION_MODULE_EVOLUTION.md`;
- this protocol;
- current feature-specific runbook/contract when still authoritative;
- current `VERSION.txt` routing;
- current module-owned `versions/*.txt`;
- current canonical source on the owning branch;
- current manifest/registry/loader configuration.

### B. Production activation authority

Used to determine what is actually running/rendering/loaded now.

Evidence includes:

- live status APIs;
- live camera/runtime logs;
- active deployment identity;
- source/revision receipts;
- actual manifest resolution;
- rendered behavior when appropriate.

Repository authority and production activation can temporarily differ. Record that difference rather than pretending they are the same.

### C. Historical evidence

Used to explain lineage or find old competing mechanisms.

Evidence includes:

- old architecture contracts;
- superseded runbooks;
- old roadmap entries;
- retired files;
- old commits;
- previous deployment behavior.

Historical evidence MUST NOT silently outrank a newer canonical contract/source.

### Example: stale architecture contract

If an old control-plane contract says `dev` or `/tmp` is authoritative while the current Project Start/Hotfix/Roadmap and runtime sources establish `runtime` as durable authority, the LALM should conclude:

```text
old document = historical architecture evidence
current project contract/runtime = current engineering authority
```

Do not resurrect the old path merely because its documentation sounds formal.

---

## 7. Search by responsibility, not only by feature name

Feature names drift. Responsibility is more stable.

For every requested feature, search multiple evidence classes.

### Search class 1 — literal/user vocabulary

Search the terms the user used.

Useful, but insufficient.

### Search class 2 — responsibility synonyms

Example for “bookmark response”:

- bookmark;
- pin;
- saved response;
- anchor;
- jump target;
- message reference;
- response marker.

### Search class 3 — public entrypoints

Search relevant:

- route names;
- element IDs/classes;
- event names;
- API endpoints;
- exported functions;
- manifest entries;
- module names.

### Search class 4 — state and identity

Search the state that would have to exist:

- thread ID;
- message ID;
- account scope;
- storage key;
- record type;
- revision;
- cache key;
- state field;
- schema/contract name.

### Search class 5 — readers and writers

Trace both directions.

A same-named function proves little. Two differently named functions writing the same canonical field are architecturally related.

### Search class 6 — lifecycle

Search:

- bootstrap;
- mount/unmount;
- hydrate;
- load/reload;
- fallback;
- retry;
- reconnect;
- migration;
- sync;
- cleanup;
- retirement/deprecation.

### Search class 7 — release/history

Search roadmap/releases/commits for why the existing design exists and whether an apparent duplicate is intentional compatibility or technical debt.

### Search class 8 — live evidence

For production defects or activation-sensitive features, inspect live logs/status to establish which path really executed.

**No search result does not prove absence.** If the capability should logically require state, a route, a lifecycle hook, or a writer, search those responsibilities before deciding it does not exist.

---

## 8. Trace both data flow and control flow

Before adding a feature, the LALM should be able to sketch its relevant flow.

### Data flow

```text
origin
  ↓
validation / identity
  ↓
canonical owner
  ↓
persistence / current state
  ↓
consumers
  ↓
presentation or reasoning
```

### Control flow

```text
trigger
  ↓
router / event / loader
  ↓
owning behavior
  ↓
side effects / emitted events
  ↓
completion / retry / fallback
```

A feature may be correct locally and still conflict globally because another path writes the same state later, a fallback replaces it, or a loader installs a stale implementation.

That is why architecture reconciliation must follow the feature through its lifecycle rather than checking only the line being edited.

---

## 9. Classify overlap before choosing a solution

When related existing work is found, classify it.

### Class A — exact existing capability

The requested feature already exists and only needs configuration, exposure, correction, or extension.

**Default action:** reuse/repair; do not create a second implementation.

### Class B — partial overlap

Existing architecture already owns part of the outcome.

**Default action:** extend the canonical owner and preserve its state/lifecycle.

### Class C — legitimate composition

Two implementations participate but have intentionally different responsibilities.

Example: server persists; Chat renders.

**Default action:** preserve separation and connect through the existing contract.

### Class D — compatibility adapter

A wrapper/bridge exists only to adapt one canonical contract to another.

**Default action:** do not mistake the adapter for the owner. Extend the real owner unless the adapter contract itself is what changes.

### Class E — fallback / last-known-good path

A second path exists only when the primary path fails.

**Default action:** preserve clear activation precedence. Never let fallback and primary simultaneously claim authority.

### Class F — historical/retired implementation

Code or docs remain for lineage but should no longer execute.

**Default action:** do not revive it. Remove stale active references when safe and relevant.

### Class G — conflicting duplicate owner

Two mechanisms currently claim the same responsibility/state/lifecycle.

**Default action:** reconcile/consolidate before adding the requested feature. Determine which owner survives and how readers/writers migrate.

### Class H — genuinely independent new responsibility

No existing module legitimately owns it and the capability has a distinct lifecycle/authority.

**Default action:** create a new structure only after passing the new-module test below.

---

## 10. Integration decision ladder

After discovery, choose the smallest coherent integration path.

Preferred order:

```text
1. REUSE
2. EXTEND CANONICAL OWNER
3. REFACTOR / CONSOLIDATE
4. MIGRATE + RETIRE OLD PATH
5. CREATE NEW INDEPENDENT STRUCTURE
```

### Reuse

Use when existing behavior already supports the outcome.

Avoid unnecessary code.

### Extend canonical owner

Use when the feature shares the same responsibility, state, lifecycle, and version authority.

This is the normal feature-addition path.

### Refactor/consolidate

Use when existing code is fragmented or two mechanisms currently compete.

The feature may be the right opportunity to restore one authority before adding behavior.

### Migrate + retire

Use when the correct architecture differs from a legacy active path.

Plan:

- authoritative destination;
- migration/compatibility period;
- readers/writers moved;
- old activation disabled;
- rollback path if needed.

### New independent structure

Use only when the feature truly owns an independent responsibility.

---

## 11. New-module test

Before creating another independently versioned module/service/subsystem, answer all of these.

1. **Independent responsibility:** does it own a domain responsibility not legitimately owned by an existing module?
2. **Independent lifecycle:** can it evolve/activate/fail independently?
3. **Independent state/authority:** does it require a distinct canonical source of truth rather than merely another view over existing state?
4. **Independent contract:** do other modules need a stable boundary to consume it?
5. **Independent versioning value:** would knowing its version separately materially help updates/compatibility/operations?

If most answers are “no,” it is probably a feature inside an existing owner, not a new module.

If the answer is “yes,” follow the Project Start new-module rule:

- stable module ID;
- `versions/<module-id>.txt`;
- `VERSION.txt` registration;
- owner-derived status/update surfaces;
- roadmap/release lineage.

---

## 12. Mask / Human / Brain placement test

The architecture scan must explicitly assign cognitive and operational ownership.

### Mask/client

Owns:

- capture;
- relay;
- presentation;
- local interaction;
- UI controls;
- device-facing capability surfaces.

It may transmit facts. It does not become the semantic authority.

### Human/server

Owns:

- authentication/authorization;
- durable operational state;
- routing;
- persistence;
- tools/actions;
- external side effects;
- protocol enforcement;
- executable capability boundaries.

### Brain/LALM

Owns:

- interpretation;
- semantic classification;
- reasoning;
- contextual meaning;
- conversational strategy;
- response planning;
- semantic repair/validation.

### Placement warning

If a proposed feature causes two planes to make the same semantic decision independently, stop and reconcile.

Example:

```text
BAD:
Chat decides user intent = correction
Server independently decides user intent = correction
LALM receives both conclusions

GOOD:
Chat relays user text + factual state
Server preserves operational context
LALM decides whether the turn is a correction
```

---

## 13. Architecture conflict signals

Treat these as strong reasons to inspect wider before implementation:

- two writers for one supposedly canonical state;
- two CSS/theme layers controlling the same geometry/visual responsibility;
- two loaders able to install different active versions of the same module;
- duplicated version literals;
- both client and server applying ordinary semantic interpretation;
- both server and LALM planning the same response behavior;
- multiple caches with no clear invalidation authority;
- a fallback that remains active after primary recovery;
- compatibility code becoming the permanent source of truth;
- old `dev`/`/tmp`/legacy paths referenced by new code despite newer authority;
- status/UI claiming a version different from active runtime evidence;
- a new service that merely wraps an existing service without a distinct contract;
- a new state store introduced because existing state was inconvenient to query;
- a second feature flag controlling the same rollout/lifecycle;
- a new event stream duplicating an existing state transition;
- a “temporary” injector that overrides canonical page/module ownership.

These signals do not automatically mean the existing design is wrong. They mean the ownership relationship must be explained before adding more work.

---

## 14. Ambiguity and stop conditions

The LALM should proceed autonomously when evidence establishes a safe integration path.

It should **not implement yet** when any of these materially affect correctness:

- canonical owner cannot be determined;
- two current authorities conflict and precedence is unknown;
- a relevant writer cannot be traced;
- a live behavior is known to differ from repository authority and the difference matters to the change;
- a migration could destroy or orphan durable state;
- an apparent legacy path may still be active and cannot be verified;
- module boundary is ambiguous enough that version ownership would be wrong;
- deployment capability is uncertain;
- security/auth ownership is unclear.

The required response to uncertainty is **more evidence gathering**, not invention.

If the unresolved ambiguity requires a human product decision rather than engineering discovery, surface the exact decision cleanly. Do not ask the user to rediscover repository facts the LALM can inspect itself.

---

## 15. Pre-implementation Architecture Reconciliation Record

Before code mutation, the programming LALM should be able to produce an internal record equivalent to:

```text
FEATURE / CHANGE:
Desired outcome:
Explicit constraints:
Implementation assumptions avoided:

ARCHITECTURE RADIUS REACHED:
R0 / R1 / R2 / R3 / R4
Why that radius is sufficient:

PLANES + MODULES:
Mask/client:
Human/server:
Brain/LALM:
Affected module IDs:

CURRENT AUTHORITIES CHECKED:
Project contracts/runbooks:
Source/manifests/registries:
State/storage authority:
Version authorities:
Live activation evidence (if relevant):

EXISTING RELATED WORK:
Canonical implementation:
Partial/adjacent implementations:
Fallbacks/compatibility layers:
Historical/retired paths:

FLOW TRACE:
Primary data flow:
Primary control/lifecycle flow:
Relevant writers:
Relevant readers/consumers:

OVERLAP CLASSIFICATION:
A/B/C/D/E/F/G/H + explanation

INTEGRATION DECISION:
reuse / extend / consolidate / migrate-retire / new structure
Why:

CHANGE BOUNDARY:
Will change:
Will intentionally NOT change:
Migration/retirement required:
Rollback/fallback implications:

VERSION IMPACT:
Server event:
Affected module versions:
New module authority required?:

DEPLOYMENT IMPACT:
Current deployment trigger checked:
Deployment-producing action required?:
Approval state if required:

VERIFICATION PLAN:
Static/source checks:
Runtime/live checks:
Single-authority regression check:

UNRESOLVED RISKS:
none / explicit items
```

For a small feature, many fields can be one line. For cross-module work, expand them.

The record is a reasoning scaffold, not a bureaucratic artifact. Its purpose is to prevent invisible architecture assumptions.

---

## 16. Post-implementation reconciliation

Architecture reconciliation is not finished when code compiles.

After implementation, verify the architecture predicted before the change still exists.

### Required post-change questions

1. Is there still one intentional authority for each affected responsibility?
2. Did any old writer remain active unexpectedly?
3. Did any reader remain pointed at the retired source?
4. Did a compatibility layer accidentally become a second owner?
5. Did a fallback become simultaneously active with the primary path?
6. Do version/status surfaces resolve the canonical authority?
7. Does live activation match the expected source/revision when live verification is required?
8. Were modules bumped only when actually changed?
9. Did the implementation stay in the correct Mask/Human/Brain plane?
10. Does the roadmap/release record preserve the architecture decision and progress?

If a post-change check reveals a conflict, do not hide it. Record the event honestly and treat the correction as a new versioned event when required by the evolution contract.

---

## 17. Verification must test architecture, not only output

A feature may appear to work while still damaging architecture.

Example:

```text
UI shows correct theme
BUT two theme injectors are now racing
```

Output-only test: PASS.
Architecture test: FAIL.

Therefore verification should include both:

### Behavioral acceptance

Does the requested outcome work?

### Ownership acceptance

Did it work through the intended canonical owner without introducing another competing source/state/lifecycle?

### Activation acceptance

When applicable, did production actually load the expected revision rather than a stale/fallback path?

All three may be required before claiming architectural completion.

---

## 18. Programming-LALM decision examples

### Example A — add response bookmarks

Request: allow several responses in a thread to be bookmarked and jumped to later; LALM recall may use them.

Reconciliation should inspect:

- Chat message/thread identity;
- existing thread UI/tray architecture;
- canonical transcript persistence;
- account/thread state storage;
- current context/history contract;
- LALM factual-context input;
- existing pin/save/anchor concepts.

Likely ownership shape:

```text
server/body = durable bookmark references
Chat/mask = create/remove/display/jump controls
LALM/brain = reason over supplied factual bookmark context when relevant
```

Do not create a separate Chat-only truth store and another LALM-only inferred bookmark store.

### Example B — improve conversational intent handling

Request: recognize corrections and continuations better.

Reconciliation should inspect:

- current LALM conversation-state compiler;
- response contract/planner;
- completion/evaluation harness;
- Chat payload/history relay;
- any server semantic classifiers.

Correct ownership is primarily Brain/LALM.

Do not add a second intent classifier in Chat merely because it is easier to write JavaScript there.

### Example C — adjust Ice Dragon visual geometry

Request: change the phone layout.

Reconciliation should inspect:

- canonical viewport/geometry stylesheet;
- early shell geometry;
- account identity module styles;
- theme hydrator;
- responsive breakpoints;
- old layout injectors.

If a canonical geometry owner exists, extend it. Do not add another late stylesheet that wins by selector specificity.

### Example D — authentication/account change

Request: alter Google account behavior.

Reconciliation should inspect:

- current Google OAuth runbook;
- server verification/auth authority;
- client GIS/session handoff;
- account storage/session identity;
- current live error evidence;
- old OAuth/client IDs as historical evidence only when relevant.

Do not diagnose from an old contract when a newer runbook/current source defines ownership.

### Example E — runtime LALM loader fix

Request: fix model load/hydration.

Reconciliation should inspect:

- active hot entrypoint;
- manifest revision;
- wrapper lineage;
- canonical base implementation;
- inherited namespace expectations;
- loader cameras;
- live production hydration logs.

If the repository says vNext but production logs still hydrate vPrevious, explicitly record source truth vs activation truth. Fix the authority/activation path rather than adding another loader.

---

## 19. Programming-LALM acceptance scenarios

A future programming LALM should be tested against scenarios like these.

### Scenario 1 — same feature, different name

Existing code calls a behavior `anchor`; request calls it `bookmark`.

Expected behavior:

- discover shared message-ID/state responsibility;
- classify overlap;
- extend/reuse rather than duplicate.

### Scenario 2 — stale formal document

Old contract says `dev` is durable source; current Project Start/Hotfix/Roadmap say `runtime`.

Expected behavior:

- recognize old document as historical evidence;
- use current authority;
- do not revive `dev`.

### Scenario 3 — two current writers

Two modules write the same canonical layout/state field.

Expected behavior:

- classify conflicting duplicate ownership;
- reconcile/consolidate before feature addition;
- do not add third writer.

### Scenario 4 — legitimate two-plane composition

Server persists a record; Chat renders it.

Expected behavior:

- preserve distinct responsibilities;
- do not collapse all logic into one plane merely because two components participate.

### Scenario 5 — semantic logic proposed in UI

Request mentions UI affordance but requires semantic inference.

Expected behavior:

- UI remains presentation/capture;
- LALM owns inference;
- server owns operational action/persistence as applicable.

### Scenario 6 — new independent subsystem

Feature has its own responsibility, lifecycle, stable contract, durable state, and update cadence.

Expected behavior:

- pass new-module test;
- create/register module version authority;
- record roadmap lineage.

### Scenario 7 — repository/live mismatch

Repo authority is new but production worker runs old revision.

Expected behavior:

- state both facts separately;
- inspect manifest/loader/cache/deployment path;
- never claim live acceptance from source alone.

### Scenario 8 — search miss

Literal feature-name search returns nothing.

Expected behavior:

- search synonyms, state, routes, readers/writers, lifecycle, manifests, and history;
- do not conclude absence from one search miss.

---

## 20. Anti-patterns the programming LALM must learn to reject

### “Just add another layer”

Creating a late override because the canonical implementation is inconvenient.

### “Same name means same architecture”

Assuming lexical similarity proves shared ownership.

### “Different name means unrelated”

Missing collisions between differently named writers of the same state.

### “Search returned nothing, so it is new”

Treating search limitations as evidence of absence.

### “Formal-looking old doc must be current”

Ignoring present source/version/runbook authority.

### “Working output proves architecture is correct”

Accepting racing/duplicated owners because the screenshot looks right.

### “Wrapper equals owner”

Extending a compatibility adapter instead of the canonical implementation.

### “Fallback is a second primary”

Allowing both paths to mutate current state simultaneously.

### “Version later”

Treating version/roadmap lineage as cleanup after implementation rather than part of the operation.

### “Ask the human where the code is”

Requesting repository facts the LALM can discover itself.

---

## 21. Efficiency rules — deep enough without becoming wasteful

Architecture reconciliation should improve engineering speed, not turn every one-line fix into a repository audit.

### Small isolated change

Usually enough:

- current owner source;
- direct reader/writer check;
- relevant version authority;
- roadmap/runbook check;
- deployment boundary;
- one-sentence reconciliation record.

### Cross-cutting change

Expand into:

- multiple planes/modules;
- persistence and protocol;
- loaders/caches/fallbacks;
- migration/compatibility;
- live evidence;
- detailed reconciliation record.

### Escalation rule

Widen based on evidence of interaction, not anxiety.

If Radius 1 shows a single clear owner with no shared state/lifecycle, do not inspect unrelated modules. If Radius 1 reveals shared state or multiple loaders, widen immediately.

---

## 22. Relationship to versioning

Architecture reconciliation happens before implementation, but versioning remains continuous throughout the event.

Required sequence:

```text
READ PROJECT CONTRACTS
        ↓
CAPTURE VERSION/SHA BASELINE
        ↓
ARCHITECTURE RECONCILIATION
        ↓
CONFIRM MODULE IMPACT
        ↓
IMPLEMENT
        ↓
RE-READ VERSION AUTHORITIES
        ↓
RECONCILE CONCURRENCY
        ↓
ASSIGN NEXT SERVER VERSION
        ↓
BUMP ONLY ACTUALLY CHANGED MODULES
        ↓
VERIFY
        ↓
ROADMAP/RELEASE RECORD INCLUDING ARCHITECTURE NOTE
```

A new module discovered during reconciliation changes the version plan before implementation is considered complete.

---

## 23. Relationship to deployment

Architecture placement and deployment capability are separate questions.

First determine **where the feature belongs architecturally**.

Then determine whether applying the correct change can actually trigger deployment under current configuration.

Do not move a feature to the wrong layer merely to avoid deployment.

Do not trigger deployment merely because the correct code lives on `main` when the current deployment configuration proves that a normal commit is inert.

If an actual deployment-producing operation is required, follow the Project Start Deployment Approval Gate before that action.

---

## 24. Relationship to roadmap/progress recording

The roadmap/release record is the durable memory of why an architectural choice was made.

At minimum record:

- affected architecture examined;
- current canonical owner;
- overlapping/legacy work found;
- chosen integration classification;
- what was reused/extended/refactored/retired;
- what was intentionally not changed;
- whether a new module was introduced;
- version/deployment state;
- verification result.

This prevents a later LALM from seeing two artifacts and guessing incorrectly about which one is intended to own the feature.

---

## 25. Compact execution algorithm

A programming LALM may implement the protocol conceptually as:

```text
frame(request)
    -> desired_outcome, constraints, implementation_assumptions

capture_version_baseline()

radius = R1
repeat:
    discover_current_owners(radius)
    trace_readers_writers_and_lifecycle()
    collect_related_implementations()
    reconcile_source_vs_live_vs_history()
    unresolved = ownership_or_interaction_unknown()
    if unresolved:
        radius = widen(radius)
until not unresolved

classify_overlap()
choose_integration_path(
    prefer=[reuse, extend, consolidate, migrate_retire, new_structure]
)

confirm_mask_human_brain_ownership()
confirm_module_and_version_impact()
confirm_deployment_capability()

if deployment_producing:
    require_explicit_approval_before_trigger()

implement_smallest_coherent_change()

re_read_version_authorities()
reconcile_concurrency()
assign_versions()
verify_behavior_and_ownership_and_activation()
record_roadmap_architecture_decision()
```

This is an engineering process description, not a hidden-reasoning logging requirement. The LALM should expose concise engineering conclusions/evidence when useful without dumping private internal reasoning.

---

## 26. Definition of done for architecture reconciliation

Pre-feature reconciliation is complete only when the programming LALM has enough evidence to state:

> I know the requested outcome, the affected architecture, the canonical owner, the relevant readers/writers/lifecycle, the overlapping existing work, and why the chosen integration path preserves or improves single-authority ownership.

The full development event is complete only when it can additionally state:

> The change was implemented through that reconciled architecture, version authorities were concurrency-checked, only affected modules were bumped, deployment rules were followed, behavioral and ownership verification passed or failures were recorded, and the roadmap/release lineage explains what happened.

---

## Bottom line

**The programming LALM must not treat architecture reconciliation as “look around briefly.” It is a bounded evidence-driven traversal from user outcome → current owner → state/readers/writers/lifecycle → overlapping implementations → authority/recency reconciliation → deliberate integration path. Search by responsibility, not just names. Distinguish repository engineering authority from live production activation and from historical evidence. Prefer reuse and extension of canonical owners; consolidate competing owners before adding new behavior; create a new module only when responsibility/lifecycle/authority genuinely justify it. Then version, verify, and record the architecture decision so the next engineering pass inherits a coherent system instead of rediscovering architectural collisions.**
