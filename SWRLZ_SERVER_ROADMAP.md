# §wyrlz Server Roadmap & Version Ledger

**Role:** durable chronological memory of Server/module evolution, architecture decisions, diagnostics, verification, deployment state, and completed project progress.

**Startup/read order is owned by `SWRLZ_PROJECT_START.md`.** This ledger reports what happened; it does not redefine the operating workflow.

## Current authoritative baseline

The values below were reconciled from current module-owned authorities for this ledger update.

- **Overall Server:** `2.3.233`
- **Chat:** `1.5.66`
- **LALM Engine:** `2.1.76` (`v65`)
- **Web Frontend:** `1.0.5`
- **LALM UI:** `1.0.0`
- **Frozen Web Collector:** `1.0.9`
- **Deployment Control:** `1.0.7`

`VERSION.txt` and the referenced `versions/<module-id>.txt` files remain the version/status identity authorities. This roadmap is lineage/history and must be reconciled to those owners rather than treated as a competing source.

---

## Current project-work contract

Project development is governed by the canonical owners routed from `SWRLZ_PROJECT_START.md`:

- Hotfix/deployment mechanics → `SWRLZ_HOTFIX_RULES.md`
- Server/module lineage → `SWRLZ_VERSION_MODULE_EVOLUTION.md`
- Architecture reconciliation → `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`
- Project-wide cameras/logs → `SWRLZ_CHAT_CAMERA_LOGS.md`
- Project-work response/readability → `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md`
- User-project architecture teaching → `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md`
- Programming-LALM runtime target + implementation truth → `docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md`

Every feature/fix/refactor first reconciles existing architecture. Every issue/debug event automatically inspects available repository/live evidence and adds bounded cameras only when observability is insufficient. Every governed event uses concurrency-safe version assignment and a durable release record. Substantial conversational updates follow the response standard.

---

## Release ledger

### Server 2.3.233 — Programming-LALM runtime architecture and model-specialization decision

**Status:** target architecture/documentation source complete; executable programming subsystem not yet implemented.  
**Affected module versions:** none.  
**LALM Engine:** `2.1.76` / `v65` unchanged.  
**Chat:** `1.5.66` unchanged.  
**Deployment / restart:** NONE.

This event documents the intended relationship between the architecture curriculum, the active LALM, user-project architecture coaching, and a possible future coding-specialist model.

**Architecture reconciliation:** reviewed Project Start, Architecture Reconciliation Protocol, Architecture Coaching Guide, current R39 v65 loader/source, current module authorities, current deployment workflow, and existing engineering docs. The repository had architecture curriculum and coaching guidance but no dedicated runtime/model specification defining how those rules become executable programming behavior or how a future coder model would coexist with the primary LALM. Active v65 preserves conversation/context-focus, response-contract, continuation, and loader/camera behavior, but no dedicated programming-mode compiler or coder-specialist delegation contract was found in the active wrapper lineage.

**Core model decision:** keep **one primary §wyrlz LALM as the cognitive/project authority**. Implement programming capability in the same LALM first through coding-task routing, a programming context compiler, architecture reconciliation state, an obligation ledger, tool/action planning, and architecture-aware acceptance. A dedicated coding model may be added later only as a **subordinate specialist/proposal engine** supplied with a bounded architecture contract by the primary LALM. It must not independently own user intent, project architecture, canonical state, deployment permission, version authority, or final acceptance.

**Internal vs user-project architecture:** the architecture curriculum is intended to become §wyrlz's internal programming operating grammar. The same principles may be applied to projects users build with §wyrlz, but proportionally: tiny projects get lightweight structure; growing/persistent/deployed projects receive stronger ownership/state/test/log/deployment boundaries; optional architecture may be simplified or removed when the user chooses a different tradeoff. The user-facing project does not need to copy §wyrlz's internal repository structure.

**Implementation-truth ladder established:** programming architecture capability must be reported distinctly as **documented → runtime scaffolded → tool-integrated → deterministically evaluated → live verified → learned/trained**. Documentation alone must never be reported as executable or trained model capability.

**Target implementation phases:** Phase 0 curriculum/governance foundation; Phase 1 same-LALM programming mode; Phase 2 programming obligation + architecture acceptance; Phase 3 repository/tool execution loop; Phase 4 user-project architecture adaptation as runtime behavior; Phase 5 optional coder specialist after benchmarking; Phase 6 training/fine-tuning only if justified by generalized evals/traces.

**Why same-model-first:** it preserves one interpretation of user intent/project context, avoids duplicated project memory and competing architecture decisions, reduces model-routing and local-resource complexity, and gives the project a clean evaluation surface before another model is introduced.

**Intentionally unchanged:** no R39 inference source, model weights, prompt runtime, repository execution loop, Chat runtime source, server API, persistence schema, loader, or deployment configuration was changed by this event. No component version was artificially bumped.

**Concurrency reconciliation:** this work began while Server `2.3.231` was current, then concurrent work advanced authority to Server `2.3.232`. The event re-read `VERSION.txt`, Server, LALM, and Chat authorities and assigned `2.3.233` from the newest state. Concurrent Chat `1.5.66` and LALM `2.1.76/v65` were preserved.

**Verification:** the new runtime-architecture specification exists on `main`; Project Start routes programming-LALM/coder work to it and explicitly separates documented curriculum from executable/trained capability; authoritative Server state is `2.3.233`; no LALM or Chat version bump occurred for this documentation-only event.

**Lineage:** Programming LALM Runtime Architecture spec `99266a98f65c917123cce5fdf2614cd7d9259459`; Project Start integration `e3767108bb2dba32a73873585a157b23a029c71c`; Server authority `68860df68d997b5b7f668dc746647726d938495b`.

### Server 2.3.232 — Canonical Redis lifecycle repair

**Status:** concurrent runtime event preserved.  
**LALM Engine:** `2.1.76` / `v65` unchanged by Server 2.3.233.  
**Chat:** `1.5.66` unchanged by Server 2.3.233.

Runtime authority advanced concurrently under commit lineage labeled `Record canonical Redis lifecycle repair`. Server 2.3.233 treated that release as current authority and did not overwrite or reinterpret its implementation.

### Server 2.3.231 — Shared module status plane

**Status:** concurrent runtime/Chat event preserved.  
**Chat:** advanced to `1.5.66`.  
**LALM Engine:** remained `2.1.76` / `v65`.

The concurrent lineage added/normalized shared module declared-status and observed-health behavior and advanced Chat accordingly. Project Start now reflects the version/status distinction and consumer-normalization rules established by that work.

### Server 2.3.230 — Project-work governance, diagnostics, reporting, and architecture coaching

**Status:** source complete / governance contract verified.  
**Affected module versions:** none at that event.  
**Deployment / restart:** NONE.

Reconciled Project Start into the canonical router; made issue diagnostics automatically inspect accessible evidence and add bounded cameras where observability is missing; created the Project Work Response Standard; broadened the camera/log contract project-wide; and added the Architecture Coaching Guide for proportional user-project structure.

### Server 2.3.229 — R39 v65 inherited-namespace repair

**Status:** preserved in lineage.  
**LALM Engine:** `2.1.76` / `v65`.

Advanced the active LALM lineage to the current v65 inherited-namespace/cold-load-safe architecture while preserving v61 context-focus behavior.

### Server 2.3.228 — Programming-LALM architecture reconciliation curriculum

**Status:** source complete.

Added the explicit architecture-reconciliation execution protocol so the programming LALM can discover owners, trace state/readers/writers/lifecycle, classify overlap, distinguish current authority/live activation/history, and deliberately choose reuse/extension/consolidation/migration/new structure before implementation.

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
- For programming/model work, is the capability only documented, runtime-scaffolded, tool-integrated, evaluated, live-verified, or actually trained?
- Did deployment/restart happen?
- What concurrency or failed-event lineage must future work preserve?

If current module authorities disagree with the snapshot at the top of this document, the module-owned authorities win and the roadmap must be reconciled during the next governed event.
