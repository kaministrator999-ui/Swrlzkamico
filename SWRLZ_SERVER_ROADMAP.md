# §wyrlz Server Roadmap & Version Ledger

**Role:** durable chronological memory of Server/module evolution, architecture decisions, diagnostics, verification, deployment state, and completed project progress.

**Startup/read order is owned by `SWRLZ_PROJECT_START.md`.** This ledger reports what happened; it does not redefine the operating workflow.

## Current authoritative baseline

- **Overall Server:** `2.3.234`
- **Chat:** `1.5.66`
- **LALM Engine:** `2.1.77` (`v66`)
- **Web Frontend:** `1.0.5`
- **LALM UI:** `1.0.0`
- **Frozen Web Collector:** `1.0.9`
- **Deployment Control:** `1.0.7`

`VERSION.txt` and the referenced `versions/<module-id>.txt` files remain the version/status authorities. This roadmap is history/lineage and must be reconciled to those owners rather than treated as a competing version source.

---

## Current project-work contract

Project development is routed from `SWRLZ_PROJECT_START.md` to canonical owners:

- Hotfix/deployment mechanics → `SWRLZ_HOTFIX_RULES.md`
- Server/module lineage → `SWRLZ_VERSION_MODULE_EVOLUTION.md`
- Architecture reconciliation → `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`
- Project-wide cameras/logs → `SWRLZ_CHAT_CAMERA_LOGS.md`
- Project-work response/readability → `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md`
- User-project architecture teaching → `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md`
- Programming-LALM target + implementation truth → `docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md`

---

## Release ledger

### Server 2.3.234 — R39 v66 same-LALM programming mode runtime scaffold

**Status:** source complete / static routing verified / runtime scaffolded / live activation pending.  
**LALM Engine:** `2.1.77` / `v66`.  
**Chat:** `1.5.66` unchanged.  
**Deployment / restart:** NONE.

This is Phase 1 of the Programming LALM Runtime Architecture. The primary §wyrlz LALM now has an executable programming-mode scaffold rather than documentation alone.

**Architecture reconciliation:** the active v65 lineage already owned conversation/context-focus, response planning, continuation, cameras, and hot-loader behavior. No separate coding-model or programming compiler was present. The change therefore extends the canonical LALM owner rather than creating a second cognitive subsystem. A separate coder model remains deferred and, if added later, must be subordinate to the primary LALM architecture contract.

**Implemented in v66:**

- conservative coding-task routing;
- `projectContext = none/new/existing`;
- `changeClass = explain/create/feature/fix/refactor/migrate/deploy/review`;
- `architectureDepth = lightweight/normal/deep`;
- architecture-reconciliation, diagnostics, project-coaching, and tool-evidence flags;
- bounded inheritance of programming mode across continuation turns such as `keep going` / `let's do this`;
- stop/cancel suppression so programming mode does not tunnel through an explicit stop;
- a programming context compiler that injects the architecture operating grammar into a copied generation payload rather than mutating canonical persisted history;
- existing-project policy: inspect evidence before inventing owners, trace authority/state/readers/writers/lifecycle, and prefer reuse → extend → consolidate → migrate+retire → genuinely new structure;
- new-user-project policy: proportional architecture with user-controlled simplification of optional structure;
- lightweight standalone-code policy that avoids unnecessary repository ceremony;
- fix/debug policy that prefers existing evidence before new instrumentation;
- explicit permission boundary: programming mode does not authorize file writes, tools, deployment, spending, or bypass of user/server gates;
- bounded `programming-mode` camera telemetry without intentional prompt/response text;
- deterministic in-engine routing self-tests for seven generalized behavior classes.

**Hot activation lineage:** v66 source was published as immutable runtime source, `runtime_hot/r39_engine.py` was advanced to fetch that immutable commit, and `runtime_hot/manifest.json` was reconciled from its stale v61 revision label to `2.1.77-hot-programming-mode-context-v66`.

**Static verification:** the exact v66 source was locally syntax-compiled before publication. The classifier/context self-test passed all 7/7 cases, including non-programming exclusion, lightweight code explanation, existing-project feature/debug routing, simple new webpage coaching, cross-cutting migration depth, and conversational programming continuation.

**Live verification:** production logs were queried against the current production deployment after publication. The narrow window contained no `SWRLZ_R39_HOT_ENTRY` records at all, so there was no request available to prove or disprove v66 hydration. Therefore the event is **not** labeled live verified. The next actual R39 request can provide activation evidence through the hot-entry and programming-mode cameras.

**Implementation truth:** `runtime scaffolded`. It is **not yet** `tool-integrated`, full architecture acceptance is not yet deterministically evaluated, a live programming mission has not yet been verified, no coder specialist exists, and no model weights were trained/fine-tuned for this behavior.

**Still future work:** programming obligation ledger, repository-evidence/authority-map compiler, overlap/integration state grounded in actual tool evidence, architecture-aware completion/patch acceptance, repository/tool action loop, richer project-scale adaptation, optional coder specialist benchmarks, and training only after strong generalized evals.

**Lineage:** v66 source commit `3b2379eecd3f68d2aec20ae9839f156b9d79e175`; hot entrypoint commit `a1d371983f551c5e394614b39e67b0c3e2e2391a`; hot manifest commit `fc1e84d86629348a86ddd8d1f69eecb8c9bacde0`; LALM authority commit `3f0a7e250bf99efbfc80e73d35c066122b67faab`; Server authority commit `49f22cd94defd44c4ace0d8ed069eae9e75294cd`; programming-runtime spec update `8d2f2c0f769381d5a6497f6ff02a32e577c457f3`.

### Server 2.3.233 — Programming-LALM runtime architecture and model-specialization decision

**Status:** documentation/target architecture complete; superseded by Phase 1 runtime scaffold status for programming-mode implementation.  
**LALM Engine at event:** `2.1.76` / `v65`.  
**Deployment / restart:** NONE.

Established one primary LALM as project/cognitive authority, same-model-first programming specialization, the subordinate-only future coder-model boundary, the implementation-truth ladder, and the phased coding architecture roadmap.

### Server 2.3.232 — Canonical Redis lifecycle repair

**Status:** concurrent runtime event preserved.

Separate Redis lifecycle work advanced Server authority before the programming architecture event; later programming work preserved it rather than overwriting its lineage.

### Server 2.3.231 — Shared module status plane

**Status:** preserved.  
**Chat:** advanced to `1.5.66`.

Normalized shared declared-module status and observed-health behavior. Later programming events preserved Chat `1.5.66`.

### Server 2.3.230 — Project-work governance, diagnostics, reporting, and architecture coaching

**Status:** source complete / governance contract verified.

Reconciled Project Start as the canonical router, made issue work automatically inspect accessible evidence and add bounded cameras only when needed, introduced the response/readability standard, broadened cameras/logs project-wide, and established proportional architecture coaching for user projects.

### Server 2.3.229 — R39 v65 inherited-namespace repair

**Status:** preserved in lineage.  
**LALM Engine:** `2.1.76` / `v65` at that event.

Advanced the cold-load-safe v65 lineage while preserving v61 context-focus behavior.

### Server 2.3.228 — Programming-LALM architecture reconciliation curriculum

**Status:** source complete.

Added the architecture-reconciliation execution protocol: discover owners, trace state/readers/writers/lifecycle, classify overlap, distinguish current authority/live activation/history, and deliberately choose reuse/extension/consolidation/migration/new structure.

### Server 2.3.226 — Mandatory pre-feature architecture reconciliation governance

**Status:** source complete.

Made architecture reconciliation mandatory before feature/fix/optimization/refactor work and required a durable reconciliation note.

### Earlier releases

Earlier detailed release records remain in Git history and `docs/releases/`. This compact roadmap emphasizes current architecture and recent lineage rather than duplicating every historical event indefinitely.

---

## Roadmap operating principle

Future work should leave this ledger able to answer:

- What is the current Server/module baseline?
- Which architecture owner was changed?
- What existing/competing work was reconciled?
- What cameras/log evidence supported diagnosis or activation?
- What verification level passed?
- For programming/model work, is capability **documented, runtime scaffolded, tool-integrated, deterministically evaluated, live verified, or learned/trained**?
- Did deployment/restart happen?
- What concurrency/failure lineage must future work preserve?

If module authorities disagree with this snapshot, module-owned authorities win and the roadmap must be reconciled during the next governed event.
