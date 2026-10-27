# §wyrlz Chat Overview — Stage Composition Contract

**Current deployment observation — 2026-10-27:** source `f925e2012ed7ece820e3272700bc6619846c2085` is running at the existing Chat site `https://kamiloki-swyrlz.hf.space`, HF revision `48515f7fc6e8cb7b4450725320e8fed64fb886e6`. HF API reported RUNNING with HEAD equal to runtime SHA, and immutable MODEL_PROVENANCE matches the source. Exact-source CI40439785973, guarded deployment40480347832 and startup recovery40486416861 succeeded. This establishes deployment identity; full 3D editor/project competence remains unaccepted. Canonical module versions are not advanced by this partial closeout. Earlier deployment statements below are dated historical observations superseded by this record. See [checkpoint](entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md).

**Deployed editor/project contracts (2026-10-27, bounded workspace acceptance):** inferred editor-page requests, literal UI labels and new-project boundaries share explicit contracts; both engines now use32K context with4096 normal,8192 project and16384 explicit large-deliverable output allowances, subject to short-format/internal-tool overrides and full-source reservation. Observed finish reasons prevent length-stopped code becoming complete artifacts. Complete multi-file artifacts gain session-owned revision ZIP downloads, bounded at2048 source files/32MiB total/512KiB per file. Default code contracts reject obvious pseudocode and unimplemented placeholders unless requested. See [generation limits](LARGE_GENERATION_BUDGETS.md). ZIP/source validation is distinct from execution. See [current checkpoint](entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md); earlier viewer-only receipts remain historical.

**Chat update history (2026-10-25):** the side menu's Chat updates action opens the latest notes and all 264 earlier recorded Chat update entries. Automatic announcements are scoped to the exact newest update ID; the dialog checkbox hides that update locally until a newer one arrives. Manual history remains available. See [dialog behavior and provenance](SWRLZ_CHAT_UPDATES.md); hosted acceptance is tracked by the active checkpoint.

**Historical successor preparation (2026-10-26; publication superseded above):** project downloads preserve explicit filenames or unambiguous leading filename metadata, with safe paths and a40MiB browser archive bound; see [filename/archive contract](PROJECT_FILENAME_METADATA.md). Static ES imports loaded through classic scripts are rejected with loading-mode feedback. A narrow [runtime-capacity endpoint](runtime-capacity.md) reports visible controller observations without choosing a model. Exact-source465d563f passed CI, but guarded publication stopped at the required700M identity-continuity gate before upload. Live source remained6240d715 at the recorded post-failure observation; actual editor/multi-file model acceptance remains open.

**Explicit long-prose source behavior (2026-10-26, actual acceptance pending):** requests for1000–12000 words can receive one buffered, model-authored complete revision if the first normally stopped draft is short. Both drafts share the original output allowance and retain mandatory context. A still-short draft ends as a failed length request; a measured length PASS does not certify factual quality. Code/project delivery stays under its own complete-source gates. See [generation and revision limits](LARGE_GENERATION_BUDGETS.md).

## Retained architecture and dated release history

**Current verified ordinary-request follow-up (2026-10-25):** LALM2.1.203/Server2.3.440; pinned Qwen7B coding and700M conversation. Live source `6240d7151692898b9f30e75675707083ddb7f4cc` generated a working HTML3D viewer from a request naming no library/version; unchanged output passed10/10 isolated browser checks. See [current release evidence](entries/2026-10-24_QWEN_PROJECT_GENERATION.md). Previous release snapshots below remain history.

**Current verified release (2026-10-24):** live source `0e361f97d9b0ec72a63581dc06ac22c610a11f1f` runs pinned Qwen7B coding with700M conversation; LALM2.1.202/Server2.3.440. Actual live700m→coder viewer output passed10/10 isolated browser checks. Older implementation snapshots below are historical. See [current generation/release checkpoint](entries/2026-10-24_QWEN_PROJECT_GENERATION.md) for scope, exact evidence, limitations and rollback.

**Role:** canonical overview for how §wyrlz Chat is composed, revealed, mutated, and audited as a theater stage.

**Read with:** `§wyrlz_§tart.md`, `docs/engineering/SWRLZ_RUNTIME_HOTLOADER_GUIDE.md`, and `docs/engineering/SWRLZ_LOCKDOWN_CAMERA_SYSTEM.md`.

**Scope:** Chat architecture. This document defines the scene vocabulary and ownership/mutation rules. The Roadmap records what was actually built.

---

## 0. Current §wyrlz Chat conversation + intent contract — 2026-10-14

**Scope and authority:** This is the Chat interaction owner's approved behavior/design contract. It applies to Chat's inference-routing, accessible widgets, and optional steering interface. It is **not** a new GitHub permission grant, model-weight training report, cross-chat data bridge, or proof that a feature has been implemented. The Roadmap records actual source/CI/hosting/live status.

### A. Topic recognition is not an action request

- An isolated word such as **“Files,” “Statistics,” “Music,” “Projects,” or “Code”** may introduce a subject, ask to browse, invite explanation, seek metrics, or mean something outside the recent task. Use current language, explicitly pinned focus, recent authenticated source context, and prior turns to propose a probable subject; **do not equate probable subject with permission to execute a particular operation**.
- Prefer **one brief natural clarification** when the action is substantially underdetermined. For example, “Files? We were exploring your GitHub `hf_space` sources. Did you want to browse, see file counts, analyze relationships, or look for something specific—or files elsewhere?” Do not force a large menu/form for every vague noun.
- A small already-verified or explicitly requested **read-only statistical preview** may be useful when cheap and correctly scoped. Identify repository, branch/commit, age/completeness of cached values, and whether another read actually occurred. Do not pretend a source inventory is an explanation, or that uninspected source was read.
- Clear read requests should work without ritual confirmations. A reasonable but mistaken **read interpretation is correctable**: explain the actual scope and result, accept the user's correction, and re-run the appropriate bounded read. Ambiguity should not become perpetual interrogation, and read results remain untrusted data.
- The last verified GitHub branch and source file are **context hints**, not default authority for unrelated topics; never silently switch to `main`, erase a file referent, expand user authorization, or invent commit/file relationships. If branch/path matters, preserve it explicitly or seek a correction.
- Distinguish *topic confidence*, *action confidence*, and *permission confidence*. Each can differ; do not invent certainty by averaging them.

### B. Strict write/mutation and permission boundary

- A **write, delete, push, merge, deploy, paid request, credential change, privilege escalation, or consequential external action** requires clear intent, target/resource identity, intended change/scope, ownership, current revision/branch, and valid **operation-specific permission/approval**. If any material dimension is ambiguous, **ask before performing the action**, rather than inferring one from prior discussion, a pin, a short noun, or an already authorized read.
- Present a bounded proposed change/preview and its consequences; use the existing confirmation/approval mechanism, compiler/integrity checks, and human acceptance path as applicable. Write permission alone does not settle what the user intended, and an unambiguous intent does not grant permission.
- **Stage 1 GitHub access remains read-only.** No phrasing, user history, pinned workspace, model tool suggestion, steering message, or vague earlier consent can unlock repository mutation. Later stages require separately governed implementation, reviews, permission gate, and explicit approval.
- Never claim a write, build, deployment, test, or model learning occurred without independent receipts. Keep corrections and rejected attempts visible without equating explanation of an error with a verified lasting behavioral improvement.

### C. Pinned, collapsible source workspaces — product direction, NOT currently verified live

- A repository explorer widget should **collapse independently from its pin state**. Pinning can retain a compact, accessible workspace strip near the top of a thread; expanding restores browsing/selection/reports. Keep mobile scrolling/composer usable and avoid overlapping the viewport.
- Distinguish *pinning an individual message*, *pinning an interactive workspace*, and *setting a working inference focus*. A focus is an opt-in **per-thread bounded pointer** to repository/branch/commit/path and relevant evidence, not a full source dump in the 700M model's context or permanent global context.
- Focus raises topic relevance **but never monopolizes conversation interpretation or authorizes tools**. When user switches to music, game, or another subject, respond to that user intent. Cross-chat coordination can expose verified shared GitHub activity, not automatically synced private histories or imagined concurrent work.
- Optimize narrow mobile rows (file name first, compact actions/overflow, bounded expanded height). Preserve widget state and differentiate UI pin visibility from read-only source provenance.

### D. Live steering composer — product direction, NOT currently verified live

- **Idle:** send button. **Generating with empty composer:** morph to stop. **Generating with text typed:** morph to a *steer/continuation* arrow so the user can add guidance or redirect an active answer. Keep a separate accessible stop action while the composer has text; typing must not remove the ability to stop.
- Interpret steering as **add guidance**, **redirect/revise**, or **queue a later task** based on message meaning; don't assume every in-progress message is a mutation. Preserve the draft until the server acknowledges its request, attach to the correct active generation, and record append-only timestamped reviewable events.
- If the current model cannot actually incorporate new guidance mid-stream, use **checkpoint → stop current generation → continue/re-generate from explicit context**. Never claim already emitted tokens were rewritten or that a steer was integrated when it was only queued. Preserve visible prior output and a source-of-truth log.
- Any steering instruction that requests a **write or privileged external action** enters the strict permission gate in B. It cannot piggyback on the permission for the original read.

### E. Live status and cross-thread continuation

- **As of this design decision:** existing v238 Chat has timestamped progress traces and the v237 feature-branch reader; owner test exports (49)/(50) proved explicit branch reads and file-specific commit history, while bare “Files” previously produced a wrong-branch 404. Candidate [v239 / PR #151](https://github.com/kaministrator999-ui/Swrlzkamico/pull/151) narrows this particular vague-file behavior to contextual clarification; source/CI/Space/phone status must be rechecked from current receipts. This contract is not a claim of deployed 700M weights, generalized intent mastery, or completed pinned/steering UI.
- **Fresh ChatGPT engineering thread handoff:** follow `§wyrlz_§tart.md`; read this section; inspect current Roadmap latest event + unresolved work, `runtime:VERSION.txt`, current PRs/CI/Space and source SHA. Continue from **verified evidence**. The user need not re-explain these approved decisions. Preserve independent cross-conversation branches and avoid racing writes.
- **Next acceptance fixtures:** “Files” after a verified feature-branch read should clarify without making a GitHub request; “List files in this folder” should execute a grounded read on that same branch; explicit write should remain blocked in Stage 1. For the future pinned workspace, verify pin vs collapse independence and mobile accessibility; for the future composer, verify send/stop/steer, acknowledgement, queued vs applied steer truth, and write approval gates.

---

### F. Read-only source specialist and cross-conversation coordination — v241 contract

**Scope:** Keep the existing v235–v240 GitHub read inference and v240 asymmetric intent safety authoritative. The model route is an optional, read-only specialization for a verified code question, **not** a new independent GitHub agent or write surface. Stage 1 still denies GitHub source mutation. The owner-approved design details live with the v241 engineering work and its draft [PR #153](https://github.com/kaministrator999-ui/Swrlzkamico/pull/153); consult the Roadmap for exact CI/deployment state rather than treating this specification as proof of live acceptance.

- For exact repository metadata/status, use existing deterministic sources. For an explicit source explanation, pin GitHub repository, branch, commit, path and blob; reject path collisions and file-byte SHA mismatches, give Qwen only bounded exact UTF-8 evidence and the original question. Treat repo text/comments as untrusted data, not instructions. Preserve incomplete coverage and do not call model output an executed test or applied change.
- LFM2-700M remains the general conversational/intent owner; Qwen is a subordinate source-analysis specialist. No automatic double inference for inexpensive questions. More elaborate 700M + Qwen engineering collaboration requires independently tested, budgeted extensions—**not** an unverified assertion that v241 already executes every future design slice.
- Shared project-work declarations belong to the signed-in account's encrypted, bounded metadata store, **not** to GitHub. Other conversations may see sanitized recent intent summaries only within the same account and verified repo; no entire transcripts, uncommitted source, assumed session liveness, or falsely exclusive source lock. Separate conversational work may proceed in parallel; overlap labels require scoped evidence.
- The coding-model capability promotion sequence is **show candidate to §wyrlz/GPT for explicit independent review → independent compiler/test evidence → final owner hands-on acceptance**. Every changed candidate resets applicable approvals. GitHub write capability remains disabled even after competency gates until an additional, separately authorized policy decision.
- If the account registry is unavailable, report coordination visibility as unavailable rather than asserting another conversation is idle. If the coder is unavailable, preserve the verified read result or explain the limitation; never silently reinterpret the request as permission to edit.
- Distinguish source candidate, CI green, guarded publication and signed-in user acceptance. PR #153's status and the Roadmap version record own implementation truth.

---

## 1. Six primitives

| Primitive | Meaning | Typical examples |
|---|---|---|
| **Scenery** | Defines the physical stage and should exist before reveal | viewport, workspace, drawer/sidebar geometry, message viewport, composer position, top bar |
| **Starting prop** | Dynamic-looking but required for the opening scene | current theme, branding/sigil, kompanion location, composer controls, selected-thread heading |
| **Actor** | Stateful participant in the performance | current thread, message list, composer, connection/runtime presentation |
| **Temporary actor / prop** | Enters for a bounded event and leaves cleanly | streamed response, toast, loading state, error notice, modal, tool-progress presentation |
| **Scene-transition prop** | Structural presentation that may change only through a controlled scene transition | theme geometry, drawer mode, account/session presentation, major responsive-layout mode |
| **Stagehand** | Machinery that prepares/manipulates the production but must not become visible scenery | loaders, hydration, cameras, transport, persistence, auth, manifest/runtime selection |

An actor can have an entrance condition and exit condition. A persistent actor may enter in the opening scene and remain for the whole session.

Stagehands do not own visible identity merely because they can mutate DOM/state.

---

## 2. Legal mutation phases

### Immutable during the play

There is one canonical owner for each fundamental stage region.

Examples:
- one application/stage root;
- one workspace;
- one message viewport;
- one composer shell;
- one canonical branding owner.

A loader or enhancement must not manufacture a competing copy.

### Open-curtain mutable

These changes are part of the visible performance:
- response text streaming;
- status/progress presentation;
- thread/message entrance;
- unread state;
- temporary notices;
- bounded interaction feedback.

They may mutate while the audience is watching because the mutation itself is meaningful performance.

### Closed-curtain mutable

These changes must be prepared as a coherent next scene and committed atomically enough that the audience does not see reconstruction:
- fundamental theme geometry;
- kompanion/branding presentation replacement;
- major responsive shell mode;
- navigation architecture replacement;
- structural drawer/workspace reconstruction;
- anything that would visibly make the stage jump through intermediate states.

---

## 3. Scene contract

```text
CURTAIN CLOSED
│
├── Build canonical scenery
├── Apply current theme
├── Place starting props
├── Determine starting actors
├── Populate scoped initial state
├── Validate geometry
│
▼
SCENE COMMIT
│
▼
CURTAIN OPEN
│
├── actors enter/leave
├── messages enter
├── responses stream
├── status changes
├── temporary actors/props appear/disappear
└── minor props update
       │
       └── major structural change required?
                    ↓
             CURTAIN TRANSITION
                    ↓
             prepare next scene
                    ↓
                 COMMIT
```

“Curtain closed” does not require a blank screen. On initial navigation it is the interval before the first authoritative scene is presented. During an existing session it can be a deliberately designed continuity-preserving transition.

The audience must not be shown a half-reconstructed DOM merely because stagehands are still working.

---

## 4. Audit schema

Before adding, migrating, or consolidating a Chat component, classify it with:

```text
owner
→ primitive/role
→ initial state
→ entrance condition
→ exit condition
→ allowed mutation phase
→ dependencies
→ camera contract
→ version owner
```

If two mechanisms claim the same visible owner/region, stop and reconcile ownership before adding another mechanism.

A useful audit table is:

| Owner | Role | Initial state | Entrance | Exit | Mutation phase | Dependencies | Camera | Version |
|---|---|---|---|---|---|---|---|---|

Duplicate visible ownership is a structural defect candidate.

---

## 5. Stagehand law

Loaders, hydration code, runtime manifests, cameras, transport, persistence, authentication, caches, and similar machinery are **stagehands**.

Stagehands may prepare or deliver scene state, but:

- they do not become competing scenery;
- they do not reveal stale presentation while preparing current presentation;
- they do not independently own branding;
- they do not rebuild a canonical region merely because they loaded later;
- failure of an enhancement should preserve the same authoritative stage, not expose a visually distinct old stage underneath it.

The Mask presents capabilities; it does not possess backstage machinery.

---

## 6. Current clean-room Chat direction

The canonical clean-room route is:

`/chat/§wyrlz`

Its construction strategy is deliberately additive:

```text
known-fast minimal stage
→ scenery
→ starting props
→ starting actors
→ open-curtain actors
→ temporary actors/props
→ controlled scene transitions
→ stagehands/integration as required
```

Do not copy the legacy Chat wholesale.

Each tier should add one coherent class of stage responsibility, verify it, preserve the known-fast baseline as far as practical, and record the receipt in the Roadmap.

---

## 7. Camera relationship

Cameras are built with the play, not installed after the theater is full.

For every stage element, the camera contract should know enough to observe:
- entrance/exit;
- owner;
- meaningful state transition;
- geometry/presentation transition when relevant;
- timing/performance;
- correlation identity;
- active source/revision.

Camera activation follows the Lockdown Camera System guide. Camera machinery remains a stagehand and must be behaviorally inert.

---

## 8. Runtime-hot relationship

Runtime hotloading is delivery machinery, not a second stage owner.

For Chat:
- page/source authority remains explicit;
- manifest assets must have one purpose and owner;
- hotload activation must not create a second visual shell;
- a runtime-loaded enhancement joins the existing scene contract rather than replacing it opportunistically;
- Runtime Manifest advances only when route/style/script activation mapping changes.

See `docs/engineering/SWRLZ_RUNTIME_HOTLOADER_GUIDE.md` for mechanics.

---

## 9. Architectural test

Before accepting a Chat change, ask:

1. What primitive is this?
2. Who owns it?
3. Does another mechanism already own the same region/state?
4. When is it legally allowed to mutate?
5. What does the audience see while it changes?
6. What stagehand delivers it?
7. Can cameras prove its lifecycle without altering behavior?
8. Which version authority advances?
9. Can failure preserve the same canonical stage instead of revealing a competing fallback presentation?

If those answers are unclear, the component is not ready to enter the play.

---

## Bottom line

**Scenery. Props. Actors. Stagehands. Curtain. Scene.**

Build one authoritative stage. Prepare structural change behind the curtain. Let legitimate performance mutate in the open. Keep stagehands backstage. Give every visible region one owner. Instrument each component from birth.
