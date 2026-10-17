# v11.18 · leg profile and supplied close-up correction

The supplied phone profile exposed a real knee-centerline error: a short segment reversed depth before the shin. The new native starter reshapes both continuous leg splines into a gradual hip–knee–ankle line and replaces the misplaced lower-leg bulge with a shaped posterior calf. Both ankle endpoints and the complete sock/shoe/heel/sole assemblies retain their previous positions. Six control knots remain compatible with native grounded pose presets.

The additional portrait reference guides a narrower cheek/chin silhouette, smaller almond eyes and catchlights, warm brown/amber irises, finer lashes and lip contours, and broader staggered cyan/coral fringe locks. A dense grooved split-dye crown replaces the coarse crown. The dark pigtail pieces now have genuine ring openings and thin folded ends. The neckline, fitted black collar with coral piping, and coral–cyan–coral forearm bands use independently editable native splines.

Posterior calf fullness and front shin taper now shape the actual leg vertices, with slightly staggered medial/lateral calf heads and a smooth Achilles taper. The upper leg, knee ring and ankle attachment remain unchanged by this contour pass. Saved native **Leg anatomy** controls support Apply, Undo, validated import, density presets and grounded poses.

Reusable native controls add **Swept split-dye crown**, **Knotted hair wrap** and two saved **Iris pigments**. Pigments participate in Apply, whole-model Undo, validated JSON import and generated vertex colors. Unannotated historical irises retain their original palette. Crown and wrap sampling changes real generated topology and is restored by the HD preset. Existing styles remain available.

Authoring uses `authoring/festival_reference_authoring_v11_18.mjs` to operate the actual editor. It saves model JSON, validates exact reimport, and exports the scene used by the packaged starter. Repeating the recipe on the completed starter must reproduce the same model exactly. A smaller viewport is used during editing; review screenshots use the full desktop viewport, followed by phone front/profile views and a real clean 2K portrait render.

The release appends one patch and one runtime module. All **175 predecessor patch/runtime files and 40 packaged assets** are byte-preserved. The package contains **88 ordered patches and 41 assets**. The exact generated source bytes and SHA-256 are in `source-manifest.json`; source/deploy commit authority is the final `DEPLOY_REQUEST.json` and its dedicated deployment run.

Checks cover the reported centerline kink, monotonic leg height, posterior calf placement, restrained anterior shin, Achilles taper, ankle/foot preservation, finite geometry and normals, actual crown relief, open wrap topology, effective sampling, saved iris colors and historical defaults. Desktop/phone editor acceptance also checks native pigment Apply/Undo, atomic invalid imports and grounded-pose return to the authored neutral legs. All 18 compatibility suites and both viewports remain required.

Publication requires validated merge, the final dedicated deploy request, terminal deployment success, exact hosted HTML/SOURCE/all-assets audit and hosted desktop/phone editor acceptance. Visual review uses the saved multiview images; this update does not assert an exact game-asset reproduction.

Measured native starter: **283 editable meshes; 1,623,252 triangles in the set; 1,339,364 in the heroine; 48,768 in the continuous head**. Native authoring/review records 77 operations. Final HTML: **2,594,314 bytes**, SHA-256 `82f833c7a7771d167e582f381b655e01b5a63e5f6d50a3abb5e2f604467b234b`. [Native receipt](LEG_REFERENCE_NATIVE_EVIDENCE_V11_18.json).

Fabric-panel curvature/fold controls are now available for the coral and ivory panels. Both bodice trim splines are fitted to actual cloth vertices with fine radii, and the coral band uses restrained curvature.
