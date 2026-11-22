# §E v11.234 candidate — Quest browser window fit and Sheep Tag camera write budget

## Owner's Quest 2 report (2026-11-02)

- Several controls/windows appear crowded or overlapping while browsing §E in Quest Browser.
- During immersive Sheep Tag Play, turning or shifting the head produces very severe lag and an impression that a camera/world position is trying to lock, move back or repeatedly correct itself.

## Source trace

- v11.168's Quest-specific stylesheet forces minimum 48px buttons into the editor's existing 48px toolbar row.
- v11.187 positions the Game/Modeler workspace tab group as a sticky left-side element; in a small resizable Quest Browser window, it can sit above scrolled siblings.
- v11.200 + v11.202 already use a **world-space** sheep camera anchor after a single initial HMD-relative snap; the current code does not intentionally seek the live HMD position during match follow. Do not regress that protection.
- v11.195's `se195MoveRig` constructs and installs a fresh XR offset reference space for every accepted world-follow correction. v11.200 smooths follow continuously. This can still issue many reference-space writes during sheep locomotion or orbit adjustment.
- v11.211 protects WebXR blur/hidden return. v11.216 intentionally lets left-stick sheep movement continue while the building wheel is open. Both remain authoritative.

## Narrow candidate

1. Keep Quest-specific topbar and Modeler tabs in a single horizontal scroll lane; remove the Game/Modeler group's sticky/overlap behavior only for Quest Browser profile. Keep modal/project overlay ordering unchanged.
2. Fit Quest's 2D toolbar hit targets inside the existing row without shifting the game viewport. Avoid broad phone/desktop changes.
3. Suppress world-follow translations smaller than 0.055 world units, and delay nonurgent successive translations by 28ms. Preserve larger corrections and all native gamepad, sheep collision, fog, build and XR visibility guards.
4. Share a single read of the tracked headset pose across each XR animation-frame sequence; invalidate the cached pose after an app-owned reference-space update so panels see updated world coordinates. Every consumer receives its own cloned vectors.
5. Add diagnostics `SWYRL_ENGINE_QUEST_FRAME_BUDGET_234.diagnose()` for write counts, skipped writes, headset-pose reads/reuses and preexisting v11.211 visibility-gap diagnostics.

## On-device verification checklist (owner)

1. Resize Quest Browser to a narrow floating 2D window; scroll §E Game/Modeler tools horizontally and open Projects, Chat, and VR Controller Studio. Controls should remain reachable, not render above each other. These are §E page controls; **Meta OS's independent browser windows are outside webpage control**.
2. Enter immersive Sheep Tag on Quest 2; hold the sheep stationary and turn/lean the head. Check that the world neither pitches toward nor snaps back to the head. A stationary sheep should not continuously trigger world-follow reference writes.
3. Walk the sheep with left stick; verify smooth following. Open A/X building wheels and continue moving; wheel selection must not stop locomotion or create a second ray.
4. Open/close Quest's native Camera menu, return and repeat. Watch for frame-rate collapse or camera drift. Do not claim this candidate resolves Quest OS compositor stutter without hardware results.
5. Compare v11.211 and v11.234 diagnostics, including game-only reference writes and callback gaps.

## Publication gate

The runtime and append-only patch are a candidate, **not a live release**. Before merging to `main`, update `source-manifest.json` ordered patches and all v11.234 identity metadata; regenerate the exact HTML length and SHA-256 by running the official builder; update release scripts, docs and source receipts; then make a separate `DEPLOY_REQUEST.json` commit. Follow `RELEASE_PROCESS.md`; no broad browser/CI suite required.
