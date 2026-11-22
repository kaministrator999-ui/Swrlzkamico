# §E v11.534 in-place mesh reshape for §Chat

The §Chat mesh bridge can reshape one existing plain primitive or loft in a durable Model Atelier project. It reuses the native shape validator and edit journal. A successful edit retains the part ID, name, transform, material, group membership and assembly references. The live representation is rebuilt from the resulting native part, and the exact account project carries the edit and its Undo history.

An eligible edit workspace advertises `meshShapeEdit` with schema `swrlz-forge-mesh-shape-edit-v1`, the supported kinds, and the eligible part IDs from the final sampled context. The shape kinds are sphere, box, cone, cylinder and loft. A single `mesh.reshape` names an eligible ID and desired kind. Loft also requires path, radii and segments, validated through the existing native loft contract. The paired §Chat bridge requires one exact preview approval and the existing lease and snapshot checks. The host rechecks the shape fields and eligibility at execution. Geometry-only changes advance the durable editor epoch. Identical geometry produces a no-change receipt and adds no journal entry.

Eligibility is limited to plain geometry descriptors. Meshes with topology, sculpt history, painted UVs or other authored surface metadata are protected. Pose and rig data, scratch drafts, and active native gestures are guarded. The ordinary native renderer, edit journal and account transport handle the approved operation.

## Verification and publication

Source candidate built from 511 ordered patches with 78 packaged assets. The sealed HTML is 11,001,625 bytes with SHA-256 `3b084f548df7aa9b241edab7891dac534ced262e8b707de73dad681832042557`. The focused source harness exercises the composed native batch, geometry validation, part identity and references, sampled context, epoch, Undo and Redo, restored history, stale and replayed batches, and protected targets. The release verifier also runs the predecessor account save, account open, revision cache and journal regressions.

Static delivery keeps each entry below 10,000,000 bytes. The shared HTML entry is 682,469 bytes with SHA-256 `02f0d73e52b3ea1c1a71ad5085f596fb6d949e524b50749b76739e5044a56881`. The versioned module is 9,485,137 bytes with SHA-256 `7f39ca82cfe9df8ef5ab8abccc10f65b00787c6e38cd65ee3df0ea42a9901b92`. Its JavaScript syntax check passed.

Publication follows the existing GitHub → Hugging Face Engine request. Compatible §Chat planning and an authorized production modeling pass are separate acceptance gates. The source tests use synthetic project records and controlled transport.
