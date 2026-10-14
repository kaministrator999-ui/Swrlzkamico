# Frostveil Maul · canonical requirements and expansion sequence

**Status:** User-directed design requirements, **not proof of implementation**. Preserve historical map files and release receipts. Scope these new mechanics behind explicit versioned Maul profiles and independently validate them.

## Gameplay invariants

- Classic Wintermaul-like, top-down cooperative tower defense. Nine separate builder territories and individual tower/maze/economy choices influence **shared team survival**. Towers, rather than cheap standalone wall pieces, create jagged, staggered left/right switching trap mazes.
- Defense sectors link along the ground route to the final shared exit. Building cannot occupy protected enemy entrance pads, gates, exit or clipped tiles. New placements must be legal on both desktop and mobile, visualized before commitment.
- The **builder actually travels to the intended tower site**. A builder must path to an accessible adjacent cell; construction starts/completes only after reaching it. Orders may be superseded or cancelled. No phantom builds or premature spending; revalidate money and path at completion. A selected builder stays in their assigned territory. Keep historical saves replayable.
- Ground creeps are physical actors and cannot overlap or simply phase through one another. Congested lanes and traffic jams are part of the strategy. Air units cross open sky and ignore ground mazes. Blocking a route entirely should invoke appropriate attack-tower/repath behavior (once implemented) instead of a permanent stall. This rule deliberately differs from the current strict route-closure rejection.
- Per-wave archetypes: fast, stealth needing detection, limited/complete resistances and immunities, teleport, Hydra spawning additional units, tiered Infernal splitting, high HP/defense, and support healers. They need explicit schema fields, telegraphed counters, deterministic targeting, balance tests and recorder events. Do not fabricate missing damage/split counts.
- Provide multiple or randomized match modes. Baseline 30-wave co-op remains playable; optional endless mode continues scaling and awards increasing currency, with milestone/broadcast behavior (including wave 1,500 as a design target rather than a current achievement).
- **Mirror Survival:** matching automatic enemy schedules, levels and random seeds across both teams. Players cannot send monsters to opponents. Winner is the team that survives longer; surviving team may continue for rewards after the other loses.
- Themed builder sets are selectable and genuinely differentiated, but **not pay-to-win**. The user mentioned parody/pop-culture themes (e.g. Family Guy, Adventure Time, DBZ, One Piece, Seven Deadly Sins); production distribution needs original/licensed artwork, not unlicensed asset copying. Choose sets and parameters through user-authored or versioned source.
- The Maul map creator must live in §E, not an external editor. Keep rules, terrain, routes, spawn pads, builder locations, wave archetypes and sector affiliation editable with versioned native Save/Load and safe preflight.

## Versioned implementation plan

| Layer | Current / next | Acceptance evidence |
|---|---|---|
| Construction | **v11.1 candidate:** walk-to-build, protected pads, four tower families, wall menu off for current Frostveil profile | Native mouse/touch travel, delayed tower appearance/charge, cancellation, no-build and preserved historical imports |
| Congestion & blocked routing | Future: physical creep spacing, deterministic queueing/traffic-jam behavior, controlled tower aggression when a route is sealed | No overlap, no deadlocks, ground vs air differentiation, replay/tick determinism across frame rates |
| Ability component system | Future: generic status/detection/resistance/immunity/split/teleport/heal components | Unit, target selection, telegraphs, death/rebirth, save/replay and 30-wave balance coverage |
| Team modes | Future: two-team identical wave seeds and isolated player input state; extended endless economy | Mirror schedules match frame-by-frame, no cross-team sends, fair currency, correct tie/win and continuation |
| Builder roster & creator | Future: separate data-driven builder/tower sets with explicit neutral balance metrics and native editor tools | Build set parity, editable authored map, Undo/Redo, asset permissions, phone workflow |

## Implementation boundaries

- The deterministic game model owns economy, combat, occupancy, paths and event time. Three.js visual actors are projections of canonical state.
- Input is an order, not an instant mutation. Its lifecycle should be recorded: requested → queued → walking → arrived → validated → constructed or cancelled. Pending orders cannot be duplicated, spent twice or left running after Stop.
- Map rules are packaged with project data; recorder exports include the initial map/rules and subsequent events. Legacy scenes retain their saved behavior unless explicitly migrated.
- Don't mix this Maul domain with the Sheep Tag or animated-episode rule sets. Extend with additive engine patches and independent CPU/browser/live acceptance. Preserve CPU-constrained Android performance.
