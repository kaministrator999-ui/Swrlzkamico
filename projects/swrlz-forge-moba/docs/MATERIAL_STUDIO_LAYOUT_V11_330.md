# Dedicated Material & Texture Studio — v11.330

Lifecycle: IMPLEMENTATION_APPROVED; SOURCE_VERIFIED; BROWSER_VERIFIED; SOURCE_PUBLISHED; FEATURE_DEPLOYED; HOSTED_ARTIFACT_VERIFIED. Owner-device visual/XR acceptance remains separate.

## Resulting behavior

Materials opens a dedicated, opaque texture-authoring workspace. Desktop reserves columns for the material library, native texture/painting surface and property inspector. Compact phones and portrait frames up to 1100 CSS pixels use Library, Preview & paint and Properties tabs. Their controls no longer float over the Game editor. A separate 3D scene mode deliberately reveals the existing native viewport and centers the existing material sample sphere within its preview area; no second renderer or animation loop is introduced.

Empty libraries hide unavailable properties instead of displaying blank fields, and offer a preset/create action. Opening Materials never creates an unsolicited material or replaces the current project. The original material selectors, authoring fields, canvas, brush controls, image/library inputs and action handlers are retained beneath the native panel. Original edit-event delegation and panel-relative queries remain intact. The original native title/layout controls are hidden at sufficient specificity; native diagnostics remain available in Tools & files.

While opaque Materials panels cover the native viewport, main-canvas draws pause outside XR; native ticks, material synchronization, history and Chat continue. Visible 3D preview, other studios and XR delegate to the existing native render predicate. Browser checks verify the actual render counter pauses and resumes.

The visible 3D preview passes pointer input to the native viewport while its surrounding controls remain interactive. Unmodified key events stay within the Materials panel; native modified shortcuts remain available and covered Game controls leave focus navigation.

All material changes still use the native validated material schema, history, texture cache, PBR assignment and project serialization. Projects and Save project delegate to the existing dialogs. Default texture mode hides unrelated game chrome; scene mode intentionally previews the current game scene and selected sample. Game, Modeling and Particle studio navigation, the saved mage and account state are outside this release's editing scope.

## Source lineage and exact integrity

Integrated on canonical owner source/request `4bfa539d`, preserving v11.321 house sightlines, crowded-Quest budgeting/diagnostics, every earlier registered patch and v11.320 studio navigation/routing. Materials appends patch **343**; no historical patch is rewritten. The dedicated deploy workflow points at `verify_v11_330_release.py`; runtime title, build identity, provenance, marker, source manifest and current documentation identify v11.330.

Full ordered reconstruction from the checksum-gated original payload measures **8,484,905 bytes** of HTML, SHA-256 **`aa783d286c545bdeb13ea654f171e0915ab70ec975ab4a9e0c51f93649019ac9`**. Index and Modeler are identical. Strict packaging validates **71 assets / 75 files**, including every asset's bytes/hash and the generated SOURCE receipt. No integrity check is waived. Private previews and account fixtures are not packaged.

## Bounded verification

Strict source packaging and inline JavaScript parsing pass, along with native material preset/validation/painting/assignment/restoration/texture/history checks, the preserved v11.320 studio-routing VM and the owner v11.321 sightline/Quest diagnostic VM. No unrelated 22-case game suite is dispatched.

The fresh-profile browser check passes native empty/create/select/edit, legal roughness input, assignment and restoration, pointer painting and brush undo, actual 256×256 PNG download and file-chooser image import, duplicate/delete, JSON library download and file-chooser import, and native project serialization. Focused-library Delete leaves scene actors and material definitions unchanged. Two complete Game → Modeling → Particle → Materials round trips preserve the scene and material library with one Material panel and one Game tab rail. Desktop 1440×1000, touch phone 390×844 and touch portrait iframe 980×1800 checks cover visible/hit-tested panel and preview controls, page bounds, paint-surface size and the existing 3D sample's visibility/centering. The run finishes with zero page errors.

```sh
python projects/swrlz-forge-moba/scripts/verify_v11_330_release.py --output dist/swrlz-forge-moba
python projects/swrlz-forge-moba/scripts/check_material_studio_v11_330.py --html dist/swrlz-forge-moba/index.html --output /tmp/swrlz-material330-check
```

The portable browser check requires Playwright/Chromium, an isolated guest profile, local sealed HTML at the canonical app origin and verified-TLS CDN/guest Chat requests. It never reuses an account session or mutates a cloud save. Browser/source checks do not establish physical-phone/Quest appearance or XR acceptance.

## Publication

- Published source: [`244e1d9146dd6ed8dd4147604eba4965007d5fac`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/244e1d9146dd6ed8dd4147604eba4965007d5fac).
- Separate request-only commit: [`6db015cd324f20e9d93f7f07e6ebcb81fc3b31be`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/6db015cd324f20e9d93f7f07e6ebcb81fc3b31be); comparison with the source is exactly one commit and only `DEPLOY_REQUEST.json`.
- Dedicated deployment [run 42365572126](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42365572126): **SUCCESS**. No unrelated game verification workflow was dispatched.
- Hugging Face revision **`30babc193eae715c3942308b89279d95f8062529`**: **RUNNING**; its official revision-pinned SOURCE receipt identifies v11.330 / 343 patches / 71 assets.
- Independently streamed official `index.html` and `modeler.html`: each **8,484,905 bytes**, SHA-256 **`aa783d286c545bdeb13ea654f171e0915ab70ec975ab4a9e0c51f93649019ac9`**. Both match the canonical reconstruction, strict local package and browser-tested HTML.

Live engine: https://huggingface.co/spaces/kamiloki/swrlz-forge-moba . Hosted artifacts and browser/source checks are complete; physical-device appearance and XR acceptance remain owner testing. This documentation-only closure does not alter runtime code, its manifest seal or the deployment request.
