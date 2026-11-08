# §E v11.346: Large-model native UV sheet paging

## User intent
Whole-character native UV export with linked parts for painter-ready, segmented UV image guides, including models with hundreds of separate native meshes. Keep the existing UV inspector and avoid visually unreadable monolithic sheets.

## Implementation
- `Select All` selects the full current native model, not only the first 96. Up to 96 are **exported per sheet**, with Previous/Next sheet controls directly inside the existing inspector. Sheets use stable model-root order, names, source part IDs and exact original UV coordinates.
- The exported filenames include `SHEET-01-of-09-GUIDE.png` and a matching `SHEET-01-of-09-MAP.json`. Mapping JSON includes `sheetIndex`, `sheetCount`, `selectedPartCount`, exact pixel rectangles and per-part geometry/UV fingerprints. Map files are scoped to their sheet for targeted import.
- Each guide uses original per-mesh UVs, not planar/viewport guesses. Atlas cells do not overlap, but overlapping islands **within** a single native part remain; no destructive re-unwrap is claimed.
- Changing selected parts or sheet clears stale guide/mapping, but does not change the model. Partial imported painted atlas still updates only explicitly mapped original parts, with one native Undo checkpoint.
- Existing per-part checkbox list is updated in place on bulk actions, avoiding unnecessary DOM row teardown for very large characters. No added clutter to VR/model studio tools or desktop controls.
- Existing VR display styles and camera-angle menus remain as in v11.345.

## Evidence
[GitHub Actions candidate run 42458051449](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42458051449) rebuilt exact source (357 patches, 9165566 bytes, SHA-256 `77228e757f77977a35f0b9b74bf0f5efc9c82659d70178256b4b9c8f2919ed23`) and ran the **shipped HTML** UV code against an 811-mesh real-Three.js fixture: 9 sheets, each at most 96; final sheet 43; part IDs ordered and unique; page controls and file suffixes validated. Physical browser download permission, actual private mage UV maps and painted artwork remain for user acceptance.

## Workflow
1. Open your mage in Model Studio → UV Layout → **Whole-model UV atlas · linked parts**.
2. Use **Select all** (or select a named group). Set 2048 or 4096px. Sheet counter shows part count.
3. On each numbered sheet select **Export UV guide PNG** and **Export part map JSON**. Use **Next sheet** for the next source meshes until complete.
4. Upload matching GUIDE.png and MAP.json pairs to ChatGPT for texture painting. Keep the guide as a separate overlay in artwork; painted PNG must not bake in labels/wireframe outlines.
5. Back in Model Studio load each sheet's mapping JSON, then import its corresponding painted image; model geometry/UVs and other sheets remain unchanged.
