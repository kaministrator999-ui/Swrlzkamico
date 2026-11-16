# §E v11.474 — progressive Model Studio tool navigation

Implementation: source candidate on main; live status is determined only by DEPLOY_REQUEST.json and a successful Hugging Face deployment workflow.

## Native-backed layers

1. **Existing right vertical rail** — select a tool family: Meshes, Sculpt, Lasso, Topology, Face, Appearance, Motion, References.
2. **Flyout immediately to the left** — select a tool inside that family. Uses the registered native context catalog and adds direct Vertex, Inset and Extrude entrances for Sculpt/Topology. Repeated family taps collapse/restore the flyout.
3. **Top horizontal specific-mode strip** — choose a tool variation: Vertex Single / Ring / Ring Fill; Inset/Extrude Face / Region; or the native manual mesh operations. It scrolls horizontally on narrow touch screens.
4. **Original far-right inspector** — appears only after a specific-mode selection with relevant settings. It is a parameter view, not another tool navigator. Hide settings without disabling selection or current tool.

The previous fixed category-to-inspector behavior and separate Face flyout no longer occupy the visible progressive-navigation route. This is a presentation adaptation of the original Model Atelier. Original brushes, mesh operations, history, Undo, UVs, cameras, saved projects and VR controller code remain the data and mutation owners.

## Real operations and boundaries

- **Vertex / Single:** native vertex component mode; no inspector required.
- **Vertex / Ring or Ring Fill:** the controller does not reenter an already active Vertex component mode, because the native setter clears selected vertex IDs even on a same-mode call. An already selected ring center must be preserved. Requires one selected real vertex as the center. Existing v11.466 graph-distance ring selection, angular arc and radius controls are reused; the far-right settings panel preserves those original handlers. No claim is made that arbitrary freehand closed rings can be flood-filled.
- **Inset / Extrude / Face:** native face mode with selected operation; the inspector displays actual amount, Preview, Apply and Cancel controls.
- **Inset / Extrude / Region:** expands the currently selected coplanar face through the existing workshop selection API where available; it does not generate geometry until an original preview is applied.
- **Manual mesh modeling:** existing native tool operation picker is represented as top horizontal modes; exact operation parameters remain native.
- **Other registered tool families:** registered contextual tool modes appear in the flyout, with an explicit top-bar action before settings are shown.

Pending previews prevent category/mode changes. This maintains a single geometry transaction, preventing accidental loss or invalidating source references. Mobile click targets, overflow, keyboard focus and pointer event isolation are preserved.

## Validation

- node --check projects/swrlz-forge-moba/runtime/model_progressive_tools_v11_474.js
- node projects/swrlz-forge-moba/tests/model_progressive_tools_v11_474.mjs
- python projects/swrlz-forge-moba/scripts/prepare_v11_474_release.py

The prepare script measures source HTML and creates a manifest receipt. verify_v11_474_release.py verifies the actual generated source and original legacy controls. The measure-engine-v11-474 GitHub workflow runs the scoped source check.

Physical Moto/mobile and Quest controller testing is still owner acceptance, not implied by unit and source verification. Do not call this feature live until the deployment workflow and hosted source receipt match.
