# Server 2.3.251 — UI Component State Ownership Reference

**Status:** documentation/source complete.  
**Runtime behavior changed:** no.  
**Changed runtime modules:** none.  
**Overall Server:** `2.3.251`.  
**Deployment / restart:** NONE.

## Purpose

Create a durable engineering reference from the user-verified Activity Log repair so future §wyrlz UI containers do not rediscover the same state-ownership failure pattern.

## Canonical document

`docs/engineering/SWRLZ_UI_COMPONENT_STATE_OWNERSHIP_REFERENCE.md`

## Architecture decision

Stateful UI components must distinguish system-owned data from user-owned intent. System data may evolve automatically; user intent may change only through the explicitly authorized user interaction path unless a component contract says otherwise.

The Activity Log is recorded as the first known-good reference:

- `message.meta.trail` is system-owned activity data;
- `message.meta.activityExpanded` is user-owned presentation intent;
- stream events may append activity;
- renderers may project state into DOM;
- completion may append terminal activity;
- background lifecycle events must not change expansion state;
- one user activation produces one logical transition;
- legacy behavior selectors must be isolated from replacement components.

## Reusable engineering rules

The new reference documents:

- one canonical owner per mutable value;
- explicit writer permissions;
- controlled-container structure;
- append/update content independent of visibility intent;
- renderer read-only behavior for user-owned state;
- native browser state as a potential competing owner;
- selector and compatibility isolation;
- MutationObserver one-way reconciliation;
- lifecycle invariants across stream, completion, reconnect, DOM replacement, and reload;
- anti-patterns that cause flicker, reopening, reclosing, or multi-tap behavior;
- a working-component registry for future verified patterns;
- a §wyrlz teaching rule: content mutation and intent mutation are separate concerns.

## Verification

The reference is grounded in the user-visible accepted Activity Log behavior after the controlled panel repair and selector isolation work. No application source was modified by this event.

## Version / deployment truth

The version authority was re-read immediately before assignment and reported Server `2.3.250`; this documentation event advances only the overall Server authority to `2.3.251`. No functional module version changes were required. No Vercel deployment was requested or performed.

## Lineage

- Engineering reference commit: `3c9a1b62b33db90881f930394b7499cb08ae72cd`
- Server authority commit: `05dca2096996dba8723074d3da50127279c44b6c`
