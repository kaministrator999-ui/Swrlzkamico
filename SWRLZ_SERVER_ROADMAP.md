# §wyrlz Server Roadmap & Version Ledger

**Role:** durable chronological memory of Server/module evolution, architecture decisions, diagnostics, verification, deployment state, and completed project progress.

**Startup/read order is owned by `SWRLZ_PROJECT_START.md`.** This ledger reports what happened; it does not redefine the operating workflow.

## Current authoritative baseline

- **Overall Server:** `2.3.252`
- **Chat:** `1.5.75`
- **LALM Engine:** `2.1.82` (`v70` coding-terminal + fence-repair hardening)
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

### Server 2.3.252 — R39 v70 coding-terminal + bounded-repair hardening

**Status:** runtime-hot source complete; deterministic repair acceptance passed; v70 live-hydrated; authenticated coding-turn completion acceptance pending.  
**LALM Engine:** `2.1.82` / `v70`.  
**Chat:** `1.5.75` unchanged by this event.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Triggering evidence:** the authenticated v69 standalone Python test proved the lightweight-context repair itself worked: v69 compacted nine Brain-owned policy records / about 16.8k characters to one / 364 characters, rendered a 444-token prompt, and inference prefetched 656 tokens rather than the prior 3,839-token baseline. The old render `NameError` was gone. After successful prefill, however, the first coding candidate ended after roughly two decode steps with only an opening Python-fence fragment. The inherited v27 requirement owner detected `runnable-code`, ran its one bounded repair, and that repair also failed, leaving duplicated opening-fence fragments. The request had zero reconnects, excluding worker handoff as the cause.

**Architecture reconciliation:** this is Brain/LALM ownership. Chat correctly relayed/persisted the model failure. The canonical semantic artifact/repair owner already exists in the v27 lineage, so v70 extends that owner rather than adding another repair system. The inherited v17 generation loop already consults a dynamic completion-gap helper before accepting EOS. v70 hardens that boundary specifically for empty/bare coding fences and normalizes v27 repair conditioning when the prior candidate consists only of an opening Python fence. v69 context compaction remains preserved.

**Repair:** a bare opening `python`/`py` fence can no longer lose `complete-code` or `requested-explanation` completion gaps. When `runnable-code` repair follows such a candidate, the broken assistant fence is removed from repair-history conditioning and the correction pass is instructed to continue inside the already-visible fence, emit executable Python instead of another opener, close that fence once, then provide the requested explanation. A bounded `coding-candidate-terminal` camera now classifies first/repair terminal source and counts without logging response text; `coding-fence-repair-normalized` records activation of the fence-continuation normalization.

**Diagnostic refinement:** live v70 hydration/self-test showed the inherited pre-v70 completion checker already returned both `complete-code` and `requested-explanation` for a bare opening Python fence. Therefore the original early terminal was not caused by the gap checker mistakenly accepting the fence as complete. The lower terminal source is the remaining diagnostic question; the new terminal-boundary camera will identify it on the next authenticated coding request.

**Verification:** production `/api/lalm/status` reports `2.1.82`, revision `2.1.82-hot-coding-terminal-repair-v70`, `interactiveReady=true`, v69 preserved, coding bare-fence completion hardening active, v27 fence-continuation repair active, candidate-terminal camera active, and the complete v70 deterministic self-test green. End-to-end success remains pending one normal authenticated coding turn; source/runtime hydration is not being mislabeled as successful coding completion.

**Concurrency:** final version gate observed Server `2.3.251`, LALM `2.1.81`, Chat `1.5.75`; no affected authority moved before assignment. This event therefore owns Server `2.3.252` and LALM `2.1.82`. Chat is unchanged.

**Lineage:** v70 source `d35c55aed8a1d83550e6639af70759fe0b310554`; hot entry `83ab61aba5ca46f858684130a008f557cec176dd`; manifest `1244d12d607302154b1047f6c9b0f57baecdbeb3`; LALM authority `8412b52261d389525539a5c0df21b3d877deca0e`; Server authority `7b9487e7304f512fb020128f033022265b08e840`; dedicated receipt `docs/releases/SERVER_2.3.252_R39_V70_CODING_TERMINAL_REPAIR.md`.

### Server 2.3.250–2.3.251 — Preserved concurrent Chat/runtime lineage

**Status:** preserved from canonical runtime authorities.  
**Observed baseline before v70:** Server `2.3.251`, Chat `1.5.75`, LALM `2.1.81`.

These independent events advanced runtime/Chat authority after the v69 release. This roadmap intentionally does not invent their feature details; their runtime commits/event-specific records remain the source for those changes. Server 2.3.252 preserved them and changed only the LALM plus overall Server authority.

### Server 2.3.249 — R39 v69 lightweight-programming prefill + bounded render repair

**Status:** source/runtime/live compaction accepted; later authenticated user turn exposed a separate post-prefill coding-terminal defect handled by Server 2.3.252.  
**LALM Engine:** `2.1.81` / `v69`.  
**Chat:** `1.5.74` unchanged by this event.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Triggering live evidence:** the first authenticated standalone programming turn after v68 proved Phase 1 routing end to end. Request `web:mu5vbli6:11914080611097954501` emitted `v68-enter` and `programming-mode` with `projectContext=none`, `architectureDepth=lightweight`, and no architecture reconciliation, diagnostics, project coaching, or tool-evidence requirement. This closed the earlier v68 uncertainty about whether the programming route could be reached by a real authenticated Chat turn.

The same request exposed a prefill/context avalanche: canonical Chat history reported zero prior messages while the final LALM payload contained nine internally injected system-policy records totaling about 16.8k characters, producing a 3,839-token prefill at roughly 10–11 tokens/s for a 200-character Python request. Those records were Brain-owned policy wrappers, not leaked canonical user history.

A second camera defect was also localized: the bounded v42 rendered-prompt camera emitted `render-error: NameError` because it referenced historical bare-global `_get_model`, whose canonical implementation remains `_impl._get_model`. Generation continued, proving this was a diagnostic-path namespace failure rather than the fatal v68 generation defect.

**Architecture reconciliation:** v69 changes only LALM/Brain ownership. It compacts recognized §wyrlz-owned policy messages only for existing classifier state `projectContext=none` + `architectureDepth=lightweight`, replacing the redundant long policy stack with one bounded lightweight-programming marker at the final pre-inference boundary. User/assistant dialogue and unknown system messages are preserved exactly; non-lightweight turns are untouched. `_get_model` is bridged back to `_impl._get_model` for the bounded render counter. The legacy v36 token-exact prompt trace remains explicitly retired so restoring that alias cannot resurrect raw prompt logging.

**Reconnect truth:** Chat continuity was inspected but not changed. Existing releases explicitly define detached model/KV state as worker-local. Same-worker reconnect can replay/follow the live job, while a replacement worker may regenerate from the beginning because there is no durable cross-worker inference checkpoint. v69 mitigates that restart cost for lightweight coding; it does not falsely claim cross-worker compute continuation.

**Acceptance:** a later authenticated v69 Python turn provided the decisive context evidence: `v69-enter` used lightweight programming, compaction changed 9 messages / 16,774 chars to 1 / 364 with `dialoguePreserved=true`, bounded rendering reported 444 tokens with no `render-error`, and the actual inference prefill was 656 tokens. Thus the v69 context/render repair is live verified. That same turn failed only after prefill in the coding terminal/repair path, which is a distinct defect lineage now owned by Server 2.3.252.

**Concurrency:** the main roadmap still displayed Server `2.3.241` when this event began, while runtime authorities had independently advanced through Server `2.3.248` and Chat `1.5.74`. The version gate re-read the module authorities and preserved all intervening work, then assigned LALM `2.1.81` and Server `2.3.249` only.

**Lineage:** v69 source `a47edea4867c8082baddf27b04182430dc92fb31`; hot entry `6003557b9868996b3f7c71cce7694e95680d3d32`; manifest `1a48de48a50735e331cbc689fb5f88ce516993da`; LALM authority `a081434edb9ac5582494e62ec5e8e48c031ad669`; Server authority `78e2852532cee133a26eb69888961fa58f651609`; dedicated receipt `docs/releases/SERVER_2.3.249_R39_V69_LIGHTWEIGHT_PREFILL_REPAIR.md`.

### Server 2.3.242–2.3.248 — Preserved concurrent runtime/Chat lineage

**Status:** preserved from canonical runtime authorities during the v69 event.  
**Observed terminal baseline before v69:** Server `2.3.248`, Chat `1.5.74`, LALM `2.1.80`.

The main roadmap had not yet been reconciled through these independently completed runtime/Chat events when v69 work began. This entry intentionally does not invent their feature details; their runtime authorities and event-specific release receipts remain the source for those changes. Server 2.3.249 preserved them and advanced only the LALM plus overall Server authority.

### Server 2.3.241 — Chat LALM-status ownership reconciliation

**Status:** runtime-hot source complete; static/syntax verified; production status authority live; user-visible refresh acceptance pending.  
**Chat:** `1.5.67`.  
**LALM Engine:** `2.1.80` / `v68` unchanged.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Symptom/evidence:** the mobile drawer could display `Local inference pending` while the same page showed the active LALM version. Current `chat_version.js` already normalized declared `STATUS=active` with `/api/lalm/status`, but the base `web/chat.html` retained an older `paintStatus()` bridge presenter that still wrote `Local inference pending`. `refreshStatus()` calls that legacy presenter after request completion, so it could overwrite the newer LALM status presentation after the canonical status module had correctly painted `active`.

**Live authority evidence:** production `/api/lalm/status` reports LALM `2.1.80`, `engine.available=true`, `readiness.ok=true`, `oneTokenReady=true`, and `interactiveReady=true`. The old pending label therefore represented a presentation-owner race rather than actual LALM readiness.

**Architecture reconciliation:** the Shared Module Status Plane introduced at Server `2.3.231` makes `web/chat_version.js` the Chat-side consumer/normalizer for LALM declared status plus observed health. The older inline bridge presenter remains useful for bridge/settings details but must not become a competing final LALM-status authority. The repair therefore extends the canonical status owner with a bounded compatibility reconciliation around the legacy presenter: bridge/settings behavior runs, then the canonical normalized LALM state is synchronously restored before the browser can present the stale result. The canonical paint owner is explicitly exposed as `chat_version.js`; the legacy writer is marked compatibility-only.

**Change:** `web/chat_version.js` now installs a one-time reconciliation adapter over the historical global `paintStatus()` function. Each legacy bridge-status refresh preserves its original bridge/settings work, then immediately reapplies the already-normalized `window.__swrlzLalmState`; if that normalized state has not yet been established, it schedules the canonical LALM status read. This removes the stale post-request `Local inference pending` terminal presentation without adding a third state source or changing LALM semantics.

**Generation defect relationship:** this event did not modify the LALM. The earlier `_latest_user_text` generation failure was independently repaired by Server `2.3.240` / LALM `2.1.80` v68. Later Server 2.3.249 live evidence closed the authenticated programming-route uncertainty; Server 2.3.252 now owns the distinct post-prefill coding-terminal repair.

**Concurrency:** event entry observed Server `2.3.240`, Chat `1.5.66`, LALM `2.1.80`. The source was changed, then Server and Chat authorities were re-read and remained at the entry values. This event therefore assigns Server `2.3.241` and Chat `1.5.67`; LALM remains `2.1.80` because no LALM source changed.

**Verification:** updated `chat_version.js` passes JavaScript syntax checking. Canonical declared/runtime status evidence agrees on an active v68 LALM. Runtime asset publication and no-deploy verification are checked after this roadmap record. User-visible acceptance requires reloading Chat and confirming the drawer remains on the canonical active state after a request/status refresh.

**Lineage:** Chat status repair `09939f48bc0002f529cb1adfedf2f736113e8c07`; Chat authority `a230bee6b5cf98afdc043ccab3141f4a4f3375aa`; Server authority `fdea0d0cb18bc06891cd4df9693ee5e231d6d278`.

### Server 2.3.240 — R39 v68 canonical latest-user namespace repair

**Status:** runtime-hot repair complete; live hydration + startup-warm verified; later authenticated programming turns confirm route entry.  
**LALM Engine:** `2.1.80` / `v68`.  
**Chat:** `1.5.66` unchanged.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Symptom/evidence:** production generation cameras showed v67 hydrating successfully and then failing with `NameError: name '_latest_user_text' is not defined`. The error propagated through the inherited conversation-state/context-focus path. Existing cameras answered the diagnostic question, so no speculative logging layer was needed.

**Root cause:** the canonical `_latest_user_text` helper already lives in the v17 engine implementation loaded as `_impl`, but later conversation wrappers still referenced the historical bare-global name. The v22 module boundary therefore isolated the real implementation from those inherited callers. The concurrent v67 source-commit typo repair restored the correct v61 source lineage but did not repair this namespace boundary.

**Architecture decision:** preserve one semantic owner. v68 bridges the historical name directly to `_impl._latest_user_text`; it does not create another parser or change prompt semantics. Hydration fails closed if the canonical owner is unavailable.

**Repair/acceptance:** v68 adds a hydration-time namespace self-test covering the helper, inherited conversation-state compiler, and programming classifier. Production `/api/lalm/status` reported `2.1.80`, `interactiveReady=true`, namespace self-test `3/3`, inherited conversation acceptance `9/9`, context-focus acceptance `5/5`, and programming-mode routing `7/7`. A fresh production `/api/server/status` reported `lalm-startup-warm.ready=true` and `phase=server-start-complete`, directly verifying the boundary that previously failed. Later authenticated Python tests emitted the intended programming-mode route, closing the user-turn route acceptance item.

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

**Status:** runtime scaffolded; deterministic routing `7/7`; later lineage live-hydrated through v70 and authenticated programming routing is proven.  
**LALM Engine at event:** `2.1.77` / v66.  
**Chat:** `1.5.66` unchanged.

Phase 1 added conservative programming-task routing, new/existing/lightweight project context, architecture depth, programming continuation inheritance, bounded programming context injection, proportional new-project policy, diagnostic policy, cameras, and generalized routing self-tests. The current v70 lineage preserves that programming classification while retaining v69 lightweight prompt compaction and v70 coding-terminal repair hardening.

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