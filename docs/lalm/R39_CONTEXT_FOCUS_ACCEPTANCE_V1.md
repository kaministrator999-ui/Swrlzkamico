# R39 Context Focus Acceptance v1

## Purpose

This contract verifies that §wyrlz can focus on the correct nearby conversational evidence without destructively pruning canonical history or turning heuristic routing into semantic authority.

Contract ID: `swrlz_context_focus_acceptance_v1`

Runtime focus contract: `swrlz_context_focus_v1`

## Required behavior classes

### Active assistant anchor

When the user uses a compact deictic reference such as `that`, `that one`, `same thing`, or `do that too`, the resolver should normally focus on the nearest substantive assistant output when one exists. The full conversation remains available to the model.

### Local correction anchor

A local correction should normally focus on the assistant output being corrected. The correction changes the rejected detail while preserving unrelated accepted structure.

### Contrast inside the active anchor

Phrases such as `the other one` often refer to alternatives inside one assistant message. The resolver must not mechanically reinterpret `other one` as “the second-oldest conversation turn.” It should keep the active assistant response as the anchor and let the model inspect alternatives inside it.

### Acknowledgement bridges

Short acknowledgement-only turns such as `yeah`, `right`, `lol`, or `got it` are not useful semantic anchors by themselves. The focus resolver may skip them when resolving a later compact reference.

### Missing target

If a compact reference has no credible history target, the resolver must mark the focus as ambiguous rather than manufacturing a referent.

## Safety and architecture rules

- Canonical history remains semantic authority.
- v1 performs no destructive history pruning.
- Focus metadata is routing evidence, not a conclusion.
- Low-confidence or missing targets must not be presented as certain.
- Existing trajectory, reset, scope, correction-lineage, and response-completion contracts remain in force.
- No user-specific facts or literal private transcript fixtures are required for this contract.

## Inspection requirements

`inspect_engine()` should expose:

- context-focus resolver enabled state;
- full-history preservation state;
- destructive-pruning state;
- deictic anchor support;
- local-correction assistant-anchor support;
- `other one` active-anchor behavior;
- a deterministic acceptance result with pass count, total count, and failures.

## Live verification

Production verification should correlate the active engine revision with `context-focus` camera events. At minimum inspect:

- mode;
- target role;
- target history distance;
- confidence;
- ambiguity flag;
- request/terminal outcome through the existing camera chain.

A published repository version is not equivalent to a hydrated production revision. Live acceptance requires observing the expected revision in production runtime telemetry.
