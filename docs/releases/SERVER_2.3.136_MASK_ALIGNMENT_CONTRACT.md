# Server 2.3.136 — Mask alignment / coherent-user-state contract

**Status:** complete; repository verification pending final authority re-read  
**Overall Server:** `2.3.136`  
**Chat:** unchanged  
**LALM:** unchanged  
**Server runtime behavior:** unchanged  
**Deployment:** NONE  
**Restart:** NONE

## Purpose

The Mask / Human / Brain architecture now explicitly distinguishes internal component ownership from the user's external experience.

Internally:

- Chat/client remains the **Mask**: sense, relay, present.
- Server remains the **Human / Body**: operational authority, durable state, routing, permission, execution.
- LALM remains the **Brain**: interpretation, reasoning, semantic decisions, answer generation.

Externally, the user experiences one coherent §wyrlz. The user must not be required to reconcile contradictory states produced by separately functioning components.

## New mask-alignment invariant

The Mask must sit straight over the system underneath it:

- A client-visible operational state must faithfully reflect the authoritative state of the component that owns it.
- The client may render, style, summarize, or expose authoritative state, but it must not fabricate or independently guess server-owned operational truth.
- If the server owns a limit/capacity/state such as conversation writability, the client learns that state through the server contract and displays it faithfully.
- If the server says a conversation is still writable, the Mask must not independently declare the conversation full.
- If the server says a true hard limit has been reached, the Mask may expose that hard-stop state and disable the corresponding operation.
- LALM-owned cognition remains LALM-owned; the client must not replace brain output with a competing semantic conclusion.

A mismatch where the Mask displays `full`, `ready`, `connected`, `failed`, `unavailable`, or another condition that disagrees with the authoritative underlying state is defined as a **tilted/misaligned mask**: the user is seeing the wrong underlying state through the wrong opening.

## User-perspective rule

Engineering/debugging should still isolate whether a problem belongs to the Mask, Human/Body, Brain, or the connection between them. That internal separation must not leak as contradictory realities to the user. Separation of responsibility exists to improve correctness while §wyrlz remains one coherent system from the user's perspective.

## Scope

This event changes only the governing project-start architecture contract and the overall Server lineage record. No Chat code, API behavior, LALM inference behavior, deployment configuration, production binary, or runtime action behavior is changed.

## Deployment evidence

Current `vercel.json` has `git.deploymentEnabled = false`. The production workflow deploys only through explicit workflow dispatch or a `main` change to `.deploy/REQUEST.txt`. This event changes neither deployment trigger, so repository documentation commits and the runtime Server-version authority update do not trigger a production deployment.

## Lineage

- Project-start contract commit: `9062758c9f1ccca94337995e7d749259b8c1bb11`
- Server-version authority commit: `2e8308d8c4ed481514f84c0db586ef19afd98c09`

## Rollback / migration

No migration is required. Reverting this event would revert the documentation contract and Server lineage metadata only; no deployed runtime behavior was introduced by this event.
