# Frostveil Maul · canonical requirements and expansion sequence

## Verified v11.1 minion-wave status (2026-10-14)

**This section describes what is in the merged, deployed v11.1 source—not a future promise.** The release manifest ends in `patches/v11_1_maul_walk_builder.py` (71 governed patches). Wave behavior is provided by `runtime/maul_core.js` and the grouped Frostveil override in `runtime/maul_batch_core.js`; source is the authority for these statuses. A feature being requested, discussed or listed later in this document does **not** mean it has shipped.

| Feature | Status in deployed v11.1 | Actual behavior / boundary |
|---|---|---|
| Thirty-round cooperative campaign | **Implemented** | Shared lives, nine connected sectors and the final exit; win after wave 30 if lives remain |
| Scattered grouped arrivals | **Implemented** | Three batches per wave at 0, 2.5 and 5 seconds, across each entrance's available arrival cells; wait if insufficient free arrival space |
| Air waves | **Implemented** | Every fifth round except boss rounds: waves 5, 15 and 25; flying units do not use ground tower mazes |
| Boss waves | **Implemented** | Every tenth round: 10, 20 and 30, with boss-tagged enemies and higher HP |
| Basic wave difficulty scaling | **Implemented** | Enemy HP, some movement speed, rewards and armor scale according to current wave rules; this is **not** a roster of special ability archetypes |
| Player builder movement | **Implemented for current Frostveil profile** | Builder travels to an adjacent cell before tower appears; completion revalidates affordability and routes; saved historical variants retain prior behavior |
| Towers form physical maze obstacles | **Implemented** | Current Frostveil hides standalone wall construction; towers block ground routes; full route closure is rejected |
| Enemy entrance construction protection | **Implemented** | Spawn pads and protected route cells cannot be built on; protected pads are outlined |
| Recorder and Maul replay presentation | **Implemented** | Lossless `.json.gz` export/import, plus Maul-aware spectator rendering; pre-existing formats retained |
| Creeps occupying space, queueing and causing traffic jams | **Not implemented** | Ground-creep movement has no general physical unit-unit collision/spacing resolver; grouped spawn occupancy checks alone do not supply full lane congestion |
| Ground creeps attacking towers when a route is completely blocked | **Not implemented** | Current build validation prevents sealing the path; no alternate creep attack/repath system yet |
| Distinct fast creep *archetypes* | **Not implemented** | Wave-speed scaling exists; special fast-unit definitions/abilities do not |
| Invisible/stealthed creeps and detection towers | **Not implemented** | No implemented stealth/detection mechanic or its counters |
| Resistance and immunity archetypes | **Not implemented** | Existing armor mitigates damage, but separate damage-class resistances/immunities do not exist |
| Teleporting creeps | **Not implemented** | No creep-teleport ability or corresponding route/replay events |
| Hydra-style child spawning on death | **Not implemented** | No enemy death-to-child-spawn mechanic |
| Multi-stage Infernal Golem splitting | **Not implemented** | No tiered split/offspring mechanic |
| Healing/support creeps | **Not implemented** | No enemy healer support ability |
| Endless or randomized wave modes, scaling rewards and milestones | **Not implemented** | The current rules cap the match at 30 waves |
| Mirror Survival between two teams | **Not implemented** | No two-team synchronized automatic-wave competition or post-defeat continuation |
| Themed, independently balanced builder/tower rosters | **Not implemented** | Current starter has four tower families; new thematic choices and parity rules remain planned |
| Dedicated native Maul creator tools | **Not implemented as a dedicated subsystem** | General §E scene editing and map Save/Load exist, but the tailored creator workflow is still planned |

### Planned minion-wave implementation and release gates

1. **Congestion/routing:** deterministic creep-to-creep spacing, physical traffic jams, controlled tower attack/repath on total blockage. Preserve flying exceptions, guaranteed simulation progress, reproducible recorded events, and per-device performance.
2. **Data-driven creep archetypes:** distinctive speed classes, stealth/detection, armor vs typed resistance/immunity, teleport, healer/support effects, Hydra splitting and tiered Infernal offspring. Define balance values and counters explicitly rather than guessing them from discussions.
3. **Wave orchestration:** editable per-wave mixes, escalation pacing, telegraphed traits, kill rewards, recording/replay fidelity and CPU-friendly scaling. Keep the original thirty waves playable while introducing versioned opt-in modes.
4. **Modes and creator:** optional endless progression, fair synchronized automatic-wave Mirror Survival, balanced themed builders and integrated native authoring tools.
5. **Acceptance before claiming implementation:** deterministic CPU tests (movement, collision, abilities, death/splits, rewards), multi-sector route tests, desktop and Android touch gameplay, Sheep Tag/legacy map regressions, recorder import/export, six engine workflows, and independent exact hosted release audit after an authorized deployment.

**Release guard:** These pending features must stay labeled *planned* until their code, automated acceptance, and live artifact verification exist. Documentation changes alone do not modify the engine, enemy waves, or the deployed Space.

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
