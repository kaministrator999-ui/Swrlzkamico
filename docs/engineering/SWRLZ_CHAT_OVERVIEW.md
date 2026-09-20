# §wyrlz Chat Overview — Stage Composition Contract

**Role:** canonical overview for how §wyrlz Chat is composed, revealed, mutated, and audited as a theater stage.

**Read with:** `§wyrlz_§tart.md`, `docs/engineering/SWRLZ_RUNTIME_HOTLOADER_GUIDE.md`, and `docs/engineering/SWRLZ_LOCKDOWN_CAMERA_SYSTEM.md`.

**Scope:** Chat architecture. This document defines the scene vocabulary and ownership/mutation rules. The Roadmap records what was actually built.

---

## 1. Six primitives

| Primitive | Meaning | Typical examples |
|---|---|---|
| **Scenery** | Defines the physical stage and should exist before reveal | viewport, workspace, drawer/sidebar geometry, message viewport, composer position, top bar |
| **Starting prop** | Dynamic-looking but required for the opening scene | current theme, branding/sigil, kompanion location, composer controls, selected-thread heading |
| **Actor** | Stateful participant in the performance | current thread, message list, composer, connection/runtime presentation |
| **Temporary actor / prop** | Enters for a bounded event and leaves cleanly | streamed response, toast, loading state, error notice, modal, tool-progress presentation |
| **Scene-transition prop** | Structural presentation that may change only through a controlled scene transition | theme geometry, drawer mode, account/session presentation, major responsive-layout mode |
| **Stagehand** | Machinery that prepares/manipulates the production but must not become visible scenery | loaders, hydration, cameras, transport, persistence, auth, manifest/runtime selection |

An actor can have an entrance condition and exit condition. A persistent actor may enter in the opening scene and remain for the whole session.

Stagehands do not own visible identity merely because they can mutate DOM/state.

---

## 2. Legal mutation phases

### Immutable during the play

There is one canonical owner for each fundamental stage region.

Examples:
- one application/stage root;
- one workspace;
- one message viewport;
- one composer shell;
- one canonical branding owner.

A loader or enhancement must not manufacture a competing copy.

### Open-curtain mutable

These changes are part of the visible performance:
- response text streaming;
- status/progress presentation;
- thread/message entrance;
- unread state;
- temporary notices;
- bounded interaction feedback.

They may mutate while the audience is watching because the mutation itself is meaningful performance.

### Closed-curtain mutable

These changes must be prepared as a coherent next scene and committed atomically enough that the audience does not see reconstruction:
- fundamental theme geometry;
- kompanion/branding presentation replacement;
- major responsive shell mode;
- navigation architecture replacement;
- structural drawer/workspace reconstruction;
- anything that would visibly make the stage jump through intermediate states.

---

## 3. Scene contract

```text
CURTAIN CLOSED
│
├── Build canonical scenery
├── Apply current theme
├── Place starting props
├── Determine starting actors
├── Populate scoped initial state
├── Validate geometry
│
▼
SCENE COMMIT
│
▼
CURTAIN OPEN
│
├── actors enter/leave
├── messages enter
├── responses stream
├── status changes
├── temporary actors/props appear/disappear
└── minor props update
       │
       └── major structural change required?
                    ↓
             CURTAIN TRANSITION
                    ↓
             prepare next scene
                    ↓
                 COMMIT
```

“Curtain closed” does not require a blank screen. On initial navigation it is the interval before the first authoritative scene is presented. During an existing session it can be a deliberately designed continuity-preserving transition.

The audience must not be shown a half-reconstructed DOM merely because stagehands are still working.

---

## 4. Audit schema

Before adding, migrating, or consolidating a Chat component, classify it with:

```text
owner
→ primitive/role
→ initial state
→ entrance condition
→ exit condition
→ allowed mutation phase
→ dependencies
→ camera contract
→ version owner
```

If two mechanisms claim the same visible owner/region, stop and reconcile ownership before adding another mechanism.

A useful audit table is:

| Owner | Role | Initial state | Entrance | Exit | Mutation phase | Dependencies | Camera | Version |
|---|---|---|---|---|---|---|---|---|

Duplicate visible ownership is a structural defect candidate.

---

## 5. Stagehand law

Loaders, hydration code, runtime manifests, cameras, transport, persistence, authentication, caches, and similar machinery are **stagehands**.

Stagehands may prepare or deliver scene state, but:

- they do not become competing scenery;
- they do not reveal stale presentation while preparing current presentation;
- they do not independently own branding;
- they do not rebuild a canonical region merely because they loaded later;
- failure of an enhancement should preserve the same authoritative stage, not expose a visually distinct old stage underneath it.

The Mask presents capabilities; it does not possess backstage machinery.

---

## 6. Current clean-room Chat direction

The canonical clean-room route is:

`/chat/§wyrlz`

Its construction strategy is deliberately additive:

```text
known-fast minimal stage
→ scenery
→ starting props
→ starting actors
→ open-curtain actors
→ temporary actors/props
→ controlled scene transitions
→ stagehands/integration as required
```

Do not copy the legacy Chat wholesale.

Each tier should add one coherent class of stage responsibility, verify it, preserve the known-fast baseline as far as practical, and record the receipt in the Roadmap.

---

## 7. Camera relationship

Cameras are built with the play, not installed after the theater is full.

For every stage element, the camera contract should know enough to observe:
- entrance/exit;
- owner;
- meaningful state transition;
- geometry/presentation transition when relevant;
- timing/performance;
- correlation identity;
- active source/revision.

Camera activation follows the Lockdown Camera System guide. Camera machinery remains a stagehand and must be behaviorally inert.

---

## 8. Runtime-hot relationship

Runtime hotloading is delivery machinery, not a second stage owner.

For Chat:
- page/source authority remains explicit;
- manifest assets must have one purpose and owner;
- hotload activation must not create a second visual shell;
- a runtime-loaded enhancement joins the existing scene contract rather than replacing it opportunistically;
- Runtime Manifest advances only when route/style/script activation mapping changes.

See `docs/engineering/SWRLZ_RUNTIME_HOTLOADER_GUIDE.md` for mechanics.

---

## 9. Architectural test

Before accepting a Chat change, ask:

1. What primitive is this?
2. Who owns it?
3. Does another mechanism already own the same region/state?
4. When is it legally allowed to mutate?
5. What does the audience see while it changes?
6. What stagehand delivers it?
7. Can cameras prove its lifecycle without altering behavior?
8. Which version authority advances?
9. Can failure preserve the same canonical stage instead of revealing a competing fallback presentation?

If those answers are unclear, the component is not ready to enter the play.

---

## Bottom line

**Scenery. Props. Actors. Stagehands. Curtain. Scene.**

Build one authoritative stage. Prepare structural change behind the curtain. Let legitimate performance mutate in the open. Keep stagehands backstage. Give every visible region one owner. Instrument each component from birth.
