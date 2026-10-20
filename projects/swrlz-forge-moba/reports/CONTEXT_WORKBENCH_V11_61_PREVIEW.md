# §E contextual tool workbench — v11.61 PREVIEW ONLY

**Status:** additive, optional secondary operations/properties overlay on the existing v11.60 Model Atelier. NOT a production v11.61 release.

## How to locate and use

1. Open §wyrl§ Engine → **Model Atelier**.
2. In the floating **⠿ Move tools** inspector header, tap **◫ Context**.
3. Choose a category on the **right-hand vertical rail**. The **secondary split popup** offers related operations on the left, and the selected operation's settings/actions on the right.
4. Example: **Lasso → Paint mask**. Edit radius or mask mode in the properties pane; it updates the actual native Lasso input through native events. Button actions are executed only when tapped.
5. **Save my values** saves that operation's settings on this browser; **Apply saved values** explicitly restores them. Just switching tools never applies saved values or changes model geometry.
6. Drag **⠿ Context tools** to reposition the secondary window. Tap **✕** or **Original inspector** to close it without removing the original editor.

## Contextual families backed by existing native controls

| Primary tool | Operation groups |
|---|---|
| Meshes | Select & organize, XYZ transform, material & shape |
| Sculpt | Brush/falloff, placement, shape, vertex editing, resolution |
| Lasso | Create region, boundary pins, groups, curves, painted masks, Boolean masks, regional deformation |
| Face | UV face sheet, landmarks, contours, photo cutout, profile calibration, extrude |
| Topology | Mesh edges/vertices/faces, adaptive topology, audits, boundaries, LOD and UV tools |
| References | Local photos, reference views and floating windows, where native controls are present |
| Motion | Pose/motion controls, only when native source controls exist |
| Appearance | Portrait/shape, materials, export where native controls exist |

The UI additionally discovers compatible unregistered native Model Atelier fieldsets and surfaces their existing controls in matching contextual groups. A control is not fabricated when it is absent; native controls remain disabled when incompatible with the selected part. Selecting a category does not automatically edit scene/model data.

## Evidence and limitations

Implementation `patches/v11_61_context_workbench_preview.py`, UI tests `tests/model_atelier_context_workbench_browser_v11_61.mjs`, Actions `.github/workflows/verify-atelier-context-v11-61.yml`.

The v11.60 source manifest, deploy trigger, original 283 model parts, 43 packaged assets, history/Undo and file import authority are unchanged. Native controls stay mounted in the original inspector for rollback and legacy compatibility; the workbench uses validated two-way proxies and user-triggered native click actions.

**Other §E surfaces:** Anime/Story, Maul/game builders and remaining editor workspaces require source-specific adapters and independent verification. This preview does not yet provide secondary popups in those workspaces. Future adapters should reuse this same registry/native-control-authority pattern.

**Release gate:** production v11.61 must first pass full regression CI, model/asset equivalence, version/manifest/hash sync, and owner-facing location guide, then follow the separate **final repository mutation** DEPLOY_REQUEST, terminal Hugging Face deployment, exact served HTML/all assets, and desktop/phone hosted checks. Do not claim this draft is live.
