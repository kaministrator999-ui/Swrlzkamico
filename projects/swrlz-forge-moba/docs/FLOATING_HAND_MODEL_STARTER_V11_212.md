# Floating Hand · Arcane Glove — native §E Model Atelier v11.212

## Request and source of truth
The owner supplied a multi-view purple/black floating glove concept and requested a new **starter project model** in §E, not another image. This is an original geometric interpretation of that reference.

Native code: runtime/model_atelier_floating_hand_v11_212.js.
Append-only integration: patches/v11_212_floating_hand_model_starter.py.
Source lineage: source-manifest.json; verifier: scripts/verify_v11_212_release.py.
Direct link: modeler.html?project=floating-hand-glove (also engine ?project=).
Projects card: **Floating Hand · Arcane Glove**.
The existing default-project checkbox discovers this card automatically. Its selection is opt-in and never replaces other defaults silently.

## Geometry and editable assemblies
- A native indexed topologyMesh gloved hand including wrist, palm, all four fingers and a separate tapered thumb is produced from the existing Model Atelier organic surface/welding helpers on first load.
- A dark sleeve, silver cuff bands, violet floating loops, silver knuckle studs and individual dorsal finger armor are distinct, selectable, editable meshes.
- Purple emissive fingertip/knuckle traces, a two-sided geometric hand crest and palm medallion add stylized magic without downloading textures.
- Native swyrl-model-atelier-v1 parts use stable IDs, standard colors/materials, topology arrays/UVs and mesh group metadata. The normal model editor can edit/sculpt/save them. Prior projects are not modified.
- Generated geometry is cached on first load and cloned for later starter opens; user project edits remain independent.

## Technical boundaries
The open palm is the **only** supplied pose. It is not yet bone-rigged, weight-painted, animated or tied to live Quest hand tracking. The reference sheet's PBR maps are visual targets, not imported material images. Current native materials approximate its metallic/emissive surfaces. Skeleton, skinned pose animation, actual PBR texture baking and live hand tracking remain separate tasks.

## Source integrity (sealed candidate)
- Source: §wyrl§ Engine v11.212
- Ordered patches: 244
- Packaged assets: 68 (no separate fetched texture assets)
- Generated HTML bytes: 7,478,674
- SHA-256: add8a1718f8d06a1ef178bf4adaa55e12ae38f9d33be1404396637c32ebfa92f
- Exact receipt was computed by a targeted GitHub Actions source-build job.
- Strict sealed-source check and Hugging Face deploy are separate gates; only a confirmed hosted release should be called live.

Owner will test the model's rendering and manipulation on phone and Quest 2. No broad VR or Sheep Tag browser suite is needed for this model-only addition.
