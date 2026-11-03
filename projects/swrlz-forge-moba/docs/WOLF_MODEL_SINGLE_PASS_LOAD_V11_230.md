# §E v11.230 — Astra Wolf Model one-pass loading repair

## Confirmed source-level fault
The real Wolf Model loader is the v11.88 `loadAnimalProject = async function` override, whose wolf asset was subsequently updated to the v11.90 furred Astra. v11.227 added wolf rig/clips to an older v11.87 loader branch instead; those writes were bypassed by the live override. Its public wrapper compensated by closing and reopening the very detailed wolf model after the first render to install the rig. That doubled initial WebGL mesh construction and could make phone starter loading fail or appear stuck.

## Fix
- Add 14-bone `wolfRig`, ten authored `wolfAnimations` clips and existing native facial details to the **active** project after `loadProject()`, before its **first** `ModelAtelier.open()`.
- Make the public `loadAnimal('wolf')` wrapper audit the already-loaded model instead of closing/reopening the workbench.
- Open in editable mode with the Wolf Rig & Motion panel visible. Keep the original furred Astra, sheep game wolves, all other starter projects, saved user scenes and gameplay authority unchanged.

## Verification
- v11.230 builds from 262 ordered source patches to **7,712,134 HTML bytes**, SHA-256 `f22f0ab28b072d6a60498ea82111e62212f2ffd71ba05a175a80a3750e689ac5`.
- The build's initial auxiliary workflow check overcounted a separate `ModelAtelier.open()` accessor within the same module. This was a test-scope issue, not a compilation failure. The updated verifier checks the active wolf setup and public wrapper separately.
- Real Android/Quest display, actual 3D skinning and clip playback remain for owner acceptance. No claim of hardware acceptance before the owner's test.
