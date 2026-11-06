# §E v11.284 — Plain Hand Base and Starter Models reclassification

## New independent Starter Model
Add a clean, neutral **Plain Hand Base** under Projects → Starter Models or `?project=plain-hand-base`.

The model reuses only the existing native connected anatomical five-finger, opposable thumb and wrist sculpt topology; it discards all glove armor, cuffs, metallic accents, glowing runes and floating effects. There is no rock geometry. Neutral matte clay shading gives a readable surface suitable for a different future rock-hand approach. The validated original 17-bone rig and its open → fist → open keyframed animation are preserved for Model Atelier sculpt, posing, rig editing, save and export.

The original Arcane Glove, mirrored left glove and Rocky Anime Hand · Emberstone remain unchanged and separately selectable.

## Starter Games / Starter Models repair
The original v11.236 categorizer was hardcoded before the newer starter cards existed. v11.284 classifies known model project IDs and **explicitly labeled Starter Model** cards into the **Starter Models** grid. This includes Rocky Anime Hand, both Arcane Glove variants, Plain Hand Base, sheep buildings and known character models.

It moves existing DOM nodes—not copies—so project IDs, event handlers and defaults remain intact. Explicit games, including Blank VR · Arcane Hands, remain in Starter Games. The separate Starter Particles feature is unaffected.

## Verification
Narrow native Node smoke checks clean source anatomy, lack of costume parts, preserved 17-bone rig and open/fist/open timeline, individual game/model classifications and intact DOM reparenting. Exact assembled HTML, JS syntax and package assets are checked in the release gate. Phone/Quest visual acceptance pending.
