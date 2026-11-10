# Model VR v11.390 — select, Grab and create

The controller workflow now has a direct path from selecting existing geometry into manipulation and from creating new geometry into the same Grab tool. Inspect remains presentation-only. A deliberate primary-trigger selection while inspecting arms the visibly labelled Grab tool; no geometry changes until the grip gesture is committed.

## Default Quest / Touch controls

| Input | Behavior |
| --- | --- |
| Right trigger | Select a part; selection from Inspect arms Grab |
| Right grip in Grab | Move and turn the existing selection together; release applies one native Undo step |
| Right stick while gripping in Grab | Resize the selection; the axis must return to neutral before camera orbit resumes |
| Left trigger + right grip | Temporary fine motion using the active profile's precision multiplier; engaging/releasing it does not jump the preview |
| Left trigger | Add/remove selection; hold and sweep to collect parts, retrace to remove new additions |
| A tap | Cycle Move → Rotate → Scale, without entering unrelated creation modes |
| A hold | Broader tool wheel, including Grab, Inspect, Sculpt, Draw and Two hands |
| X + A | Open Create; release the buttons, choose a shape with the trigger |
| X + right trigger | Duplicate selected parts as one native Undo transaction; copies become the selection |
| Right trigger during placement | Confirm a shape with a fresh trigger press; the menu click that armed it cannot also place it |
| B / Y / X+Y | Cancel / Undo / Redo |

The existing left-grip workbench navigation, menu-window dragging, explicit two-hand geometry mode, camera orbit, Selector front/through lassos, focus and project controls remain available. Focus frames the entire selected group. Draw now hands off to the already selected eligible face for extrusion, so the grip does not require precise re-aiming or change the target selection.

Built-in left-handed presets mirror the shortcuts. Custom profiles are retained and drive actual dispatch, sweep input, placement hand and controller labels. Modifier combinations tolerate an already-held modifier; capturing a shortcut closes a previous wheel without choosing an unrelated hovered card. Menu ray hits take priority over Duplicate. The essential workflow does not require a reserved Meta/Menu button.

## Native creation and transaction safety

Create offers Cube, Sphere, Cylinder and Cone alongside Draw, Sculpt and Duplicate. Shape selection produces a translucent native-geometry preview. Aim into the workspace, use the stick to adjust size/orientation, then press the primary trigger again to commit. Either controller can operate the menu; the active profile's primary selection controller performs placement. The created part is selected and ready for Grab immediately.

Preview geometry belongs only to the XR presentation scene. Source descriptors and history remain unchanged before confirmation. Cancel, tracking loss, profile changes, document/native rebuild changes and VR exit discard the preview. Confirmation validates the original document identity and source fingerprint, uses the native part validator, and creates one checkpoint.

Bulk Duplicate clones up to 32 native parts in a single atomic transaction, retaining geometry, UV paint, materials and group metadata. Root-space offset is converted through native assembly placement, preserving the visible relationship between copies. Invalid, stale or oversized operations reject before modifying the model. Manipulation and placement remain separate native Undo steps.

Fine-motion changes use incremental rebasing for Move/Rotate/Scale, Grab, extrusion and explicit two-hand transforms. Temporary preview data never replaces the authoritative descriptors. The existing save schema, rigs, account revision checks and native editing limits remain in force.

## Validation and delivery

Tests use actual Three.js r169, the native primitive factory/part validator, and pinned official IWER 2.8.0 Quest emulation with the real XR renderer and frame loop. Coverage includes combined Grab motion, fine-clutch boundaries, source-safe previews, one-step create/duplicate history, group focus, remapped selection sweep, both-controller menu access and Cancel-before-release priority.

Source seal: **389 ordered patches, 9569287 HTML bytes, SHA-256 `5b1de0f292dd51ddfcad1becbaa59aadc6e464fcacbc44ca0ed86e57ee7fea0a`**, 77 bundled assets. `index.html` and `modeler.html` are identical and agree with `SOURCE.json` and the manifest. The latest graphics controls and Quest guest LAN synchronization are preserved.

Software verification does not establish physical Quest comfort, tracking feel, haptics or sustained hardware frame time; those remain owner acceptance testing.


### Local verification completed

The exact sealed artifact passed **15 end-to-end IWER controller workflows with zero page errors**. Four actual-Three/native resolver suites passed **54 groups** (22 input, 10 Grab pose, 15 native creation, seven flow/transaction checks); the updated spatial UI and controller-hint checks also passed. The full package rebuilt to matching index/Modeler HTML and verified all 77 asset hashes across 81 files.

An additional read-only Quest-browser preview loaded the original 59-part mage, displayed native creation ghosts, canceled them, and restored the editor with serialized model data and history unchanged. A short rendered interaction recording accompanies the preview; this is emulation, not physical headset footage. Hosted verification is complete.


### Confirmed hosted delivery

- Coherent source commit: `172649b17d1f86265443447dd189ffedb6b4cdca`.
- Separate request-only commit: `1bdd5745d91b208687bcd9ea8e20ffcff231373c` (one commit, one changed deployment request).
- Deployment [42925139497](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42925139497): **SUCCESS**.
- Hugging Face revision `c7f4338465507c430bb6398b050c589ea39a71e6`: **RUNNING**.
- Official revision-pinned `SOURCE.json` matches the version, all 389 ordered patches, HTML size/hash and all 77 local asset receipts. Independently streamed hosted `index.html` and `modeler.html` each match **9,569,287 bytes**, SHA-256 `5b1de0f292dd51ddfcad1becbaa59aadc6e464fcacbc44ca0ed86e57ee7fea0a`.
- The read-only mage run includes pending native creation previews and a canceled preview recording, with all 59 native targets visible, unchanged serialized model/history and native parent restoration.
- No account or cloud model mutations were required. This closure changes documentation only and does not bump the runtime version or issue another deployment.
