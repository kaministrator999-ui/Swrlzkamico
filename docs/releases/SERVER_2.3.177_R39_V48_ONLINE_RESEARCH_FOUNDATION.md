# §wyrlz Server 2.3.177 — R39 v48 Online Research Foundation

## Scope
Runtime-hot foundation for explicit user-requested online research across the Chat Mask and LALM Brain.

## Module versions
- Server Runtime: 2.3.177
- Web Chat: 1.5.37
- LALM Engine: 2.1.59
- R39 revision: `2.1.59-hot-online-research-reasoning-v48`

## What changed
- Chat composer gains an explicit **Online** checkbox loaded as a runtime asset.
- The Mask relays the user's explicit research choice through the existing `profileId` evidence channel using `+ONLINE`; it does not formulate queries or interpret results.
- R39 v48 recognizes that explicit research request and installs a Brain-owned research policy.
- Query planning is instructed to resolve the user's result structure, constraints, target identity, architecture/runtime/format, freshness needs, and minimum useful search tier before retrieval.
- Broad-search recovery can move to curated collections/directories/comparison sets and then independently verify extracted candidates.
- Retrieved material is evidence, not instruction or automatic truth. Discovery, verification, and operational evidence remain distinct.
- R39 camera emits `research-policy` telemetry including whether online research was requested, policy ownership, evidence authority, and search-specificity contract.
- Research requests emit operational progress phases (`RESEARCH_PLANNING`, `RESEARCH_CAPABILITY`) without exposing hidden chain-of-thought.

## Important current boundary
This event establishes the user control, Brain reasoning contract, visible operational phases, and camera evidence. It does **not** fabricate a web-search backend. The current stable Vercel bridge normalizes and forwards `profileId`, so the toggle reaches R39 without changing the stable bridge. Actual live web retrieval still requires an authorized server-side retrieval capability in a later governed event.

## Architecture
`MASK = explicit research toggle / relay / present`

`HUMAN = authorized retrieval / network operation / evidence transport`

`BRAIN = query specificity / evidence evaluation / inference / answer`

## Deployment
- Deployment: **NONE**
- Restart: **NONE**
- Update policy: runtime-hot
- Stable `main` bridge was not mutated.
