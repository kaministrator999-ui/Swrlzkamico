# §E v11.454 — top viewport Inset → Depth slider

## Intent
After choosing **Inset** and selecting a planar face, a compact panel at the top of the **model viewport** shows a single slider and a **Set** action on the right. The same panel progresses from **Rim width** to **Depth inward**, with observable live geometry previews.

## Existing source of truth
- The native Model Studio workshop (v11.430) remains the geometry and Undo owner. Inset produces a connected coplanar rim; signed negative Extrude produces a recessed cavity.
- v11.450 supplies the preview and selectable connected face region.
- v11.451 supplies native amount input and guided actions.
- v11.452 supplies contextual Face flyouts, which remain present and recoverable.
- v11.453 supplies the visible inner rim line and direct viewport rim handle outside this top workflow.

## New two-stage behavior
1. **Rim · 1/2**: selecting Inset opens the top overlay. If a face is missing, the user taps a face. No conversion or bake is performed by the top overlay; established native conversion safeguards remain in charge. Dragging the slider updates a validated transient Inset preview. **Set rim** invokes the existing native Apply once, producing one Undo checkpoint.
2. **Depth · 2/2**: the native Inset Apply leaves the inner region selected. The overlay automatically changes the workshop operation to **Extrude**, makes an inward negative-depth candidate, and shows the new slider. Dragging checks collision/topology and updates a transient preview without document writes. **Set depth** invokes native Apply once, producing the second Undo checkpoint.

Set is disabled until the respective preview is valid. An invalid depth leaves the last valid preview intact and disables Set until another valid value is chosen. A depth adjustment cannot silently commit a rim or geometry. The X button discards stage 1 without changes, while in stage 2 it discards only the pending depth and retains the previously Set rim; Undo removes the rim separately.

The old guided modifier drawer and viewport diamond are hidden only while the two-stage overlay owns the workflow, not deleted. Project save/load, mesh topology, touch orbit/pan/zoom, the existing VR menu and other categories are unchanged.

## Acceptance
Select a cube, choose Face → Inset, tap the top connected square, adjust rim, observe a real inner outline, tap **Set rim**, adjust negative depth, observe the cavity, tap **Set depth**. Undo twice to restore the cube. Verify invalid depths cannot be Set and Cancel at either stage follows the stated behavior. Also verify no camera reframe or draggable panel jump during slider interaction.

Automated checks test both consecutive native Apply calls, negative signed depth preview, invalid value blocking and the separate cancellation paths. Physical phone and Quest acceptance remains a separate user test after verified HF publication.
