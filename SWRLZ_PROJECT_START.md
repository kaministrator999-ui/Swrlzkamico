# §wyrlz Project Start — READ THIS FIRST

**Purpose:** This is the single short instruction file to use whenever §wyrlz project development work starts or resumes in a new ChatGPT thread.

## START COMMAND

When the user says **“start project work”**, **“resume project work”**, **“work on §wyrlz”**, or explicitly tells you to read this file:

1. Read this file first.
2. Immediately read `SWRLZ_HOTFIX_RULES.md`.
3. Immediately read `SWRLZ_SERVER_ROADMAP.md`.
4. Treat those three files as the current operating contract before touching the repository.
5. Fetch the current target file/commit state before making any edit.

Do not ask the user to repeat these instructions unless the repository/files are genuinely inaccessible.

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

**Every intentional completed project update MUST automatically receive an overall Server version increase and a roadmap entry.**

This happens as part of the update workflow, not as an optional follow-up task.

Before the update:
- Read the current overall Server version and component versions from `SWRLZ_SERVER_ROADMAP.md`.
- Determine which components actually changed.

During the update:
- Apply the appropriate change on `runtime` or `main` according to the hotfix/deployment boundary.
- Increase the overall Server version for the release.
- Increase only the component version(s) that actually changed.

Before declaring the work complete:
- Append a completed release entry to `SWRLZ_SERVER_ROADMAP.md`.
- Include the overall Server version, every component version, deployment status, exact update notes, verification, and rollback/migration notes when applicable.
- If the release changed `main`, deploy and verify production before closing the release.
- If the release was runtime-only, explicitly record `Deployment: NONE` and verify the live runtime source without deployment.

**Never finish an intentional project update with the roadmap still saying “NEXT RELEASE.”** Replace that placeholder with the actual completed release entry and reserve the next version only after the current release is recorded.

## CURRENT BASELINE

At the creation of this instruction file:

- Overall Server: `2.2.0`
- Chat: `1.4.2`
- Next overall release: `2.2.1`

These numbers are informational only. Always read the roadmap before the next update because the values may have advanced.

## REQUIRED RELEASE LOOP

```text
START PROJECT WORK
      ↓
READ THIS FILE
      ↓
READ SWRLZ_HOTFIX_RULES.md
      ↓
READ SWRLZ_SERVER_ROADMAP.md
      ↓
FETCH CURRENT TARGET
      ↓
MAKE SMALLEST SAFE CHANGE
      ↓
COMMIT TO runtime OR main
      ↓
VERIFY LIVE RESULT
      ↓
INCREASE OVERALL SERVER VERSION
      ↓
INCREASE ONLY CHANGED COMPONENT VERSIONS
      ↓
APPEND RELEASE ENTRY TO ROADMAP
      ↓
ONLY THEN DECLARE UPDATE COMPLETE
```

## SOURCE DOCUMENTS

- `SWRLZ_PROJECT_START.md` — single entrypoint; tells future §wyrlz what to read and what must happen every update.
- `SWRLZ_HOTFIX_RULES.md` — exact hotfix vs. redeploy boundary and safe editing rules.
- `SWRLZ_SERVER_ROADMAP.md` — authoritative overall/component version ledger and release history.

If any of these documents conflict, stop and resolve the conflict against the newest authoritative repository state before editing application code.

## BOTTOM LINE

**One instruction to remember:**

> Read `SWRLZ_PROJECT_START.md`, then automatically read `SWRLZ_HOTFIX_RULES.md` and `SWRLZ_SERVER_ROADMAP.md`. Follow the hotfix/deployment boundary. Every intentional update automatically gets a new overall Server version, only the changed components get component bumps, and the completed release is recorded in the roadmap before the work is declared done.
