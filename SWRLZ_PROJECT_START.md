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

### Conditional references

Read these when relevant:

- `docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md` — Google sign-in, OAuth, account/session, or related Chat-auth work.
- `docs/engineering/SWRLZ_ARCHITECTURE_COACHING_GUIDE.md` — when helping a user start/grow their own project, teaching architecture, explaining tradeoffs, or simplifying/removing optional architecture at the user's request.
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
| Module version routing | `VERSION.txt` → `versions/<module-id>.txt` |

Do not create a second policy document for a concern that already has a canonical owner. Extend the owner or deliberately migrate/retire the old contract.

---

## 3. Automatic workflow for every governed development event

```text
READ PROJECT CONTRACT
      ↓
FETCH CURRENT TARGET + VERSION AUTHORITIES
      ↓
CAPTURE VERSION/SHA BASELINE
      ↓
ARCHITECTURE RECONCILIATION
      ↓
ISSUE/DEFECT? → AUTOMATIC CAMERA + LOG EVIDENCE LOOP
      ↓
CONFIRM CANONICAL OWNER + MODULE IMPACT
      ↓
CHECK CURRENT DEPLOYMENT CAPABILITY
      ↓
DEPLOYMENT-PRODUCING ACTION?
      ├─ YES → STOP + EXPLAIN + GET EXPLICIT USER APPROVAL
      └─ NO  → CONTINUE
      ↓
IMPLEMENT THROUGH THE RECONCILED OWNER
      ↓
RE-READ VERSION AUTHORITIES
      ↓
RECONCILE ANY CONCURRENT ADVANCE
      ↓
ASSIGN SERVER + ACTUALLY CHANGED MODULE VERSIONS
      ↓
VERIFY BEHAVIOR + OWNERSHIP + ACTIVATION AS RELEVANT
      ↓
UPDATE ROADMAP / RELEASE RECORD
      ↓
REPORT RESULT USING RESPONSE STANDARD
```

Version state observed at the beginning is a baseline, **not a reservation**.

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
- whether source authority, live activation, and historical evidence agree.

Do not add a third owner to two mechanisms already fighting each other.

Every completed governed event records a concise architecture-reconciliation note in the roadmap/release record.

---

## 5. Automatic diagnostic/camera rule for issue work

When the work is primarily **fixing, debugging, investigating, or verifying a defect**, `SWRLZ_CHAT_CAMERA_LOGS.md` applies automatically.

§wyrlz must, without waiting for the user to separately request it:

1. inspect relevant repository-side diagnostic evidence: current source, existing cameras, manifests/loaders, version authorities, roadmap/releases, engineering logs, tests, recent commits, and workflow/build logs when relevant;
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

Before any repository action that can actually trigger deployment/redeployment, determine the current deployment configuration/workflow and **obtain explicit user approval before the deployment-producing action**.

A request to fix, implement, document, commit, merge, or architect is not deployment authorization.

Prefer runtime-hot work when it is the correct architectural owner; do not move behavior to the wrong layer merely to avoid deployment.

---

## 7. Version + roadmap rule

`SWRLZ_VERSION_MODULE_EVOLUTION.md` owns the exact lineage rules.

Core invariants:

- every governed Server development event gets the next overall Server version, including failed/partial governed events as defined by the evolution contract;
- only modules that actually changed receive module-version bumps;
- `VERSION.txt` routes stable module IDs to their authoritative `versions/<module-id>.txt` owners and must not become a duplicate numeric ledger;
- capture authoritative values/SHAs at event entry;
- re-read affected authorities immediately before version assignment/commit;
- if another process advanced them, reconcile from the newest state instead of overwriting it;
- every completed event gets a durable roadmap/release record including architecture, diagnostic/verification, deployment, failure, and lineage state as applicable.

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

Never report **source complete** as **live fixed** when activation has not been observed.

---

## 11. Conditional Google account/OAuth rule

If the task touches Google sign-in, Google accounts, OAuth, account sessions, Chat account UI, browser auth state, or an auth regression, read `docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md` before diagnosing or changing that flow.

Treat current source/live evidence as current authority and older incident information as historical evidence unless the runbook establishes otherwise.

---

## 12. Conflict resolution

If project documents, source, live behavior, or historical records appear to conflict:

1. do not silently choose whichever file was found first;
2. use the architecture protocol to classify **current engineering authority vs live activation vs historical evidence**;
3. use module-owned version files for version identity;
4. inspect current source/manifests/loaders and relevant live evidence;
5. reconcile the conflict before adding another implementation or claiming completion;
6. record any meaningful authority migration/retirement in the roadmap/release lineage.

---

## 13. Definition of done

A governed project event is not complete until the applicable parts are true:

- architecture owner was reconciled before implementation;
- issue work used the automatic diagnostic evidence/camera loop;
- the change went through the intended canonical owner;
- deployment rules were followed;
- version authorities were concurrency-checked;
- only actually changed modules were bumped;
- behavioral, ownership, and activation verification were performed as applicable or explicitly recorded as pending;
- roadmap/release history reflects the event;
- the user-facing update follows the project-work response standard.

---

## Bottom line

**Project Start is the router. Read the seven required project-work documents, then follow their ownership instead of duplicating their rules. Reconcile architecture before implementing. During issue work, automatically inspect repository/live logs and add bounded cameras only where evidence is missing. Version from current authority, preserve concurrency and roadmap lineage, never trigger deployment without explicit approval, and report the result in a structured readable way. When helping users build their own projects, teach these architecture principles proportionally and respect their informed choice to simplify optional structure.**