# §E v11.438 — simulation/render continuity boundary
Date: 2026-11-13. Source version: v11.438. Physical Quest acceptance pending.

## Owner goal
Prevent AI work from stalling visual presentation in Sheep Tag and establish a reusable engine scheduling and measurement boundary. WebXR and the editor must preserve native cameras, controls, graphics and LAN multiplayer.

## Implementation
- The congestion-aware native movement path now dispatches eligible SOLO XR NPC numeric A* searches to a dedicated Web Worker. Nothing in the worker accesses THREE objects, renderer, DOM, camera pose, browser storage, or network authority.
- Jobs receive cloned blocked-grid navigation snapshots with start/destination coordinates. Worker logic mirrors nearest-open-cell selection, 8-neighbor A* and the native 18,000-node expansion cap.
- Queues are bounded at 12 in-flight requests. A waiting bot has no new path rather than forcing a synchronous A* burst; other simulation updates and rendering continue.
- Results are applied only when session, navigation version, target, and unit are still valid. A stopped session discards outstanding work. Unsupported workers fall back to original native paths.
- Shared diagnostic SWYRL_ENGINE_RENDER_BRIDGE_438.diagnose() tracks worker completions/fallbacks/queue pressure, simulation CPU time, render-submission CPU time, and XR callback gaps. No added RAF, timer or replacement XR loop.
- The v11.437 capture diagnostic is correctly exposed in the new assembled release, without rewriting historical patches.

## Preserved architecture
Native WebXR animation loop, headset pose tracking, normal game-state and physics updates, player movement, LAN authority, collision checks and path-block retries, existing v11.411/v11.419 AI budgets, v11.434 visual batching/shadow reuse, v11.437 territory and capture pooling, Model Studio, starter scenes and account saves.

## Verification and integrity
- The new focused test runs the actual worker route solver against a blocked grid, verifies route avoidance, player/non-XR fallback, stale reply cancellation and unchanged render/update entrypoints.
- Source assembly produced 415 ordered patches, matching index.html/modeler.html and 9,958,565 bytes. SHA-256: e25a12c1f299a457d67443a61d90774d73ce22c2ace932aab8a093061576ebbc.
- JavaScript parsing and focused native tests passed in the source-seal preview; a complete release gate is separately version-pinned.

## Limits and owner acceptance
This does not put the entire simulation in a Worker or move GPU work off-thread. Physics, actor setup, building geometry, capture transitions and scene mutations can still block the main thread. GPU compositor timing is not measured. Worker startup is lazy and the first route can use the legacy solver; CSP/unsupported Worker browsers retain native behavior.

Physical Quest 2/3S: crowded solo match with seven sheep AI and 70+ houses, stand and turn beyond 20 seconds, repeatedly capture sheep (including final-capture victory), test Meta-menu entry/return, then verify mobile editor Play/Simulate and phone/Quest LAN match. Diagnostic workerReady/workerCompleted confirms whether offloading is active; actual headset frame pacing and comfort require physical testing.
