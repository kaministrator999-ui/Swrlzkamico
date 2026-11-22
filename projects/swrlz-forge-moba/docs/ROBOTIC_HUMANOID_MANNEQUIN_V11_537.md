# §E v11.537 — Robotic Humanoid Mannequin

## Delivered starter

Projects → Starter Models → Robotic Humanoid Mannequin. The robotic-humanoid-mannequin route creates a fresh, editable native Model Atelier project directly from original procedural topology. Direct entry is also supported by the ?project=robotic-humanoid-mannequin URL parameter.

This is a neutral-gray, untextured, mechanically segmented humanoid in a symmetrical horizontal T-pose, developed as a foundation for later character modeling and rigging. All visible detail is geometric, not an image plane, external 3D asset or texture map.

## Anatomy and mechanical surfaces

- Head: skull and jaw taper, facial mask, modeled orbital housings and lenses, brows, cheek structures, mouth seam, ears and neck collars.
- Torso: pectoral planes, individual abdominal plates, serratus and oblique transitions, clavicles, scapulae, sternum and pelvis structures.
- Arms: shoulder bearings and deltoids, biceps and triceps, elbow swivels, forearms and wrist couplings, palms, four fingers with three geometric phalanges each and opposable thumbs.
- Legs: iliac and hip volumes, quad and hamstring contours, patella and knee bearing, calf and shin profiles, ankles, shaped feet and five toes per foot.

The starter uses separately named and indexed native topologyMesh sections with UV coordinates (a geometry compatibility field, not a painted texture) and nondestructive edit groups. No proprietary geometry or external textures are used.

## Scope and limitations

This modeling starter is not yet skinned to a skeleton, has no animation clips and does not imply automatic humanoid retargeting. The separate surfaces are intentionally visible at mechanical joint locations.

## Validation

Automated checks: tests/robotic_humanoid_mannequin_v11_537.cjs validates mesh limits, proportions, T-pose bilateral reach, hand details, grouping and native open. scripts/verify_v11_537_release.py verifies the rebuilt source HTML. scripts/package_static_delivery_v11_537.py checks served JS packaging. Native generator: runtime/robotic_humanoid_mannequin_v11_537.js.

Physical Moto and Quest visual quality, editing ergonomics and performance remain owner acceptance tests; automated topology checks do not establish those results.
