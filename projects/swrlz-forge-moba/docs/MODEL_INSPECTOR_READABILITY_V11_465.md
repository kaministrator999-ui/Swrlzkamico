# §E v11.465 — Native inspector readability and reliable Expand/Dock

## Reproduction

On an Android-sized viewport with the existing Model Studio four-track layout, the user dragged the right inspector to about 120 CSS pixels. The v11.464 inspector styles contained `overflow-wrap:anywhere`; long labels such as **Learn Create geometry** rendered vertically, one character per line, including controls that otherwise functioned. The v11.464 Expand overlay also did not reliably release the right grid track because the prior touch-dock layout sets `--se320-right` with `!important` at higher specificity.

## Focused change

- Keep the original inspector, native button inputs, pointer/keyboard splitters, viewport camera and its selected-mesh Undo/Redo bar. No cloned controls or edits to inspector width storage.
- Restore word-boundary wrapping for labels, buttons, summaries and help text. On dock widths under 236 CSS pixels, display a brief **Tools are compact** note directing users to the existing **Expand** action or dragging wider. Hide only the visual layout of rich controls while compact; their original DOM and handlers remain mounted.
- A ResizeObserver measures the existing inspector itself, not the entire page. It handles initial mount, resize and remount without leaking observers/listeners. Expanding or dragging wider returns the full form; docking back to narrow returns the compact note.
- Correct the native desktop-style mobile grid to allocate zero to the *right grid track* while the original inspector is overlaid. Restore saved native widths when docking. Also make Expand work for a desktop mouse user who intentionally drags the inspector unusually narrow.
- Preserve v11.462 wireframe / v11.464 X-Ray and lighting, v11.463 history toolbar, VR hand controls and sculpt editing.

## Verification

Compile all 442 existing §E ordered patches and verify actual final HTML bytes, SHA-256, static asset receipts and inline JS syntax. Run the new inspector regression (narrow, minimum threshold, Expand, Dock, remount and desktop rules) alongside the prior visual, wire, orbit and history tests. Only after all checks pass, seal the release and generate a separate Hugging Face deployment request.

**Acceptance to verify on the Moto:** narrow inspector shows a readable short message; Expand displays the full Inset/Extrude and tutorial controls; Dock restores previous widths and both drag grips; moving between categories does not hide or duplicate controls; model orbit/Undo remain functional. This report does not assert physical phone acceptance.
