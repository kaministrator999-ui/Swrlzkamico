# §E v11.466 · Ring and arc modeling candidate

Status: feature-branch implementation candidate, not a published release. Owner mobile/VR acceptance is pending. Source commits alone are not deployment evidence.

## Native controls
In Vertex mode select exactly one vertex, open **Ring / arc modeling**, and choose **Use selected vertex as center**. Grow the connected selection by edge rows, selecting either the exact outer ring (Outline) or the filled radius (Fill). Restrict the result to a configurable angular arc in XZ, XY or YZ. Use the 180°/360° presets or specify angles. Native vertex IDs, not decorative overlays, are selected.

A selected ring or arc can be moved in X/Y/Z, uniformly scaled or scaled asymmetrically left/right, tilted about X/Y/Z, with optional connected-row falloff. Preview uses the existing native workshop transaction; Apply commits one Undo step; Cancel discards the preview.

**Subdivide selected edges** adds actual midpoint vertices and retriangulates every incident face consistently, with UV interpolation. It does not promise quad loop cuts.

**Preview boundary extrusion** extends one complete open boundary loop. Interior closed-mesh crown sections should use Face Select → Inset → Extrude. Open arcs cannot be blindly extruded into manifold geometry and are rejected.

Face extrusion now supports signed depths up to 30 local units, subject to source bounds and clearance. The existing Face Extrude Preview reads scale, left/right scale, offset and tilt parameters. For collision safety, these shape modifiers are rejected on negative/inward face extrusions pending a stronger solver.

## Important limitations
- Graph radius means connected edge-hop rows, not an exact Euclidean circle; triangulation affects shape.
- Angles use a selected Cartesian plane, not draggable viewport arc handles.
- Boundary extrusion supports one connected open loop, not arbitrary interior loop bridging.
- Triangle edge subdivision exists; general quad loop cut, edge-loop dissolve and simplification do not.
- Full VR-controller parity has not been established; physical Moto/Quest acceptance is pending.
- Structural topology validation is not a complete self-intersection solver.

## Verification
Unit test: node projects/swrlz-forge-moba/tests/model_ring_kernel_v11_466.mjs
Prepare measured build: python projects/swrlz-forge-moba/scripts/prepare_v11_466_release.py
Verify sealed build: python projects/swrlz-forge-moba/scripts/verify_v11_466_release.py --output /tmp/se466-verified

The focused GitHub Actions workflow also checks source assembly, inline JavaScript syntax, SHA-256 integrity and bundled assets. Do not deploy unless source manifest, built artifact, deployment workflow version, and standalone DEPLOY_REQUEST.json commit identify exactly the same validated source.
