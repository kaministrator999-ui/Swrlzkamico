# §E v11.219 — Finger rails aligned beneath joint links

## Owner acceptance reference
The owner supplied two actual v11.218 mobile screenshots and approved a new reference showing **each of the four non-thumb purple finger lines seated on the back of its finger, running through the links just below the topmost fingertip node**. The thumb's wrapped double helix must remain unchanged.

## Implemented changes
- New append-only patch: `patches/v11_219_finger_rail_contact.py`.
- New shared parametric helper: `runtime/model_atelier_finger_rails_v11_219.js`.
- One purple rail per index/middle/ring/pinky finger, defined by six dorsal surface control points. Rails are recentered according to each individual finger's origin, taper, height and splay; the path transitions from the raised dorsal armor toward the fingertip setting. No duplicate decorative rails.
- The two silver finger retaining links now use the exact same geometric point function as the rails (at 45% and 77% of each finger's length). Their centers sit over the luminous line while their ends descend toward the finger edges rather than floating as separate arcs.
- The tip connection reaches `f.to-.085`, underneath the last metallic fingertip bezel.
- Unchanged: continuous 3D thumb spiral, original anatomical glove surface, curved palm, backhand sigil, conductor attachments, colors, cuff, all other projects and game/Quest controls.
- Only **new opens** of the Floating Hand starter receive the change. Existing saved workspaces are intentionally preserved. Every rail/strap is still a native selectable Model Atelier part.

## Source integrity and testing
**§wyrl§ Engine v11.219**, 251 ordered patches, 68 packaged assets.
HTML: **7,504,085 bytes**.
SHA-256: `f2c7177cd479e001b823f2684f3ceae1fcd5235e6333bd97d006a631661ef3c0`.
Candidate native source build, focused marker assertions, JavaScript syntax and Python syntax passed. Physical phone/Quest visual and editing acceptance remains owner-controlled.
