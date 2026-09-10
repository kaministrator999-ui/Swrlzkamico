# §wyrlz Server + Module Version Evolution Contract — READ THIS THIRD

**Purpose:** define the formal engineering rules for how §wyrlz evolves across Server releases and independently versioned modules. This document is the third required project-start document and is intended to become the engineering curriculum/specification used to teach the future programming-side LALM how to modify §wyrlz safely.

## Position in the project-start contract

The required reading order is:

1. `SWRLZ_PROJECT_START.md` — project entrypoint and operating sequence.
2. `SWRLZ_HOTFIX_RULES.md` — branch, hotfix, deployment, and verification boundary.
3. `SWRLZ_VERSION_MODULE_EVOLUTION.md` — version ownership, evolution, release lineage, and engineering rules.
4. `SWRLZ_SERVER_ROADMAP.md` — authoritative historical ledger of completed releases.

Do not modify application code until the first three documents have been read and reconciled with the current repository state.

## 1. Core evolution law

Every server development event that changes, attempts to change, tests, fixes, or otherwise advances server runtime state receives a new overall **Server version**.

This includes:

- successful changes;
- failed changes;
- failed fixes;
- test-only versioned events;
- partial attempts that alter runtime state;
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

## 5. Version update sequence

For every server development event:

1. Read the current project-start contract.
2. Read the hotfix/deployment rules.
3. Read this version/module evolution contract.
4. Read the current roadmap/release state.
5. Determine the current overall Server version.
6. Determine the current versions of every module that may be affected.
7. Fetch the current target source from the authoritative branch before editing.
8. Identify exactly which module(s) will change.
9. Make the smallest safe change.
10. Assign the next overall Server version to the event.
11. Increment only the module version(s) that actually changed.
12. Update each affected module's canonical version source.
13. Ensure cross-module consumers resolve versions from authoritative owners rather than duplicate literals.
14. Record the event in the roadmap/release record.
15. Record failures or unsuccessful verification honestly; do not rewrite history to hide them.
16. Commit the complete versioned event with its relevant code and records.
17. Reload/request affected routes according to the hotfix/deployment boundary.
18. Verify behavior, version responses, visible version displays, and source lineage.
19. If verification fails, treat the correction as a new versioned event.
20. Only declare the event complete after the required verification and release record are present.

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
- failure state, when applicable;
- verification state;
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

## 8. Branch and deployment interaction

Versioning does not override the hotfix/deployment boundary.

- `runtime` remains the durable live application source for ordinary runtime changes.
- `main` remains the stable loader/infrastructure/deployment boundary.
- Runtime-only changes follow the no-deploy/no-restart hotfix path defined by `SWRLZ_HOTFIX_RULES.md`.
- Stable infrastructure changes follow the deployment path defined by `SWRLZ_HOTFIX_RULES.md`.

The version event must record which path was used.

## 9. Source-of-truth discipline

Before changing a version or module, establish the current source of truth from the repository.

Do not rely on:

- an old ChatGPT conversation;
- a stale screenshot;
- a cached browser page;
- `/tmp`;
- a guessed filename;
- a hardcoded copy in another module.

Repository state is authoritative for current engineering work.

## 10. Programming-LALM curriculum requirements

This contract is intentionally written as an engineering teaching specification for the future programming-side LALM.

The programming LALM should eventually learn to reason about every proposed change using this sequence:

```text
REQUEST
  ↓
SOURCE-OF-TRUTH DISCOVERY
  ↓
CURRENT VERSION DISCOVERY
  ↓
MODULE IMPACT ANALYSIS
  ↓
BRANCH / DEPLOYMENT DECISION
  ↓
MINIMAL CHANGE
  ↓
SERVER VERSION ASSIGNMENT
  ↓
AFFECTED MODULE VERSION BUMPS
  ↓
CANONICAL VERSION-SOURCE UPDATE
  ↓
CROSS-MODULE RESOLUTION CHECK
  ↓
ROADMAP / RELEASE RECORD
  ↓
COMMIT
  ↓
REQUEST / RELOAD
  ↓
VERIFICATION
  ↓
SUCCESS → CLOSE EVENT
FAILURE → RECORD + CREATE NEXT VERSIONED EVENT
```

The LALM must understand that versioning is part of the engineering operation itself, not a cosmetic documentation task performed after coding.

It must also understand the two reporting layers:

```text
ENGINEERING RECORD
→ detailed implementation, lineage, evidence, commits, failures

HUMAN PROJECT UPDATE
→ what changed, what it accomplishes, resulting behavior, status
```

## 11. Required reasoning questions for future programming agents

Before declaring a change complete, the programming agent should be able to answer:

1. What is the current Server version?
2. What is the current canonical version of each affected module?
3. Which branch owns the requested behavior?
4. Which exact source file is authoritative?
5. Which modules actually changed?
6. Which module versions therefore need to advance?
7. Where is each affected module's canonical version source?
8. Does any consumer duplicate another module's version instead of querying it?
9. What Server version records this event?
10. What happened if an attempt failed?
11. What commit contains the event?
12. What verification was performed?
13. Was deployment required, or was this a runtime-only hotfix?
14. Does the roadmap accurately describe the completed event?
15. What should the human user be told this change **accomplishes**, without exposing implementation syntax unless requested?

If any answer is unknown, the agent must resolve the repository state before claiming completion.

## 12. Evolution law in one block

```text
EVERY SERVER DEVELOPMENT EVENT
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
RECORD CHANGE + FAILURE + VERIFICATION + COMMIT LINEAGE
        ↓
VERIFY
        ↓
REPORT HUMAN-READABLE ACCOMPLISHMENT TO USER
        ↓
FAILURE = NEW VERSIONED EVENT FOR THE NEXT ATTEMPT
```

## Bottom line

**Server versioning is chronological event lineage. Module versioning is independent component lineage. Canonical ownership prevents drift. Cross-module resolution prevents stale duplication. Roadmap entries preserve history. Failed attempts remain visible. Verification closes each event. The roadmap records the technical implementation; the conversational update explains the resulting accomplishment in human language.**

This document is therefore both the **third required project-start contract** and the foundation for the future **programming-side LALM engineering curriculum/specification**.
