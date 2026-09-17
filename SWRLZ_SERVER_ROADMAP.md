# §wyrlz Server Roadmap & Version Ledger

**Role:** durable chronological memory of Server/module evolution, architecture decisions, diagnostics, verification, deployment state, and completed project progress.

**Startup/read order is owned by `SWRLZ_PROJECT_START.md`.** This ledger reports what happened; it does not redefine the operating workflow.

## Current authoritative baseline

- **Overall Server:** `2.3.237`
- **Chat:** `1.5.66`
- **LALM Engine:** `2.1.78` (`v66` camera-lineage revision)
- **Web Frontend:** `1.0.5`
- **LALM UI:** `1.0.0`
- **Frozen Web Collector:** `1.0.9`
- **Deployment Control:** `1.0.8`

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

### Server 2.3.237 — Fail-closed Vercel Git gate + source-bound manual production verification

**Status:** source/config complete; automatic-Git gate verified with multiple no-deploy canaries.  
**Deployment Control:** `1.0.8`.  
**LALM Engine:** `2.1.78` / v66 camera-lineage revision unchanged by this event.  
**Chat:** `1.5.66` unchanged.  
**Deployment / restart:** one unintended native-Git production deployment was observed **before** this repair; no production deployment was intentionally triggered by the repair event.

**Triggering defect:** a documentation-only `main` commit (`88eed351f6e768d3da544a5cd0c69aeb8f17545e`) created production deployment `dpl_FPM6etnF9ZMHVeVmhx7AnLMSCwCe`. Vercel identified its source as `git`, target `production`, branch `main`. This contradicted the project contract that documentation/governance commits are deployment-inert.

**Architecture reconciliation:** deployment had two effective writers: the intended explicitly approved GitHub Actions/Vercel CLI path and an unintended native Git integration path. Inspection proved the unexpectedly deployed commit already contained `git.deploymentEnabled=false`, so merely re-adding the modern guard would not repair the observed behavior. Vercel documentation also exposes a GitHub-specific compatibility kill switch. The integration decision was therefore to preserve the manual CLI deployment owner and harden native Git to fail closed with both declarations rather than add another deployment mechanism.

**Git gate repair:** `vercel.json` now retains the modern `git.deploymentEnabled=false` declaration and adds the GitHub-specific compatibility guard `github.enabled=false`. The dual guard is intentional because observed production behavior showed the modern declaration alone was insufficient in this project/integration state.

**Manual workflow repair:** `.github/workflows/manual-vercel-production.yml` no longer hardcodes stable server `2.3.110`. The workflow now:

- captures the exact SHA of the approved checked-out source;
- derives the stable server version from canonical `VERSION` in `api/index.py` using Python AST parsing;
- deploys through the explicit Vercel CLI path only after its existing approval gate;
- requires `/api/server/status` to report the derived stable version;
- requires `deploymentCommit` to equal the exact approved source SHA;
- requires `deploymentEnvironment=production`;
- preserves manifest-authority, continuity, RMCCA, and collector acceptance checks.

This explicitly separates the stable deployed server authority (`api/index.py`, currently `2.3.111`) from the runtime-hot overall Server lineage (`versions/server-runtime.txt`).

**Canary verification:** after the dual guard was committed, Vercel deployment history showed no new production deployment. A second `main` commit modifying the manual deployment workflow also produced no new deployment. Later engineering-contract commits in this same closure sequence are checked against the same deployment history before final acceptance. The pre-repair docs deployment remains the newest production deployment unless an explicitly approved manual deployment occurs.

**Hotfix contract update:** `SWRLZ_HOTFIX_RULES.md` now records automatic Git as fail-closed, the explicitly approved manual workflow as canonical production deployment owner, source-SHA-bound deployment acceptance, and the requirement to verify platform behavior rather than trust config text alone.

**Concurrency reconciliation:** this repair began after Server `2.3.234`, while concurrent runtime/LALM work advanced Server through `2.3.236` and LALM to `2.1.78` / v66 camera-lineage. The event re-read current authorities, preserved those advances, bumped only Deployment Control (`1.0.7 → 1.0.8`), then assigned Server `2.3.237` from the current `2.3.236` authority.

**Additional live evidence discovered during diagnosis:** production logs now prove the v66 hot entrypoint hydrated successfully with `hotServerVersion=2.1.77`, revision `2.1.77-hot-programming-mode-context-v66`, and callable programming-profile/programming-context contracts. Subsequent concurrent camera-lineage work advanced the LALM authority to `2.1.78`; this Server 2.3.237 event did not modify that LALM source. Thus the Phase 1 programming runtime is no longer merely awaiting loader-level activation evidence; v66 hydration is proven live, while full programming-mission/tool-loop acceptance remains later work.

**Lineage:** Vercel dual Git guard `492b23f56bb4533c448da47adf7f15b6f622b09d`; manual source-bound verification `9fdab0ea4ab72747b471cabd942702d5f1959cb1`; Deployment Control authority `717d4ed563c48fec551ae66a0059b4507eff5c64`; Server authority `7dfe75b6f5c5c94bbcec8aceed894bf366aeb118`; Hotfix contract repair `62dfae9abd0f9af152b64d224cf14d6b5a520a2e`.

### Server 2.3.235–2.3.236 — Concurrent v66 camera-lineage activation work

**Status:** preserved concurrent runtime/LALM lineage.  
**LALM Engine:** advanced to `2.1.78`, revision `2.1.78-hot-programming-mode-context-v66-camera-lineage`.

These events advanced inherited camera/activation lineage around v66 while Server 2.3.237 deployment-control work was in progress. Server 2.3.237 preserved them rather than reusing stale planned versions.

### Server 2.3.234 — R39 v66 same-LALM programming mode runtime scaffold

**Status:** runtime scaffolded; static routing suite passed 7/7; loader-level live hydration is now verified by later production evidence.  
**LALM Engine at event:** `2.1.77` / v66.  
**Chat:** `1.5.66` unchanged.  
**Deployment / restart at event:** none intentionally performed for the runtime-hot v66 change.

Phase 1 added conservative coding-task routing, new/existing/lightweight project context, change class and architecture depth, architecture/diagnostic/project-coaching flags, bounded programming continuation inheritance, stop suppression, a copied-payload programming context compiler, proportional new-project architecture behavior, existing-project reconciliation grammar, programming cameras, and seven generalized deterministic routing cases.

The later production hot-entry evidence shows v66 fetched immutable source `3b2379eecd3f68d2aec20ae9839f156b9d79e175` and completed hydration with planner, response-contract, conversation-state, programming-profile, programming-context, and camera contracts present. That proves loader-level live activation; it does not by itself prove the future repository/tool execution loop or architecture-acceptance phases.

### Server 2.3.233 — Programming-LALM runtime architecture and model-specialization decision

**Status:** target architecture established.

Established one primary LALM as project/cognitive authority, same-model-first programming specialization, a subordinate-only future coder-model boundary, the implementation-truth ladder, and phased coding architecture roadmap.

### Server 2.3.232 — Canonical Redis lifecycle repair

**Status:** preserved concurrent runtime event.

### Server 2.3.231 — Shared module status plane

**Status:** preserved.  
**Chat:** advanced to `1.5.66`.

### Server 2.3.230 — Project-work governance, diagnostics, reporting, and architecture coaching

**Status:** source complete / governance contract verified.

Reconciled Project Start as canonical router, made issue work inspect accessible evidence automatically, introduced the response/readability standard, broadened cameras/logs project-wide, and established proportional architecture coaching for user projects.

### Server 2.3.229 — R39 v65 inherited-namespace repair

**Status:** preserved in lineage.

### Server 2.3.228 — Programming-LALM architecture reconciliation curriculum

**Status:** source complete.

Added the architecture-reconciliation execution protocol: discover owners, trace state/readers/writers/lifecycle, classify overlap, distinguish current authority/live activation/history, and choose reuse/extension/consolidation/migration/new structure deliberately.

### Server 2.3.226 — Mandatory pre-feature architecture reconciliation governance

**Status:** source complete.

---

## Roadmap operating principle

Future work should leave this ledger able to answer:

- What is the current Server/module baseline?
- Which architecture owner was changed?
- What existing/competing work was reconciled?
- What cameras/log evidence supported diagnosis or activation?
- What verification level passed?
- For programming/model work, is capability **documented, runtime scaffolded, tool-integrated, deterministically evaluated, live verified, or learned/trained**?
- Did deployment/restart happen, and through which authority?
- Did any Git commit unexpectedly become a deployment writer?
- What concurrency/failure lineage must future work preserve?

If module authorities disagree with this snapshot, module-owned authorities win and the roadmap must be reconciled during the next governed event.
