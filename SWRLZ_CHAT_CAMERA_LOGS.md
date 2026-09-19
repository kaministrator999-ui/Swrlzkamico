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

However, normal production Chat/LALM camera events are not magically stored in a GitHub `/logs/` folder.

Use this distinction:

```text
GitHub / repository
→ source, instrumentation, engineering history, release records, CI/workflow evidence

Runtime provider / active system
→ live production events and currently executing behavior

User/device evidence
→ what the user actually saw/experienced
```

If a repository artifact explicitly contains an exported runtime capture, it may of course be used as runtime evidence with its timestamp/source recorded.

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
