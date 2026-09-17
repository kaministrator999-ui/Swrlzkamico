# §wyrlz Server Roadmap & Version Ledger

**Role:** durable chronological memory of Server/module evolution, architecture decisions, diagnostics, verification, deployment state, and completed project progress.

**Startup/read order is owned by `SWRLZ_PROJECT_START.md`.** This ledger reports what happened; it does not redefine the operating workflow.

## Current authoritative baseline

- **Overall Server:** `2.3.240`
- **Chat:** `1.5.66`
- **LALM Engine:** `2.1.80` (`v68` latest-user namespace repair)
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

### Server 2.3.240 — R39 v68 canonical latest-user namespace repair

**Status:** runtime-hot repair complete; live hydration + startup-warm verified; authenticated post-v68 Chat generation still awaiting direct evidence.  
**LALM Engine:** `2.1.80` / `v68`.  
**Chat:** `1.5.66` unchanged.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Symptom/evidence:** production generation cameras showed v67 hydrating successfully and then failing with `NameError: name '_latest_user_text' is not defined`. The error propagated through the inherited conversation-state/context-focus path. Existing cameras answered the diagnostic question, so no speculative logging layer was needed.

**Root cause:** the canonical `_latest_user_text` helper already lives in the v17 engine implementation loaded as `_impl`, but later conversation wrappers still referenced the historical bare-global name. The v22 module boundary therefore isolated the real implementation from those inherited callers. The concurrent v67 source-commit typo repair restored the correct v61 source lineage but did not repair this namespace boundary.

**Architecture decision:** preserve one semantic owner. v68 bridges the historical name directly to `_impl._latest_user_text`; it does not create another parser or change prompt semantics. Hydration fails closed if the canonical owner is unavailable.

**Repair/acceptance:** v68 adds a hydration-time namespace self-test covering the helper, inherited conversation-state compiler, and programming classifier. Production `/api/lalm/status` reports `2.1.80`, `interactiveReady=true`, namespace self-test `3/3`, inherited conversation acceptance `9/9`, context-focus acceptance `5/5`, and programming-mode routing `7/7`. A fresh production `/api/server/status` reports `lalm-startup-warm.ready=true` and `phase=server-start-complete`, directly verifying the boundary that previously failed.

**Remaining truth state:** no authenticated post-v68 Chat request has yet emitted a `v68-enter` generation camera. Production Chat correctly requires its private browser/admin credential, and this event did not bypass that authority merely to manufacture a test. Full user-turn generation therefore remains pending direct evidence; startup/runtime activation is live verified.

**Concurrency:** the event entered around Server `2.3.238` / LALM `2.1.79` v67. A separate project-response identity event advanced Server to `2.3.239` during the repair. The final version gate preserved it, then assigned LALM `2.1.80` and Server `2.3.240` from current authority.

**Lineage:** v68 source `9420c0e02b63821c1271ad38c6f826b00c3b013c`; active entrypoint `d6a1a1839a28580b18d104de441c3fd06b5afa07`; manifest `35a39b10f9eb77092c36f71a9f16a2a732ceabf2`; LALM authority `72ced3419d1d0f6678f00f62f169168143880e6e`; Server authority `6f5b8b5200b94e28774ce46c2ee15005d8dcdd7d`. Dedicated receipt: `docs/releases/2.3.240-r39-v68-latest-user-namespace-repair.md`.

### Server 2.3.239 — Large centered §wyrlz project-response identity opener

**Status:** source complete / governance contract updated.  
**Changed runtime modules:** none.  
**Chat:** `1.5.66` unchanged.  
**LALM Engine:** `2.1.79` unchanged by this event.  
**Deployment / restart:** none requested or performed.

Project Start now requires governed project-work responses to begin with the exact large centered identity mark `𓆩⁽§⁾wyrlz𓆪`, while the Project Work Response Standard continues to own the structure after that opener. This concurrent event was preserved by Server 2.3.240.

### Server 2.3.238 — v67 R39 lineage repair

**Status:** runtime/LALM lineage repair preserved.  
**LALM Engine:** `2.1.79`, revision `2.1.79-hot-v66-programming-context-v65-lineage-repair-v67`.  
**Chat:** `1.5.66` unchanged.

Corrected a pinned v65 → v61 source commit typo and restored intended lineage hydration. Later live evidence proved a separate inherited `_latest_user_text` namespace defect remained; Server 2.3.240 repaired that without rewriting the v67 fix.

### Server 2.3.237 — Fail-closed Vercel Git gate + source-bound manual production verification

**Status:** source/config complete; automatic-Git gate verified with multiple no-deploy canaries.  
**Deployment Control:** `1.0.8`.  
**LALM Engine:** `2.1.78` / v66 camera-lineage revision unchanged by this event.  
**Chat:** `1.5.66` unchanged.

A docs-only `main` commit unexpectedly created a native-Git production deployment even though `git.deploymentEnabled=false` was already present. The repair preserved the explicitly approved GitHub Actions/Vercel CLI workflow as canonical deployment owner, added the GitHub compatibility guard `github.enabled=false`, and changed manual acceptance to bind production to the exact approved source SHA and stable server version derived from `api/index.py`. Multiple subsequent `main` commits remained deployment-inert.

### Server 2.3.235–2.3.236 — Concurrent v66 camera-lineage activation work

**Status:** preserved concurrent runtime/LALM lineage.  
**LALM Engine:** advanced to `2.1.78`, revision `2.1.78-hot-programming-mode-context-v66-camera-lineage`.

### Server 2.3.234 — R39 v66 same-LALM programming mode runtime scaffold

**Status:** runtime scaffolded; deterministic routing `7/7`; later lineage now live-hydrates through v68.  
**LALM Engine at event:** `2.1.77` / v66.  
**Chat:** `1.5.66` unchanged.

Phase 1 added conservative programming-task routing, new/existing/lightweight project context, architecture depth, programming continuation inheritance, bounded programming context injection, proportional new-project policy, diagnostic policy, cameras, and generalized routing self-tests. The current v68 lineage preserves this programming context and verifies the classifier during hydration.

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
