# §E Unified Popup Browser · candidate

**Owner design:** Replace scattered editor tool access with one Garry's Mod–style tabbed browser. Preserve the top-level Game Engine / Modeling / Particle Studio / Materials & Textures workspaces.

## Integrated source (candidate; not live)
- `runtime/unified_popup_browser_v11_226.js` and `.css` implement the browser shell, search, move/resize, context tabs and compact game/model viewport.
- The native Game assets/scene panels, Model Atelier inspector, Particle Studio inspector and Material Studio inspector are **temporarily portaled** into the browser, not duplicated. The exact DOM elements, event handlers, working project state and renderer remain authoritative. Closing/switching restores the element to its original parent.
- Native tool buttons remain available in a searchable action gallery. Clicking an action restores the native panel, closes the browser, then calls the original button's handler.
- Browser opens from the original workspace tab bars with **☷ Browser**. Keyboard: Ctrl/⌘+Space toggles; Escape dismisses. Clicking outside closes. Workspace-specific last category is saved only in sessionStorage.
- Keeps the existing Sheep Tag radial quick-build controls and native immersive WebXR input unchanged. This implementation is for the **2D editor surface** (including Quest's flat browser); an in-world XR browser would need separate native controller-ray and headset acceptance.

## Source and release gate
- Append-only candidate patch: `patches/v11_226_unified_popup_browser.py`.
- Targeted candidate integrity computation: `scripts/candidate_v11_226_integrity.py`, optionally exercised through the dedicated source-only workflow.
- Do not insert this candidate into the canonical patch list and ship it without resealing its **actual** generated HTML byte count and SHA-256. Any concurrent change to main must be incorporated first; do not reuse a taken version number or overwrite another contributor's source.
- Once current main has stabilized: apply candidate as a new ordered patch, recalculate canonical manifest/version/marker and documentation, run the narrow source verifier, commit to main, and use the required separate pinned `DEPLOY_REQUEST.json` commit for publishing. Validate deployed SOURCE.json before calling it live.

## Owner acceptance
On Moto G Power and Quest 2's flat browser: open/close browser; browse Game assets and scene; add a building; switch to Modeler and edit/rig hand; open Materials/Particles; verify native authoring still works and the panels return correctly. Then inspect immersive VR separately (quick-build wheel still works; no new in-world browser yet).

Do not run broad Chromium/22-case suites as routine acceptance. Real-device interaction belongs to the owner.
