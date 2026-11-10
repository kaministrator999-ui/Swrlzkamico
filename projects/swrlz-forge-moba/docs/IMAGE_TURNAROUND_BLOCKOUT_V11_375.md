# §E v11.375 — Integrated §C image-to-editable 3D blockout

## Purpose and source of truth

Inside an **independent Blank 3D model** project, open the existing integrated **§ Chat** panel and expand **Image → editable 3D blockout**. Upload a PNG/JPEG/WebP sheet (up to 12 MB) containing labeled front, left, right, back and overhead views in that order. The five adjustable guides indicate the source regions. Choose **Build rough 3D in viewport** to create native, editable parts.

This is an experimental local **silhouette blockout**—not AI-generated topology, depth-accurate photogrammetry, full facial reconstruction, or automatic UV/material projection. No claim is made that the §C vision model inferred a mesh. Pixel classification is performed in the browser; the image itself is not uploaded to a modeling backend or saved to the project by this feature.

## Native editing and safety

- Front and back contribute silhouette width; both profiles contribute apparent depth; the top panel provides a bounded upper-silhouette cue.
- Geometry is stored as separate native loft parts with approximate colors sampled from the actual reference; an opt-in side-prop detector may create a separate editable narrow shape.
- The tool uses **ModelAtelier.chatAction** to add meshes through the existing validation/checkpoint/render/Undo pathway. No alternate renderer, scene data type, native mesh execute permission, or untrusted executable model code is introduced.
- A canonical blank starter is cloned using the existing project clone machinery before any geometry is modified. Projects with existing authored meshes are rejected, not silently replaced. The one blank seed may be removed only after real geometry has been created.
- Generated native model geometry is saved locally using the existing owner project library. Use the current project Save/Clone or Save to Account controls for durable storage and syncing. The reference image pixels are not persisted by this feature.
- If a step fails, previous successful native actions remain; the user sees a failure message and can inspect the mesh, undo, or create a new blank copy.

## Verification

Source sealing uses the append-only v11.375 patch and exact final HTML SHA in source-manifest.json. The synthetic image acceptance exercises five view sampling, valid native loft parameters, optional prop extraction, guide rejection and a blank-project safety check. Node syntax plus the full source-release validator must pass before the separate deploy request. Visual similarity and device performance still require owner testing with real images and Quest/Android.

## Next engineering iteration

Owner-selected view crop adjustments, selective part refinement, semantic source-to-part correspondence, texture projection/UV, and exact scale inference are future work—not silently simulated by the current tool.