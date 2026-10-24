# Qwen project generation and authorized HF publication

Mode: IMPLEMENT. State: FIRST_RELEASE_LIVE_VERIFIED / GENERIC_REQUEST_FOLLOW_UP_IN_PROGRESS. Owner explicitly clarified that Qwen must generate working projects, including HTML3D viewers; an engineer-built reference is not model acceptance. Owner explicitly authorized publishing all validated updates live. No additional deploy confirmation is required.

## Scope and authority

Continue accepted Chatv294 source `0c34ecf36bc0e8a1c64b03cd036060610cc70c32` with the previously verified local source-grounded candidate. Immutable r3 source/evidence package SHA256 `cdef7d3ee5960280ef40ef1dba2d8fbb5472cef556867c2072b3eabbf7343a02` remains historical. Preserve independent ongoing main Forge/§E work; the HF request can pin an exact new source commit rather than merging divergent accepted Chat into main. Existing HF Space `kamiloki/Swyrlz` and request→guarded workflow chain remain canonical.

Documentation Impact Set: programming architecture, Chat capabilities, source/checkpoint/roadmap, model and dependency provenance, validation, integration and deployment receipts. No new execution privilege, credentials, hosting service, editor or project store.

## Implementation

- Shared response cognition now distinguishes the leading create/build/code request from feature verbs such as inspect, analyze or compare. An explicitly requested HTML/software application remains a code deliverable when its subject is3D or music. Actual asset/audio/text requests preserve their medium. Corrections and source-analysis requests preserve their operation.
- Programming artifact classification recognizes HTML viewers/applications/dashboards/calculators/games as web pages. The prior classifier treated HTML model viewers as plain code and rejected embedded CSS/JavaScript as a language substitution; it also denied the web output allowance. Explicit strict-language constraints remain authoritative.
- Both model engines receive bounded version-scoped public library facts for an explicitly requested Three.js dependency. Facts derive from verified official Three0.160.0 npm package bytes, independently matched to the jsDelivr core module. They cover module/import availability and documented API boundaries, not a complete viewer template or an expected patch. Different explicitly requested versions do not receive these facts. Original user/project constraints outrank facts; no runtime fetch or executed test is claimed by local evidence injection. The same facts survive compact repair-context construction.
- Plain requested behaviors beginning with Create/Show/Use/Wire/etc now enter the persistent MUST contract; previously these were dropped in favor of a generic fallback. Fenced source remains excluded from natural-language requirement extraction.
- Structured repair receipts preserve nested expected/actual measurements. Passing case names no longer contaminate failure categories/dependency diagnoses; passing observations stay in the behavior ledger without being counted as failed nested tests. A successful transport wrapper does not hide failed child cases. This was reproduced from the actual layout-repair receipt and covered by4 focused regressions.
- A single lightweight coder configuration now owns loader selection, catalogue identity and probe label. The candidate selects official Qwen2.5-Coder7B Q4_K_M, pinned revision `13fb94bfda8c8cf22497dc57b78f391a9acb426a`, SHA256 `509287f78cb4d4cf6b3843734733b914b2c158e43e22a7f4bf5e963800894d3c`. Known variants verify byte length and checksum before native loading. Explicit custom configurations retain prior behavior without a false official-pin claim.7B is selected on measured viewer quality; smaller3B still omitted required features. Normal700M conversation remains unchanged. CPU latency is materially higher and live acceptance is still pending.
- Candidate CI includes the new integration branch pattern and cognition/web regression checks. No deploy trigger has been used as an access experiment.

## Real model evaluation

CPU-only actual GGUF weights/tokenizers, llama-cpp-python0.3.35, exact official artifact pins and fixed seed42. Direct real Qwen engine route, not model doubles or a handcrafted passing candidate. The model sees the original feature request and, when applicable, verified library API facts; evaluator source/expected implementations and the hand-built sandbox reference are never model inputs.

The current task asks for a single-file HTML viewer with an initial cube, drag orbit, wheel zoom, working wireframe checkbox, responsive sizing and an import map pinned to Three0.160.0. This is a normal library-based viewer task. Earlier forced-offline own-projection failures are retained but are a stronger and different task.

- Before fixes:3B generated three drafts; the local language gate rejected CSS/JS in the HTML viewer. No accepted artifact was emitted (192.2s).
- After cognition/artifact fixes:3B emitted an HTML candidate (89.2s) but called a nonexistent geometry API; isolated browser execution failed.7B rendered actual geometry with a correct import map (183.3s) but omitted orbit/zoom and had inconsistent initial wireframe state.
- A separate driver-only checklist experiment produced the right feature list but3B still emitted invalid API usage and omitted requested controls. That experiment is NOT integrated or represented as a quality improvement.
-7B same-thread repair was given actual independent failing interactions and the original source/history. It added an invalid namespace OrbitControls call; no success is claimed.
- With library evidence,3B corrected some API usage but still omitted the import map/control requirements.7B generated a real working WebGL viewer with orbit, zoom, wireframe and correct dependency imports:8/9 independent checks, with mobile overflow remaining. The actual generated source was not edited by the engineer. A final7B layout-only repair uses its exact history plus the independent failing viewport receipt and passing8-case list; the second attempt fixed viewport overflow and passed all9 original WebGL checks (408.7s including a rejected unchanged first draft). A separate source review found that the checkbox became overflow-clipped below the canvas; an additional reachability check records9/10 and the subsequent model-only UI repair passed10/10, as recorded in final acceptance below. The9-case PASS is not represented as complete UI acceptance.

The independent browser evaluator runs only within Bubblewrap: cleared environment, no credentials/host checkout or outside network, resource limits, read-only synthetic source/software. It uses real Chromium SwiftShader WebGL, verified by clear/readPixels with glError0. CDN URLs are fulfilled with exact pinned official module bytes; candidate HTML is unchanged. Causal interaction tests use identical seeded randomness and an explicit equal-frame RAF scheduler; automatic animation cannot count as drag/zoom. The earlier clock-based viewer harness produced a false drag attribution and is historical, superseded by the equal-frame method. Async resize is allowed to deliver its real event before measuring. Source review remains separate from a syntax/shape PASS.

These are development/regression tasks, not a statistically held-out benchmark or evidence of universal project competence. API evidence is runtime grounding, not fine-tuning. No training success or new model size is claimed before validation.

## Verification, integration and release evidence

72 focused tests +88 subtests and19 HF candidate checks pass for the current candidate. Nine adjacent scripts plus the repair/ledger regressions pass. GitHub candidate validation runs40126954168 and40127574003 completed SUCCESS for exact sources0b0165df and294a96f0; the final receipt-scope revision requires its own CI before publication. Existing source/approval/truth gates remain authoritative. Runtime module versions will be reconciled with freshly read canonical `runtime:VERSION.txt`; no version is silently allocated from stale history.

Sandbox baseline/reference updates were published at `310ce70` on Swrlzing-core main after their independent16/24 browser checks. They remain engineer-built fixtures, not proof of Qwen generation.

Initial publication status: PENDING (historical; superseded by final acceptance below). Source SHA, guarded workflow run, rollback Space revision, deployed Space revision and live behavior will be recorded from actual results. An upload or green workflow alone is not model-quality acceptance.

## Guarded publication request

Owner authorized live publication. Exact candidate source `0e361f97d9b0ec72a63581dc06ac22c610a11f1f`; CI run 40128272787 completed SUCCESS. This request starts the canonical HF workflow; upload/build/runtime acceptance remain pending and will be recorded separately.

## Observed live release — final acceptance

Guarded deploy run [40128464710](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40128464710) completed SUCCESS. Space is RUNNING at `a390838d5da21354c702573666bfb432b59e3a91`, with MODEL_PROVENANCE binding exact source `0e361f97d9b0ec72a63581dc06ac22c610a11f1f`. Previous Space revision `ffc9d264e3ae7f9df8edca5cc878fd2c8587f9fc` remains the rollback reference. The live catalogue names pinned Qwen7B.

Fresh anonymous700M inference completed in9.8s. A fresh live viewer request entered as model700m, automatically routed to coder, and completed in79.4s. Its unmodified generated HTML passed all10 independent isolated WebGL/browser checks, including visible geometry, import map, real drag/zoom, wireframe, mobile sizing, reachable control, dependency loads and no browser errors. This is first-request live success for this explicit task; the earlier native development sequence required repair and remains historical. No engineer-written viewer was substituted. Local final repair also passed10/10 with JavaScript preserved during the UI correction.

Canonical runtime registry updated after observed publication: Repository Work1.0.239, Server2.3.440, LALM2.1.202. Web Chat1.5.157, streamV2, manifest152 and deployment-control1.0.41 remain unchanged. Registry commit `6788c54b6117ddfab68c52b1ebfe439d711d9eea`. Source archive SHA256 `3c7930270cf07749ec80456602764f8db85dc9089ed883a46314041fe41fb53d`; its pending observations are historical and supplemented by this release receipt.

Disposition: source/integration/build/live-model evidence recorded. This verifies one concrete coding task and iterative repair capability, not universal project competence or trained-weight improvement. Signed-in Google/GitHub provider acceptance and existing Stage-1 write restrictions remain separate. No passwords or verification codes were used.

## Generic request follow-up, 2026-10-24

The original goal includes ordinary wording such as “create a3D HTML viewer,” without naming a library/version. For a fresh standalone3Dweb request with no chosen stack, the Brain can now supply the same bounded optional verified library reference. Explicit offline/no-library/raw-WebGL/other-framework constraints prevent that inference. A repair retains the facts when its canonical source confirms the pinned module. Plain numerical “three buttons” no longer falsely selects the Three library. No project template or expected code is supplied.

This is a bounded inference-activation correction to the already live7B backend. First release/source0e361f97 and its10/10 live acceptance remain historical valid evidence. Follow-up CI, exact source publication, generic prompt and final version receipt are pending.

## Standalone module-resolution repair — same generic-request follow-up

The plain-wording probe after sourcea7003aa9 completed model generation, but browser execution failed resolving the bare `three` import used by the pinned OrbitControls module. Only initial checks executed; this is NOT a10-case failure score or accepted viewer. The earlier explicitly pinned task's10/10 remains valid history.

The Brain now checks standalone browser module declarations before delivery: direct bare imports require an import-map mapping, and verified external module facts expose transitive bare dependencies. Prefix/scoped maps and HTML-relative module script URLs are supported. Comments, strings, templates and regex-like literals are not treated as import statements. Declared bundler/repository contexts remain separate. This bounded source check does not fetch dependencies, execute JavaScript, prove full syntax or grade unknown library internals. Its receipt remains `executionVerified=false`.

Both model engines now receive the actual bounded source-rejection reasons on retries. Retry token allowances are recomputed against the actual context without silently discarding source; insufficient retry context fails closed. No missing import map or project source is inserted by the engineer: Qwen must produce a new complete candidate. A real prior broken live output is rejected by this gate. Six regressions cover direct/transitive imports, scoped/prefix maps, literal/comment preservation, build contexts and actual reason delivery to both engine retry prompts.80focused tests+97subtests and19HFcandidate checks pass. Final generic live browser acceptance remains pending this source repair and guarded publication.
