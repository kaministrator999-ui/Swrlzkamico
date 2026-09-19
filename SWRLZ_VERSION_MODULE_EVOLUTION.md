# §wyrlz Server + Module Version Evolution Contract — READ THIS THIRD

**Role:** canonical owner of Server-event lineage, independently evolving module versions, version-source authority, concurrency-safe assignment, failure lineage, and roadmap/release recording.

**Startup/read order is owned by `SWRLZ_PROJECT_START.md`.** This document must not create a competing project-start sequence.

Architecture placement is owned by `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`. Mutation/deployment mechanics are owned by `SWRLZ_HOTFIX_RULES.md`. Diagnostics are owned by `SWRLZ_CHAT_CAMERA_LOGS.md`. User-facing project reporting is owned by `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md`.

---

## 1. Core evolution law

Repository work, deployed Server releases, and component/module evolution are three distinct lineages.

Every completed governed repository update advances the canonical **Repository Work** version. This records which repository engineering tier/update is current even when no running Server or runtime component is touched.

The **Server Runtime** version advances only when a Server release/deployment event actually changes the deployed Server lineage. Editing documentation, adding directories/scaffolding, or changing a runtime-hot component without deploying/releasing the Server does not advance Server Runtime merely because repository work occurred.

Each independently evolving component/module advances only when that component actually changes.

Conceptually:

```text
Repository Work = what governed repo update/tier are we at?
Server Runtime  = what deployed Server release are we at?
Module version  = what evolution state is this component at?
```

A single repository tier may therefore advance Repository Work only, Repository Work + Chat, or Repository Work + Server + affected modules depending on what actually changed and what was deployed/released.

Governed events include successful changes and, when they mutate/advance governed project state, failed or partial attempts that must remain visible in lineage.

A failed attempt is never silently rewritten out of history. A corrective attempt is a later event/version.

---

## 2. Independent module lineage

Each independently evolving module owns its own version.

A module version answers:

> What evolution state is this module in after the relevant Server event?

Rules:

- bump the Repository Work version for every completed governed repository update;
- bump Server Runtime only for an actual Server release/deployment event that advances deployed Server lineage;
- bump only modules that actually changed;
- do not bump unrelated modules merely because the Server event advanced;
- a module may remain unchanged across many Server releases;
- a failed event that actually changed a module preserves that module's changed lineage rather than pretending it never happened.

Example:

```text
Server 2.4.10
├─ Chat 1.8.2      changed
├─ LALM 2.3.1      unchanged
└─ Server UI 1.1.4 unchanged
```

---

## 3. Canonical version ownership

`VERSION.txt` is the **complete overview router/index** from stable governed version IDs to their authoritative version files. Any governed component/artifact that carries an independently advanced version identifier (including activation manifests) MUST be registered here so one bounded registry read discovers the complete version pool.

It must not become a second manually maintained copy of every module number: the registry collects routes, while each referenced authority owns the actual version value.

Pattern:

```text
VERSION.txt
   ↓
versions/<module-id>.txt
   ↓
module/status/update consumer
```

Cross-module consumers query the owning authority. They do not hardcode another module's version.

Examples of current/reserved owners include:

- `versions/repository-work.txt`
- `versions/server-runtime.txt`
- `versions/server-ui.txt`
- `versions/web-frontend.txt`
- `versions/web-chat.txt`
- `versions/runtime-manifest.txt`
- `versions/stream-contract.txt`
- `versions/lalm-ui.txt`
- `versions/lalm-engine.txt`
- `versions/online-research.txt`
- `versions/admin-web.txt`
- `versions/google-account.txt`
- `versions/client-apk.txt`
- `versions/server-apk.txt`
- `versions/frozen-web-collector.txt`
- `versions/deployment-control.txt`

Always read current `VERSION.txt`; this list may evolve.

If the real current version of an artifact cannot be verified, use an explicit unassigned/unknown state rather than inventing one.

---

## 4. New independently evolving structure

If architecture reconciliation proves that a genuinely independent subsystem/module is required, the same governed event establishes its version ownership.

That normally includes:

1. stable module ID;
2. `versions/<module-id>.txt` authority;
3. registration in `VERSION.txt`;
4. status/update surfaces deriving from that authority;
5. cross-module consumers querying the owner;
6. roadmap/release lineage from that point forward.

Do not create an independent module authority merely because another file/class/service is convenient. The architecture protocol owns the new-module test.

---

## 5. Event baseline — mandatory

At event entry:

1. read current `VERSION.txt`;
2. read `versions/repository-work.txt`;
3. read `versions/server-runtime.txt`;
4. read every module authority that the requested work may affect;
5. record exact version values and file/blob SHAs as the **event baseline**;
6. read the current roadmap/release state;
7. fetch the current target source before editing.

The baseline is an observation, **not a reservation**.

---

## 6. Concurrency invariant

Immediately before assigning versions or committing the versioned event:

1. re-read `VERSION.txt`;
2. re-read `versions/repository-work.txt`;
3. re-read `versions/server-runtime.txt`;
4. re-read every affected module authority;
5. compare current values/SHAs with the event baseline.

If relevant authority moved:

- assume another process/agent/developer advanced the project;
- do not use stale planned version numbers;
- inspect the concurrent event enough to preserve it;
- reconcile this work on top of the newest authority;
- then assign the next valid versions.

Conceptually:

```text
READ AUTHORITY AT ENTRY
        ↓
DO ARCHITECTURE RECONCILIATION + WORK
        ↓
RE-READ AUTHORITY AT VERSION BOUNDARY
        ↓
UNCHANGED → assign next versions
CHANGED   → reconcile newest state first
```

Use SHA/precondition protection where available so stale writes fail rather than overwrite newer work.

---

## 7. Relationship to architecture reconciliation

Versioning follows the architecture decision; it does not choose architecture.

Before module impact is finalized, the architecture protocol must establish:

- desired outcome;
- canonical owner(s);
- overlapping/partial/legacy/fallback work;
- relevant readers/writers/lifecycle;
- source vs live vs historical evidence when relevant;
- integration path: reuse, extend, consolidate, migrate+retire, or new structure;
- Mask/Human/Brain placement.

Only then determine which modules actually changed and therefore require module bumps.

A feature that touches several files but remains inside one module may require one module bump. A change that truly crosses module-owned contracts may require several.

---

## 8. Relationship to diagnostics

Issue-fixing work follows `SWRLZ_CHAT_CAMERA_LOGS.md` automatically.

Camera/log evidence can change the module-impact conclusion. For example, a visual symptom may be caused by a loader or server-state owner rather than the visible Chat layer.

Do not bump the apparent symptom module until architecture/evidence establishes what actually changed.

If new persistent instrumentation changes an affected runtime module, that module's version should advance accordingly.

---

## 9. Relationship to deployment

Versioning does not authorize deployment.

`SWRLZ_HOTFIX_RULES.md` owns the Deployment Approval Gate.

A module can receive a new source version while production activation remains pending if no approved deployment/restart/live activation has occurred.

Release records must distinguish:

- source complete;
- static verified;
- runtime verified;
- live/user-visible verified;
- published, activation pending;
- blocked/failed.

Do not equate “new version committed” with “new version observed live.”

---

## 10. Version assignment

After architecture/work is ready and authorities have been revalidated:

1. assign the next Repository Work version from the newest `repository-work` authority for the completed governed repository tier;
2. advance Server Runtime only when this tier actually performs/records a Server release or deployment that advances deployed Server lineage;
3. increment only actually changed module versions;
4. update each changed authority file;
5. update `VERSION.txt` only when module routing/registration changed;
6. ensure consumers derive version state from the owner;
7. preserve concurrent events and failed events rather than reusing their numbers.

No duplicate version literal should become authoritative merely because it appears in a page, filename, commit message, roadmap, or release document.

---

## 11. Transactional roadmap journal — mandatory

The roadmap is a before/after engineering journal, not only a post-hoc changelog.

Before the first implementation mutation of every governed update, create an **UPDATE STARTED** record in `SWRLZ_SERVER_ROADMAP.md` containing, as applicable:

- event intent/requested outcome;
- observed Server/module version and SHA baseline;
- expected canonical owner and module impact;
- expected files/surfaces when useful;
- deployment expectation;
- verification/acceptance plan;
- `Status: IN PROGRESS`.

Do not treat a planned next version as reserved at START; concurrency rules still apply.

After mutation, re-read authorities, reconcile concurrency, assign versions, and verify the result. Then update the event with **UPDATE FINISHED** and record:

- actual changes and canonical owner;
- resulting Server and changed-module versions;
- verification truth state (source/static/runtime/live);
- runtime-hot/activation evidence as applicable;
- deployment/restart state;
- failure/correction/supersession lineage when applicable;
- `Result: COMPLETE` or another explicit terminal state.

If an `UPDATE STARTED` record has no terminal marker, future governed work MUST reconcile it before overlapping mutation. Inspect current source, version authorities, commits, roadmap, and runtime evidence as applicable, then explicitly resume+finish it or mark it **ABORTED** or **SUPERSEDED** with evidence. Never erase or silently skip interrupted work.

### Continuation lifecycle — mandatory

A governed update that is interrupted and later resumed/recontinued keeps one event identity and an explicit session lifecycle:

```text
UPDATE STARTED
  ↓
[work / interruption]
  ↓
UPDATE CONTINUATION STARTED
  ↓
[resumed work]
  ↓
UPDATE CONTINUATION ENDED
  ↓
[optional later interruption/resume]
  ↓
UPDATE CONTINUATION STARTED
  ↓
...
  ↓
UPDATE FINISHED | ABORTED | SUPERSEDED
```

Rules:

- The original UPDATE STARTED is never replaced by a continuation marker.
- Every resumed/recontinued session gets its own UPDATE CONTINUATION STARTED **before** new implementation mutation.
- If that session pauses/stops while the overall event remains open, it gets UPDATE CONTINUATION ENDED before leaving the work. Record the exact stop point, mutations made, current authority/version/truth state, verification/deployment state, and remaining work.
- If that resumed session closes the overall event, UPDATE FINISHED, ABORTED, or SUPERSEDED is the continuation's end marker; do not require a duplicate CONTINUATION ENDED immediately before it.
- A later resume gets a new continuation-start marker. Never reuse an older continuation marker for a new session.
- Startup reconstruction must treat a continuation-start marker without either a later continuation-end marker or terminal event marker as interrupted-in-continuation work requiring reconciliation before overlapping mutation.

This makes every continuation recoverable: **event start → each continuation start → each continuation end → terminal event end**.

Roadmap/documentation bookkeeping is deployment-inert and does not authorize deployment. The deployment gate remains owned by `SWRLZ_HOTFIX_RULES.md`.

## 11A. Atomic registered-module Roadmap synchronization — mandatory

Whenever a module registered in `runtime:VERSION.txt` receives a new version value, that version mutation and its Roadmap lineage are one governed transaction.

- Before implementation/version mutation, the governing Roadmap event must already contain UPDATE STARTED or the required CONTINUATION checkpoint.
- Every registered module whose version changes must be named in that same event with its prior version, resulting version, reason for advancement, verification/activation truth, and deployment/restart consequence.
- The module authority file and Roadmap must not intentionally finish at different resulting versions. Re-read both before UPDATE FINISHED.
- A changed module may not be omitted from the Roadmap merely because Repository Work also advances.
- Untouched modules do not bump; when useful for avoiding ambiguity, record them as intentionally unchanged.
- Repository Work still advances for every completed governed repository tier according to its policy, and its resulting version is recorded in the same FINISHED event.
- If a version file was advanced but the Roadmap was not synchronized, treat the governed event as incomplete and repair the ledger before beginning unrelated overlapping work.

The invariant is: **registered version mutation ⇄ same-event Roadmap lineage**. Neither side is governably complete without the other.

---

## 12. Roadmap / release record — mandatory

Every completed governed event receives a durable record in `SWRLZ_SERVER_ROADMAP.md` and/or the appropriate release record.

Record, as applicable:

- overall Server version;
- affected module versions;
- important unchanged modules when useful;
- requested outcome / event purpose;
- architecture reconciliation summary;
- canonical owner and overlap found;
- reused/extended/refactored/migrated/retired paths;
- exact change/attempt description;
- camera/log diagnostic evidence when issue work used it;
- source/static/runtime/live verification state;
- failures or unsuccessful acceptance;
- deployment/restart state;
- commit/source lineage;
- migration/rollback notes.

The roadmap is durable engineering memory. It should explain why future work sees the architecture it sees.

Do not finish a completed governed event while the roadmap still presents the prior Server baseline as current.

---

## 13. Failure lineage

Failure is data.

If a governed attempt fails:

- record what changed/was attempted;
- record the evidence showing failure;
- preserve the Server/module lineage required by this contract;
- do not overwrite or relabel the failed event as success;
- perform the correction as the next event when applicable.

This prevents later engineering agents from repeating an invisible failed path.

---

## 14. Source-of-truth precedence for version identity

For version identity:

```text
module-owned versions/<module-id>.txt
        ↓
authoritative API/status derived from it
        ↓
UI/update checker consuming that authority
```

Roadmaps, changelogs, filenames, labels, release notes, and commit messages describe lineage but do not outrank the module-owned authority.

For architecture and runtime behavior, use the architecture protocol's distinction between:

- current engineering/source authority;
- live production activation;
- historical evidence.

---

## 15. Programming-LALM curriculum

This document teaches the programming LALM the **evolution grammar** of a project.

The architecture reconciliation protocol teaches **where a change belongs**.

Together, the programming workflow is:

```text
REQUEST
  ↓
DESIRED OUTCOME + CONSTRAINTS
  ↓
CAPTURE VERSION/SHA BASELINE
  ↓
ARCHITECTURE RECONCILIATION
  ↓
AUTOMATIC DIAGNOSTIC EVIDENCE LOOP IF FIXING AN ISSUE
  ↓
CONFIRM MODULE IMPACT
  ↓
WRITE ROADMAP UPDATE STARTED
  ↓
DEPLOYMENT CAPABILITY CHECK
  ↓
IMPLEMENT THROUGH CANONICAL OWNER
  ↓
VERIFY OWNERSHIP
  ↓
RE-READ VERSION AUTHORITIES
  ↓
RECONCILE CONCURRENCY
  ↓
ASSIGN SERVER + CHANGED-MODULE VERSIONS
  ↓
UPDATE CANONICAL VERSION SOURCES
  ↓
VERIFY BEHAVIOR / OWNERSHIP / ACTIVATION AS RELEVANT
  ↓
WRITE ROADMAP UPDATE FINISHED
  ↓
HUMAN UPDATE USING RESPONSE STANDARD
```

Versioning is part of engineering itself, not cosmetic cleanup after coding.

---

## 16. Completion questions

Before declaring a versioned event complete, §wyrlz should be able to answer:

1. What Server authority was observed at event entry?
2. Which module authorities were potentially affected?
3. What exact values/SHAs formed the baseline?
4. What architecture owner did reconciliation establish?
5. Which modules actually changed?
6. Did diagnostics reveal a different owner than the visible symptom suggested?
7. Were authorities re-read immediately before assignment?
8. Did concurrent work advance them?
9. If yes, was that work preserved and this event rebased conceptually on the newest authority?
10. What Server version records this event?
11. Which module versions advanced and which intentionally did not?
12. Do consumers resolve those versions from canonical owners?
13. What verification level actually passed?
14. Was deployment/restart none, pending, approved, or performed?
15. Does the roadmap/release record accurately preserve architecture, diagnostics, failure, verification, and lineage?

If a required answer is unknown, resolve it before claiming completion.

---

## 17. Human-readable reporting

Detailed engineering evidence belongs in durable repository records.

The conversational project update follows `docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md` and should make the result easy to scan without dumping raw internals unless requested.

Always distinguish the overall Server event from independently changed module versions.

---

## Bottom line

**Repository Work versions are chronological governed-repository-update lineage. Server Runtime versions are deployed Server release lineage. Module versions are independent component lineage. Capture authority at entry, reconcile architecture before deciding module impact, inspect diagnostics automatically for defects, re-read authority before version assignment, preserve concurrent and failed events, bump only what actually changed, keep version values in module-owned sources, record the completed event durably, and report the truth state clearly to the user.**