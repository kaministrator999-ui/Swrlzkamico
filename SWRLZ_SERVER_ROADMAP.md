# §wyrlz Server Roadmap & Version Ledger

**Role:** durable chronological memory of Server/module evolution, architecture decisions, diagnostics, verification, deployment state, and completed project progress.

**Startup/read order is owned by `SWRLZ_PROJECT_START.md`.** This ledger reports what happened; it does not redefine the operating workflow.

## Current authoritative baseline

The values below were reconciled from current module-owned authorities for this ledger update.

- **Overall Server:** `2.3.230`
- **Chat:** `1.5.65`
- **LALM Engine:** `2.1.76` (`v65`)
- **Web Frontend:** `1.0.5`
- **LALM UI:** `1.0.0`
- **Frozen Web Collector:** `1.0.9`
- **Deployment Control:** `1.0.7`

`VERSION.txt` and the referenced `versions/<module-id>.txt` files remain the version identity authorities. This roadmap is lineage/history and must be reconciled to those owners rather than treated as a competing version source.

---

## Current project-work contract

Project development is governed by the canonical owners routed from `SWRLZ_PROJECT_START.md`:

- Hotfix/deployment mechanics → `SWRLZ_HOTFIX_RULES.md`
- Server/module lineage → `SWRLZ_VERSION_MODULE_EVOLUTION.md`
- Architecture reconciliation → `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`
- Project-wide cameras/logs → `SWRLZ_CHAT_CAMERA_LOGS.md`
- Project-work response/readability → `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md`
- User-project architecture teaching → `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md`

Every feature/fix/refactor first reconciles existing architecture. Every issue/debug event automatically inspects available repository/live evidence and adds bounded cameras only when observability is insufficient. Every governed event uses concurrency-safe version assignment and a durable release record. Substantial conversational updates follow the response standard.

---

## Release ledger

### Server 2.3.230 — Project-work contract reconciliation, automatic diagnostics, readable reporting, and architecture coaching

**Status:** source complete / governance contract verified.  
**Affected module versions:** none.  
**LALM Engine:** `2.1.76` / `v65` unchanged.  
**Chat:** `1.5.65` unchanged.  
**Deployment / restart:** NONE.

This event reconciled the project-development contract around four user goals:

1. issue-fixing should automatically inspect §wyrlz-accessible logs/evidence and add diagnostic cameras where observability is missing;
2. project-work responses should use a consistent readable engineering handoff structure;
3. Project Start should clearly route every rule family to one canonical owner rather than duplicate/compete with subordinate documents;
4. the architecture curriculum should also help §wyrlz teach proportional architecture to users building their own projects and respect informed simplification of optional structure.

**Architecture reconciliation:** reviewed Project Start, Hotfix Rules, Version/Module Evolution, Architecture Reconciliation Protocol, the prior Chat camera runbook, Engineering Log, roadmap/release behavior, deployment workflow, current module authorities, and the newly created response standard. The main overlap found was governance duplication: Project Start had grown into a large secondary owner of architecture/version/deployment details; Hotfix still labeled itself “READ THIS FIRST”; Version Evolution carried a second startup sequence; and camera guidance was named/scoped as Chat-specific despite diagnostic needs being project-wide.

**Integration decision:** preserve one owner per concern. Project Start was refactored into the canonical router/orchestrator; Hotfix now owns mutation/deployment mechanics and explicitly sits second; Version Evolution now owns lineage/concurrency/version authority only; the existing camera filename remains for compatibility but its contract is project-wide; a separate Response Standard owns conversational project reporting; the existing Architecture Reconciliation Protocol remains the engineering method; and a separate Architecture Coaching Guide owns user-facing teaching/adaptation so internal architecture rules are not forced onto every user project.

**Automatic diagnostic behavior added to contract:** when fixing/debugging/investigating/verifying defects, §wyrlz automatically inspects current source, existing cameras, manifests/loaders, version authorities, roadmap/releases, Engineering Log, tests, recent commits and workflow/build logs as relevant, plus accessible live/runtime evidence such as Vercel logs/status. If evidence cannot distinguish competing explanations, the agent adds the smallest bounded camera at the relevant architecture boundary, reproduces the path, fixes the canonical owner, and re-checks the same evidence. Default diagnostic order is **inspect first → instrument second → mutate third**.

**Response/readability behavior added:** `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md` defines structured Status / findings / changes / verification / version-deployment / remaining-state reporting, precise source-vs-runtime-vs-live truth vocabulary, and concise progress updates during long work.

**User architecture coaching added:** `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md` teaches proportional project structure, plain-language reasons for architecture boundaries, progressive architecture as complexity grows, user choice over preference-level structure, distinction between requirements/recommendations/preferences, and clean removal/simplification when the user rejects optional architecture.

**Authority/concurrency reconciliation:** event work began around Server `2.3.228`, but concurrent runtime work advanced the authoritative Server to `2.3.229` and LALM Engine to `2.1.76` / `v65`. This event preserved that work and assigned `2.3.230` from the re-read authority rather than overwriting/reusing stale numbers. Current Chat remained `1.5.65`. Additional roadmap snapshot drift was corrected from current authorities: Web Frontend `1.0.5`, Frozen Web Collector `1.0.9`, Deployment Control `1.0.7`.

**Intentionally unchanged:** no R39 inference source, Chat runtime behavior, server API, persistence schema, production loader, deployment configuration, Web Frontend source, Collector source, or Deployment Control source was changed by this governance event. Therefore no component version was artificially bumped.

**Verification:** Project Start now routes seven mandatory project-work documents and conditional architecture/OAuth guides; Hotfix and Version Evolution no longer compete for startup-order ownership; project-wide diagnostic rules and response standard have dedicated owners; Server authority advanced to `2.3.230` after concurrency revalidation. Deployment configuration remained manual/inert for these documentation commits; production deployment is not part of this event.

**Lineage:** response standard `eacad54746efefbc0756a02635795b33c3b58419`; project-wide diagnostic contract `bf64fba083e5cc07cf3c380b3868ee5905921bab`; architecture coaching guide `935421ce92d27ad8d575ca94c8f55c65f11c9d38`; Project Start router refactor `d752630179522b6e63b32bf5700f2ffdca417d30`; Hotfix contract clarification `4e4ede2bf9527ff8671dbe31c020157babb4895a`; Version Evolution ownership cleanup `f7370ccd1d64c993a59e386fabdedfdec3fb50e3`; Server authority `3680dc63d3b62892563e1fc7a0249e2d65a4be23`.

### Server 2.3.229 — R39 v65 inherited-namespace repair

**Status:** concurrent runtime event preserved; this governance pass did not modify it.  
**LALM Engine:** `2.1.76` / `v65`.  
**Chat:** `1.5.65` unchanged.  
**Deployment / restart:** not performed by Server 2.3.230.

Runtime authority advanced concurrently from the previous v64 lineage to revision `2.1.76-hot-v61-complete-inherited-namespace-v65`. Server 2.3.230 re-read and preserved that authority before assigning its own Server version.

### Server 2.3.228 — Programming-LALM architecture reconciliation curriculum

**Status:** source complete.  
**Affected module versions:** none.

Added the explicit architecture-reconciliation execution protocol so the programming LALM can discover owners, trace state/readers/writers/lifecycle, classify overlap, distinguish current authority/live activation/history, and deliberately choose reuse/extension/consolidation/migration/new structure before implementation.

### Server 2.3.227 — R39 v64 complete cold-load namespace repair

**Status:** preserved in lineage; superseded by current LALM v65 authority.

Expanded the R39 cold-load repair lineage and loader cameras while preserving conversation/context-focus behavior.

### Server 2.3.226 — Mandatory pre-feature architecture reconciliation governance

**Status:** source complete.

Made architecture reconciliation mandatory before feature/fix/optimization/refactor work and required a durable architecture-reconciliation note in the release record.

### Earlier releases

Earlier detailed release entries remain in Git history and `docs/releases/`. This compact roadmap intentionally emphasizes the current architecture and recent lineage rather than duplicating every historical record into one ever-growing file.

---

## Roadmap operating principle

A future project-work event should leave this ledger able to answer:

- What is the current Server baseline?
- Which modules actually changed?
- What architecture owner was used?
- What competing/legacy work was found or retired?
- What camera/log evidence supported issue diagnosis?
- What verification level passed?
- Did deployment/restart happen?
- What concurrency or failed-event lineage must future work preserve?

If current module authorities disagree with the snapshot at the top of this document, the module-owned authorities win and the roadmap must be reconciled during the next governed event.