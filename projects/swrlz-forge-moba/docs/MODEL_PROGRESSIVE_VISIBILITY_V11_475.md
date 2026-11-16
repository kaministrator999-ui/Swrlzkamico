# §E v11.475 — Visible progressive mobile toolbar repair

Owner screenshot: Right-side **Meshes** remained visually selected after tapping **Sculpt**. No tool list appeared beside the category rail, so the new top specific-mode strip could not be reached.

## Cause

The v11.474 controller appended the tool flyout inside the native `#modelAtelierToolRail` scrolling grid column. v11.320's older, higher-specificity rules impose `overflow-x:hidden!important` and `overflow-y:auto!important` on that rail. Moving the flyout horizontally outside its parent therefore clipped it. On touch devices in desktop-site mode, an additional coarse-pointer placement rule placed it above the full-height rail.

The v11.474 click capture intentionally prevented old category-handler side effects. It also bypassed the native `aria-pressed` highlight update, leaving the old family button highlighted.

## Repair

- **Same actual flyout, new parent:** Move the live `#se474ToolFlyout` node to `.atelier-body`; do not recreate buttons or intercept their native event handlers. Position it beside the selected family using real bounds of the rail, body and button. Compact horizontal rails use an above-rail placement. Keep the flyout inside the work area and above the viewport.
- **Exclusive active state:** Set `aria-pressed` and family-state attributes on each native category button from the one progressive tool controller. One family is active at a time, and inherited stale highlights are cleared.
- **Top modes within viewport:** Position `#se474SpecificModes` using the real scene bounds, below the existing native transform strip when visible. It still appears only once a tool has been chosen from the flyout.
- **Idempotent repair:** Observe category/flyout state and relevant resizes without polling model geometry or duplicating tool logic. Preserve the native inspector, Ring Fill, Sculpt, Inset, Extrude, project, UV, VR, Undo and category-rail fold behavior.
- **Ring UI scope correction:** Browser runtime tests exposed a pre-existing v11.466 ReferenceError: the ring installer was declared inside ModelAtelier but referenced by the global adaptive-panel installer. A single narrow window bridge now invokes the original function, which still owns its native settings, radius and selection actions. No parallel ring editor is introduced.
- **Quest input scope correction:** The same adaptive initializer also called the v11.467 Quest pointer installer outside its lexical scope. A second narrow installer bridge restores that pre-existing controller setup, without modifying its capture rules or XR models.

## Verification

Focused unit checks:
- `node projects/swrlz-forge-moba/tests/model_progressive_rail_fix_v11_475.mjs`
- `node projects/swrlz-forge-moba/tests/model_progressive_tools_v11_474.mjs`

Browser acceptance uses actual Chromium taps on two touch-profile widths: category highlight, visible left tool flyout, clickable Vertex tool, visible top Ring Fill mode, and inspector gating. It also checks that the top mode bar stays inside the viewport without overlapping the native transform strip.

The v11.475 452-patch canonical source build and exact SHA-256 receipt gate deployment; physical Moto/Quest acceptance remains separate.
