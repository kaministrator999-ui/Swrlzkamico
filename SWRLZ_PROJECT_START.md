# §wyrlz Project Start — READ THIS FIRST

**Purpose:** This is the single short instruction file to use whenever §wyrlz project development work starts or resumes in a new ChatGPT thread.

## START COMMAND

When the user says **“start project work”**, **“resume project work”**, **“work on §wyrlz”**, or explicitly tells you to read this file:

1. Read this file first.
2. Immediately read `SWRLZ_HOTFIX_RULES.md`.
3. Immediately read `SWRLZ_VERSION_MODULE_EVOLUTION.md`.
4. Immediately read `SWRLZ_SERVER_ROADMAP.md`.
5. Treat those four files as the current operating and engineering contract before touching the repository.
6. Fetch the current target file/commit state before making any edit.
7. Fetch the current `VERSION.txt` module router and the authoritative `versions/<module-id>.txt` file for every module the requested work may affect, and record those authority values as the event baseline.
8. Determine deployment capability from the **current repository/deployment configuration and workflows**, not from branch name alone.
9. **Before making any repository mutation that can actually cause a deployment/redeployment, apply the Deployment Approval Gate below and obtain explicit user approval first.**

Do not ask the user to repeat these instructions unless the repository/files are genuinely inaccessible.

## DEPLOYMENT APPROVAL GATE — HARD STOP

**No deployment or redeployment is ever implicitly authorized by a request to architect, investigate, document, debug, implement, test, version, commit, merge, or otherwise work on §wyrlz.**

Before touching the repository in any way that could cause a deployment/redeployment, the agent MUST stop and verify with the user:

1. **What exactly will trigger the deployment** — branch, path, configuration, merge, workflow, explicit deploy action, or other mechanism.
2. **Why it will trigger deployment** — distinguish an actual architectural deployment requirement from an automatic deployment consequence of repository/deployment configuration.
3. **What the deployment affects** — runtime, stable infrastructure, production behavior, or other deployed surfaces.
4. **Whether the work can be completed through the non-deployment `runtime` path instead.**
5. **What action is being requested for approval** — the precise repository mutation or deployment-producing operation.

The agent MUST obtain an explicit approval from the user before performing that deployment-capable repository action.

### Deployment capability must be proven from current state

A branch name by itself does **not** prove that a commit deploys. Before applying the gate, inspect the current deployment configuration and relevant workflows.

- If Git-based deployment is disabled and no repository workflow or other automation will deploy the proposed mutation, a normal commit is **not** a deployment-producing action.
- Documentation-only changes on `main` are therefore allowed without deployment approval when the current configuration proves they cannot trigger deployment.
- If the deployment configuration later changes, re-evaluate this every event; never permanently assume that documentation or `main` is deployment-safe.
- An explicit deploy command/action still requires approval even when ordinary Git commits do not deploy.

### Strict rules

- **Never assume deployment approval.**
- A request to “fix,” “update,” “document,” or “commit” something is **not** permission to trigger deployment.
- A Git commit is **not** deployment authorization, but a Git commit also must not be mislabeled deployment-capable when current configuration proves it cannot deploy.
- A merge into a deployment-watched branch is **not** deployment authorization.
- Documentation changes are subject to the gate when they can actually trigger deployment; they are not automatically deployment-capable merely because they live on `main`.
- If deployment behavior is uncertain, treat the action as potentially deployment-producing and **STOP + ASK** before repository mutation.
- If a runtime-only solution exists, prefer it and do not cross the deployment boundary unnecessarily.
- If stable infrastructure must change, explain the deployment requirement and obtain approval **before the first repository action that can actually cause deployment**.
- The user may choose to perform the actual deployment manually. Do not automatically deploy unless the user has explicitly authorized that deployment action.
- After approval, record the approved deployment-producing event and its resulting deployment/verification state in the roadmap when applicable.

**This gate applies during architecture, investigation, debugging, documentation, implementation, testing, release preparation, versioning, branch operations, commits, merges, and all other repository work whenever the proposed action is actually deployment-capable.**

## REQUIRED DOCUMENT ORDER

The project-start contract is intentionally structured as four layers:

```text
1. SWRLZ_PROJECT_START.md
   ↓
2. SWRLZ_HOTFIX_RULES.md
   ↓
3. SWRLZ_VERSION_MODULE_EVOLUTION.md
   ↓
4. SWRLZ_SERVER_ROADMAP.md
```

### Document 1 — Project Start

Defines the entry sequence and the non-negotiable project-start procedure, including the Deployment Approval Gate.

### Document 2 — Hotfix Rules

Defines the `runtime` vs. `main` boundary, safe editing rules, deployment/restart rules, verification requirements, and module-owned version-file workflow.

### Document 3 — Version + Module Evolution Contract

Defines how §wyrlz evolves as an engineered system. It governs overall Server versioning, independent module versioning, failed-event lineage, canonical version ownership, the `VERSION.txt` router, per-module `versions/*.txt` authorities, automatic cross-module version resolution, release records, verification, and commit lineage.

**This is also the foundation for the future programming-side LALM engineering curriculum/specification.** The programming LALM must eventually learn this structure as an engineering process, not as optional documentation.

### Document 4 — Server Roadmap

Records the actual chronological Server/module release history and current version ledger.

## NON-NEGOTIABLE WORK RULE

`runtime` = durable live application source of truth.

`main` = stable loader/infrastructure contract boundary. Whether a `main` mutation deploys is determined by current deployment configuration/workflows, not by branch name alone.

For Chat, pages, page-owned JS/CSS, stream UI, runtime assets, runtime-loadable LALM/R39, and runtime-owned module version authorities: edit `runtime`, make the smallest targeted change, commit it, reload/request, verify it live, and **DO NOT DEPLOY or RESTART** for ordinary runtime changes.

For stable API, middleware, authentication/security boundaries, runtime loader/source resolution, hydration/sync infrastructure, deployment/build configuration, or capabilities the current loader cannot serve: edit `main` as required. If applying the change to production requires an actual deployment action, **DEPLOY + VERIFY only after passing the Deployment Approval Gate above**.

Never use `dev` as the Chat/runtime hotfix source.
Never use `/tmp` as durable source of truth.
Never replace a complete page for a small targeted change.
Never introduce a competing hardcoded page/version injector in `main`.
Never duplicate another module's version number when that module owns an authoritative version file.

## MODULE VERSION AUTHORITY RULE — REQUIRED

`VERSION.txt` is the **module-version router/index**. It identifies which module-owned file contains the authoritative version for each independently evolving structure.

The authoritative values live in module-owned files such as:

```text
versions/server-runtime.txt
versions/server-ui.txt
versions/web-chat.txt
versions/stream-contract.txt
versions/lalm-ui.txt
versions/lalm-engine.txt
versions/admin-web.txt
versions/google-account.txt
versions/client-apk.txt
versions/server-apk.txt
versions/frozen-web-collector.txt
```

The exact registered set must always be read from current repository state because new structures may be added over time.

### New independently evolving structure

If work introduces a structure that can evolve independently — such as a new account subsystem, admin surface, client/server application, authentication architecture, profile/memory/search system, protocol, or other substantial module — the same development event must:

1. assign a stable module ID;
2. create its own `versions/<module-id>.txt` authority;
3. register that owner in `VERSION.txt`;
4. make its own visible/status/update surfaces consume that authority where appropriate;
5. make other modules query the owner instead of carrying duplicate version literals;
6. include that module in roadmap/release lineage going forward.

If the true current version of an artifact cannot be verified, record an explicit unassigned/unknown state. **Do not invent a version.**

### Display/update behavior

When Chat, Admin, LALM, an APK, installer, updater, or another consumer needs a version:

```text
consumer
   ↓
VERSION.txt
   ↓
module-owned versions/<module-id>.txt
   ↓
render / compare / update decision
```

A component update checker compares its installed/local version against the authoritative hosted module version under that component's update policy.

## AUTOMATIC VERSION + ROADMAP RULE

**Every server development event governed by the version-evolution contract MUST automatically receive an overall Server version and a durable roadmap/release record.**

This happens as part of the update workflow, not as an optional follow-up task.

Before the update:
- Read the current overall Server version and component versions from `SWRLZ_SERVER_ROADMAP.md`, `VERSION.txt`, and the authoritative module-owned version files.
- Record the exact authoritative version values/SHAs as the **event baseline**.
- Read `SWRLZ_VERSION_MODULE_EVOLUTION.md` and determine which components actually change.

Immediately before assigning versions or committing:
- Re-read `VERSION.txt` and every affected authoritative `versions/<module-id>.txt` file.
- Compare the current authority state against the event baseline.
- If any relevant authority changed, assume another instance/process advanced the project while this event was in progress.
- **Do not write the previously planned version numbers. Reconcile against the newest authority first, then assign the next valid Server/module versions.**
- Use repository SHA/precondition checks where available so a concurrent write fails instead of silently overwriting newer state.

During the update:
- Apply the appropriate change on `runtime` or `main` according to the hotfix/deployment boundary.
- Increase the overall Server version for the development event when required by the Server event contract.
- Increase only the component version(s) that actually changed.
- Update each affected module's `versions/<module-id>.txt` authority.
- Update `VERSION.txt` only when module registration/routing changes; do not duplicate version values there.
- Ensure cross-module version displays resolve the owning module's authoritative version automatically.

Before declaring the work complete:
- Record the completed event in `SWRLZ_SERVER_ROADMAP.md`.
- Include the overall Server version, affected module versions, exact update notes, failures/attempts, deployment status, verification, commit lineage, and rollback/migration notes when applicable.
- If the event changed stable infrastructure on `main` and production application requires deployment, deploy and verify production before closing the release **only if deployment was explicitly approved under the Deployment Approval Gate**.
- If the event does not require deployment, explicitly record `Deployment: NONE` and verify the relevant repository/live source as appropriate.
- Re-read the authoritative version files after the mutation/commit and verify they match the versions assigned to the event.
- If an attempt fails, preserve that event in the lineage and treat the next correction as another versioned event.

**Never finish a versioned server development event with the roadmap still saying “NEXT RELEASE.”** Replace that placeholder with the actual completed release entry and reserve the next version only after the current event is recorded.

## CURRENT BASELINE

The baseline numbers written into this file are informational snapshots only and may be stale immediately after future work. **Do not use them as version authority.** Always resolve current versions from `VERSION.txt`, the referenced module-owned version files, and the current roadmap before an update.

## REQUIRED RELEASE LOOP

```text
START PROJECT WORK
      ↓
READ THIS FILE
      ↓
READ SWRLZ_HOTFIX_RULES.md
      ↓
READ SWRLZ_VERSION_MODULE_EVOLUTION.md
      ↓
READ SWRLZ_SERVER_ROADMAP.md
      ↓
FETCH VERSION.txt ROUTER
      ↓
FETCH AFFECTED versions/<module-id>.txt AUTHORITIES
      ↓
CAPTURE VERSION/SHA BASELINE
      ↓
FETCH CURRENT TARGET SOURCE
      ↓
DETERMINE MODULE IMPACT
      ↓
DEPLOYMENT RISK CHECK FROM CURRENT CONFIG/WORKFLOWS
      ↓
IF DEPLOYMENT-CAUSING → STOP + EXPLAIN + GET USER APPROVAL
      ↓
MAKE SMALLEST SAFE CHANGE
      ↓
RE-READ VERSION ROUTER + AFFECTED AUTHORITIES
      ↓
AUTHORITY CHANGED? → RECONCILE BEFORE VERSIONING
      ↓
ASSIGN NEW OVERALL SERVER VERSION WHEN REQUIRED
      ↓
INCREMENT ONLY CHANGED COMPONENT VERSIONS
      ↓
UPDATE AFFECTED MODULE-OWNED VERSION FILES
      ↓
UPDATE VERSION.txt ONLY FOR OWNER/ROUTING CHANGES
      ↓
VERIFY CROSS-MODULE VERSION RESOLUTION
      ↓
COMMIT TO runtime OR appropriate main PATH
      ↓
UPDATE ROADMAP / RELEASE RECORD
      ↓
RE-READ AUTHORITIES + VERIFY ASSIGNED VERSIONS
      ↓
RELOAD / REQUEST AFFECTED ROUTES
      ↓
VERIFY LIVE RESULT
      ↓
SUCCESS → CLOSE EVENT
FAILURE → RECORD EVENT + CREATE NEXT VERSIONED EVENT
```

## SOURCE DOCUMENTS

- `SWRLZ_PROJECT_START.md` — single entrypoint; tells future §wyrlz what to read and what must happen every update.
- `SWRLZ_HOTFIX_RULES.md` — exact hotfix vs. redeploy boundary and safe editing rules.
- `SWRLZ_VERSION_MODULE_EVOLUTION.md` — third required contract; formal Server/module evolution rules and future programming-LALM curriculum foundation.
- `SWRLZ_SERVER_ROADMAP.md` — authoritative overall/component release history.
- `VERSION.txt` — router from stable module IDs to authoritative module-owned version files.
- `versions/*.txt` — authoritative version/revision identity for each independently evolving structure.

If any of these documents conflict, stop and resolve the conflict against the newest authoritative repository state before editing application code.

## BOTTOM LINE

**Read `SWRLZ_PROJECT_START.md`, then automatically read `SWRLZ_HOTFIX_RULES.md`, `SWRLZ_VERSION_MODULE_EVOLUTION.md`, and `SWRLZ_SERVER_ROADMAP.md`. Resolve current module versions through `VERSION.txt` and each module's own `versions/<module-id>.txt`. Capture those authorities as the event baseline, then re-read them immediately before version assignment/commit so concurrent updates are detected and reconciled rather than overwritten. Follow the hotfix/deployment boundary based on current deployment configuration and workflows, not branch name alone. Before any action that can actually cause deployment, STOP, explain exactly what would cause it and why, and obtain explicit user approval. Every server development event receives the Server lineage treatment required by the evolution contract; only actually changed components receive component bumps; independently evolving structures own their own version files; cross-module displays resolve those authorities automatically; failures remain in lineage; and the completed event is recorded in the roadmap before the work is declared done.**
