# Plain Chat loft surface normals — v11.295 candidate

Lifecycle: IMPLEMENTATION_APPROVED; SOURCE_VERIFIED. Full reconstruction and
bounded package verification passed. Publication and owner-device visual
acceptance remain separate.

## Observed problem

The §c-driven Little Crystal Mage saved ivory hair as `#f4ece0` / `silk`, but
its curved strands rendered dark cyan while the sphere hair cap retained ivory.
Read-only inspection found that the legacy `atelierOrganicLoft` emits outward
radial vertex normals with triangle winding in the opposite direction. The
existing courier wrapper already corrects textured lofts, but plain Chat lofts
do not enter that path. Double-sided shading therefore flips their supplied
normals toward the strong cyan rear light.

Real Three.js 0.169 checks of the saved staff, braids, fringe and smile reproduced
opposed face and supplied-normal directions. This is a surface-orientation
repair; the saved color fields were not missing or recolored.

## Bounded implementation

Patch `v11_295_chat_loft_surface_normals.py` appends after canonical v11.294,
which fixed the Hooded Vanguard's inherited socket graph. The runtime wraps the
existing geometry factory and reverses triangle winding, then recomputes vertex
normals, only for plain `loft` parts with an `atelier-chat-` ID. Existing
`textureBinding`, `hdFinish`, `surfaceStyle` and `organicSurface` rendering paths
are excluded. Historical non-Chat lofts and other geometry kinds retain their
existing path, avoiding a second reversal of the textured correction.

Positions, UVs, vertex colors, model descriptors, palette, transforms, native
history and saved-project bytes are preserved. Existing saved Chat lofts receive
the corrected derived geometry when viewed/exported by this engine build. No
new renderer, animation callback, model preset, inference route or account
permission is introduced. Actual character construction remains through §c.

## Source and verification

The predecessor is canonical v11.294, 325 ordered patches, 8,261,794 HTML bytes,
SHA-256 `39088e9ae2b215246515f3e3601f0b001ed2436ab0d1e7d1d7f7f70bbfbab7fd`.
This candidate is patch 326. Its full manifest-dependent reconstruction measured
8,263,130 HTML bytes, SHA-256
`b993cd47e55d42ae32315c3ff536e6adc5a7ca6f743d4d9f9d8d458eb374e5c8`.
Strict source/package verification passed with `SEALED_SOURCE_VERIFIED`:
identical index/modeler HTML, all 71 asset bytes/hashes, and exactly 75 expected
package files with no temporary test dependency in the HF output. Assembled
JavaScript parsing passed (three scripts, shaderScriptChars=7812149); the native
character-tool and real-Three loft checks passed. The official pinned-download
path also passed independently. This does not assert a deployed or
owner-accepted release.

Verification command (exit 0):

```sh
python projects/swrlz-forge-moba/scripts/verify_v11_295_release.py --output /workspace/scratch/swrlz-mage-v11-295 --three-module /workspace/scratch/loft-295-candidate/three-0.169.0-esm.mjs
```

Local evidence: `/workspace/scratch/engine-loft-295-verify.log`. The live
integration owner retains publication and the final request-only commit.

`tests/chat_loft_surface_normals_v11_295.mjs` executes extracted assembled
organic/courier/repair code using the same Three.js revision 169 as the app.
It covers straight and curved-up paths and the saved 12-segment braid sampling,
outward triangle/normal agreement, repeated geometry construction, unchanged
positions/UVs/colors and part properties, and exclusions for textured, styled,
organic, historical and non-loft parts. The verifier also retains the complete
v11.293 native character-tool checks, v11.294 loader anchor, one-render-loop and
JavaScript syntax checks, and validates the actual bytes/hash of all 71 bundled
assets plus identical index/modeler HTML.

The optional local Three test module must match the official app ESM exactly:
`https://cdn.jsdelivr.net/npm/three@0.169.0/+esm`, 684,391 bytes,
SHA-256 `260fdf7db2ecda0e726a82e37c829cdeb974015c9a4304ea9c51177b2c8b2c1a`.
Without a local module argument, verification downloads those exact pinned bytes
to a temporary directory outside the HF output and rejects any mismatch.

The dedicated deployment workflow references the new verifier. Its trigger and
other Chat/Core workflows are unchanged. `DEPLOY_REQUEST.json` deliberately
continues to identify the existing release until the integration owner publishes
the reviewed source and issues a separate request-only commit.
