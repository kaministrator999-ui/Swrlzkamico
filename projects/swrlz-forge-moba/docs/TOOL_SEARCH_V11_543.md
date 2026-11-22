# §E v11.543 — Find tool / navigate to actual editor controls

## User evidence and why it matters

The screenshot of Model Studio's UV Editor shows the literal control **"UV wireframe"**, not "Current UV Guide". Previous assistant guidance used the latter nonexistent UI name even though the source was accessible. The owner requested a compact search menu that can locate controls and take the user directly to the correct workspace/panel.

## Existing controls reused

- **UV Editor:** \`window.SWYRLZ_E_UV_POPUP.open()\`. The selected mesh and whole-model atlas remain native. Search results open the popup and click the actual labels \`UV wireframe\`, \`Applied texture\`, \`Surface map (optional)\`, \`Stretch heatmap\`, and \`Whole model atlas\`.
- **Model categories and modes:** \`window.SWYRL_E_UNIFIED_TOOLS.select(category,mode)\` and \`window.SWYRL_E_CONTEXT.groups()/current()\`. The index is derived from the native runtime's actual current modes, not a copied list. This covers right-hand tool categories including Meshes, Sculpt, Lasso, Topology, Face, Appearance, Motion, and References.
- **Rigging and animation:** existing \`window.SWYRL_ENGINE_MINI_STUDIOS_496.set('rig'|'animate'|'model')\`.
- **Workspaces:** native \`window.SWYRL_ENGINE_STUDIOS.change('modeler'|'game'|'materials'|'particles')\`.
- **Projects:** existing \`#se320ModelProjects\`/native \`#projectBtn\`, without cloning project libraries.
- **File, View and Settings:** existing native UI click handlers, not alternate implementations.

**Actual UV export placement:** The native `#se336UVExport` button is moved (not copied) from the bottom of the UV Editor to the controls beside the UV wireframe preview. Its original PNG export listener and mesh-selection enabled state stay attached. Searching "Export UV wireframe" or "Current UV Guide" navigates to and highlights that button; choosing a search result does **not** initiate a download. "UV wireframe" alone still finds the preview display mode, which is a different control.

The Find button is added to the existing top workspace tab strip and Model Studio header where available. The overlay is responsive for narrow Android screens; it includes a keyboard-accessible search input, focus trapping, Escape and close, live result status, and Ctrl/Cmd+K shortcut. Search results display the exact current UI name and location. Synonyms such as "Current UV Guide" now map to the actual Export UV wireframe control, not the preview toggle.

No indexed project text, external network search, model changes or save mutations. Command discovery is restricted to grounded native destinations; inaccessible controls report a failure instead of a fake success. Existing geometry, UV PNG, cloud account and historical starter projects remain untouched.

## Acceptance

\`tests/tool_navigation_search_v11_543.cjs\` loads the exact runtime and checks synonym matching and actual call paths to the UV controls, model category/mode selection, Rigging, Materials and Projects. The release verifier checks the assembled native HTML, SHA-sealed patch lineage, source identity, assets and existing editor/account regressions. The owner's phone/Quest test remains the practical UI acceptance gate.

Try searching: **Export UV wireframe**, **UV wireframe**, **current UV guide**, **sculpt**, **push-pull**, **rigging**, **animation**, **starter projects**, **materials**, or **stretch heatmap**.
