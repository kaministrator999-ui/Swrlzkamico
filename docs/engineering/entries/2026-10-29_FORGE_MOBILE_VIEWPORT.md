# §E mobile editor viewport repair

Mode: IMPLEMENT. Lifecycle: IMPLEMENTATION_VERIFIED / DOCUMENTATION_SYNCED. Status: exact successor source verified; publication pending.

The owner supplied normal Android browser screenshots of §E compressed into the
upper part of the screen, overlapping level/selection/keyboard overlays and a
large empty lower workspace. The same device renders the canvas at full height
in desktop mode. Initial unstyled Hugging Face page chrome is separate observed
host-page loading evidence, not an established editor JavaScript failure.

Baseline: main ad4e71d331e717c5153d4544c11115d79c7d279f, §E v11.169,201 patches,
6,995,807 bytes/SHA2561c484cf4f627a87c95d720d11fabfe1fb9005f114c2a7712b67f7474222a3d84.
Published static Space6fdc0351b04c6b27a5f65b6c4402dfb259b61a72, successful
Actions40931411290. Existing integration remains published; owner mobile editor
layout acceptance is REPAIR_REQUIRED. Google/private-store/device acceptance
not exercised by these screenshots remains pending. Previous source ZIPs and
release handoff are immutable and retained.

Confirmed cause: original max-width620px layout uses block .workspace and
absolutely stretched main.viewport-wrap. v11.143 forced position:relative!important
for native canvas overlays; on mobile this collapses main to the canvas intrinsic
aspect height. Actual default Dragon Den Chromium reproduced canvas191.55px in a
650px workspace at390x740,205.23px in825px at412x915. Desktop layout fills normally.
The earlier integration tests verified native actions and Chat panel geometry,
without asserting the underlying mobile canvas fills its workspace; this gap is
now covered explicitly.

Bounded goal: restore native mobile canvas fill, move mobile inspector/outliner
controls below actual level controls, remove desktop-only/stale viewport hints
on narrow screens and keep Chat controls clear of HF branding. Preserve existing
scene/renderer/gameplay, native actions and independent Chat backend. No model,
account or provider authorization change. Append one §E patch/version; use the
existing package/upload lane with separate final request-only main commit.

Documentation impact: checkpoint, root Roadmap event, §E README/Space README/
Roadmap/Start, source manifest/runtime identity/release verifier, source package,
workflow/runtime evidence and updated owner-device disposition. Tests are focused
on native viewport/layout and adjacent Chat/native controls; no broad game suite.

Next gate: bounded repair, real Chromium default/blank/project/resize/mobile and
desktop verification, exact package seal, source overlay/checksum and authorized
publication. Approval waiting: NOT APPLICABLE within existing publication scope.

## Concurrent-source reconciliation and final candidate

Fresh main advanced to 4b1b1c7c6882a8defe1367edc5ed6758e2c44aab while local repair was active. Preserve the owner's v11.170 My Projects, v11.171/173 modal layering and v11.172 clean Chat header. The local unpublished mobile v11.170 candidate is historical, not a promoted duplicate version. This repair is appended as **v11.174**,206 ordered patches,68 assets. Exact rebuilt HTML **7,008,228 bytes / SHA2561254e78c5bfd0d55a940f0e7d7c5fd590c325f89d4a45dc893b54f0f76fb9ce4**. Current repository authority is1.0.244; Chat/Server/LALM/account modules unchanged.

Repair-cycle evidence retained: first local geometry fix exposed the open inspector drawer covering its own toggle; measure the drawer below both toolbar and tab row and keep tabs actionable. Next candidate exposed the stats pill being a global app child, not a viewport child; narrow-screen selector now targets its actual owner. Final mobile tests use actual pointer clicks and touch taps, not synthetic dispatch. A first successor verifier attempt rejected a stale finalArtifact filename before any upload; corrected to swyrl_engine_v11_174.html with the measured source seal unchanged. No failed attempt is labeled success.

## Final bounded verification

Exact v11.174 source package verifier PASS:206 patches,68 local assets verified by bytes/hash, complete generated receipt and deploy markers. Real Chromium final matrix PASS: canvas650/650 at390×740,825/825 at412×915 and1732/1732 at980×1850; default Dragon Den, blank Model Atelier and returned scene, both landscape resizes. Real Inspector clicks and touch taps open/close, native fullscreen CSS remains fixed and fills the viewport, Chat begins at48px and closes normally. No page errors. One concurrent software-rendered touch run timed out during dispatch at5seconds after actionability checks, with no intercepted hit target; serial rerun with15second touch dispatch timeout passes. Failure receipt retained. Adjacent Chat/native desktop/mobile tests PASS on the same1254e78c… artifact, including literal labels, real native edits/Undo/Redo, closed-host denial and account-change metadata clearing.

Receipts: mobile-v174-layout-r2.json and mobile-v174-chat-native.json under cloud-setup/eval. These are controlled native Chromium checks with transport fixtures, not real Google/private-store/device acceptance. No broad game or hosted browser suites were dispatched. Documentation gate PASS: manifest/runtime/patch/source verifier/dedicated workflow and affected living docs agree. Canonical immutable overlay/checksum and actual publication observation follow in the release closure.
