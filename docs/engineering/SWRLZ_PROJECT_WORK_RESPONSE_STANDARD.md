# §wyrlz Project Work Response Standard — READ THIS SEVENTH

**Role:** this document owns the communication contract for how §wyrlz reports project work back to the user. It does not own architecture, versioning, deployment, diagnostics, or roadmap lineage; those remain in their canonical documents.

**Purpose:** make every project-work response easy to scan, easy to trust, and explicit about what changed, what is verified, what is only source-complete, and what remains unresolved.

---

## 1. Core communication rule

Project-work responses should optimize for **readability, status clarity, and decision usefulness**, not for dumping implementation detail.

The user should be able to answer these questions quickly after reading a response:

1. What did §wyrlz discover?
2. What did §wyrlz change?
3. What does that change accomplish?
4. What architecture/owner was involved?
5. What version changed, if any?
6. Was deployment or restart involved?
7. What was actually verified?
8. Is anything still pending, blocked, or unverified?

Do not force the user to reconstruct those answers from a wall of prose.

---

## 2. Default response shape

For substantial project work, use this general structure when the sections are relevant:

```text
## Status
One compact statement of the result/current state.

## What I found
The important diagnosis or architecture fact.

## What changed
What was implemented, corrected, documented, reconciled, or intentionally left alone.

## Verification
What source/static/runtime/live checks actually passed, and what was not tested.

## Version / deployment
Server/module versions, deployment/restart state, and whether production activation was observed.

## Remaining state
Only real blockers, pending acceptance, or the next meaningful engineering fact.
```

This is a default shape, not a rigid template. A tiny change may need only Status + Verification + Version/deployment. A large cross-module event may need all sections.

---

## 3. Formatting requirements

- Use short descriptive Markdown headings for substantial updates.
- Prefer compact paragraphs and small bullet groups over long dense walls of text.
- Bold the most important state changes, versions, acceptance states, and warnings.
- Keep raw commit hashes, internal function names, implementation syntax, and long file lists out of the main conversational summary unless they materially help the user or the user asks for them.
- Put the human-visible accomplishment before low-level implementation detail.
- Keep terminology consistent across the response: do not alternate between several names for the same owner/state without explaining the relationship.
- Use code blocks only for code, exact schemas/flows, commands, or other content that materially benefits from monospace structure.
- Use tables only when comparison/ownership/version information is genuinely easier to understand in a table.
- Do not repeat the same status in several headings using slightly different wording.

---

## 4. Truth-state vocabulary

Use precise completion language. These states are not interchangeable.

### Source complete

The repository/source change exists and has been re-read/verified.

### Static verified

Syntax, deterministic tests, schemas, or source-level acceptance checks passed.

### Runtime verified

The running system emitted evidence showing the relevant path executed.

### Live/user-visible verified

The actual production/runtime/UI behavior was observed and matched the intended result.

### Published, activation pending

The authoritative source/version is published, but live evidence has not yet shown that the active worker/client loaded it.

### Blocked

A concrete prerequisite prevents completion. State the prerequisite rather than implying generic uncertainty.

Never collapse “source complete” into “fixed live” when live activation has not been observed.

---

## 5. Architecture reporting

Project responses should surface architecture conclusions without dumping private reasoning.

When architecture reconciliation materially affected the work, state concisely:

- the canonical owner that was reused or extended;
- any competing/legacy path that was found;
- whether anything was consolidated, migrated, retired, or intentionally left unchanged;
- whether a genuinely new module/authority was introduced.

Do not narrate every search query or every internal possibility considered. Report the evidence-backed conclusion.

---

## 6. Diagnostic/fix reporting

For issue-fixing work, responses should distinguish:

```text
SYMPTOM
what the user/system experienced

EVIDENCE
what source/cameras/logs/runtime actually showed

CAUSE
the supported diagnosis

FIX
what changed at the canonical owner

ACCEPTANCE
what proved or did not yet prove the fix
```

If cameras/instrumentation were added because the previous observability was insufficient, say so briefly and state whether those cameras are persistent or temporary.

---

## 6A. Compact startup stage report

When the response is the terminal report for `§§` / `@GitHub §§`, preserve the normal readable stage presentation but include a compact **versioned-module handoff ledger** covering every authority registered in `runtime:VERSION.txt`. Each entry should show the authoritative current version and the latest supported Roadmap handoff/state for that module.

Then include a visually distinct **Where we actually left off** section identifying the newest completed governed event and, separately, the newest unresolved/interrupted event when one exists. Do not equate newest commit with newest unresolved engineering work.

The agent may reconstruct more forensic detail internally than it displays. Surface the details needed to understand readiness, ownership, activation, blockers, and the current handoff; keep low-value retrieval narration backstage.

---

## 7. Version/deployment reporting

For every governed versioned event, the conversational response should state:

- resulting overall Server version;
- affected module version(s), only when those modules actually changed;
- intentionally unchanged major modules when that prevents confusion;
- deployment/restart status;
- live activation status when relevant.

Do not imply a component changed merely because the overall Server event advanced.

---

## 8. Progress updates during long work

For long multi-step work, provide occasional concise progress updates that communicate meaningful discoveries or state transitions.

Good progress updates include:

- a newly discovered architecture owner;
- a conflicting implementation found;
- a version-concurrency advance that changed the planned release number;
- a camera/log finding that changes the diagnosis;
- source publication completed and live acceptance beginning.

Avoid low-value narration such as announcing every file fetch, every search query, or every trivial edit.

---

## 9. Avoid false certainty and vague hedging

Bad:

> Should be fixed now.

Better:

> Source and deterministic verification pass; production has not yet emitted the new revision, so live acceptance is still pending.

Bad:

> Something in the loader seems wrong.

Better:

> The repository points to v65, while runtime logs show the worker hydrating v64; the mismatch is in the activation path, not the response planner itself.

State the narrowest conclusion supported by evidence.

---

## 10. User control over detail

The default should be readable engineering status, not maximum verbosity.

If the user asks for implementation detail, expand into files, functions, commits, traces, schemas, or exact code as appropriate.

If the user prefers shorter updates, preserve the key truth states and versions while compressing implementation detail.

Readability must not come at the cost of omitting a material failure, deployment requirement, data-risk issue, or verification limitation.

---

## 11. Relationship to the other project documents

This document owns **how results are communicated to the user**.

It does not replace:

- `SWRLZ_PROJECT_START.md` — project-work router/orchestrator;
- `SWRLZ_HOTFIX_RULES.md` — mutation/deployment/version mechanics;
- `SWRLZ_VERSION_MODULE_EVOLUTION.md` — Server/module lineage;
- `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md` — architecture discovery/integration method;
- `SWRLZ_SERVER_ROADMAP.md` — durable historical/progress ledger;
- `SWRLZ_CHAT_CAMERA_LOGS.md` — diagnostic camera/log evidence contract.

The detailed engineering record belongs in the roadmap/release/docs. The conversation should communicate the useful result cleanly.

---

## 12. Definition of a good project-work response

A response is good when the user can scan it once and understand:

> what happened, why it matters, whether it is actually verified, what versions/owners changed, whether deployment occurred, and whether anything remains unresolved.

The response should feel like a clear engineering handoff, not an internal debug transcript.

---

## Bottom line

**Project work must be reported in a structured, readable, evidence-aware way. Lead with status and accomplishment; separate findings from changes and verification; distinguish source/static/runtime/live acceptance; report versions and deployment honestly; surface architecture conclusions without dumping private reasoning; and keep low-level implementation detail in durable engineering records unless the user asks for it.**
