# §wyrlz Project Start — READ THIS FIRST

**Purpose:** This is the single short instruction file to use whenever §wyrlz project development work starts or resumes in a new ChatGPT thread.

## START COMMAND

When the user says **“start project work”**, **“resume project work”**, **“work on §wyrlz”**, or explicitly tells you to read this file:

1. Read this file first.
2. Immediately read `SWRLZ_HOTFIX_RULES.md`.
3. Immediately read `SWRLZ_VERSION_MODULE_EVOLUTION.md`.
4. Immediately read `SWRLZ_SERVER_ROADMAP.md`.
5. Immediately read `SWRLZ_CHAT_CAMERA_LOGS.md` so live Chat diagnostics are read from the correct production observation source and correlated with repository instrumentation.
6. Treat those five files as the current operating, engineering, and Chat-observation contract before touching the repository.
7. If the task touches Google sign-in, Google accounts, OAuth, account sessions, Chat account UI, browser auth state, or an auth regression, immediately read `docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md` before diagnosing or editing that flow.
8. **Before implementing any feature, fix, optimization, refactor, or substantial behavior/UI addition, perform the Pre-Feature Architecture Reconciliation below across the selected/affected architecture and existing related work.**
9. Fetch the current target file/commit state before making any edit.
10. Fetch the current `VERSION.txt` module router and the authoritative `versions/<module-id>.txt` file for every module the requested work may affect, and record those authority values as the event baseline.
11. Determine deployment capability from the **current repository/deployment configuration and workflows**, not from branch name alone.
12. **Before making any repository mutation that can actually cause a deployment/redeployment, apply the Deployment Approval Gate below and obtain explicit user approval first.**

Do not ask the user to repeat these instructions unless the repository/files are genuinely inaccessible.

## CHAT CAMERA / RUNTIME LOG RUNBOOK — REQUIRED

`SWRLZ_CHAT_CAMERA_LOGS.md` is the persistent observation runbook for Chat diagnostics. GitHub contains the camera/instrumentation source; actual live Whole Conversation Camera and structured Chat/LALM observations are normally inspected in Vercel production runtime logs. Use request IDs, thread IDs, canonical revisions, engine versions, and terminal state to correlate a live turn. Do not confuse repository source with live runtime evidence, and do not claim production acceptance from source alone.

## GOOGLE ACCOUNT / OAUTH RUNBOOK — REQUIRED WHEN RELEVANT

For Google account or OAuth work, `docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md` is the persistent incident and architecture reference. It records the canonical and retired Web OAuth client IDs, canonical production origin, stable/runtime ownership boundaries, browser storage keys, server verification flow, boot-order requirement, recovery page, diagnostic ladder, known failure signatures, the 2026-09-12 Chrome/Edge regression timeline, and the verified recovery sequence.

Do not change Google credentials, browser storage behavior, Google Identity Services initialization, account-session verification, or related runtime ordering until that runbook has been read and the live evidence ladder has been followed.

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

The project-start contract is intentionally structured as five layers:

```text
1. SWRLZ_PROJECT_START.md
   ↓
2. SWRLZ_HOTFIX_RULES.md
   ↓
3. SWRLZ_VERSION_MODULE_EVOLUTION.md
   ↓
4. SWRLZ_SERVER_ROADMAP.md
   ↓
5. SWRLZ_CHAT_CAMERA_LOGS.md
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

### Document 5 — Chat Camera Logs

Defines where Chat/Whole Conversation Camera instrumentation lives, where live production observations are actually read, how to correlate a turn, and how to distinguish source facts, runtime facts, user-visible facts, and diagnosis.

## PRE-FEATURE ARCHITECTURE RECONCILIATION — REQUIRED

**Before implementing each feature, fix, optimization, refactor, subsystem, or substantial behavior/UI addition, perform a brief but complete reconciliation of the selected/affected architecture and the already-implemented work that revolves around it.**

The purpose is to prevent a new change from fighting an existing owner, duplicating an already-present feature, creating a second source of truth, reviving a retired path, or adding another layer that solves the same problem differently.

This is a **bounded architecture check**, not a requirement to re-audit the entire repository before every edit. Start with the architecture selected by the requested feature and expand only far enough to identify every existing implementation that shares the same owner, source of truth, state, lifecycle, route, protocol, storage, authentication boundary, cache, loader, UI surface, tool/action path, version authority, or other directly interacting responsibility.

### Required pre-feature check

Before implementation:

1. **Define the feature and affected architecture.** Identify the relevant Mask/client, Human/server, Brain/LALM, module(s), routes, state owners, protocols, storage, assets, version authorities, and other affected surfaces.
2. **Inspect the current canonical owner(s).** Read the relevant source, manifests/registries, architecture/runbook material, roadmap/release history, and version authorities before deciding where to add anything.
3. **Search for existing or partial implementations.** Check for the same capability, earlier attempts, fallbacks, retired paths, duplicate injectors, compatibility layers, hooks, flags, state machines, caches, loaders, or adjacent features that already perform part or all of the requested behavior.
4. **Check neighboring behavior that shares the same architecture.** A feature can conflict with work that has a different name but owns the same state, lifecycle, transport, layout, reasoning, persistence, or authority. Reconcile those relationships before editing.
5. **Choose an integration path deliberately.** Prefer extending/reusing the canonical owner. Refactor or retire obsolete competing work when appropriate. Do not create a parallel implementation merely because adding another layer is easier.
6. **Resolve conflicts before implementation.** If two existing mechanisms already fight each other, determine the intended authority and reconciliation/migration path before adding the new feature. A new feature must not knowingly become a third competing owner.
7. **Confirm ownership boundaries.** Apply the Mask / Human / Brain rules, module ownership, version ownership, runtime/main boundary, and any feature-specific architecture/runbook contract before implementation.
8. **Only then implement the feature.** The implementation should fit the reconciled architecture rather than forcing the architecture to accommodate a duplicate path after the fact.

If the architecture or existing implementation is unclear, **search and inspect more before creating new code.** Uncertainty is a reason to widen the affected-architecture check, not a reason to assume the feature does not exist.

### Architecture reconciliation must be recorded

Every governed development event must include a brief architecture-reconciliation note in its roadmap/release record. The note should state, as applicable:

- which architectural surfaces/owners were checked;
- what existing implementation or authority was reused/extended;
- whether overlapping or competing work was found;
- what was reconciled, retired, migrated, or intentionally left unchanged;
- whether the new work introduces a genuinely new independent structure/module;
- why the chosen implementation does not create a duplicate source of truth.

For a small isolated feature this record may be one concise sentence. For cross-module or architectural work it should be detailed enough to preserve the reasoning behind the ownership choice.

### Relationship to versioning, deployment, and roadmap

The architecture reconciliation is an **additional pre-implementation gate**; it does not replace the version, deployment, or verification contracts.

```text
READ PROJECT CONTRACT
        ↓
CAPTURE CURRENT VERSION/SHA BASELINE
        ↓
PRE-FEATURE ARCHITECTURE RECONCILIATION
        ↓
CONFIRM CANONICAL OWNER + MODULE IMPACT
        ↓
DEPLOYMENT-RISK CHECK / APPROVAL GATE IF NEEDED
        ↓
IMPLEMENT THROUGH THE RECONCILED ARCHITECTURE
        ↓
RE-READ VERSION AUTHORITIES / RECONCILE CONCURRENCY
        ↓
ASSIGN SERVER + AFFECTED MODULE VERSIONS
        ↓
VERIFY RESULT
        ↓
RECORD ARCHITECTURE CHECK + PROGRESS IN ROADMAP/RELEASE RECORD
```

**Core rule:** check what already exists around the feature before building it; integrate with the canonical architecture instead of stacking another implementation beside it; then version, verify, and record the event normally.

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

## MASK / HUMAN / BRAIN ARCHITECTURE RULESET — NON-NEGOTIABLE

§wyrlz uses three separate architectural components. They may communicate closely, but their responsibilities MUST remain distinct:

```text
🎭 Chat interface / client = MASK
🧍 Server                  = HUMAN / BODY
🧠 LALM                    = BRAIN
```

This is an engineering boundary, not merely a visual metaphor.

### 1. The Chat interface is the Mask

The Chat client is the presentation, sensing, input, and relay surface through which an outside user interacts with the system.

The mask may be visually rich, expressive, animated, themed, highly interactive, and capable. It may expose controls, cameras, microphones, files, account/profile surfaces, notifications, haptics, local-device information, accessibility features, AR/VR affordances, or other client capabilities. A mask does not have to resemble a human face; it may extend with additional sensors, controls, levers, or mechanisms.

Those capabilities do **not** make the client a cognitive authority.

The client MAY relay factual information that it legitimately owns or receives, including for example:

- the user's exact submitted text;
- bounded conversation/history data selected under the current context contract;
- request/thread/session identity;
- account/profile fields the user has authorized for use;
- approved device-local time, date, timezone, locale, or other factual device context;
- files, images, voice, clicks, selections, control inputs, permissions, and other user-provided or device-provided facts;
- presentation and transport diagnostics needed to operate the interface.

The client MUST NOT turn those facts into cognitive instructions for the LALM.

For example, this is allowed:

```text
prompt = "Hey 👋"
localTime = "18:16"
timeZone = "America/Chicago"
preferredName = <authorized profile value>
```

This is NOT allowed as Chat-owned cognition:

```text
intent = social
responseTopology = social-participation
daypartInterpretation = evening
recommendedGreeting = "Good evening"
instruction = "Do not say morning"
```

The mask relays the user's signal and factual metadata through its "sockets." It does not whisper an interpretation of those facts to the brain.

#### User-facing alignment rule — the mask must sit straight

The three components remain separate internally, but **the user experiences one coherent §wyrlz**. Component boundaries are an engineering/debugging concern; the user must not be required to reconcile contradictory Mask, Human/Body, and Brain states.

The mask's openings must align with the real system underneath them. What the user sees through the mask must faithfully expose the authoritative state or output of the component that owns it. The mask may render or summarize an authoritative fact for presentation, but it MUST NOT fabricate, independently guess, or prematurely declare operational state that belongs to the server/body, and it MUST NOT substitute its own interpretation for LALM/brain cognition.

Examples:

```text
server/body says conversationUsage = 92%, canAppend = true
    -> mask may display "92%" / near-limit styling
    -> mask must keep the conversation writable

server/body says hardLimitReached = true, canAppend = false
    -> mask may display the hard-stop state and disable append controls

brain/LALM produces an answer or interpretation
    -> mask presents that output
    -> mask does not replace it with a competing semantic conclusion
```

If the mask displays "full," "unavailable," "connected," "ready," "failed," or another operational condition while the authoritative body/server state says otherwise, the mask is **tilted/misaligned**: the user is seeing the wrong underlying state through the wrong opening. Treat that as a synchronization/ownership defect even if each component is functioning independently.

Likewise, if the server/body truly has a capacity or protocol limit, the mask must learn that limit from the authoritative server contract/state and display it faithfully; the client must not invent its own limit merely because it can estimate usage locally.

**User-perspective invariant:** internally diagnose whether a defect belongs to the Mask, Human/Body, Brain, or the connection between them; externally preserve one coherent §wyrlz. Separation of responsibility must improve correctness without exposing contradictory component realities to the user.

### 2. The LALM is the Brain

The LALM owns cognition.

Interpretation, reasoning, semantic classification, contextual meaning, intent understanding, domain synthesis, task recognition, temporal interpretation, response planning, requirement tracking, conversational behavior, semantic validation, repair, and answer generation belong in the LALM unless a narrowly defined non-cognitive safety or protocol boundary requires otherwise.

Examples:

```text
18:16 -> infer that this is evening if relevant
"Hey 👋" -> understand that it is a greeting
user asks for code -> determine the programming task and response structure
conversation correction -> preserve valid prior context and revise the affected interpretation
```

The LALM may decide that supplied context is irrelevant and omit it from the response. The client must not force a cognitive conclusion merely because factual metadata was supplied.

There should be one primary cognitive authority. Do not duplicate LALM reasoning in Chat and then ask the LALM to reason over Chat's interpretation of the user.

### 3. The Server is the Human / Body

The server is the capable acting system around the LALM brain.

The server owns operational authority and execution boundaries such as:

- authentication and authorization;
- sessions and request ownership;
- durable state and storage;
- transcript persistence and synchronization;
- network and service access;
- tools and external actions;
- files and data access;
- rate/security boundaries;
- routing and stream transport;
- action execution;
- enforcement of user-granted permissions and pre-authorized automation rules.

The server SHOULD remain operational rather than cognitive. It may validate schema, permissions, identities, safety/authority boundaries, protocol integrity, and whether an action is allowed or technically possible. It must not become a competing reasoning engine for ordinary conversation semantics.

The LALM may reason that an action is useful, but the server controls whether and how that action can actually occur under the authority given to the system.

### 4. Capability is not cognition

A component can become more capable without becoming more intelligent.

Adding a camera, microphone, file picker, notification system, AR surface, robot control, account panel, device bridge, or UI automation to the client is analogous to adding another opening, lever, sensor, or mechanism to the mask. That does not transfer interpretation or reasoning ownership to the mask.

Likewise, adding tools, network access, databases, schedulers, actuators, or integrations to the server expands the human/body's capabilities. It does not make the server the brain.

### 5. Relay facts; do not relay conclusions

When factual context originates outside the LALM, preserve it as factual context whenever practical.

Preferred pattern:

```text
user input + factual metadata + bounded history
                ↓
             server
                ↓
              LALM
                ↓
        interpretation/reasoning
```

Avoid:

```text
user input
   ↓
Chat interprets it
   ↓
Chat writes reasoning instructions
   ↓
server adds another interpretation
   ↓
LALM reasons over the interpretations
```

The latter creates competing cognitive authorities, hidden prompt coupling, harder debugging, and contradictions between layers.

### 6. Human/server action authority remains separate from LALM thought

The LALM is the brain, but a thought is not automatically an action.

The server/human layer owns the mechanisms that turn an allowed decision into an external effect. User approval, stored permissions, policy, explicit automation rules, and available capabilities determine whether an action can occur.

A pre-authorized automation is still an action whose authority originated from a deliberate rule established through the system. It is not independent agency created by the mask.

### 7. Presentation may be complex; the cognitive connection should stay simple

The front of the mask may be spectacular. The connection behind it should remain straightforward.

The preferred Chat-to-server/LALM payload is factual and compact: request identity, user text, bounded/canonical history, authorized user/device/account context, attachments/capabilities when relevant, and transport metadata.

Do not grow the Chat backend into a second semantic planner merely because the frontend becomes richer.

### 8. Ownership test for future features

Use this test whenever deciding where new behavior belongs:

- **Does it capture, relay, transport, render, expose, or execute a capability?** Place it in Chat/client or server according to the owning surface.
- **Does it interpret, infer, classify meaning, reason, decide conversational strategy, plan an answer, or validate semantic correctness?** Place it in the LALM.
- **Does it decide whether an external action is authenticated, authorized, permitted, durable, routable, or executable?** Place it in the server.

When uncertain, preserve raw/factual evidence and let the LALM perform the interpretation rather than pre-interpreting it in Chat.

### 9. Refactor rule

Existing Chat-side cognitive logic is technical debt when it duplicates or steers LALM cognition. During relevant work, prefer migrating such logic into the LALM and reducing Chat to factual context relay, interface behavior, continuity, and presentation.

Do not remove transport integrity, transcript continuity, authentication, user-authorized context capture, UI state, or presentation safeguards merely because cognitive logic is being removed. The goal is separation of responsibility, not loss of capability.

### Architecture shorthand

```text
🎭 MASK  = sense / relay / present
🧍 HUMAN = authorize / operate / execute
🧠 BRAIN = interpret / reason / decide
```

**Core rule: The mask relays evidence to the human/brain system; it does not whisper conclusions to the brain. The server provides the body and action boundary; the LALM provides cognition. Keep all three components distinct internally, while presenting one coherent aligned §wyrlz to the user.**

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
- Perform the required Pre-Feature Architecture Reconciliation over the selected/affected architecture and existing related work before implementation; identify the canonical owner/reuse path and any overlap that must be reconciled.

Immediately before assigning versions or committing:
- Re-read `VERSION.txt` and every affected authoritative `versions/<module-id>.txt` file.
- Compare the current authority state against the event baseline.
- If any relevant authority changed, assume another instance/process advanced the project while this event was in progress.
- **Do not write the previously planned version numbers. Reconcile against the newest authority first, then assign the next valid Server/module versions.**
- Use repository SHA/precondition checks where available so a concurrent write fails instead of silently overwriting newer state.

During the update:
- Apply the appropriate change on `runtime` or `main` according to the hotfix/deployment boundary.
- Implement through the reconciled canonical owner(s); do not create a parallel feature/state/authority path when the existing architecture should be reused, extended, refactored, migrated, or retired.
- Increase the overall Server version for the development event when required by the Server event contract.
- Increase only the component version(s) that actually changed.
- Update each affected module's `versions/<module-id>.txt` authority.
- Update `VERSION.txt` only when module registration/routing changes; do not duplicate version values there.
- Ensure cross-module version displays resolve the owning module's authoritative version automatically.

Before declaring the work complete:
- Record the completed event in `SWRLZ_SERVER_ROADMAP.md`.
- Include a brief architecture-reconciliation note identifying the affected architecture checked, existing owner/work reused or reconciled, and any duplicate/conflicting path retired or intentionally left unchanged.
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
READ SWRLZ_CHAT_CAMERA_LOGS.md
      ↓
IF GOOGLE ACCOUNT/OAUTH RELATED → READ docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md
      ↓
FETCH VERSION.txt ROUTER
      ↓
FETCH AFFECTED versions/<module-id>.txt AUTHORITIES
      ↓
CAPTURE VERSION/SHA BASELINE
      ↓
FETCH CURRENT TARGET SOURCE + RELATED ARCHITECTURE/IMPLEMENTATIONS
      ↓
PRE-FEATURE ARCHITECTURE RECONCILIATION
      ↓
CONFIRM CANONICAL OWNER / REUSE-EXTEND-REFACTOR-RETIRE PATH
      ↓
DETERMINE MODULE IMPACT
      ↓
DEPLOYMENT RISK CHECK FROM CURRENT CONFIG/WORKFLOWS
      ↓
IF DEPLOYMENT-CAUSING → STOP + EXPLAIN + GET USER APPROVAL
      ↓
MAKE SMALLEST SAFE CHANGE THROUGH RECONCILED OWNER
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
UPDATE ROADMAP / RELEASE RECORD + ARCHITECTURE RECONCILIATION NOTE
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
- `SWRLZ_CHAT_CAMERA_LOGS.md` — required Chat observation runbook; maps repository instrumentation to live Vercel runtime logs and turn-correlation workflow.
- `docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md` — required architecture, diagnostic, incident, and recovery reference for Google account/OAuth work.
- `VERSION.txt` — router from stable module IDs to authoritative module-owned version files.
- `versions/*.txt` — authoritative version/revision identity for each independently evolving structure.

If any of these documents conflict, stop and resolve the conflict against the newest authoritative repository state before editing application code.

## BOTTOM LINE

**Read `SWRLZ_PROJECT_START.md`, then automatically read `SWRLZ_HOTFIX_RULES.md`, `SWRLZ_VERSION_MODULE_EVOLUTION.md`, `SWRLZ_SERVER_ROADMAP.md`, and `SWRLZ_CHAT_CAMERA_LOGS.md`. The Chat camera runbook establishes that GitHub contains instrumentation/source while live production camera observations are normally read from Vercel runtime logs and correlated by request/thread identity. For Google account/OAuth work, also read `docs/runbooks/GOOGLE_OAUTH_CHAT_AUTH_RUNBOOK.md` before diagnosing or editing that flow. Resolve current module versions through `VERSION.txt` and each module's own `versions/<module-id>.txt`. Capture those authorities as the event baseline. Before implementing each feature/fix/optimization/refactor, perform a brief but complete reconciliation of the selected/affected architecture and existing related implementations, confirm the canonical owner and integration path, and avoid introducing duplicate or competing feature/state/authority paths. Then re-read version authorities immediately before version assignment/commit so concurrent updates are detected and reconciled rather than overwritten. Follow the hotfix/deployment boundary based on current deployment configuration and workflows, not branch name alone. Before any action that can actually cause deployment, STOP, explain exactly what would cause it and why, and obtain explicit user approval. Every server development event receives the Server lineage treatment required by the evolution contract; only actually changed components receive component bumps; independently evolving structures own their own version files; cross-module displays resolve those authorities automatically; failures remain in lineage; and the completed event—including a brief architecture-reconciliation note—is recorded in the roadmap before the work is declared done. Preserve the Mask / Human / Brain boundary: Chat relays and presents factual evidence, the Server owns operational/action authority, and the LALM owns cognition and interpretation.**