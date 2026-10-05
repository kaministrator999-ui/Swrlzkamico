# §wyrlz Project Diagnostic Cameras + Logs — READ THIS SIXTH

**Compatibility filename:** `SWRLZ_CHAT_CAMERA_LOGS.md` remains the canonical path so existing references do not break.

**Role:** this document owns the project-wide diagnostic observation contract: when to inspect existing evidence, when to add cameras/instrumentation, where repository-side diagnostic evidence lives, where live observations live, and how to separate source facts from runtime facts and user-visible facts.

**Purpose:** future §wyrlz engineering sessions should not diagnose issues from source guesses alone or wait for the user to repeatedly request logging. When fixing an issue anywhere in the project, §wyrlz automatically checks the relevant existing cameras/logs/evidence and adds bounded instrumentation where the current observability cannot answer the important question.

This document does not own architecture placement, versioning, deployment, or conversational formatting. Those remain in their dedicated project documents.

---

## 1. Automatic issue-diagnostic rule

Whenever project work is primarily **fixing, debugging, investigating, or verifying a defect**, the engineering agent MUST automatically perform the diagnostic loop below without waiting for the user to separately ask for logs.

```text
SYMPTOM / FAILURE
      ↓
ARCHITECTURE OWNER RECONCILIATION
      ↓
CHECK EXISTING REPOSITORY-SIDE DIAGNOSTIC EVIDENCE
      ↓
CHECK AVAILABLE LIVE / RUNTIME / WORKFLOW EVIDENCE
      ↓
ENOUGH OBSERVABILITY?
   ├─ YES → diagnose from evidence
   └─ NO  → add bounded camera/instrumentation at the missing boundary
                         ↓
                  reproduce / request
                         ↓
                   inspect evidence
                         ↓
                 fix canonical owner
                         ↓
              re-check cameras/logs
                         ↓
                     acceptance
```

The default is **inspect first, instrument second, mutate third** when diagnosis is uncertain.

During an active lockdown/debugging phase, do not ration cameras merely because existing evidence answers one question. Preserve useful existing cameras and maintain full-map observability so one request can be reconstructed end-to-end. Log volume and presentation cleanliness are secondary until behavior is accepted; cleanup is a later reconciliation step.

---

## 2. What “camera” means

A camera is structured diagnostic instrumentation placed at a meaningful architecture boundary or lifecycle transition so §wyrlz can observe what the system actually did.

A camera may record facts such as:

- request/thread/session identity;
- module/version/revision/source identity;
- route or lifecycle phase;
- selected state transition;
- loader/hydrator/fallback choice;
- ownership/source selection;
- bounded history/context metadata;
- start/success/failure/terminal state;
- timing/latency data;
- cache or persistence decision;
- compatibility/fallback activation;
- sanitized error classification.

A camera is never permission to expose credentials, secrets, authentication tokens, cookies, device proofs, or other security material. During an explicitly authorized single-user lockdown/debugging phase, however, raw application payloads, prompt/policy text, stream events, inference/token metadata, state mutations, and frame geometry may be recorded when needed to reconstruct execution completely.

### Camera design rule

Normal operation should prefer structured records. During active lockdown diagnosis, **coverage wins over terseness**: emit structured records at every meaningful transition and retain the lower-, middle-, and high-level cameras simultaneously. A dense trace is intentional evidence, not accidental noise.

When practical, include enough identity to correlate the event across layers:

```text
event / phase
requestId or operationId
thread/session/account scope when legitimately available
module + version/revision
source/owner identity
result / transition
bounded diagnostic fields
```

Never log secrets merely because they would make debugging easier.

---

## 3. Repository-side evidence — automatically inspect it

GitHub is the engineering/source side of the diagnostic story. When fixing an issue, automatically inspect the relevant repository evidence before assuming the cause.

Depending on the feature, that may include:

- current canonical source on `runtime` or `main`;
- existing camera/instrumentation code;
- manifests, registries, loaders, fallbacks, and cache ownership;
- `VERSION.txt` and affected `versions/*.txt` authorities;
- current Project Start / architecture / feature-specific runbooks;
- `SWRLZ_SERVER_ROADMAP.md` and relevant release records;
- `docs/engineering/Engineering_Log.md` when it contains related incident/verification history;
- recent commits for the affected architecture;
- test fixtures or deterministic acceptance harnesses;
- GitHub Actions workflow/build/job logs when the failure is in CI/deployment/verification.

This is the agent's **repository-side evidence check**. It should happen automatically during issue work when relevant.

Repository documents and engineering logs explain design, lineage, previous failures, and intended instrumentation. They do not automatically prove what the currently running production worker did.

---

## 4. Live/runtime evidence — automatically inspect it when available

Live observations answer what actually executed.

For the production web/server/LALM stack, live evidence commonly comes from **Vercel production runtime logs** and status/diagnostic endpoints. Other subsystems may use GitHub Actions logs, browser screenshots, device logs, or module-specific diagnostics.

When tooling/access exists, §wyrlz should inspect the relevant live evidence itself instead of telling the user to manually search logs that the agent can access.

For Chat/LALM/server work, high-value correlation fields include:

- `requestId`;
- `threadId`;
- canonical message/revision IDs;
- module/engine version and hot revision;
- camera event and route;
- source/manifest/loader identity;
- terminal state;
- prefill/decode/TTFT/latency telemetry;
- fallback/cache/hydration decisions;
- structured error phase.

A request/operation ID is normally the strongest join key for tracing one action across layers.

---

## 5. Existing Chat / Whole Conversation Camera behavior

The repository contains the camera instrumentation/source that determines what Chat/LALM telemetry can emit. Historically important surfaces include:

- `runtime/web/chat_account_state_sync_v1.js` and current successors — browser-side Whole Conversation Camera/account-state instrumentation and debug submission;
- `runtime_hot/r39_engine_v*.py` and active R39 entrypoints — LALM/R39 structured telemetry/camera records;
- Chat debug/client-debug routing and middleware on `main` — receives/records browser diagnostic events;
- `runtime_pages/manifest.json`, runtime manifests, and current loaders — establish which assets/revisions are intended to be active.

Search current source rather than assuming these filenames remain the only owners.

The Whole Conversation Camera is **structured diagnostic telemetry**, not a literal screenshot camera.

---

## 6. When to add a camera

Add or improve instrumentation when an important diagnostic question cannot be answered reliably from current evidence, especially around:

- intermittent failures;
- loader/hydration/bootstrap boundaries;
- cache/fallback/last-known-good selection;
- competing architecture owners;
- source-vs-live revision mismatches;
- request handoff between Mask → Human/server → Brain/LALM;
- persistence write/read conflicts;
- authentication/session transitions;
- streaming terminal-state problems;
- UI state that depends on server/runtime authority;
- tool/action dispatch and completion;
- migrations or compatibility adapters;
- race/order problems.

A camera should be placed at the **boundary that can distinguish the competing hypotheses**.

Example: if it is unclear whether the loader fetched v65 but hydrated v64, instrument fetch identity and hydration identity separately. Do not add ten generic `console.log("here")` statements.

---

## 6A. Full-lockdown / frame-to-terminal mode

When the user explicitly places §wyrlz in full-lockdown diagnostic mode, the camera target is the **complete causal path**, not merely the currently suspected fault.

For a Chat/LALM request this means, as applicable:

```text
user input/send frame
→ UI/message state
→ request construction
→ browser transport
→ server ingress/auth/admission
→ canonical persistence/history
→ routing/hydration
→ Brain/LALM wrappers
→ policy/context/prompt construction
→ tokenization
→ every prefill block/token/layer/matrix path that is instrumentable
→ decode token steps
→ generated/validated stream events
→ persistence/checkpointing
→ server stream relay
→ browser stream parsing/consumption
→ DOM/message mutations
→ every active animation frame and geometry state
→ terminal event
→ final settled frame/state
```

Keep existing cameras at all resolutions. Low-level cameras catch broad divergence, middle cameras localize ownership, and high-resolution cameras identify the exact writer/operation. All events should carry correlation identity and high-resolution timing whenever available.

The engineering logger should expose this evidence directly during development. Do not suppress events merely to keep the interface pretty. Cleanup, sampling, aggregation, or lower-noise presentation occurs only after the behavior is accepted and the retained observability contract is deliberately reconciled.

Security remains invariant: full-lockdown mode may expose application state and inference instructions, but **must redact credentials and authentication material**.

---

## 7. Persistent vs temporary cameras

### Persistent camera

Keep instrumentation when it observes a high-value boundary that is likely to matter again, such as canonical request lifecycle, loader identity, state commits, or critical fallback activation.

Persistent cameras should be low-noise, bounded, structured, and documented enough that future §wyrlz instances understand their purpose.

### Temporary camera

Use temporary instrumentation when it exists only to isolate a one-off ambiguity or would be too noisy/expensive to keep permanently.

After diagnosis:

- remove it if no longer valuable; or
- deliberately promote it to a persistent camera and document its contract.

Do not leave accidental debug spam as permanent architecture.

Camera additions/removals are normal governed development changes and follow architecture, versioning, roadmap, and deployment rules for the component actually changed.

---

## 8. Recommended diagnostic workflow

For any defect:

1. Read the required Project Start document chain.
2. Frame the symptom and reconcile the affected architecture using `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`.
3. Fetch current source, manifests/registries, version authorities, and related release/engineering history.
4. Identify existing cameras and what diagnostic questions they can already answer.
5. Pull the relevant live/runtime/workflow logs when access exists.
6. Correlate source + runtime + user-visible evidence by concrete identifiers where possible.
7. If the system is in lockdown/full-map diagnostic mode, fill every missing observation point on the governed path rather than adding only one camera at a time. Outside lockdown mode, add the smallest camera needed at the correct owner/boundary.
8. Reproduce/request the affected path and inspect the new evidence.
9. Fix the canonical owner rather than compensating in a neighboring layer.
10. Re-check the same cameras/logs after the change.
11. Verify behavior, ownership, and live activation when each is relevant.
12. Record the diagnosis/camera/fix/acceptance state in the roadmap/release record.

The user should not have to remind §wyrlz, “check your logs,” when the available diagnostic evidence can be inspected directly.

---

## 9. Camera versus screenshot

These are different evidence classes.

### Camera/runtime evidence

Useful for:

- request/state transitions;
- route/loader identity;
- server/Brain behavior;
- timing;
- persistence;
- fallbacks;
- terminal states;
- version/revision activation.

### Screenshot/direct UI evidence

Useful for:

- actual rendered geometry;
- theme/spacing;
- flicker/flash;
- controls;
- responsive behavior;
- readability;
- visual state visible to the user.

For server/Brain problems, prefer structured logs/cameras first. For visual Mask problems, use both when possible.

---

## 10. Source vs runtime vs user-visible evidence

Every diagnosis should distinguish four things:

1. **Source fact** — what current canonical code/contracts are designed to do.
2. **Runtime fact** — what live logs/status show actually executed.
3. **User-visible fact** — what the user observed or screenshot/device evidence demonstrates.
4. **Diagnosis** — the explanation supported by the first three.

Do not infer live acceptance from source alone.

Do not blame a component merely because it is near the failure.

Do not treat an old release/engineering-log entry as proof that the same behavior is still active now.

---

## 11. Repository log anti-confusion rule

The repository can contain **engineering logs, release records, workflow logs, exported diagnostic artifacts, and instrumentation source**. Those are valuable and should be checked automatically when relevant.

Normal production Chat/LALM camera events are **not universally mirrored** into GitHub. Repository persistence exists only where a governed camera explicitly owns a bounded writer.

Current explicit runtime-diagnostic persistence includes:

```text
runtime-diagnostics/repair/<request-id>/repair-diagnostic.json
runtime-diagnostics/repair/<request-id>/repair-outcome-diagnostic.json
runtime-diagnostics/programming/<request-id>/candidate-attempt-telemetry.json
```

The programming attempt file is a privacy-bounded receipt, not conversation archival. It may contain attempt number, retry trigger, timing, deterministic validation status/reasons, candidate fingerprints/change flags, Station timing, final artifact action/revision, source revision, and GitHub persistence status. It must not contain the user's prompt, generated source code, user/assistant profile text, credentials, cookies, or hidden/private reasoning.

These writes reuse the dedicated `SWRLZ_DIAGNOSTIC_GITHUB_TOKEN` transport and target the `runtime` branch. They are asynchronous and best-effort so repository I/O cannot become inference authority or block the generation critical path. The Station/session export should expose the persistence receipt so an engineer can distinguish `QUEUED`, successful GitHub storage, and a bounded persistence failure.

Use this distinction:

```text
GitHub / repository
→ source, instrumentation, engineering history, release records, CI/workflow evidence
→ plus explicitly governed bounded runtime-diagnostic artifacts under runtime-diagnostics/

Runtime provider / active system
→ live production events and currently executing behavior
→ process-local/full session evidence that is intentionally too rich for repository persistence

User/device evidence
→ what the user actually saw/experienced
```

If a repository artifact explicitly contains an exported runtime capture or bounded runtime diagnostic, it may be used as runtime evidence with its timestamp/source recorded. Never infer that all runtime events are durable merely because some governed camera families are persisted.

---

## 12. Automatic log-check expectations by issue class

### Source/code regression

Check current source, ownership, release history, commits, tests, and relevant live logs.

### Loader/cache/fallback issue

Check manifest/source authority, active revision, loader cameras, cache/fallback decision, and production activation evidence.

### UI/render issue

Check canonical UI owner, competing style/injector layers, browser/client debug events where available, and screenshot/render evidence.

### Authentication/session issue

Check the feature-specific auth runbook, server/client auth boundaries, sanitized auth cameras, status/errors, and relevant runtime logs. Never log secrets.

### CI/deployment issue

Check workflow definition, commit/source identity, workflow run/job/step logs, deployment status/build logs, and deployment approval state.

### LALM/reasoning issue

Check active LALM revision, conversation-state/response-contract cameras, completion/quality telemetry, bounded context identity, and whether the expected engine actually hydrated.

---

## 13. Acceptance rule

When a fix depends on runtime behavior, a source commit alone is not final acceptance.

Preferred acceptance ladder:

```text
SOURCE VERIFIED
      ↓
STATIC / DETERMINISTIC VERIFIED
      ↓
EXPECTED REVISION/OWNER ACTIVATED
      ↓
RELEVANT CAMERA/LOG PATH OBSERVED
      ↓
USER-VISIBLE / END-TO-END BEHAVIOR VERIFIED WHEN APPLICABLE
```

If the ladder stops early, report the exact level reached.

---

## 14. Short memory aid

```text
What SHOULD happen?     → current source + contracts.
What DID happen?        → cameras/runtime/workflow logs.
What did the USER SEE?  → screenshot/direct device/UI evidence.
Why did it happen?      → diagnosis after correlating the evidence.
```

---

## Bottom line

**When fixing issues anywhere in §wyrlz, automatically inspect the relevant repository-side diagnostic evidence and the available live/runtime/workflow logs. If existing observability cannot distinguish the cause, add the smallest bounded camera at the architecture boundary that can. Use structured, correlated, privacy-safe diagnostics; fix the canonical owner; then inspect the same evidence again for acceptance. Keep repository engineering history, live runtime evidence, and user-visible evidence distinct so source completion is never mistaken for a verified live fix.**


## v122 behavioral invariant / best-known repair-base cameras

Programming repair state may now expose a bounded `behaviorLedger` derived only from external receipt cases. This is evidence bookkeeping, not model self-grading.

Key fields:
- `currentScore` / `bestKnownScore` — named-case pass/total/fail counts for comparable external test suites.
- `currentPassingCases` / `currentFailingCases` — newest externally observed named case state.
- `preservePassingCases` — union of cases already proven passing within the comparable repair lineage; these become preservation obligations.
- `resolvedCases` — cases that failed in the previous comparable receipt and now pass.
- `regressedCases` — cases proven passing earlier that fail in the newest receipt.
- `bestKnownArtifact` — artifact ID, exact revision, source hash and bounded source fingerprint of the best externally tested artifact for that suite.
- `rebaseRecommended` — true only when the newest comparable tested artifact scores below the retained best-known artifact.

`behaviorRepairBase` records which source lineage the worker actually receives:
- `latest-failing-source` — normal repair from the newest receipt source.
- `best-known-tested-source` — repair is intentionally rebased onto the better historical artifact while the newest receipt remains the authoritative failure delta.

When `best-known-tested-source` is selected, the repository camera stores only artifact identity/hash/fingerprint and mode, never the source body. The source snapshot remains process-local/session evidence. Candidate validation may emit `behavior-repair-base-unchanged` when the model merely returns the better historical base unchanged even though the latest external receipt still establishes unresolved behavior failures.

Compact repair-budget telemetry may expose `behaviorRepairBaseMode`, current/best scores, regression count and preserve count. Durable repair/programming diagnostics should expose the same bounded ledger summary so reviews can distinguish: evidence parsing, regression detection, rebase selection, model repetition, and post-rebase candidate change.

Behavior ledger state does not mark a newly generated candidate correct. Even after rebasing and structural PASS, `executionVerified=false` / `AWAITING_EXTERNAL_RECEIPT` remains authoritative until fresh external compiler/test/runtime evidence arrives.

## v121 persistent repair-state camera additions

Programming repair intent may now expose a bounded `repairConstraints` snapshot. Its dependency fields are stateful evidence, not a copy of only the newest receipt:

- `dependencyPolicy` — e.g. `standard-library-only`, `no-install`, or `evidence-bounded`.
- `unavailableDependencies` / `forbiddenDependencies` — active dependency identifiers proven unavailable in the current repair lineage.
- `currentReceiptDependencies` — dependency identifiers proved by the newest receipt only.
- `addedDependencies` — identifiers newly added by the current receipt.
- `carriedUnavailableDependencies` — active identifiers inherited from earlier receipts because the newer receipt did not invalidate them.
- `releasedDependencies` — identifiers explicitly released only when current evidence says they are now installed/available.

This distinction is intentional: a later assertion/type/behavior receipt may add new failure evidence without erasing an earlier environment fact such as `ModuleNotFoundError` for the same repair lineage. Candidate-validation telemetry may expose an `activeRepairConstraints` subset so cameras can prove the gate consumed the same state Brain produced.

Structured test receipts may also expose bounded `structuredReceipt` normalization metadata:

- `formats` — currently includes `json` when bounded JSON receipt objects were decoded.
- `jsonObjectCount` — decoded top-level embedded JSON values.
- `caseCount` — bounded test/result objects with explicit status.
- `failedCaseCount` — those normalized as failures.

The detailed normalized facts continue to live in the existing receipt semantics (`categories`, `failingTests`, `expectedActual`, `failureSignals`, `sourceLocations`, etc.). The structured camera counts prove parser coverage without adding source code, prompt text, or private reasoning to repository diagnostics.

Durable `runtime-diagnostics/repair/...` and `runtime-diagnostics/programming/...` records should carry the same bounded repair-constraint / structured-receipt summaries when applicable, allowing a review to distinguish: receipt parser loss, accumulated-state loss, candidate-gate loss, and model strategy failure.

## v120 programming repair camera additions

For programming repair turns, the Station/session camera may now include bounded `contextBudget.repairContext` metadata. This reports the compaction mode and size/count summaries needed to prove that original intent, canonical source, receipt semantics and repair direction were retained while oversized generic/history context was dropped. It is budgeting telemetry, not model reasoning.

Programming candidate attempts may include deterministic rejection reasons such as `repair-stalled-no-executable-change`, `strategy-repeat-previous-attempt`, or `dependency-still-referenced:<name>`. These are gate receipts only; a later structural PASS is still not external execution proof.

Repository diagnostic persistence remains asynchronous and best-effort, but the Station-owned writer now serializes writes and applies bounded HTTP 409 recovery. Persistence receipts may report `attempts`, `conflictCount`, `conflictRecovered`, and a bounded `errorPreview`. The preview is only the GitHub API error response and must never contain prompt/source/profile/private reasoning. A successful live run can prove durable files landed without proving that a 409 was actually induced during that run.

Code-artifact lineage now carries `artifactRevision` plus `artifactSourceHash`. Repair intent may expose `baseRevision` / `baseSourceHash`, and mutation receipts may expose requested/current revision/hash on rejection. Exact revision/hash identity is stronger than originating-message identity and is the authority for stale-edit protection.



## v123 response cognition cameras

General and programming response generation may emit a bounded `RESPONSE_COGNITION` event from the Brain-owned `swrlz-response-cognition-v1` classifier.

The camera stores classification only, never prompt/history text or hidden reasoning. Bounded fields include:
- `relation` — standalone, topic-reset, continuation, correction, expansion, selection, confirmation, decline, creative-delegation, or return-to-prior;
- `operation` — answer/explain/compare/rewrite/create/continue/correct/select/confirm/decline/code/etc.;
- history availability/count and nearest user/assistant anchor indices;
- explicit-reference/question flags;
- detail mode, requested item count, output-only constraint, preserve/do-not-change constraint, and whether programming mode is active.

Station may retain this bounded event in the active generation and final assistant-message metadata so a response-quality review can prove which conversational relationship reached the engine without storing another copy of the conversation.

The classifier is advisory response cognition, not operational authority. The current user turn always outranks history, programming intent/repair gates retain ownership of coding correctness, and a response-cognition classification never proves semantic answer quality by itself.


## v124 online research and widget cameras

HF Station now carries bounded Online Research state through the same request lineage as inference.

### Online research camera

The Brain/router may emit `ONLINE_RESEARCH` with a privacy-bounded `swrlz-online-camera-v1` summary. The camera may contain:
- retrieval kind (`search` or `weather`);
- status and activation reason;
- provider;
- result/source counts;
- widget kinds;
- whether an explicit client location was used;
- whether a location is still required;
- elapsed retrieval time.

It does **not** persist the raw user prompt or precise client coordinates.

### Widget envelope

Presentation data uses `swrlz-widget-v1`. Initial kinds:
- `weather` — current measurements plus bounded daily forecast;
- `search-results` — bounded title/source/snippet/link rows.

Station retains widget envelopes on the active generation and commits them into the final assistant message metadata so live-stream and later history rendering share the same structured result.

Chat is a presentation consumer only. Provider/network ownership stays backstage. Widget rendering uses DOM/text nodes and HTTP(S)-validated links; provider HTML is not inserted into the page.

### Weather privacy boundary

A named place can be geocoded server-side. Location-relative requests such as “weather here” may use browser geolocation only after the browser grants permission. Exact coordinates are request-scoped input to the weather provider and are intentionally omitted from persisted widget/source/camera metadata. Timezone is never treated as proof of physical location.

### Evidence boundary

General search continues to use the canonical Online Research public-network/SSRF guard and prepared reasoner. Retrieved material remains untrusted external evidence and has no instruction authority over the Brain.


## v125 online research trace + durable log cameras

Online retrieval now exposes one bounded live trace from the network owner through Station to Chat and to durable runtime diagnostics.

### Live trace contract

`swrlz-online-trace-event-v1` events may contain:
- phase;
- provider;
- public site hostname;
- presentation-safe public URL containing scheme + host + path only;
- bounded activity text;
- timestamp;
- HTTP status, response bytes, result count, or bounded error type where applicable.

The trace intentionally excludes:
- raw user prompt/history;
- search-provider query strings;
- URL fragments/credentials;
- provider HTML;
- exact shared geolocation coordinates;
- private reasoning.

Representative phases include provider visit/results/empty/error/selected, page fetch start/complete/error, weather geocode/forecast visit/complete, and research lifecycle events.

### Durable runtime logs

When `SWRLZ_DIAGNOSTIC_GITHUB_TOKEN` is configured, each online request may persist:

- `runtime-diagnostics/online-research/<requestId>/online-research-trace.json`
- `runtime-diagnostics/online-research/<requestId>/online-research-outcome.json`

The trace log captures the bounded retrieval camera, public source sites, requested/selected model lineage, and retrieval result metadata. The outcome log adds terminal generation state, widgets, timing, final selected model, and completion/failure state. A generation failure after successful retrieval does not erase the online receipt.

### Chat presentation

During a live Station generation, Chat consumes the same SEARCH/FETCH/WEATHER trace:
- the primary progress row shows the current retrieval phase and site/provider;
- a compact six-event trail shows recently visited providers/sites and activity;
- sanitized URLs may be opened from the trail;
- the Work/agent action surface continues to show the same structured action events.

Chat does not invent percentage progress or a site name. If Station did not emit a network trace event, Chat must not display one.
