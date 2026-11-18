# §WYRL§ Engine v11.515 — immersive spatial menu clarity and controller hardware guides

**Tracking:** issue [#472](https://github.com/kaministrator999-ui/Swrlzkamico/issues/472), physical Quest acceptance pending for #3 and #8. This update also ensures v11.514 Rigging / Weight Painting are actually reachable through the **current** three-stage spatial menu. No starter or Sorting Hat geometry updates.

## Architecture: preserve native immersive VR

This release modifies the existing `se340CreateModelVRUI` presentation and `se372MenuOrbit` / `se372MenuDragFinish` positioning plus the `se362` Quest Touch controller model/label pipeline. No new HTML panels, second WebXR scene, parallel controller loop, custom selection dispatcher or duplicate source of truth.

The far-right §E primary tool rail continues opening a middle operation list, which opens the native left-hand detail panel. Existing Grip moving the whole panel, Trigger ray hover/press, panel-vs-scene hit precedence, B cancel, controller shortcut profiles, selected states, scene ownership, reduced-motion animation and on-exit cleanup remain authoritative.

## #3 — menu controls clipping/disappearing

**Observed before:** Undo/Display and lower controls disappear or shift as head angle/menu position changes, while shifting the panel vertically can hide upper controls.

**Rendering correction:** Three.js transparent sorting can put two meshes with identical `renderOrder` in an angle-dependent order. The existing three-stage menu formerly assigned `8400` to both backdrops and interactive buttons even though both used transparent, depth-test-disabled materials. The source patch now applies deterministic strata within that **same menu**: `8380` for backdrops, `8520` for operation labels/cards, `8610` for quick Undo/Redo/Save, `8660` for Close actions. UI ray targets and visibility timing remain unchanged.

**Placement correction:** The previous `se372MenuOrbit` coupled panel world position to model-camera orbit, causing lateral menu motion when adjusting perspective. The menu now retains the saved world-space anchor independent of camera orbit and billboards its front toward the viewer without headset-following translation. Grip-drag still repositions the same panel and saves the actual chosen world position. Reset uses the prior native saved-placement path.

**Limits:** A manually positioned menu outside the physical field of view cannot be made visible without changing the user's chosen anchor. This correction does not force panels to head-follow. Verify on real Quest at typical working distances/heights; intentionally moved offscreen panels remain user-repositionable via existing controls.

## #8 — smaller, precise controller labels, matched cues

The existing `se362` Quest Touch visual still owns the controller meshes/assets and uses the native profile's live per-key label text. Each five-key controller now has:

- Compact canvas label plane `0.070 × 0.0197 m`, reduced from `0.094 × 0.0264 m`; no giant detached name tag.
- Thin two-endpoint leader from a hardware-button part's authored mesh center (in the existing model's normalized grip coordinate system) to the corresponding smaller label; graceful button-specific fallback if an optional controller visual asset does not load.
- Low-opacity colored button glow at the same hardware center. Physical press scales/brightens the glow. Each key uses the same stable color for its canvas border/key caption, leader and glow.
- Real `se362CurrentBindings` / controller input profile text continues to determine the action displayed. Rigging shows the current joint selection/right-Grip pose instructions; Weight Painting shows the actual right Trigger paint mode.
- Single existing controller `se362Frame` and connection/disconnection lifecycle. The supplementary line and glow geometry is cleaned up with the original controller. None of these visual-only hints enter the menu raycast target list.

## Existing three-stage Rigging access

The current v11.445 native primary rail now includes **Rigging**. It expands the original operation list with **Bone posing**, previous/next joint, Weight Painting and X/Y/Z nudge actions. Choosing a control opens the appropriate **existing** v11.514 native Rigging or Weight Painting settings page and calls its existing controller action. This specifically avoids a misleading implementation present only in the old, hidden horizontal tabs.

## Verification and acceptance

Automated Three.js r169 integration test `tests/model_vr_spatial_polish_v11_515.mjs`: stable world menu anchor under viewer movement and model orbit; front-facing orientation; Grip-drag commit preserves world position; 10 controller key labels and leader/glow pairs; smaller label geometry; exact known model-button center; matched color and press feedback; native model load and disconnect.

Build-level acceptance: full ordered 492-patch source manifest, original unified XR menu/loop remains singular, three-stage category and Rigging page integration, JavaScript source syntax, historical regression checks, browser static files under 10 MB, immutable source SHA and governed Hugging Face deploy.

**Pending owner-device acceptance:** look up/down and sideways while Undo/Display/open settings visible, verify that all three spatial columns and hardware buttons are readable and selectable; test both hands including trigger, grip, stick, A/B/X/Y, and test after toggling Rigging / Weight Painting. No claim of physical Quest behavior before the user tests it.

## Out of scope

No change to VR project browsing #7, model camera/object rotation #5, rigging rest-edit/deformation work #10/#11/#12, source/UV models, projects, schema, account permissions or save history. Those QA items remain open.