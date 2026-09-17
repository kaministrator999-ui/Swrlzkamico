# §wyrlz Server + Module Version Evolution Contract — READ THIS THIRD

**Purpose:** define the formal engineering rules for how §wyrlz evolves across Server releases and independently versioned modules. This document is the third required project-start document and, together with `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`, forms the engineering curriculum/specification used to teach the future programming-side LALM how to modify §wyrlz safely.

## Position in the project-start contract

The required engineering reading order is:

1. `SWRLZ_PROJECT_START.md` — project entrypoint and operating sequence.
2. `SWRLZ_HOTFIX_RULES.md` — branch, hotfix, deployment, and verification boundary.
3. `SWRLZ_VERSION_MODULE_EVOLUTION.md` — version ownership, evolution, release lineage, and engineering rules.
4. `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md` — programming-LALM method for discovering affected architecture, current authority, related implementations, overlap/conflict, and the correct integration path.
5. `SWRLZ_SERVER_ROADMAP.md` — authoritative historical ledger of completed releases.
6. `SWRLZ_CHAT_CAMERA_LOGS.md` — production Chat/LALM observation and source-vs-live verification contract.

Do not modify application code until the first four engineering documents have been read and reconciled with the current repository state. Read the roadmap and camera runbook before implementation/diagnosis as required by Project Start.

## 1. Core evolution law

Every server development event that changes, attempts to change, tests, fixes, or otherwise advances server runtime or governed project state receives a new overall **Server version**.

This includes:

- successful changes;
- failed changes;
- failed fixes;
- test-only versioned events;
- partial attempts that alter runtime state;
- governed engineering-contract changes;
- subsequent corrections to a failed attempt.

A failed attempt is never silently erased from lineage. The next attempt receives another Server version.

The overall Server version is the chronological umbrella for the event. It does **not** mean every module changed.

## 2. Independent module evolution

Every module actually changed during a Server event receives its own module-version increment.

If only one module changes:

```text
Server vX.Y.Z
└── LALM vA.B.C  ← changed
```

If several modules change:

```text
Server vX.Y.Z
├── Chat vA.B.C       ← changed
├── LALM vD.E.F       ← changed
└── Server UI vG.H.I  ← unchanged
```

If a module does not change, its version does not advance merely because the Server version advanced.

### Failed-event example

```text
Server v5.5.6
└── Chat v5.5.5
    - Attempted sidebar fix; verification failed.

Server v5.5.7
└── Chat v5.5.6
    - Corrected the failed sidebar fix.
```

The failed event remains part of the engineering history. The successful correction is a separate event and version.

## 3. Version ownership is canonical

Each module owns its own authoritative version source.

The canonical source must be updated whenever that module changes. Do not create a second manually maintained copy merely so another module can display the value.

Current ownership model:

| Scope | Canonical owner |
|---|---|
| Overall Server | Server's authoritative version source / roadmap lineage |
| Chat | Chat's runtime-owned canonical version source |
| LALM UI | LALM control-plane canonical UI version source |
| LALM engine | Active LALM/R39 runtime revision/version source |
| Server UI | Server UI's canonical version source |
| Deployment control | `versions/deployment-control.txt` |
| Other modules | Their own authoritative module source as established by the architecture |

The exact file or API location must always be confirmed from the current repository state before editing.

## 4. Cross-module version resolution

When one module displays another module's version, it must retrieve that value from the owning module's authoritative source automatically.

**Never:**

- hardcode another module's version into a second module;
- maintain duplicate version literals that can drift;
- infer a version from a filename, commit message, or stale UI text when an authoritative source exists.

**Required pattern:**

```text
Module A needs Module B version
              ↓
Query Module B authoritative version source
              ↓
Render current value
```

This makes version propagation architectural rather than manual.

## 5. Version + architecture update sequence

For every server development event:

1. Read the current Project Start contract.
2. Read the hotfix/deployment rules.
3. Read this version/module evolution contract.
4. Read `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`.
5. Read the current roadmap/release state and relevant observation/runbook material.
6. Determine the current overall Server version.
7. Determine the current versions of every module that may be affected.
8. Record the authoritative version values and file/blob SHAs as the **event baseline**.
9. Separate the requested **desired outcome and explicit constraints** from unproven implementation assumptions.
10. Fetch the current target source from the authoritative branch before editing.
11. Perform the required **Pre-Feature Architecture Reconciliation** using the protocol: widen architecture radius only as needed, identify current canonical owner(s), build the relevant authority map, trace state/readers/writers/control/lifecycle, and distinguish current engineering authority from live activation and historical evidence.
12. Search for exact, partial, adjacent, fallback, compatibility, retired, or conflicting implementations that share the responsibility even when their names differ.
13. Classify overlap and deliberately select the integration path: **reuse → extend canonical owner → refactor/consolidate → migrate+retire → genuinely new independent structure**.
14. Confirm Mask / Human / Brain ownership and identify exactly which module(s) will actually change.
15. If a genuinely new independent structure is justified, establish its module/version-authority plan before treating implementation as complete.
16. **Perform the deployment-risk check against the current repository/deployment configuration and workflows before any deployment-capable mutation.**
17. If the proposed action can actually cause deployment/redeployment, **STOP and obtain explicit user approval before that action.**
18. Make the smallest coherent change through the reconciled canonical owner(s).
19. Verify post-change ownership: no unintended second writer/owner, stale active path, competing fallback, duplicated semantic authority, or duplicate version source was introduced.
20. **Immediately before assigning new versions or committing, re-read `VERSION.txt` and every affected authoritative `versions/<module-id>.txt` file.**
21. Compare those authorities and SHAs to the event baseline.
22. If a relevant authority changed, assume another instance/process advanced the project while this work was in progress. **Do not use the previously planned version numbers. Reconcile against the newest authority first.**
23. Assign the next overall Server version from the newest authoritative state.
24. Increment only the module version(s) that actually changed.
25. Update each affected module's canonical version source.
26. Ensure cross-module consumers resolve versions from authoritative owners rather than duplicate literals.
27. Record the event in the roadmap/release record, including the architecture-reconciliation decision and relevant reused/refactored/retired paths.
28. Record failures or unsuccessful verification honestly; do not rewrite history to hide them.
29. Commit the complete versioned event with its relevant code and records, using repository SHA/precondition checks where available so stale writes fail instead of overwriting newer state.
30. Re-read the authoritative version files after the mutation/commit and verify they match the versions assigned to the event.
31. Reload/request affected routes according to the hotfix/deployment boundary.
32. Verify behavior, ownership architecture, version responses, visible version displays, source lineage, and live activation when relevant.
33. If verification fails, treat the correction as a new versioned event.
34. Only declare the event complete after the required verification and release record are present.

### Concurrency invariant

The version state observed at project-entry time is a **baseline, not a reservation**.

```text
READ AUTHORITY AT ENTRY
        ↓
DO ARCHITECTURE RECONCILIATION + WORK
        ↓
RE-READ AUTHORITY AT COMMIT BOUNDARY
        ↓
UNCHANGED → assign next versions
CHANGED   → reconcile first, then assign from newest state
```

This is the default optimistic-concurrency protocol for multiple §wyrlz instances, developers, agents, or automated processes working against the same project. A stale version snapshot must never be used to overwrite a newer authority.

## 6. Module versions are lineage, not decoration

A module version answers:

> "What is the evolution state of this module after this Server event?"

The Server version answers:

> "Which chronological server development event are we talking about?"

Therefore:

- Server versions advance on every server development event governed by this contract.
- Module versions advance only when the corresponding module changes.
- A module may remain at the same version across many Server releases.
- A failed attempt still advances the Server lineage and advances a module if that module was actually changed.

## 7. Roadmap and release lineage

Every versioned Server event must have a durable record containing, at minimum:

- overall Server version;
- affected module versions;
- modules intentionally unchanged when relevant;
- exact change/attempt description;
- **architecture-reconciliation summary: affected architecture checked, canonical owner, overlap found, chosen integration path, and any reused/refactored/migrated/retired path**;
- failure state, when applicable;
- verification state, including ownership/activation verification when relevant;
- deployment state;
- relevant commit lineage;
- rollback/migration notes when applicable.

The roadmap is the historical ledger. It must not be left saying `NEXT RELEASE` after an event has been completed.

The release record must describe what actually happened, including failed attempts when they are part of the event lineage.

### Human-readable update/reporting rule

The roadmap may contain implementation-level engineering detail, including source files, commits, hashes, exact technical mechanisms, and test evidence. **The conversational update to the human user must not be a code dump.**

When a Server/module event is reported in Chat, summarize the work in plain human/project language:

- identify the new Server version;
- identify the affected module version(s);
- explain **what the change accomplishes for the user/system**;
- explain the resulting behavior or capability;
- state what was intentionally unchanged when useful;
- state deployment/restart status;
- state verification status honestly;
- mention the roadmap was updated.

Do **not** normally expose implementation syntax, variable assignments, internal function names, raw diffs, or code fragments in the conversational release summary unless the user specifically asks for technical implementation details.

The roadmap remains the detailed engineering record; the Chat update is the human-readable project-status layer.

## 8. Deployment approval is a pre-mutation safety boundary

**Deployment is never implicitly authorized by the existence of a development request.** The agent must not treat a request to architect, investigate, document, debug, implement, test, version, commit, merge, or otherwise work on §wyrlz as permission to cause deployment.

Before **any** repository action that can actually cause deployment/redeployment, the agent must:

1. identify the exact deployment trigger;
2. identify the branch/path/configuration/action involved;
3. explain why the trigger causes deployment;
4. distinguish an actual architectural deployment requirement from an automatic consequence of the deployment configuration;
5. identify the deployed surface that would be affected;
6. determine whether the work can instead be performed through the non-deployment `runtime` path;
7. state the exact repository action awaiting authorization;
8. **STOP and obtain explicit user approval before performing that deployment-producing action.**

### Branch names do not prove deployment capability

Before invoking the approval gate, inspect the current deployment configuration and relevant workflows.

- A commit to `main` is not inherently a deployment.
- A Markdown/documentation edit is not inherently deployment-capable.
- If Git-based deployment is disabled and no workflow or automation deploys the proposed mutation, an ordinary commit may proceed without deployment approval.
- If the configuration later changes so that a branch/path becomes deployment-watched, the gate applies again.
- Explicit deploy commands/actions remain deployment-producing and require approval.

This applies equally to source code and documentation: the gate follows the **actual deployment trigger**, not the file extension or branch label.

If deployment behavior is uncertain, the agent must treat the action as deployment-capable and stop for approval.

A commit is not deployment authorization. A merge into a deployment-watched branch is not deployment authorization. A general request to update the repository is not deployment authorization.

If deployment is approved, the approval applies to the specifically explained deployment-producing action. The agent must not broaden that approval to unrelated deployment-producing changes.

If the user chooses to deploy manually, the agent must not automatically initiate the deployment.

This rule takes precedence over convenience and applies during architecture, investigation, debugging, documentation, implementation, testing, release preparation, branch operations, commits, merges, and all other repository work.

## 9. Branch and deployment interaction

Versioning does not override the hotfix/deployment boundary or the deployment approval gate.

- `runtime` remains the durable live application source for ordinary runtime changes.
- `main` remains the stable loader/infrastructure and engineering-contract boundary.
- Runtime-only changes follow the no-deploy/no-restart hotfix path defined by `SWRLZ_HOTFIX_RULES.md`.
- Stable infrastructure changes may be authored on `main`; whether applying them to production requires a deployment is determined by the current deployment configuration and capability.
- If production deployment is required, explicit user approval is required before the action that actually triggers it.
- Documentation changes must be evaluated for deployment impact, but must not be treated as deployment-capable when current configuration proves they are not.

The version event must record which path was used and whether deployment was none, approved, or otherwise explicitly authorized.

## 10. Source-of-truth and evidence discipline

Before changing a version or module, establish the current source of truth from the repository.

Do not rely on:

- an old ChatGPT conversation;
- a stale screenshot;
- a cached browser page;
- `/tmp`;
- a guessed filename;
- a hardcoded copy in another module.

For architecture reconciliation, distinguish three evidence classes defined by the Architecture Reconciliation Protocol:

1. **Current engineering/source authority** — current Project Start/Hotfix/Version contracts, current relevant runbooks, current canonical source, manifests/registries, `VERSION.txt`, and module-owned authorities.
2. **Production activation authority** — live status, runtime cameras/logs, active deployment/revision receipts, manifest resolution, and rendered behavior where relevant.
3. **Historical evidence** — older contracts, superseded runbooks, old commits, retired code, and old roadmap entries.

Historical evidence can explain lineage or reveal stale competing mechanisms, but it does not silently outrank newer current authority. Repository engineering authority and production activation may temporarily differ; if that difference matters to the change, record both facts and reconcile the activation path rather than pretending they match.

The version authority must be checked twice for a versioned event: once to establish the event baseline and again immediately before version assignment/commit. This second read is what protects concurrent development from stale-version overwrite.

## 11. Programming-LALM curriculum requirements

This contract and `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md` are intentionally written together as the engineering teaching specification for the future programming-side LALM.

The Version/Module Evolution Contract teaches **how project changes evolve, version, deploy, verify, and record**. The Architecture Reconciliation Protocol teaches **how to discover where a requested change belongs and how to avoid duplicate/competing architecture before implementing it**.

The programming LALM should learn to reason about every proposed change using this sequence:

```text
REQUEST
  ↓
DESIRED OUTCOME + EXPLICIT CONSTRAINTS
  ↓
SEPARATE OUTCOME FROM UNPROVEN IMPLEMENTATION ASSUMPTIONS
  ↓
SOURCE-OF-TRUTH DISCOVERY
  ↓
CURRENT VERSION DISCOVERY
  ↓
CAPTURE AUTHORITY/SHA BASELINE
  ↓
ARCHITECTURE-RADIUS DISCOVERY
  ↓
BUILD AUTHORITY MAP
  ↓
TRACE STATE + READERS + WRITERS + CONTROL/LIFECYCLE
  ↓
RECONCILE CURRENT SOURCE AUTHORITY VS LIVE ACTIVATION VS HISTORICAL EVIDENCE
  ↓
SEARCH EXACT + PARTIAL + ADJACENT + FALLBACK + COMPATIBILITY + RETIRED WORK
  ↓
CLASSIFY OVERLAP
  ↓
CHOOSE INTEGRATION PATH
(reuse → extend → consolidate → migrate/retire → new independent structure)
  ↓
MASK / HUMAN / BRAIN OWNERSHIP CHECK
  ↓
MODULE IMPACT ANALYSIS
  ↓
DEPLOYMENT RISK ANALYSIS FROM CURRENT CONFIG/WORKFLOWS
  ↓
IF DEPLOYMENT-CAPABLE → STOP + EXPLAIN + GET USER APPROVAL
  ↓
SMALLEST COHERENT CHANGE THROUGH CANONICAL OWNER
  ↓
POST-CHANGE SINGLE-AUTHORITY CHECK
  ↓
RE-READ VERSION AUTHORITIES
  ↓
AUTHORITY CHANGED? → RECONCILE FIRST
  ↓
SERVER VERSION ASSIGNMENT
  ↓
AFFECTED MODULE VERSION BUMPS
  ↓
CANONICAL VERSION-SOURCE UPDATE
  ↓
CROSS-MODULE RESOLUTION CHECK
  ↓
ROADMAP / RELEASE RECORD + ARCHITECTURE DECISION
  ↓
COMMIT WITH STALE-WRITE PROTECTION
  ↓
RE-READ AUTHORITIES
  ↓
REQUEST / RELOAD
  ↓
BEHAVIORAL + OWNERSHIP + ACTIVATION VERIFICATION WHEN RELEVANT
  ↓
SUCCESS → CLOSE EVENT
FAILURE → RECORD + CREATE NEXT VERSIONED EVENT
```

The LALM must understand that architecture reconciliation and versioning are part of the same engineering operation, not optional documentation before/after coding.

It must understand that **no literal feature-name match does not prove absence**. Search by responsibility, state, routes, readers/writers, lifecycle, manifests, and history when needed.

It must understand that multiple participating components are acceptable when their responsibilities are distinct; the target is not “one file,” but **one intentional authority per responsibility**.

It must also understand that project rules are a **default engineering grammar, not a cage**: when another project/user provides a different explicit architecture or operating contract, the LALM should learn and follow that project-specific contract while preserving universal safety/source-of-truth principles.

It must also understand the two reporting layers:

```text
ENGINEERING RECORD
→ detailed implementation, architecture decision, lineage, evidence, commits, failures

HUMAN PROJECT UPDATE
→ what changed, what it accomplishes, resulting behavior, status
```

## 12. Required reasoning questions for future programming agents

Before declaring a change complete, the programming agent should be able to answer:

### Architecture placement and reconciliation

1. What outcome is the user actually asking the system to produce?
2. Which apparent implementation ideas are explicit requirements versus assumptions that still need architecture discovery?
3. Which architecture radius was required, and why was it sufficient?
4. Which Mask/client, Human/server, Brain/LALM, module, route, state, protocol, storage, loader, cache, UI, or tool surfaces are affected?
5. What is the canonical owner for each affected responsibility?
6. What are the relevant writers, readers/consumers, and lifecycle/activation paths?
7. What existing exact, partial, adjacent, fallback, compatibility, retired, or competing implementation was found?
8. Is each piece of evidence current engineering authority, live production activation evidence, or historical evidence?
9. If source authority and live activation differ, was that difference made explicit and reconciled where relevant?
10. Which overlap class applies, and why?
11. Was the integration path deliberately chosen as reuse, extension, consolidation/refactor, migration+retirement, or a genuinely new independent structure?
12. If multiple implementations participate, are their responsibilities intentionally distinct rather than competing?
13. Does the final design preserve the Mask / Human / Brain ownership boundary?
14. If a new module/subsystem was created, did it actually pass the independent responsibility/lifecycle/state-contract/versioning test?
15. After implementation, is there still one intentional authority for each affected responsibility, with no unintended second writer/owner/fallback/version source?

### Version, concurrency, deployment, and release

16. What is the current Server version?
17. What is the current canonical version of each affected module?
18. What authority values/SHAs were captured at event entry?
19. Were those authorities re-read immediately before version assignment/commit?
20. Did another instance/process advance any relevant authority while this event was in progress?
21. If yes, was the work reconciled from the newest state instead of overwriting it?
22. Which branch owns the requested behavior?
23. Which exact source file/artifact is authoritative?
24. Which modules actually changed?
25. Which module versions therefore need to advance?
26. Where is each affected module's canonical version source?
27. Does any consumer duplicate another module's version instead of querying it?
28. What Server version records this event?
29. What happened if an attempt failed?
30. What commit contains the event?
31. What behavioral, ownership, and activation verification was performed as applicable?
32. **Could any repository action for this event actually cause deployment/redeployment under current configuration/workflows?**
33. **If yes, what exactly causes it, why does it happen, and was explicit user approval obtained before that deployment-producing action?**
34. Was deployment required, or was this a non-deployment runtime/main update?
35. Does the roadmap accurately describe the completed event and architecture decision?
36. What should the human user be told this change **accomplishes**, without exposing implementation syntax unless requested?

If any material answer is unknown, the agent must resolve the repository/architecture state before claiming completion. If deployment risk is unknown, the agent must stop before the deployment-capable action.

## 13. Evolution law in one block

```text
EVERY SERVER DEVELOPMENT EVENT
        ↓
READ + CAPTURE CURRENT AUTHORITIES
        ↓
FRAME OUTCOME / CONSTRAINTS
        ↓
ARCHITECTURE RECONCILIATION PROTOCOL
        ↓
MAP OWNER + READERS/WRITERS/LIFECYCLE + RELATED WORK
        ↓
CLASSIFY OVERLAP + CHOOSE INTEGRATION PATH
        ↓
CONFIRM MASK/HUMAN/BRAIN + MODULE OWNERSHIP
        ↓
DEPLOYMENT RISK CHECK FROM CURRENT CONFIG
        ↓
DEPLOYMENT-CAPABLE? → STOP + EXPLAIN + GET USER APPROVAL
        ↓
MAKE MINIMAL COHERENT CHANGE THROUGH CANONICAL OWNER
        ↓
POST-CHANGE OWNERSHIP CHECK
        ↓
RE-READ AUTHORITIES AT COMMIT BOUNDARY
        ↓
CHANGED? → RECONCILE BEFORE VERSIONING
        ↓
NEW OVERALL SERVER VERSION
        ↓
IDENTIFY ACTUALLY CHANGED MODULES
        ↓
BUMP ONLY THOSE MODULE VERSIONS
        ↓
UPDATE THEIR CANONICAL SOURCES
        ↓
CONSUMERS QUERY OWNERS — NEVER DUPLICATE
        ↓
RECORD ARCHITECTURE DECISION + CHANGE + FAILURE + VERIFICATION + COMMIT LINEAGE
        ↓
RE-READ AUTHORITIES + VERIFY
        ↓
VERIFY BEHAVIOR + OWNERSHIP + ACTIVATION WHEN RELEVANT
        ↓
REPORT HUMAN-READABLE ACCOMPLISHMENT TO USER
        ↓
FAILURE = NEW VERSIONED EVENT FOR THE NEXT ATTEMPT
```

## 14. Per-module version authority files — REQUIRED GOING FORWARD

Every independently evolving §wyrlz structure must have its **own authoritative version file**. The repository-level `VERSION.txt` is an index/router to those owners, not a second place that duplicates everybody's version number.

The required pattern is:

```text
VERSION.txt
   ↓ identifies owner
versions/<module-id>.txt
   ↓ authoritative version/revision
module UI / status / update checker / installer
```

Current and reserved module authorities include:

- `versions/server-runtime.txt`
- `versions/server-ui.txt`
- `versions/web-chat.txt`
- `versions/stream-contract.txt`
- `versions/lalm-ui.txt`
- `versions/lalm-engine.txt`
- `versions/admin-web.txt`
- `versions/google-account.txt`
- `versions/client-apk.txt`
- `versions/server-apk.txt`
- `versions/frozen-web-collector.txt`
- `versions/deployment-control.txt`

The Android APK version files may remain `UNASSIGNED` until the actual current artifact versions are verified. **Never invent a current version merely to fill the registry.**

### New-module rule

Whenever a new independently evolvable structure is introduced — for example profile/account architecture, memory, search, Windows client/server, admin tooling, authentication architecture, a protocol, an APK, or another substantial subsystem — the same development event must:

1. pass the independent-structure test in `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`;
2. assign it a stable module ID;
3. create `versions/<module-id>.txt`;
4. register that owner in `VERSION.txt`;
5. make the module's own UI/status/update surfaces read that authority where appropriate;
6. make cross-module consumers fetch the owner instead of copying its value;
7. include the module in release/roadmap lineage from that point forward.

### Update rule

When a module changes, update **its own version file** in the same versioned event. Do not bump unrelated module files. If a user-facing surface displays the module version, it must derive that display from the authoritative module file or an API/status surface that itself derives from that file.

### Update-check rule

Clients, APKs, installers, and web/admin surfaces should compare their installed/local version against the authoritative hosted module version. A mismatch is the basis for update availability; equality means the installed/local component is current under that component's update policy.

### Version-source precedence

For version identity, precedence is:

```text
module-owned version file
        ↓
authoritative API/status derived from it
        ↓
UI/update checker consuming that source
```

Roadmaps, changelogs, filenames, labels, and commit messages describe lineage but do not outrank the module-owned version authority.

## Bottom line

**Server versioning is chronological event lineage. Module versioning is independent component lineage. Architecture reconciliation determines where a requested outcome belongs before implementation: discover current authority, map state/readers/writers/lifecycle, distinguish source authority from live activation and historical evidence, find overlapping work by responsibility rather than names, classify the overlap, and deliberately choose reuse/extension/consolidation/migration-retirement/new structure. Canonical ownership prevents drift. Cross-module resolution prevents stale duplication. Authority revalidation prevents concurrent instances from overwriting newer work. Roadmap entries preserve both implementation history and the architecture decision that produced it. Failed attempts remain visible. Verification must test behavior and ownership, plus live activation when relevant. Before any repository action that can actually trigger deployment, §wyrlz must stop, explain the trigger and requirement, and obtain explicit user approval before that deployment-producing action. Branch names and documentation file types do not by themselves prove deployment capability. Every independently evolving structure must justify its independence and own its own version file, with `VERSION.txt` routing consumers to the correct authority rather than duplicating module versions.**

This document is therefore the **third required project-start contract** and, together with `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`, the foundation for the future **programming-side LALM engineering curriculum/specification**.
