# §wyrlz Lockdown Camera System — Build-Time Observability Guide

**Role:** canonical operating guide for designing, integrating, switching, and verifying §wyrlz lockdown cameras across Server pages, modules, runtime components, transport paths, LALM paths, persistence paths, loaders, and UI presentation.

**Entry point:** `SWRLZ_PROJECT_START.md` routes here for all new or materially changed components.

**Relationship to existing diagnostics:** `SWRLZ_CHAT_CAMERA_LOGS.md` remains the evidence/diagnostic workflow owner. This guide defines how cameras are built into architecture from the beginning and how full-lockdown capture is activated or disabled without rewriting the component.

---

## 1. Core doctrine

Do not wait for a whole play to exist and then bolt cameras onto it.

Every new component is designed with its observation points at the same time as its functional boundaries.

```text
BUILD COMPONENT
   ├─ behavior contract
   ├─ state/ownership contract
   ├─ version authority
   ├─ lifecycle
   └─ camera contract
```

The camera path is part of architecture, but full-lockdown emission is not required to be permanently active.

> **Cameras exist from birth. Lockdown decides how much they emit.**

---

## 2. Operating modes

Every camera-capable component should support a bounded mode contract conceptually equivalent to:

```text
OFF
  no full-lockdown emission; only mandatory safety/error telemetry if separately owned

NORMAL
  low-noise structured lifecycle/health telemetry

LOCKDOWN
  high-resolution end-to-end evidence for every meaningful transition

FULL_MAP
  maximal safe correlation across the complete governed path, including frame/token/transport/state transitions where instrumentable
```

Exact names may differ by implementation, but semantics must remain explicit.

Turning cameras off must not alter functional behavior. Turning them on must not change ownership, routing, inference, persistence, rendering, or business logic.

---

## 3. Runtime-hot activation contract

Where architecture supports runtime-hot control, camera mode/configuration should be runtime-switchable without requiring a stable Server deployment.

```text
durable runtime authority
      ↓
camera policy/config
      ↓
existing hotloader / runtime manifest / runtime-hydrated owner
      ↓
component reads mode
      ↓
telemetry density changes
```

Use the existing runtime-hot architecture when it is the correct owner. Do not create a second loader merely for cameras.

A stable Server change is required only when the current stable ABI cannot expose the needed camera switch/boundary safely.

---

## 4. Camera contract for every new component

Before implementation is considered complete, define:

1. **Component identity** — stable owner/module/page name.
2. **Version identity** — component/module version + Repository Work lineage.
3. **Correlation identity** — requestId, operationId, bootId, navTraceId, threadId, generationId, or another bounded join key.
4. **Lifecycle events** — enter/start, meaningful state changes, exit/terminal, failure.
5. **Boundary events** — ingress/egress, reads/writes, ownership transfer, loader selection, fallback selection, persistence transitions.
6. **Performance events** — timestamps/durations for expensive or latency-sensitive stages.
7. **Presentation events** — when UI/frame/layout state is itself part of the component contract.
8. **Error classification** — bounded, structured, attributable.
9. **Privacy/security redaction** — never log credentials, tokens, cookies, device proofs, or unnecessary raw private content.
10. **Mode behavior** — what OFF/NORMAL/LOCKDOWN/FULL_MAP emits.
11. **Activation owner** — where runtime camera mode is controlled.
12. **Verification method** — how a future engineer proves the camera path works before the component grows complex.

---

## 5. Stage / theater mapping

- **Stage/Mask cameras** observe scene state, layout, actor/prop entrance/exit, interaction, and presentation transitions.
- **Backstage/Human-server cameras** observe transport, routing, persistence, tools/actions, permissions, worker coordination, and server boundaries.
- **Brain/LALM cameras** observe prompt/context composition, tokenization, prefill, decode, routing, validation, and model/tool handoff as supported.
- **Stagehand cameras** observe loaders, hydrators, manifests, hotload selection, caches, and fallback activation.
- **Curtain/scene cameras** observe atomic scene preparation/commit and detect intermediate states accidentally exposed to the audience.

The audience should never see camera machinery merely because cameras are active.

---

## 6. Build-from-start rule

```text
define owner
→ define functional contract
→ define camera contract
→ define version authority
→ add runtime-hot camera switch if supported
→ implement smallest component
→ verify behavior with cameras OFF
→ verify same behavior with cameras ON
→ compare functional outputs
→ record roadmap receipt
```

Acceptance requires ON/OFF parity for functionality.

If turning cameras on changes behavior materially, the camera implementation is defective.

---

## 7. Full-lockdown scope

During active issue diagnosis or explicit lockdown mode, capture every meaningful transition needed to reconstruct the governed path.

### Web/page
- document/navigation start
- manifest/source identity
- boot/start
- first meaningful frame
- DOM/content ready
- geometry/layout mutations
- fetch start/end/error
- actor/prop entrance/exit
- scene commit
- terminal settled frame

### Server/API
- ingress
- auth/admission
- normalized request
- routing decision
- persistence read/write
- upstream/tool call
- stream/event relay
- terminal state

### LALM
- active engine/model/revision
- request/context identity
- prompt/history composition metadata
- tokenization counts
- prefill stages/timing
- decode steps/timing
- validation/repair
- tool/evidence handoff
- terminal output state

### Runtime hotloader
- runtime branch/head identity
- manifest revision
- selected route/source/assets
- fetch/hash
- cache/fallback decision
- hydration/invalidation
- active camera-mode source

---

## 8. Correlation law

A camera event without lineage is weak evidence.

```text
navTraceId
  + bootId
  + requestId
  + threadId
  + generationId
  + component/revision
  + monotonic timestamp
```

Not every event needs every identifier, but adjacent layers must share enough identity to join the path without guessing.

---

## 9. Performance discipline

In NORMAL mode:
- bounded fields;
- low event volume;
- no expensive serialization of large state;
- no repeated DOM reconstruction just to log;
- no blocking network logging in the critical path.

In LOCKDOWN/FULL_MAP:
- higher volume is expected;
- still avoid secrets and unnecessary raw payloads;
- use asynchronous/buffered emission where architecture allows;
- record camera overhead when it could affect timing conclusions.

Never mistake camera-induced slowdown for the original defect.

---

## 10. Runtime-hot page integration

For a manifest-routed page such as `/chat/§wyrlz`:

1. keep the page source canonical;
2. add a page-owned camera module only when the page has enough lifecycle to observe;
3. declare that camera asset in the route manifest if it belongs to the page;
4. keep camera mode sourced from one runtime-hot authority;
5. do not inherit the legacy Chat camera stack wholesale;
6. start with the smallest observation surface and expand with the page.

For the current clean-room Chat, the camera system should grow in the same scoped tiers as the stage itself.

---

## 11. Repository/version effects

A camera architecture/docs tier:
- Repository Work ↑
- no Server Runtime bump
- no component bump unless executable component behavior/source changed

A page camera implementation:
- Repository Work ↑
- affected page/module version ↑
- Runtime Manifest ↑ if activation assets/routes changed
- Server Runtime unchanged unless a Server release/deployment is actually required

A stable Server camera capability:
- source can be prepared on main without deployment;
- Server Runtime advances when an actual Server release/deployment advances deployed Server lineage.

---

## 12. Verification matrix

```text
CAMERAS OFF      → behavior correct
CAMERAS NORMAL   → behavior correct
CAMERAS LOCKDOWN → behavior correct + detailed trace
CAMERAS FULL_MAP → behavior correct + complete bounded trace
```

Then verify:
- same functional result across modes;
- expected event coverage;
- correlation continuity;
- no secret leakage;
- bounded overhead;
- runtime mode changes activate without unintended deployment when hotload architecture owns the switch.

---

## 13. Relationship to the roadmap

The roadmap records what was actually built and verified.

For camera work, record:
- component covered;
- observation boundaries added;
- runtime mode authority;
- version changes;
- verification level;
- whether cameras are source-complete/runtime-active/live-verified;
- failures or missing correlation points;
- performance overhead if material.

The roadmap does not replace this guide.

---

## Bottom line

**Build the cameras when you build the play. Keep them structurally present, runtime-switchable, behaviorally inert, correlated across boundaries, privacy-safe, and scalable from OFF to FULL_MAP. The goal is that any future failure can be observed without first redesigning the component just to see inside it.**
