# §wyrlz Project Start — READ THIS FIRST

**Role:** canonical router/orchestrator for every §wyrlz project-development session.

**Purpose:** tell the engineering agent what must be read, which document owns each rule family, and what automatic workflow applies before changing the project.

This file deliberately does **not** duplicate every architecture, versioning, diagnostic, deployment, or reporting rule. Those rules live in their dedicated owners below.

---

## 1. Start command

When the user says **start project work**, **resume project work**, **work on §wyrlz**, explicitly references this file, or otherwise asks for repository development:

Read these documents in this order before implementation:

1. `SWRLZ_PROJECT_START.md` — this router.
2. `SWRLZ_HOTFIX_RULES.md` — runtime/main mutation boundary, deployment gate, hotfix mechanics.
3. `SWRLZ_VERSION_MODULE_EVOLUTION.md` — Server/module version lineage and concurrency rules.
4. `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md` — how to inspect existing architecture before adding/fixing anything.
5. `SWRLZ_SERVER_ROADMAP.md` — current project/version baseline and durable release/progress ledger.
6. `SWRLZ_CHAT_CAMERA_LOGS.md` — project-wide diagnostic cameras/logs/evidence workflow. The compatibility filename remains historical; the document is project-wide, not Chat-only.
7. `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md` — how project-work progress and final results are formatted and reported to the user.

Treat those seven documents as one coordinated project-work contract.

### Project response identity opener — mandatory

Once this project-work contract is loaded, every governed project-work response must begin with the exact §wyrlz identity mark below as the **first visible element**, rendered as a **large centered heading**:

```html
<h1 align="center">𓆩𓆩⁽§⁾𓆪wyrlz𓆪</h1>
```

Rules:

- use the exact glyph sequence `𓆩𓆩⁽§⁾𓆪wyrlz𓆪`;
- place no prose, heading, status label, bullet, or other visible content before it;
- render it prominently and centered rather than as a small inline prefix;
- if the current response surface strips raw HTML alignment, use the strongest available centered heading equivalent while preserving the exact glyph sequence and first-element position;
- this rule owns the **project-entry identity opener only**. All response structure after the opener remains owned by `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md`.

### Conditional references

Read these when relevant:

- `docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md` — Google sign-in, OAuth, account/session, or related Chat-auth work.
- `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md` — when helping a user start/grow their own project, teaching architecture, explaining tradeoffs, or simplifying/removing optional architecture at the user's request.
- `docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md` — whenever work changes or evaluates programming/coding behavior in the LALM, coding-task routing, architecture-aware coding state, code-tool planning, coding evaluation, or a future dedicated coder model. This document owns the target runtime architecture and the truth boundary between documented curriculum, executable runtime behavior, and trained model capability.
- feature-specific runbooks/contracts — when the affected subsystem has one.

**Order authority:** this Project Start file owns the startup/read order. If an older subordinate document contains a legacy “READ THIS FIRST” label or old ordering, this file wins unless the repository has explicitly replaced this router with a newer authority.

---

## 2. Document ownership map

Each rule family has one primary owner.

| Concern | Canonical document |
|---|---|
| Project-work entry/order | `SWRLZ_PROJECT_START.md` |
| Runtime vs main, hotfix/deploy boundary | `SWRLZ_HOTFIX_RULES.md` |
| Server/module version lineage | `SWRLZ_VERSION_MODULE_EVOLUTION.md` |
| Pre-feature architecture discovery/reconciliation | `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md` |
| Durable progress/release history | `SWRLZ_SERVER_ROADMAP.md` |
| Cameras/logs/diagnostic evidence | `SWRLZ_CHAT_CAMERA_LOGS.md` |
| Project-work response formatting/readability | `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md` |
| Architecture teaching for user-owned projects | `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md` |
| Programming LALM runtime target + implementation truth | `docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md` |
| Module version + declared operational status routing | `VERSION.txt` → `versions/<module-id>.txt` |
| Observed runtime health/readiness | owning module/server status endpoint, reconciled with declared module status |

Do not create a second policy document for a concern that already has a canonical owner. Extend the owner or deliberately migrate/retire the old contract.

---

## 3. Automatic workflow for every governed development event

```text
READ PROJECT CONTRACT
      ↓
FETCH CURRENT TARGET + VERSION/STATUS AUTHORITIES
      ↓
CAPTURE VERSION/STATUS/SHA BASELINE
      ↓
ARCHITECTURE RECONCILIATION
      ↓
ISSUE/DEFECT? → AUTOMATIC CAMERA + LOG EVIDENCE LOOP
      ↓
CONFIRM CANONICAL OWNER + MODULE IMPACT
      ↓
WRITE ROADMAP UPDATE STARTED RECORD
      ↓
CHECK CURRENT DEPLOYMENT CAPABILITY
      ↓
DEPLOYMENT-PRODUCING ACTION?
      ├─ YES → STOP + EXPLAIN + GET EXPLICIT USER APPROVAL
      └─ NO  → CONTINUE
      ↓
IMPLEMENT THROUGH THE RECONCILED OWNER
      ↓
RE-READ VERSION/STATUS AUTHORITIES
      ↓
RECONCILE ANY CONCURRENT ADVANCE
      ↓
ASSIGN SERVER + ACTUALLY CHANGED MODULE VERSIONS
      ↓
SET/VERIFY DECLARED MODULE STATUS APPROPRIATELY
      ↓
VERIFY BEHAVIOR + OBSERVED RUNTIME HEALTH + OWNERSHIP + ACTIVATION AS RELEVANT
      ↓
WRITE ROADMAP UPDATE FINISHED RECORD
      ↓
REPORT RESULT USING RESPONSE STANDARD
```

Version/status state observed at the beginning is a baseline, **not a reservation**.

### Transactional roadmap journal — mandatory

Before the first implementation mutation of a governed update, write an **UPDATE STARTED** record to `SWRLZ_SERVER_ROADMAP.md`. It must describe the requested outcome, expected canonical owner/module impact, observed version/SHA baseline, deployment expectation, and verification plan.

After implementation, concurrency reconciliation, version assignment, and verification, update that same event with an **UPDATE FINISHED** marker describing the actual change, resulting Server/module versions, verification/activation truth state, deployment/restart state, and any correction/supersession lineage.

If Project Start finds an **UPDATE STARTED** record without a matching terminal marker, treat it as interrupted work. Reconcile repository/runtime/version evidence before beginning overlapping mutation, then explicitly **resume and finish**, **ABORT**, or **SUPERSEDE** the event. Never silently discard an unfinished update.

When the decision is to resume, write an **UPDATE CONTINUATION STARTED** checkpoint into the existing roadmap event **before any new implementation mutation**. The continuation checkpoint must identify the prior START record being resumed, the newly observed source/version/SHA/runtime baseline, what work was already completed, what remains, whether assumptions or architecture ownership changed, the current deployment boundary, and the verification plan for this continuation. A continuation checkpoint is lineage inside the original governed event; it does not silently create a second overlapping event or reserve stale version numbers. Each later interrupted/resumed work session gets another continuation checkpoint so the roadmap shows where execution actually stopped and restarted. Detailed continuation-journal fields remain owned by the Version Evolution contract; this router enforces that the checkpoint exists before resumed mutation.

Roadmap journal writes and other documentation/governance bookkeeping are deployment-inert under the current deployment contract and do not authorize or trigger a stable-server deployment. If fresh deployment evidence contradicts that invariant, treat it as a deployment-control defect and stop before any deployment-producing action.

---

## 4. Pre-feature architecture reconciliation — mandatory

Before each feature, fix, optimization, refactor, subsystem, or substantial UI/behavior change, follow `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`.

The engineering agent must determine, at the minimum:

- desired outcome vs implementation assumptions;
- affected Mask/client, Human/server, Brain/LALM, modules, routes, state, storage, loaders, caches, protocols, and version owners;
- current canonical owner/source of truth;
- relevant readers, writers, lifecycle, fallback, compatibility, and retired paths;
- whether similar/partial functionality already exists under another name;
- whether the correct integration is **reuse, extend, consolidate/refactor, migrate+retire, or genuinely new structure**;
- whether source authority, declared module status, live activation/runtime health, and historical evidence agree.

Do not add a third owner to two mechanisms already fighting each other.

Every completed governed event records a concise architecture-reconciliation note in the roadmap/release record.

---

## 5. Automatic diagnostic/camera rule for issue work

When the work is primarily **fixing, debugging, investigating, or verifying a defect**, `SWRLZ_CHAT_CAMERA_LOGS.md` applies automatically.

§wyrlz must, without waiting for the user to separately request it:

1. inspect relevant repository-side diagnostic evidence: current source, existing cameras, manifests/loaders, version/status authorities, roadmap/releases, engineering logs, tests, recent commits, and workflow/build logs when relevant;
2. inspect accessible live/runtime evidence such as Vercel runtime logs, status/diagnostic endpoints, GitHub Actions logs, browser/device evidence, or subsystem-specific logs;
3. correlate evidence by request/operation/revision/version identity when possible;
4. decide whether current observability is enough;
5. if not, add the **smallest bounded camera/instrumentation** at the architecture boundary that can distinguish the competing explanations;
6. reproduce/request the path, inspect the evidence, fix the canonical owner, and re-check the same evidence for acceptance.

Default diagnostic order when the cause is uncertain:

> **inspect first → instrument second → mutate third**

Do not add noisy logging when existing evidence already answers the question. Never log secrets merely for debugging convenience.

---

## 6. Runtime / main / deployment boundary

`SWRLZ_HOTFIX_RULES.md` owns the exact mechanics.

Core invariant:

- `runtime` = durable live application source for ordinary runtime-hot behavior.
- `main` = stable loader/infrastructure and engineering-contract boundary.
- branch name alone does **not** prove deployment capability.

Before an action that is explicitly deployment-producing under the current deployment contract, determine the current deployment configuration/workflow and **obtain explicit user approval before that deployment-producing action**. Ordinary Git/documentation mutations remain deployment-inert unless fresh evidence shows the deployment-control contract has changed or failed.

A request to fix, implement, document, commit, merge, or architect is not deployment authorization; it also must not cause ordinary deployment-inert Git work to be mislabeled as deployment-capable.

Documentation-only changes are engineering-contract maintenance and must be deployment-inert. They do not require deployment approval. If repository/deployment configuration causes documentation-only commits to deploy application code, treat that configuration as a defect and correct the deployment filtering rather than treating documentation as deployment-sensitive.

Prefer runtime-hot work when it is the correct architectural owner; do not move behavior to the wrong layer merely to avoid deployment.

---

## 7. Version + status + roadmap rule

`SWRLZ_VERSION_MODULE_EVOLUTION.md` owns the exact lineage rules.

Core invariants:

- every governed Server development event gets the next overall Server version, including failed/partial governed events as defined by the evolution contract;
- only modules that actually changed receive module-version bumps;
- `VERSION.txt` is the complete governed version registry: anything that has or receives an independently advanced version identifier MUST be registered there and routed to its authoritative `versions/<module-id>.txt` owner; it must not become a duplicate numeric/status ledger;
- each module-owned version file may also declare the module's intended operational `STATUS`; consumers should resolve that status through `VERSION.txt` rather than hardcoding another copy;
- **VERSION and STATUS answer different questions:** `VERSION` identifies the module's evolution state; `STATUS` declares whether that module is intended to be `active`, `preparing`, `maintenance`, `disabled`, or another explicitly defined lifecycle state;
- declared `STATUS=active` means the module is intended to be available; it does **not** override evidence of an actual runtime fault;
- runtime-capable modules should expose observed health/readiness through their owning server/status surface. Consumers reconcile **declared module status + observed runtime health** into presentation/behavior;
- a consumer such as Chat must not invent a permanent local “warming” state merely because one legacy readiness field is absent. It should read canonical declared status, inspect observed health when available, and normalize the result;
- shared consumers may expose the normalized state as a reusable event/object/API so other UI surfaces do not each invent their own status semantics;
- capture authoritative values/SHAs at event entry;
- re-read affected authorities immediately before version assignment/commit;
- if another process advanced them, reconcile from the newest state instead of overwriting it;
- every completed event gets a durable roadmap/release record including architecture, diagnostic/verification, deployment, failure, lineage, and meaningful status-state changes as applicable.

Canonical relationship:

```text
VERSION.txt
    ↓ routes module ID
versions/<module-id>.txt
    ├─ VERSION = evolution identity
    └─ STATUS  = declared operational intent
                 ↓
      owning runtime/status endpoint
      = observed health/readiness
                 ↓
      consumer normalization
      = active / preparing / maintenance / disabled / error / unknown
                 ↓
      Chat / admin / other UI behavior
```

**Never use a UI color, label, cached browser value, roadmap entry, or hardcoded string as the status authority.** Green/yellow/red are presentations of reconciled state, not sources of truth.

Never finish a governed event while the roadmap still represents an obsolete baseline for that completed event.

---

## 8. Mask / Human / Brain ownership

The detailed placement method lives in the architecture protocol.

```text
🎭 MASK / client = sense / relay / present / interact
🧍 HUMAN / server = authorize / persist / route / operate / execute
🧠 BRAIN / LALM = interpret / reason / plan / semantic repair
```

Keep responsibilities distinct internally while presenting one coherent §wyrlz to the user.

Do not move ordinary semantic cognition into Chat/server merely because those layers can technically compute it.

---

## 8A. §imple Mask / theater depth model

Use the theater analogy as the canonical structural teaching model for **Mask boundaries**. It is explanatory architecture, not a requirement to create one service per metaphorical role.

### Core mapping

- **Audience** = the user or external consumer.
- **Stage / Chat Mask** = the visible performance surface. It captures ordinary user interaction and renders approved presentation output. It may be visually rich while remaining architecturally **§imple**.
- **Actor / Brain (LALM)** = interprets the objective, reasons, decides what capabilities or evidence are needed, and dresses the final answer for the performance.
- **Backstage / Human-server authority** = authorizes, persists, routes, budgets, operates, executes, audits, and enforces boundaries.
- **Workers wearing masks/hats** = specialized bounded services/adapters. A component can be backstage relative to one boundary while presenting a Mask toward another world. A Mask is therefore a **boundary role**, not one unique UI object.
- **Outside/Web Mask** = the controlled interface to the external web/world. It exposes bounded operations to authorized backstage workers without leaking provider machinery into Chat.
- **Mission workers / information collectors** = cooperate on a specific objective, may hand off questions/findings/obstacles through a bounded mission workspace, and retrieve the smallest sufficiently complete evidence package rather than flooding the Brain with everything visible outside.
- **Frozen Web Collector** = the scenery workshop: it collects, cleans, deduplicates, establishes provenance, organizes, freezes, and versions durable material.
- **Frozen knowledge/scenery** = the resulting durable knowledge artifact. It may sit dormant until the Brain needs relevant scenery; the Collector itself is not the scenery.
- **Cameras/telemetry** = behind-the-scenes production records. They may preserve barrels, locked doors, redirects, provider failures, timing, and worker handoffs for operations/debugging without making those mechanics Chat cognition.

### Mission coordination rule

The Brain may delegate a bounded objective such as “retrieve the current temperature for Kansas City.” Backstage workers may coordinate laterally within granted authority: one worker may ask another for a route, report that a provider is blocked, hand off a URL to a reader, request corroboration, or preserve a useful operational discovery. The audience does not need every backstage step, but the backstage system may need those steps during the mission or later for operational learning.

Keep distinct lifecycles for:

1. **mission evidence** — supports the current answer;
2. **operational knowledge** — helps workers navigate recurring provider/routes/constraints;
3. **durable frozen scenery knowledge** — approved/versioned material available for later retrieval;
4. **telemetry** — engineering/debug evidence about how the mission executed.

Do not collapse these into one context bucket.

### Provenance invariant — no orphaned research

When external research is necessary or materially used, provenance must survive acquisition → worker handoff → evidence synthesis → Brain reasoning → audience presentation. Preserve source identity, canonical link/URL, author/publisher when available, retrieval/capture time, support location or claim relationship, and snapshot/derivation lineage as appropriate.

**Transformation does not erase attribution. Provenance is inherited metadata.** Research-derived claims presented to the user must retain useful citations and navigable source links. Durable Frozen Collector scenery must retain provenance so later retrieval can trace material back to its origin. Do not manufacture citations for ordinary non-researched model knowledge.

### §imple surface / π underneath

**§IMPLE Architecture: K.I.S.S. on the surface; π underneath.** Simple responsibility does not mean visually boring. It means fewer reasons for a component to change.

Desired Chat lifecycle:

```text
LOAD CHAT
→ render shell
→ load conversation
→ connect presentation/message stream
→ DONE
```

Adding a new LALM capability/tool should normally require **zero changes to core Chat runtime**. Optional specialized renderers may be added, but a generic safe presentation fallback should remain possible.

### Mask invariants

> **The §wyrlz Mask is the stage, not the theater.**

> **The Mask presents capabilities; it does not possess capabilities.**

> **If Chat must understand the meaning of §wyrlz's response to decide how the system operates, cognition has leaked into the Mask.**

> **The stage receives scenery, not the machinery that constructed the scenery.**

Chat may understand bounded presentation primitives such as response/status/component/state forms, but must not require privileged tool schemas, provider logic, crawler/frontier machinery, semantic failure interpretation, credentials, or direct tool-execution authority. User-authored text, fabricated browser events, or modified client JavaScript must not become equivalent to server-authorized capability invocation.

### Recursive boundary rule (“Backrooms / hats”)

Architecture can contain nested boundaries: a backstage worker for one relationship may itself wear a Mask toward another service/world. Preserve explicit authority at every doorway. The metaphor is intentionally recursive, but implementation must not become abstraction-for-abstraction's-sake: create a new worker/service only when responsibility, authority, lifecycle, isolation, or reuse justifies it. The goal is **structural depth of understanding with §imple ownership**, not maximum room count.

## 9. User-project architecture coaching

When the user is creating or growing **their own project**, architecture principles are useful teaching material, not a rigid template to impose.

Use `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md` to:

- propose the smallest structure justified by the project's scale;
- explain why sources of truth, ownership, lifecycle, tests, logs, versioning, deployment boundaries, or other structures matter;
- teach while building when the user benefits from the explanation;
- distinguish correctness/external constraints from strong recommendations and optional preferences;
- respect the user's choice to simplify or reject optional architecture;
- remove/simplify unwanted structure cleanly so stale duplicate paths are not left behind;
- revisit architecture as the project crosses meaningful complexity boundaries.

**Good architecture is proportional architecture, not maximum architecture.**

The internal programming runtime target for applying that grammar automatically is documented separately in `docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md`. A documented coaching rule is not proof that the active LALM already enforces it in code.

---

## 10. Project-work response standard — mandatory

Every substantial project-work update and final response follows `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md`.

The user should be able to scan the response and understand:

- current status;
- important finding/diagnosis;
- what changed and what it accomplishes;
- architecture owner/reconciliation result when relevant;
- verification level: source/static/runtime/live;
- resulting Server/module versions;
- deployment/restart status;
- anything genuinely pending or blocked.

Use readable Markdown structure, compact paragraphs, and small bullet groups. Do not dump raw implementation internals unless requested or genuinely necessary.

Never report **source complete** as **live fixed** when activation has not been observed. Likewise, never report declared `STATUS=active` as proof of runtime health when observed evidence says the module is failing.

---

## 11. Conditional Google account/OAuth rule

If the task touches Google sign-in, Google accounts, OAuth, account sessions, Chat account UI, browser auth state, or an auth regression, read `docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md` before diagnosing or changing that flow.

Treat current source/live evidence as current authority and older incident information as historical evidence unless the runbook establishes otherwise.

---

## 12. Conflict resolution

If project documents, source, declared module status, live behavior, or historical records appear to conflict:

1. do not silently choose whichever file was found first;
2. use the architecture protocol to classify **current engineering authority vs declared operational intent vs live activation/runtime health vs historical evidence**;
3. use module-owned version files for version identity and declared module status;
4. inspect current source/manifests/loaders and relevant live evidence;
5. reconcile the conflict before adding another implementation or claiming completion;
6. record any meaningful authority migration/retirement in the roadmap/release lineage.

For programming/coder capability specifically, also distinguish **documented curriculum**, **runtime scaffold**, **tool integration**, **deterministic evaluation**, **live verification**, and **trained/learned capability** using the Programming LALM Runtime Architecture specification.

---

## 13. Definition of done

A governed project event is not complete until the applicable parts are true:

- architecture owner was reconciled before implementation;
- issue work used the automatic diagnostic evidence/camera loop;
- the change went through the intended canonical owner;
- deployment rules were followed;
- version/status authorities were concurrency-checked;
- only actually changed modules were bumped;
- declared module status is appropriate for the resulting lifecycle state;
- behavioral, ownership, observed runtime-health, and activation verification were performed as applicable or explicitly recorded as pending;
- roadmap/release history reflects the event;
- the user-facing update follows the project-work response standard.

---

## Bottom line

**Project Start is the router. Read the seven required project-work documents, then follow their ownership instead of duplicating their rules. Begin governed project-work responses with the required large centered `𓆩𓆩⁽§⁾𓆪wyrlz𓆪` identity opener. Reconcile architecture before implementing. During issue work, automatically inspect repository/live logs and add bounded cameras only where evidence is missing. Resolve module VERSION and declared STATUS through `VERSION.txt` and the module-owned authority; reconcile that declared state with observed runtime health before a consumer chooses behavior or UI. Version from current authority, preserve concurrency and roadmap lineage, never trigger deployment without explicit approval, and report the result in a structured readable way. When helping users build their own projects, teach these architecture principles proportionally and respect their informed choice to simplify optional structure. When changing programming-LALM/coder capability, read the Programming LALM Runtime Architecture spec and never confuse documented curriculum with executable or trained capability.**