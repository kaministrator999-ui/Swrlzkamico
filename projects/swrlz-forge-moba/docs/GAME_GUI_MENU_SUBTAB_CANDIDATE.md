# §E Game Engine GUI / Menus mini-tab — isolated candidate

**Target:** Game Engine workspace of `kaministrator999-ui/Swrlzkamico`. **Status:** feature implementation and focused JavaScript logic checks complete **on feature branch only**; not yet in the governed assembled HTML or deployed Hugging Face Space.

## Owner request

Keep the four native top-level workspaces. Add compact **Scene** and **GUI / Menus** sub-tabs within the **Game Engine** workspace. Permit hiding and showing both individual GUI layers and all GUI/menu previews **while editing**; these visibility changes must not silently remove or disable runtime UI.

## Implemented

- Native Game Engine tab receives a compact child sub-tab strip, plus persistent Show/Hide UI preview button.
- GUI / Menus opens a responsive inspector over the existing live game viewport. The **Sheep Tag Main Menu** inspector is moved into it, retaining its original text, button-color and camera-orbit callbacks. The old Menu UI shortcut opens this new editor.
- Project-owned `swyrl-gui-studio-v1` supports up to 24 text labels, buttons and panels. Edit name, text, foreground/background color and relative viewport position and size.
- Every layer can be hidden or shown for editor preview independently of its saved **Show in Play** setting. **Show all/Hide all** affect preview only.
- Buttons can have one safe built-in Play action: display only, Start game, Next level, or Stop game. No custom scripts, HTML interpretation or unapproved actions.
- Stores validated `currentProject.guiStudio` with native project serialization; the v11.141 multi-level snapshot system gets an additive capture/restore adapter for per-level UI.
- Reuses the native viewport's **canvas wrapper** and one existing Three.js renderer. Preserves the four top-level workspaces, game simulation and XR navigation.
- No routine GH Chromium, multi-starter, or VR test suite triggered.

## Candidate files

- `runtime/game_gui_menu_subtab_v11_227.js` — GUI model, editor and runtime overlay, Level capture/restore and native inspector reuse.
- `runtime/game_gui_menu_subtab_v11_227.css` — desktop/phone responsive presentation and preview layering.
- `patches/v11_227_game_gui_menu_subtab.py` — append-only HTML injection and release metadata candidate.
- `tests/game_gui_menu_subtab_v11_227.cjs` — focused model, project and level lifecycle tests.

## Source integrity / remaining release gate

The latest packaged, signed engine at inspection was **v11.225**, with **257 patches**, HTML SHA-256 `7407ca6b520912437c280035c1f4258f5b1e7a8ab577f3701b855db26f7bf3a7`. The repository also has v11.226 candidate patches (wolf and Sheep Tag buildings), not included in the inspected v11.225 manifest. Do not override or bypass those pending lines.

The candidate patch is **not** appended to `source-manifest.json` until the authoritative builder can execute, measure the *actual assembled HTML* and reseal `finalBytes`/`finalSha256`. Only after sequencing the pending v11.226 changes (if accepted) should the release operator update the manifest, exact version IDs, `README`, `SPACE_README`, `ROADMAP`, `§tart_§E.md`, current release verifier/workflow references, then commit to `main` and make a **separate final** `DEPLOY_REQUEST.json` commit.

**Validation performed here:** JavaScript syntax parse; targeted in-isolate execution of Create, Edit, editor-only Hide, Show all, project export, native level capture, switch and restore, input-type rejection, Play edit lock, balanced Undo transactions. **Not performed:** assembled HTML build, deployed browser run, physical Android/Quest 2 acceptance.

The two separate browser/hardware acceptance questions are: (1) Does the small child tab remain reachable on the owner's mobile, given the four-workspace top rail? (2) Does switching to GUI/Menu allow useful preview and edit while the native Sheep Tag level-bar/Menu Inspector stays tappable?
