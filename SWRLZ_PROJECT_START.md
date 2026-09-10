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

Do not ask the user to repeat these instructions unless the repository/files are genuinely inaccessible.

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

Defines the entry sequence and the non-negotiable project-start procedure.

### Document 2 — Hotfix Rules

Defines the `runtime` vs. `main` boundary, safe editing rules, deployment/restart rules, and verification requirements.

### Document 3 — Version + Module Evolution Contract

Defines how §wyrlz evolves as an engineered system. It governs overall Server versioning, independent module versioning, failed-event lineage, canonical version ownership, automatic cross-module version resolution, release records, verification, and commit lineage.

**This is also the foundation for the future programming-side LALM engineering curriculum/specification.** The programming LALM must eventually learn this structure as an engineering process, not as optional documentation.

### Document 4 — Server Roadmap

Records the actual chronological Server/module release history and current version ledger.

## NON-NEGOTIABLE WORK RULE

`runtime` = durable live application source of truth.

`main` = stable loader/infrastructure/deployment boundary.

For Chat, pages, page-owned JS/CSS, stream UI, runtime assets, and runtime-loadable LALM/R39: edit `runtime`, make the smallest targeted change, commit it, reload/request, verify it live, and **DO NOT DEPLOY or RESTART** for ordinary runtime changes.

For stable API, middleware, authentication/security boundaries, runtime loader/source resolution, hydration/sync infrastructure, deployment/build configuration, or capabilities the current loader cannot serve: edit `main` and **DEPLOY + VERIFY**.

Never use `dev` as the Chat/runtime hotfix source.
Never use `/tmp` as durable source of truth.
Never replace a complete page for a small targeted change.
Never introduce a competing hardcoded page/version injector in `main`.

## AUTOMATIC VERSION + ROADMAP RULE

**Every server development event governed by the version-evolution contract MUST automatically receive an overall Server version and a durable roadmap/release record.**

This happens as part of the update workflow, not as an optional follow-up task.

Before the update:
- Read the current overall Server version and component versions from `SWRLZ_SERVER_ROADMAP.md` and authoritative module sources.
- Read `SWRLZ_VERSION_MODULE_EVOLUTION.md` and determine which components actually change.

During the update:
- Apply the appropriate change on `runtime` or `main` according to the hotfix/deployment boundary.
- Increase the overall Server version for the development event.
- Increase only the component version(s) that actually changed.
- Update each affected module's canonical version source.
- Ensure cross-module version displays resolve the owning module's authoritative version automatically.

Before declaring the work complete:
- Record the completed event in `SWRLZ_SERVER_ROADMAP.md`.
- Include the overall Server version, affected module versions, exact update notes, failures/attempts, deployment status, verification, commit lineage, and rollback/migration notes when applicable.
- If the event changed stable infrastructure on `main`, deploy and verify production before closing the release.
- If the event was runtime-only, explicitly record `Deployment: NONE` and verify the live runtime source without deployment.
- If an attempt fails, preserve that event in the lineage and treat the next correction as another versioned event.

**Never finish a versioned server development event with the roadmap still saying “NEXT RELEASE.”** Replace that placeholder with the actual completed release entry and reserve the next version only after the current event is recorded.

## CURRENT BASELINE

At the creation of this instruction file:

- Overall Server: `2.2.0`
- Chat: `1.4.2`
- Next overall release: `2.2.1`

These numbers are informational only. Always read the roadmap and authoritative module sources before the next update because the values may have advanced.

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
FETCH CURRENT TARGET + VERSION SOURCES
      ↓
DETERMINE MODULE IMPACT
      ↓
MAKE SMALLEST SAFE CHANGE
      ↓
ASSIGN NEW OVERALL SERVER VERSION
      ↓
INCREMENT ONLY CHANGED COMPONENT VERSIONS
      ↓
UPDATE CANONICAL VERSION SOURCES
      ↓
VERIFY CROSS-MODULE VERSION RESOLUTION
      ↓
COMMIT TO runtime OR main
      ↓
UPDATE ROADMAP / RELEASE RECORD
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
- `SWRLZ_SERVER_ROADMAP.md` — authoritative overall/component version ledger and release history.

If any of these documents conflict, stop and resolve the conflict against the newest authoritative repository state before editing application code.

## BOTTOM LINE

**Read `SWRLZ_PROJECT_START.md`, then automatically read `SWRLZ_HOTFIX_RULES.md`, `SWRLZ_VERSION_MODULE_EVOLUTION.md`, and `SWRLZ_SERVER_ROADMAP.md`. Follow the hotfix/deployment boundary. Every server development event receives a new overall Server version; only actually changed components receive component bumps; canonical version sources stay authoritative; cross-module displays resolve versions automatically; failures remain in lineage; and the completed event is recorded in the roadmap before the work is declared done.**
