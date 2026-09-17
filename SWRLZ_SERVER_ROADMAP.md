# §wyrlz Server Roadmap & Version Ledger

**Role:** durable chronological memory of Server/module evolution, architecture decisions, diagnostics, verification, deployment state, and completed project progress.

**Startup/read order is owned by `SWRLZ_PROJECT_START.md`.** This ledger reports what happened; it does not redefine the operating workflow.

## Current authoritative baseline

- **Overall Server:** `2.3.255`
- **Chat:** `1.5.75`
- **LALM Engine:** `2.1.85` (`v73` inherited n-gram NumPy namespace repair)
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

### Server 2.3.255 — R39 v73 inherited n-gram NumPy namespace repair

**Status:** source complete; static threshold acceptance passed; published with live worker/user-turn activation pending.  
**LALM Engine:** `2.1.85` / `v73`.  
**Chat:** `1.5.75` unchanged.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Triggering evidence:** authenticated request `web:mu5zycye:4201205958924473599` showed both the first coding candidate and bounded repair terminating `FAILED / inference-failed` after exactly two decode steps and nine characters. Completion gaps remained armed, the degeneration guard had not fired, and v70 fence normalization activated correctly. Source inspection then found the exact two-token threshold in v55: `_ngram_guarded_sample` delegates while history has fewer than two tokens, but at history length two it first executes `np.argpartition(...)`; v55 never imported NumPy into the exec-shared hot namespace.

**Architecture reconciliation:** this is Brain/LALM inherited decode-policy ownership. Chat, persistence, v69 context compaction, and v70 semantic repair are not the cause. v73 preserves the v55 n-gram sampler as semantic owner and repairs only its missing inherited `np` dependency at the current hot edge.

**Repair:** v73 hydrates immutable v72, restores NumPy in the shared namespace after the full inherited exec chain loads, fail-closes if the n-gram sampler is absent, and runs a hydration self-test that calls `_ngram_guarded_sample` with a two-token history to deliberately cross the exact branch that previously failed before token three. v72 diagnostics and all v71/v70/v69 programming behavior remain preserved.

**Verification:** immutable v73 source was re-fetched from its exact commit; syntax compilation passed; the hot entry and manifest now select revision `2.1.85-hot-ngram-numpy-namespace-repair-v73`; version authorities were re-read immediately before assignment and had not advanced. A fresh production worker has not yet emitted v73 hydration/user-turn evidence, so end-to-end coding success remains pending one normal authenticated request.

**Concurrency:** the version gate observed Server `2.3.254`, LALM `2.1.84`, Chat `1.5.75`; affected authorities remained unchanged before assignment. This event therefore owns Server `2.3.255` and LALM `2.1.85` only.

**Lineage:** v73 source `023ac7efdabbe8c317490bc23f410e3a370b5eaf`; hot entry `90ac4c548506d25b1a6f61c0dd15098dccc88b31`; manifest `6eeb60934e8b119e38c61b486da0739e5ded92ba`; LALM authority `fa2b37776f5f3a76fc8b3388ef3527e0ddc2b529`; Server authority `5263ae849029674c29bb66b4404ccd1b60044692`; dedicated receipt `docs/releases/SERVER_2.3.255_R39_V73_NGRAM_NUMPY_NAMESPACE_REPAIR.md`.

### Server 2.3.254 — R39 v72 coding inference failure-detail camera

**Status:** diagnostic source complete/static verified; superseded at the active edge by v73 before a live v72 candidate failure was needed.  
**LALM Engine:** `2.1.84` / `v72`.  
**Chat:** `1.5.75` unchanged.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Triggering state:** v71 correctly classified the two-token candidate terminals as `inference-failed`, but intentionally did not retain the underlying base-generator exception type/detail. The base v17 generator already emitted a bounded error category and Python exception message, leaving a narrow diagnostics gap at the v27 candidate boundary.

**Architecture reconciliation:** this was Brain/LALM instrumentation only. v72 preserved response semantics and wrapped the existing first/repair candidate generator rather than adding another repair owner.

**Change:** v72 adds bounded `coding-inference-terminal-detail` evidence containing failure category, Python exception type, and a short sanitized detail preview while preserving the original terminal event unchanged. It logs no prompt/response body, secret, or hidden reasoning.

**Verification/lineage:** source, hot entry, manifest, and module authorities were published and source/static checked. Before a real v72 failure was required, repository inspection of the inherited sampler exposed the deterministic cause and v73 repaired it. v72 remains preserved in v73 for any lower failure that survives. Source `3c41765183650793ad6c4c552c2d2a2cc5db6056`; hot entry `0447348f81d1d3b9b00e50a06327fd103dcb459a`; manifest `bafb39d94fee30e98c2904b26eb6ce1963d5839e`; LALM authority `6d065f71b7b0215a69cf68fe243cd3a931a55461`; Server authority `261ca08045078516aa37750b8ae07c2103d0e312`; receipt `docs/releases/SERVER_2.3.254_R39_V72_CODING_INFERENCE_FAILURE_DETAIL.md`.

### Server 2.3.253 — R39 v71 coding-terminal camera-contract namespace repair

**Status:** runtime-hot source complete; v71 live-hydrated; camera-contract self-test live verified; authenticated coding turn proved the lower terminal was `inference-failed`.  
**LALM Engine:** `2.1.83` / `v71`.  
**Chat:** `1.5.75` unchanged by this event.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Triggering state:** v70 already owned the coding-terminal + bounded-repair hardening and added the bounded `coding-candidate-terminal` camera. During closure, the exec-based inherited lineage exposed a diagnostics-only namespace collision: v70 used the generic global `_CONTRACT`, and nested hydrated layers could overwrite that name before the camera/self-test resolved it. The generation/repair behavior itself remained owned by v70.

**Architecture reconciliation:** this is Brain/LALM compatibility instrumentation, not another repair system. v71 preserves the v70 semantic owner and repairs only the camera-contract namespace. Chat persistence/transport, v69 context compaction, deployment infrastructure, and tool authority are unchanged.

**Repair:** v71 hydrates immutable v70, establishes unique `r39-v71-coding-terminal-camera-contract-v1`, restores the dynamically resolved contract after inherited hydration, recomputes/fail-closes the coding-terminal self-test against that contract, and emits `v71-enter` before delegating to v70. No coding-response semantics were changed by v71.

**Verification:** production hot-load logs verified the v71 contract. The later authenticated request `web:mu5zycye:4201205958924473599` exercised the camera: first and repair candidates both reached `FAILED / inference-failed` after exactly two decode steps, ruling out EOS, completion-gap acceptance, degeneration, and Chat transport as the terminal cause.

**Failure/concurrency lineage:** v71 source/entry/manifest had already been published and live-hydrated while canonical authorities still reported Server `2.3.252` / LALM `2.1.82` v70. The restarted repair session preserved the active v71 source and closed lineage as Server `2.3.253` / LALM `2.1.83` rather than duplicating the repair.

**Lineage:** v71 source `b1bfa7eaec5eec7b21b020a7f8d7ec423416d5ab`; hot entry `b25858e67b8b3e7801134263a695034194c68402`; manifest `e03dd747c54c6cf8c4bf3d7128821550771da704`; LALM authority `23b4728072a5808bb0dc88d1309b1c9144bd32a9`; Server authority `6b75f7c9fdb9ca7220683c35dc4ac27c5e882642`; dedicated receipt `docs/releases/SERVER_2.3.253_R39_V71_CAMERA_CONTRACT_REPAIR.md`.

### Server 2.3.252 — R39 v70 coding-terminal + bounded-repair hardening

**Status:** runtime-hot source complete; deterministic repair acceptance passed; v70 live-hydrated; later v71 evidence proved a lower inference failure still existed.  
**LALM Engine:** `2.1.82` / `v70`.  
**Chat:** `1.5.75` unchanged by this event.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Triggering evidence:** the authenticated v69 standalone Python test proved the lightweight-context repair itself worked: v69 compacted nine Brain-owned policy records / about 16.8k characters to one / 364 characters, rendered a 444-token prompt, and inference prefetched 656 tokens rather than the prior 3,839-token baseline. The old render `NameError` was gone. After successful prefill, however, the first coding candidate ended after roughly two decode steps with only an opening Python-fence fragment. The inherited v27 requirement owner detected `runnable-code`, ran its one bounded repair, and that repair also failed, leaving duplicated opening-fence fragments. The request had zero reconnects, excluding worker handoff as the cause.

**Architecture reconciliation:** this is Brain/LALM ownership. Chat correctly relayed/persisted the model failure. The canonical semantic artifact/repair owner already exists in the v27 lineage, so v70 extends that owner rather than adding another repair system. The inherited v17 generation loop already consults a dynamic completion-gap helper before accepting EOS. v70 hardens that boundary specifically for empty/bare coding fences and normalizes v27 repair conditioning when the prior candidate consists only of an opening Python fence. v69 context compaction remains preserved.

**Repair:** a bare opening `python`/`py` fence can no longer lose `complete-code` or `requested-explanation` completion gaps. When `runnable-code` repair follows such a candidate, the broken assistant fence is removed from repair-history conditioning and the correction pass is instructed to continue inside the already-visible fence, emit executable Python instead of another opener, close that fence once, then provide the requested explanation. A bounded `coding-candidate-terminal` camera classifies first/repair terminal source and counts without logging response text; `coding-fence-repair-normalized` records activation of the fence-continuation normalization.

**Diagnostic refinement:** live v70 hydration/self-test showed the inherited pre-v70 completion checker already returned both `complete-code` and `requested-explanation` for the bare fence. Therefore the original early terminal was not caused by the gap checker mistakenly accepting the fence as complete.

**Verification:** production `/api/lalm/status` reported `2.1.82`, revision `2.1.82-hot-coding-terminal-repair-v70`, `interactiveReady=true`, v69 preserved, coding bare-fence completion hardening active, v27 fence-continuation repair active, candidate-terminal camera active, and the complete v70 deterministic self-test green.

**Concurrency:** final version gate observed Server `2.3.251`, LALM `2.1.81`, Chat `1.5.75`; no affected authority moved before assignment. This event therefore owns Server `2.3.252` and LALM `2.1.82`. Chat is unchanged.

**Lineage:** v70 source `d35c55aed8a1d83550e6639af70759fe0b310554`; hot entry `83ab61aba5ca46f858684130a008f557cec176dd`; manifest `1244d12d607302154b1047f6c9b0f57baecdbeb3`; LALM authority `8412b52261d389525539a5c0df21b3d877deca0e`; Server authority `7b9487e7304f512fb020128f033022265b08e840`; dedicated receipt `docs/releases/SERVER_2.3.252_R39_V70_CODING_TERMINAL_REPAIR.md`.

### Server 2.3.250–2.3.251 — Preserved concurrent Chat/runtime lineage

**Status:** preserved from canonical runtime authorities.  
**Observed baseline before v70:** Server `2.3.251`, Chat `1.5.75`, LALM `2.1.81`.

These independent events advanced runtime/Chat authority after the v69 release. This roadmap intentionally does not invent their feature details; their runtime commits/event-specific records remain the source for those changes. Server 2.3.252 preserved them and changed only the LALM plus overall Server authority.

### Server 2.3.249 — R39 v69 lightweight-programming prefill + bounded render repair

**Status:** source/runtime/live compaction accepted; later authenticated user turn exposed a separate post-prefill coding-terminal defect handled by Server 2.3.252 onward.  
**LALM Engine:** `2.1.81` / `v69`.  
**Chat:** `1.5.74` unchanged by this event.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Triggering live evidence:** the first authenticated standalone programming turn after v68 proved Phase 1 routing end to end. Request `web:mu5vbli6:11914080611097954501` emitted `v68-enter` and `programming-mode` with `projectContext=none`, `architectureDepth=lightweight`, and no architecture reconciliation, diagnostics, project coaching, or tool-evidence requirement.

The same request exposed a prefill/context avalanche: canonical Chat history reported zero prior messages while the final LALM payload contained nine internally injected system-policy records totaling about 16.8k characters, producing a 3,839-token prefill at roughly 10–11 tokens/s for a 200-character Python request. Those records were Brain-owned policy wrappers, not leaked canonical user history.

A second camera defect was localized: the bounded rendered-prompt camera emitted `render-error: NameError` because it referenced historical bare-global `_get_model`, whose canonical implementation remains `_impl._get_model`. Generation continued, proving this was a diagnostic-path namespace failure rather than the fatal v68 generation defect.

**Architecture reconciliation:** v69 changes only LALM/Brain ownership. It compacts recognized §wyrlz-owned policy messages only for `projectContext=none` + `architectureDepth=lightweight`, replacing the redundant long policy stack with one bounded lightweight-programming marker. User/assistant dialogue and unknown system messages are preserved exactly; non-lightweight programming requests remain unchanged. `_get_model` is bridged back to `_impl._get_model`; the legacy raw prompt-token trace remains retired.

**Reconnect truth:** Chat continuity was inspected but not changed. Same-worker reconnect can replay/follow the live job, while a replacement worker may regenerate from the beginning because there is no durable cross-worker inference checkpoint. v69 mitigates that restart cost for lightweight coding; it does not falsely claim cross-worker compute continuation.

**Acceptance:** a later authenticated v69 Python turn provided the decisive context evidence: compaction changed 9 messages / 16,774 chars to 1 / 364, bounded rendering reported 444 tokens with no `render-error`, and actual inference prefill was 656 tokens. Thus v69 context/render repair is live verified.

**Concurrency:** the main roadmap still displayed Server `2.3.241` when this event began, while runtime authorities had independently advanced through Server `2.3.248` and Chat `1.5.74`. The version gate preserved all intervening work, then assigned LALM `2.1.81` and Server `2.3.249` only.

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

**Live authority evidence:** production `/api/lalm/status` reported LALM `2.1.80`, `engine.available=true`, `readiness.ok=true`, `oneTokenReady=true`, and `interactiveReady=true`. The old pending label therefore represented a presentation-owner race rather than actual LALM readiness.

**Architecture reconciliation:** the Shared Module Status Plane makes `web/chat_version.js` the Chat-side consumer/normalizer for LALM declared status plus observed health. The older inline bridge presenter remains compatibility-only and must not become a competing final LALM-status authority.

**Change:** `web/chat_version.js` installs a one-time reconciliation adapter over historical `paintStatus()`: bridge/settings work runs, then the canonical normalized LALM state is synchronously restored.

**Concurrency:** event entry observed Server `2.3.240`, Chat `1.5.66`, LALM `2.1.80`. This event assigned Server `2.3.241` and Chat `1.5.67`; LALM remained unchanged.

**Lineage:** Chat status repair `09939f48bc0002f529cb1adfedf2f736113e8c07`; Chat authority `a230bee6b5cf98afdc043ccab3141f4a4f3375aa`; Server authority `fdea0d0cb18bc06891cd4df9693ee5e231d6d278`.

### Server 2.3.240 — R39 v68 canonical latest-user namespace repair

**Status:** runtime-hot repair complete; live hydration + startup-warm verified; later authenticated programming turns confirm route entry.  
**LALM Engine:** `2.1.80` / `v68`.  
**Chat:** `1.5.66` unchanged.  
**Deployment Control:** `1.0.8` unchanged.  
**Deployment / restart:** NONE.

**Symptom/evidence:** production generation cameras showed v67 hydrating successfully and then failing with `NameError: name '_latest_user_text' is not defined` through the inherited conversation-state/context-focus path.

**Root cause / architecture:** canonical `_latest_user_text` already lives in the v17 implementation loaded as `_impl`, while later wrappers referenced the historical bare-global name. v68 bridges directly to `_impl._latest_user_text`; it does not create another parser or change prompt semantics.

**Repair/acceptance:** v68 adds a hydration-time namespace self-test covering the helper, inherited conversation-state compiler, and programming classifier. Production verified `2.1.80`, `interactiveReady=true`, namespace self-test `3/3`, conversation acceptance `9/9`, context-focus acceptance `5/5`, programming routing `7/7`, and startup-warm `ready=true`. Later authenticated Python tests closed the route-entry acceptance item.

**Lineage:** v68 source `9420c0e02b63821c1271ad38c6f826b00c3b013c`; active entrypoint `d6a1a1839a28580b18d104de441c3fd06b5afa07`; manifest `35a39b10f9eb77092c36f71a9f16a2a732ceabf2`; LALM authority `72ced3419d1d0f6678f00f62f169168143880e6e`; Server authority `6f5b8b5200b94e28774ce46c2ee15005d8dcdd7d`.

### Server 2.3.239 — Large centered §wyrlz project-response identity opener

**Status:** source complete / governance contract updated.  
**Changed runtime modules:** none.  
**Chat:** `1.5.66` unchanged.  
**LALM Engine:** `2.1.79` unchanged by this event.  
**Deployment / restart:** none requested or performed.

Project Start requires governed project-work responses to begin with the exact large centered identity mark `𓆩⁽§⁾wyrlz𓆪`, while the Project Work Response Standard owns the structure after that opener.

### Server 2.3.238 — v67 R39 lineage repair

**Status:** preserved. **LALM Engine:** `2.1.79`.

Corrected a pinned v65 → v61 source commit typo and restored intended lineage hydration. Later evidence proved a separate inherited `_latest_user_text` namespace defect remained; Server 2.3.240 repaired it without rewriting v67.

### Server 2.3.237 — Fail-closed Vercel Git gate + source-bound manual production verification

**Status:** source/config complete; automatic-Git gate verified with multiple no-deploy canaries. **Deployment Control:** `1.0.8`.

A docs-only `main` commit unexpectedly produced a native-Git deployment despite `git.deploymentEnabled=false`. The repair preserved the explicitly approved GitHub Actions/Vercel CLI workflow as deployment owner, added `github.enabled=false`, and bound manual acceptance to exact approved source SHA + canonical stable-server version. Subsequent main commits remained deployment-inert.

### Server 2.3.235–2.3.236 — Concurrent v66 camera-lineage activation work

**Status:** preserved concurrent runtime/LALM lineage. **LALM Engine:** advanced to `2.1.78`.

### Server 2.3.234 — R39 v66 same-LALM programming mode runtime scaffold

**Status:** runtime scaffolded; deterministic routing `7/7`; later lineage live-hydrated and authenticated programming routing proven. **LALM Engine at event:** `2.1.77`.

Phase 1 added conservative programming-task routing, project context, architecture depth, continuation inheritance, bounded programming context, proportional new-project policy, diagnostics, cameras, and generalized routing tests.

### Server 2.3.233 — Programming-LALM runtime architecture and model-specialization decision

**Status:** target architecture established.

Established one primary LALM as project/cognitive authority, same-model-first programming specialization, subordinate-only future coder boundary, implementation-truth ladder, and phased coding roadmap.

### Server 2.3.232 — Canonical Redis lifecycle repair

**Status:** preserved concurrent runtime event.

### Server 2.3.231 — Shared module status plane

**Status:** preserved. **Chat:** advanced to `1.5.66`.

### Server 2.3.230 — Project-work governance, diagnostics, reporting, and architecture coaching

**Status:** source complete / governance contract verified.

Reconciled Project Start as canonical router, made issue work inspect accessible evidence automatically, introduced the response/readability standard, broadened cameras/logs project-wide, and established proportional architecture coaching.

### Server 2.3.229 — R39 v65 inherited-namespace repair

**Status:** preserved in lineage.

### Server 2.3.228 — Programming-LALM architecture reconciliation curriculum

**Status:** source complete.

Added architecture reconciliation execution: discover owners, trace state/readers/writers/lifecycle, classify overlap, distinguish current authority/live activation/history, and choose reuse/extension/consolidation/migration/new structure deliberately.

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