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
