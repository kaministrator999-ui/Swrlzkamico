## 2026-10-20 · Repeated native More repair (stacked candidate)

After selecting **More**, opening **References** in the contextual sheet, and selecting **More** again, v11.60's last-choice click-to-hide behavior could conceal the native inspector at the same time v11.61 closed the secondary sheet. The additive v11.62 repair restores the native inspector when its own rail click has just closed it, on phone presentation only. A new repeat-selection assertion runs at each phone viewport in the six-viewport mobile test. This is a source/test candidate and is **not shipped**; its final verification must be read from the stacked PR's CI. Desktop and original 283-part/43-asset states must remain unchanged.

# §E v11.62 mobile tool layout — preview user guide

**Status:** Development branch / pull request #278. This is NOT shipped in production. Production §E remains v11.61 until a full release passes all gates.

## Why this matters

The v11.60 original floating inspector and v11.61 secondary contextual inspector both used large fixed windows on mobile, and the primary tool rail was high on the right. This preview replaces the competing surfaces with **one visible active tool sheet on phones**, a reach-friendly bottom tool category rail, more readable properties and tool discovery. It preserves the original native controls, project save semantics, and undo/redo.

## Exact tool locations and usage on phone

1. Open §wyrl§ Engine → **Model Atelier**.
2. The **bottom horizontal rail** shows Meshes / Sculpt / Lasso / Face / Topology / More, followed by References, Motion and Appearance. Swipe the rail sideways for categories not visible.
3. Tap **Lasso** (or any relevant category). A **single contextual sheet** opens directly above the bottom rail. The native inspector is hidden while this sheet is open, never destroyed.
4. Use **All / Quick / Recent** to browse available operations. For example choose **Lasso → Paint mask**, which reveals its actual editable native settings, or **Sculpt → Brush & falloff**. Tap ☆ beside an operation to favorite it; favorites are prioritized and are available in Quick. Recent lists tools you selected earlier.
5. Tap **▤ Half** in the sheet's top bar to cycle **Half → Expanded → Compact → Half**. Or drag the empty header area up/down to snap between states. Compact leaves the viewport largely unobstructed.
6. Tap **Thumb: Right/Left** to switch the bottom rail's starting side for your preferred thumb. The setting and sheet size are stored locally in that browser.
7. **Original inspector** closes the secondary sheet and brings back the complete native inspector. **✕** closes the secondary sheet; native tools remain accessible. The top-left viewport zoom/Frame controls remain available while the sheet is in its usable half state.
8. Save/Apply per-tool values are the existing explicit v11.61 actions. Favorites/recents are for navigation only and do not apply edits to the model.

## Placement rules

- Portrait phone: stacked horizontal operation picker + single-column fields in a bottom sheet above the rail.
- Short landscape phone: vertically scrolling operation choices beside native settings, with a shorter sheet and thumb rail.
- Physical Android browser UI, safe-area/notch/home gesture inset and virtual keyboard: the sheet uses current visualViewport height and keyboard obstruction offsets. A phone layout ignores stale manually dragged desktop pixel coordinates.
- Desktop: original v11.61 freely draggable split workbench and inspector layout remains unchanged; no forced mobile presentation.
- Native source/part selection, mesh edits, export/import, scene data, previews and Undo remain owned by the original Model Atelier.

## Source and acceptance

- Candidate: `patches/v11_62_mobile_adaptive_preview.py` atop exact immutable v11.61 output.
- Dedicated test: `tests/mobile_adaptive_tool_layout_browser_v11_62.mjs` checks 320×720, 360×640, 412×915, 430×932, 844×390 landscape, and 1280×900 desktop.
- Test workflow: `.github/workflows/verify-atelier-mobile-v11-62-preview.yml`, including original v11.61 contextual input/preset and v11.60 dock browser tests.
- Full production §E v11.62 requires a separately measured 94-patch manifest, exact SHA and byte-size release verifier, complete 15-workflow regression suite, new release docs, main merge, a **last-mutation** `DEPLOY_REQUEST.json`, successful Hugging Face deployment and independent exact hosted HTML/43-asset audit.

## Limitations

This patch reorganizes **Model Atelier** (including its eight native tool families). **Story Studio already uses a separate mobile bottom sheet**; Maul, Sheep Tag, animation timeline and other §E workspaces have different interaction/HUD requirements and must be assessed and migrated by their own scoped adapters, not simply hidden by global CSS. This preview does not claim those adapters are shipped. Automated Chromium phone emulation is not owner-on-physical-device approval.
