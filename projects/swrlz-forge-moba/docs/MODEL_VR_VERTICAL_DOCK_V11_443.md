# §E v11.443 — vertical Model Studio VR tools
Date: 2026-11-14

## Owner problem and design
The prior VR spatial console presented many unrelated editor controls together in a 12-card grid and a horizontal row of navigation tabs. Tool selection should be immediate and its detailed controls should not obscure the modeling viewport. The Quest satchel tutorial exposed this navigation burden during manual flap work.

The Model Studio UI now wraps the existing console in a world-space **vertical tool dock** with a right-side contextual settings drawer. The dock stays available while its settings panel opens/closes and slides out to the right of the same assembly. Select, Grab, Move, Rotate, Scale, Create, Draw, Sculpt, Mesh edit, Objects, Display, and Projects remain available, with native Undo/Redo/Save shortcuts.

The original console's native tool cards are reused as the settings body; no command is replaced by a fake visual control. Native tool state, object selection, previews, Cancel, Undo/Redo, and model/source serialization remain with their existing owners.

## VR input contract
- Both dock and drawer share the original VR UI root, root tracking, and existing independently draggable Grip gesture, including its ray-hit offset and persisted world-space menu placement.
- Hover and Trigger use the current XR frame's controller ray. The background remains an input-blocking UI surface, so selecting or dragging the dock does not edit geometry behind it.
- The attached panel can be closed independently without hiding the dock. Closed/transitioning drawer targets are excluded from hit-testing; a new tool opens the appropriate native controls.
- Native controller quick wheels, model gestures, tutorial windows and projects retain their routes.
- The active native gizmo contact takes priority over a mesh behind it (but never over a visible menu), including its larger padded handle targets, Grip-only transform transaction, highlighted handle and a distinct target ray.

## Verification and limitations
The release process rebuilds the entire authored HTML using the ordered versioned patches, checks exact SHA-256/byte receipts, native tests and script syntax, then commits the deployment request separately. A successful pipeline does not replace physical Quest 2/3S controller acceptance.

This change reorganizes VR presentation and input priority, not the flat/mobile Model Studio layout or the underlying drawing algorithm. Precision-assisted drawing remains a separate work item, not an unverified feature claim.
