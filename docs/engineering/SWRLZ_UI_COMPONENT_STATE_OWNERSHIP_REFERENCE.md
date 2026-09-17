# §wyrlz UI Component State Ownership Reference

**Role:** canonical engineering reference for UI containers and interactive components whose content may change independently from user-controlled presentation state.

**Primary rule:** system-owned data may update continuously; user-owned intent changes only from explicit user action.

This document exists so known-good component behavior can be reused instead of rediscovered through bug fixing. It applies to Activity Logs, drawers, accordions, inspectors, expandable diagnostics, modals, side panels, pinned sections, pause/resume controls, acceptance controls, and similar stateful UI containers.

---

## 1. State ownership contract

Every mutable value must have one canonical owner and a clearly defined set of allowed writers.

### System-owned state

Examples:

- activity entries
- progress text
- streamed diagnostics
- response phase
- server status
- timestamps
- generated content

The system may append, replace, reconcile, or refresh this data as required by the component contract.

### User-owned intent state

Examples:

- expanded / collapsed
- pinned / unpinned
- paused / resumed
- accepted / declined
- muted / unmuted
- selected tab
- explicit visibility preference

These values must not be silently rewritten by streaming, completion, rerendering, observers, lifecycle transitions, retries, hydration, network reconnects, or compatibility code unless the product contract explicitly defines a separate automatic mode.

For a simple boolean control, the preferred contract is:

```text
closed + user activates control -> open
open + user activates control   -> closed
anything else happens           -> unchanged
```

The renderer reads the value. The user interaction handler writes the value.

---

## 2. The Activity Log known-good pattern

The Chat Activity Log established the first accepted reference implementation.

### Canonical split

- `message.meta.trail` = system-owned activity data.
- `message.meta.activityExpanded` = user-owned presentation intent.
- activity events may append to `trail`.
- activity events must never change `activityExpanded`.
- stream updates may rerender the panel from current model state.
- completion may append terminal activity such as `Response complete`.
- completion must not open or close the panel.
- DOM replacement must reconstruct the same visible state from `activityExpanded`.

### Why this works

The content stream and the visibility decision are independent state machines. New log entries do not imply a request to open the log, and a completed response does not imply a request to close it.

The UI therefore remains deterministic even when the response DOM is replaced many times during generation.

---

## 3. Controlled-container structure

Prefer a controlled component when application state already owns the interaction state.

Conceptual structure:

```html
<section class="component-panel" data-expanded="false">
  <button
    type="button"
    class="component-toggle"
    aria-expanded="false">
    Activity log
  </button>

  <div class="component-content" hidden>
    <!-- system-owned content -->
  </div>
</section>
```

Conceptual controller:

```js
function renderPanel(panel, model) {
  const expanded = Boolean(model.activityExpanded);
  panel.dataset.expanded = expanded ? 'true' : 'false';
  panel.querySelector('.component-toggle')
    ?.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  panel.querySelector('.component-content').hidden = !expanded;
}

function onUserToggle(model) {
  model.activityExpanded = !model.activityExpanded;
  saveState();
  renderFromModel();
}
```

The important property is not the exact markup. It is the writer contract: `onUserToggle()` is the only writer of the user-owned boolean.

---

## 4. Append-only content vs intent

A container can have two independent mutation policies at once.

For an Activity Log:

```text
trail[]             system append/update
activityExpanded    user write only
```

For a task inspector:

```text
steps[]             system append/update
selectedStepId      user write only
inspectorExpanded   user write only
```

For a notification tray:

```text
notifications[]     system append/remove by domain rules
trayExpanded        user write only
```

Do not infer presentation intent from content mutation. A new entry means "new data exists," not "change the user's current UI choice."

---

## 5. Rendering rules

A renderer may:

- create a missing container;
- append or refresh system-owned content;
- restore DOM from canonical model state;
- replace transient DOM nodes;
- update labels, timestamps, counts, progress, and diagnostics;
- read user-owned state to determine presentation.

A renderer must not:

- toggle user-owned booleans as a side effect of rendering;
- reset state because generation started or finished;
- infer a click from a lifecycle event;
- use DOM state as a competing source of truth when model state already exists;
- write the model because a rerender happened.

Rendering is a projection of state, not an independent state authority.

---

## 6. DOM controls and browser-native state

Native elements such as `<details>` can own their own state. That is useful only when native DOM state is intentionally the canonical owner.

Do not combine:

```text
native <details>.open ownership
+ application boolean ownership
+ observer reconciliation ownership
```

unless a formal bridge defines exactly one writable authority.

If the application already persists an `expanded` boolean, a normal button plus controlled content region is usually safer. The browser then cannot silently introduce a second state machine.

---

## 7. Selector and compatibility isolation

A replacement component must not reuse a legacy behavior selector merely for styling.

Bad:

```html
<section class="trace new-activity-panel">
```

when older modules attach behavior to `.trace`.

Preferred:

```html
<section class="swrlz-activity-panel">
```

with dedicated styling selectors.

Rules:

1. semantic/behavior classes and styling classes should not accidentally alias retired component contracts;
2. legacy nodes may remain temporarily for compatibility, but should be explicitly hidden or retired;
3. new components should use unique selectors so old event listeners cannot recognize them;
4. compatibility code must not become a second state owner.

---

## 8. Interaction boundary

For user-owned state, capture the state change at one explicit interaction boundary.

Preferred:

```text
user click/tap/keyboard activation
        -> one handler
        -> one model mutation
        -> persist
        -> render from model
```

Avoid multiple handlers on overlapping selectors, native toggle events plus custom click handlers, or observers that convert DOM changes back into model writes.

A physical activation should produce exactly one logical transition.

```text
one tap -> one state transition
```

---

## 9. MutationObserver policy

Observers are reconciliation tools, not intent engines.

Allowed uses:

- detect newly inserted DOM that requires decoration;
- attach presentation to newly rendered nodes;
- restore canonical model state after DOM replacement.

Disallowed uses for user-owned state:

- observing `open`, `hidden`, or class mutations and treating them as new user intent;
- toggling the model because another renderer changed the DOM;
- creating feedback loops where model -> DOM -> observer -> model.

If an observer is necessary, it should normally be one-way:

```text
DOM replacement detected -> read canonical state -> repaint
```

not:

```text
DOM changed -> rewrite canonical user intent
```

---

## 10. Lifecycle invariants

A well-structured component preserves its user intent through:

- initial render
- streaming updates
- partial rerenders
- full DOM replacement
- network reconnect
- terminal completion
- error state
- thread reload
- persistence restore

For each lifecycle boundary, ask:

> Does this event have product authority to change the user's choice?

If the answer is no, the user-owned state must survive unchanged.

---

## 11. Architecture reconciliation checklist

Before implementing or repairing a stateful container:

1. Identify every mutable value.
2. Classify each value as user-owned, system-owned, server-owned, or derived.
3. Name one canonical owner for each value.
4. List every writer.
5. Remove or demote competing writers.
6. Identify native browser state that could become an accidental second owner.
7. Search for old selectors that may attach legacy behavior.
8. Define lifecycle invariants across render, stream, completion, reconnect, and reload.
9. Verify one user action causes exactly one state transition.
10. Verify background updates change content without changing user intent.

If two mechanisms both claim authority over the same state, reconcile them before adding another patch.

---

## 12. Known anti-patterns

### Lifecycle-owned expansion

```js
details.open = message.state === 'streaming';
```

This lets generation state overwrite user intent.

### Continuous forced expansion

```js
details.open = true;
```

inside every stream update.

This makes the component impossible for the user to keep collapsed.

### DOM-to-model feedback

```js
observer -> DOM open changed -> activityExpanded = trace.open
```

when DOM changes can also be caused programmatically.

### Multiple behavioral identities

A new controlled panel reuses a class that older code treats as a native accordion.

### State initialization on every render

```js
model.expanded = false;
```

inside a rendering or reconciliation path.

Initialization should happen only when the state is genuinely absent.

---

## 13. Working-component reference registry

This document should grow by adding verified patterns, not speculative ones.

### Activity Log controlled panel

**Status:** user-verified working reference.

**Canonical runtime area:** `runtime/web/chat_activity_immediate.js` on the runtime branch.

**Accepted properties:**

- activity content may continue to populate automatically;
- expansion state is user-owned;
- one activation flips state once;
- background updates do not change expansion state;
- response completion does not change expansion state;
- legacy native trace behavior is isolated from the visible controlled panel.

Future component entries should document:

- canonical owner;
- state variables;
- writer permissions;
- lifecycle invariants;
- known legacy compatibility boundaries;
- user-visible acceptance evidence.

---

## 14. §wyrlz teaching rule

When reasoning about interactive software, §wyrlz should explicitly distinguish **content mutation** from **intent mutation**.

Reusable rule:

> System-owned data may evolve automatically. User-owned intent remains stable until the user explicitly changes it.

When debugging a UI that appears to fight the user, inspect ownership before timing. Repeated animation, flicker, reopening, reclosing, or needing multiple taps is often evidence that more than one mechanism is writing the same state.

---

## 15. Definition of done for a controlled container

A component is not considered structurally complete until all of the following are true:

- one canonical state owner exists per mutable value;
- all writers are intentional and documented;
- user intent survives unrelated system activity;
- content can update without changing intent;
- one user activation creates one logical transition;
- rerenders reproduce state rather than invent it;
- legacy selectors cannot attach unintended behavior;
- accessibility state such as `aria-expanded` mirrors canonical state;
- persistence, if required, stores the canonical value;
- user-visible behavior has been verified on the target interface.

This reference is the default starting point for future §wyrlz stateful-container work.