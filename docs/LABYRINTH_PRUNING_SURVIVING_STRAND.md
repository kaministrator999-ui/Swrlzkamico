# Labyrinth Pruning — Finding the Surviving Strand

## Core model

The search space is not something §wyrlx must exhaustively traverse. It is something evidence progressively **trims away** until the surviving causal/evidentiary strand becomes visible.

```
possible space ♾️
      ↓ evidence
large candidate graph
      ↓ contradictions / observations
smaller graph
      ↓ discriminating tests
few surviving strands
      ↓ verification
〰️ surviving strand 〰️
```

The goal is not "explore infinity." The goal is to make irrelevant infinity disappear around the answer.

## Evidence is a pruning operation

Each reliable observation should remove candidates, hypotheses, routes, or causal explanations that can no longer be true.

A useful observation has high **discriminatory value**: it removes substantial unsupported space while preserving the valid path.

This is the same primitive across domains:

- intent inference: remove meanings incompatible with context;
- visual search: remove regions/candidates that fail observed features;
- debugging: remove fault locations incompatible with logs/state;
- web research: remove claims unsupported by provenance/evidence;
- deployment diagnosis: remove explanations contradicted by repo/build/runtime telemetry.

## Critical failure mode: premature pruning

Choosing a wrong path is recoverable if alternatives remain.

A more dangerous failure is deleting the correct path too early.

Therefore §wyrlx should preserve plausible candidates until evidence actually contradicts them. Unknown evidence is not contradictory evidence.

Every elimination should retain a machine-inspectable reason.

## The strand

The surviving strand is the smallest evidence-supported route connecting the problem's start state to its supported conclusion.

For a debugging problem this may be:

`symptom → request → server → deployment → runtime → stream → renderer → UI`

The strand can be squiggly. It does not need to be aesthetically simple; it needs to remain causally/evidentially intact after unsupported branches are removed.

## 𓆪.𓆩 observability

Telemetry should make pruning auditable:

- candidate/hypothesis introduced
- evidence attached
- discriminating observation performed
- branch retained
- branch eliminated + reason
- contradiction detected
- previously eliminated branch restored after new evidence
- surviving strand updated
- confidence recalibrated

The system must be able to answer not only "what survived?" but "what was cut, by which evidence, and could that cut have been premature?"

## Evaluation

Test from specific questions through broad, noisy, cross-domain problems. Measure whether §wyrlx repeatedly preserves the correct route while trimming irrelevant space.

Success is not memorizing endpoints. Success is reliable navigation/pruning on unseen mazes.

**Short form:** Trim the ♾️ until the evidence-supported squiggly strand is the thing left flapping.


## Case Study — Chat Stage / Backstage Pruning

### Symptom

The Chat interface had a visibly slow initial page load even when no LALM response was being generated.

### Architectural clue

The useful analogy was **stage vs backstage**:

- **Chat page / stage:** render graphics and controls, accept user controls, dispatch actions, receive output/state, and update the interface.
- **Backstage:** LALM generation, inference, routing, persistence, response lifecycle work, and detailed lockdown-camera telemetry.
- **Camera boundary:** response-specific cameras should wake for a user-response lifecycle and observe the backstage path through terminal/settled output. They should not continuously film an idle front-stage UI.

That distinction converted a vague performance complaint into an ownership test: *what work is occurring on the stage while there is no show?*

### Evidence found

Source inspection exposed several unconditional front-end loops and redundant refresh paths:

- an admin UI repaint every 500 ms;
- settings/status repaint every 1 second;
- hot-revision polling every 5 seconds;
- ops polling every 15 seconds;
- additional render/status work on visibility and `pageshow` events.

These were not treated as guilty merely because they existed. They became a tightly bounded candidate branch because the symptom occurred at page startup and the work violated the intended thin-stage boundary.

### Pruning action

The front-end was changed from continuous idle polling/repainting toward event-driven behavior:

- removed the 500 ms admin repaint loop;
- removed the 1 second settings/status repaint loop;
- removed unconditional 15 second ops polling;
- replaced 5 second hot-revision polling with visibility-triggered checking;
- removed redundant full renders from page/visibility restoration;
- preserved response-specific stream/LALM instrumentation.

### Observed result

After deployment, the user reported the Chat page loaded **instantly**.

This is strong practical evidence that the removed idle front-end work was on the relevant performance strand. It does not prove that every removed operation contributed equally; isolating individual contribution would require controlled per-operation measurements.

### Why this matters for §wyrlx reasoning

This is a concrete example of the pruning architecture operating on the system that implements it:

```text
START: chat page is slow at initial load
        |
        v
separate stage duties from backstage duties
        |
        v
inspect work occurring while stage should be idle
        |
        v
identify continuous polling/repaint candidate branch
        |
        v
remove idle work while preserving response cameras
        |
        v
deploy + observe
        |
        v
SURVIVING STRAND: unnecessary front-stage background activity
        |
        v
RESULT: instant observed page load
```

The key lesson is not “timers are always bad.” It is:

> **Use architecture to generate candidate boundaries, evidence to prune them, and observed behavior after intervention to validate the surviving strand.**

Or in the project shorthand:

> **Keep the stage thin. Put the machinery and cameras backstage. Trim the ♾️ until the evidence-supported squiggly strand is the thing left flapping.**
