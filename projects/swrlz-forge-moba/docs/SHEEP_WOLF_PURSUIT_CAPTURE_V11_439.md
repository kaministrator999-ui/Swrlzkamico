# §E v11.439 — pursuit CPU and capture-contact repair

Date: 2026-11-13. Native Quest acceptance: pending.

## Owner observation
With three wolves tailing a still-moving sheep, Sheep Tag briefly hitches even before the sheep is captured. Wolves are faster, yet capture often waits until the sheep slows or stops.

## Root causes investigated in actual source
The effective lane-based wolf AI invokes an approach helper that can try the current prey position plus eight alternate points, each potentially invoking synchronous A* pathfinding. Its cache expires whenever the moving sheep shifts 0.2 world units; with sheep movement of approximately 5.4 units/second, this can repeatedly invalidate approach decisions on consecutive simulation updates. Several wolves increase the work. Existing v11.438 path-worker offload covered normal path selection, but this helper directly called the older native A* route solver.

The native collision separation between a wolf (radius 0.68) and sheep (radius 0.27) includes 0.015 padding, or approximately 0.965 units. Capture was checked at strictly less than 1.05 units. The physical mover advances up to 0.09 per micro-step, so one rejected step can cross the narrow capture band without moving the wolf into it. Thus wolves may appear close enough while tailing the sheep but fail to capture.

## Scoped implementation
- For SOLO XR sheep pursuit, the approach helper first tests clear static lane movement and immediately uses the sheep's current position; it does not synchronously evaluate up to nine A* alternate approach candidates each time prey moves. Blocked routes fall back to the existing wolf/building planning path.
- The native movement path can directly follow nearby visible sheep along unobstructed lanes, preserving its existing swept body collision and shared WebXR render loop. Outside SOLO XR, the original planner is retained.
- Full wolf AI decisions are limited to one per SOLO XR simulation update. Every wolf still moves and checks actual capture every game update; other roles and LAN authority are unaffected.
- When native dynamic body collision blocks a step, the closest point on that attempted movement segment is tested against the **unchanged** 1.05 capture radius. If the segment actually reaches an unprotected sheep on the same level, it triggers the existing one-shot capture. Captured flags and invulnerability prevent repeats.
- Capture/approach CPU timings and counters expose approach cost, near-range check counts, planner deferrals, collision sweeps, valid captures and the next few game-frame durations. They are available as SWYRL_ENGINE_SHEEP_CAPTURE_PURSUIT_439.diagnose(). GPU/Quest compositor durations are not measured.

## Verification
Focused Node VM regression reproduces three wolves, repeated close approaches to moving prey, deferred wolf decision cadence, a stopped 0.09-unit movement step crossing the legal tag radius, no double capture, rescue invulnerability, and unchanged non-SOLO fallback. It passed in GitHub Actions.

Governed 416-patch source assembly: 9,967,451 bytes; SHA-256 1b837415765c159041bec244cadf5673b8fdb2865c73afea16555bbc7c6fa910. Inline JavaScript parsed successfully. Existing v11.438 worker, v11.434 rendering and v11.437 territory/spirit changes remain part of the build.

## Physical Quest acceptance
Test at least three wolves chasing one sheep on open ground without forcing the sheep to stop, then in corridors between buildings. Observe whether frame hitches occur before physical contact, at capture, or during the three immediately following updates. Test rescuing a captured sheep to verify its existing three-second invulnerability. Confirm final sheep capture and normal win transition. Repeat phone/Quest multiplayer and Model Studio camera controls to catch regressions. Do not claim headset FPS or compositor fixes from simulated CPU-only results.
