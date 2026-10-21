# Chat v294 — Desktop first-conversation welcome card

**Date:** 2026-10-21
**Owner request:** Apply the approved centered glass-card PC mockup to real §wyrlz Chat code rather than returning an image.

## Cause and architecture
At the v293 published Chat source `e90b2f395589da8cbfb0315a5c1db9f70e2afcb4`, `chat/§wyrlz/index.html` renders the original `.first-run-welcome` into the existing flex `.message-list` with `margin:auto 0` and no width bound. It consequently stretches horizontally on PC. The canonical `main` copy of the Chat UI remains an older `1.0.59` snapshot; no old main UI is used as the release base. v294 starts from the immutable currently deployed Chat source, keeping newer Chat behavior and the separate §E codebase intact.

## Code fix
- Original first-run message content and `renderFirstRunWelcome` logic remain untouched.
- For desktop viewport widths ≥761 CSS pixels, make the greeting a 560px maximum-width centered glass card with 26–28px inner padding, refined 23px heading, soft sapphire gradient/shadow, strengthened kicker and a divided settings note.
- Keep the ≤760px original mobile behavior, and honor reduced-transparency/high-contrast a11y settings.
- Change only the existing styling/Chat version owner in `chat/§wyrlz/index.html` and `chat/§wyrlz/VERSION.txt`: local clean-room Chat `1.1.18 → 1.1.19`. Version-neutralize the preexisting v292 keyboard regression, add a v294 source/lifecycle regression and Playwright Chromium responsive test. Add browser CI workflow and candidate-CI test step.

## Source, exact CI, approval
[PR #288](https://github.com/kaministrator999-ui/Swrlzkamico/pull/288) merged from `fix/chat-v294-desktop-welcome-card` into version-pinned `integration/chat-v294-desktop-welcome-card`, integration SHA `0c34ecf36bc0e8a1c64b03cd036060610cc70c32`. Final candidate `774a4b6c669895e2b0278dd52440b98036c892ed` and merged integration source share exact Git tree `fd50757f1b7432f2951dccb77ae01047a0e3e6a3`. Seven CI workflows passed: HF Candidate Offline Validation #39673096942, Chat v294 desktop welcome responsive acceptance #39673097110, Android v287 scroll #39673096899, v290 live cue #39673096933, v284 rich widgets #39673096808, v285 conversational widgets #39673097081, mobile lyric reader #39673096925.

**Measured browser behavior:** at 1440x900, 1024x768, and 800x680, card width 560px, centered within a 740px conversation column, title font 23px, divider present, no horizontal overflow. At 390x844 mobile, card width 362px equals the available message column, with original 20px title, no horizontal overflow. Reduced-transparency test passes. Tests run in real headless Chromium but use a first-run CSS/DOM fixture, not a signed-in user account.

**Deployment authority:** guarded `main:.deploy/HF_SPACE_REQUEST.txt` request at `91698305e7e68fb5fe243997da5965ca4853bcbc` targets only `kamiloki/Swyrlz` with source `0c34ecf36bc0e8a1c64b03cd036060610cc70c32`; [deployment workflow #39673337508](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39673337508). The workflow success, published Space SHA, direct live page and user-device acceptance must be independently verified before claimed. No §E deployment, GitHub access mutation or LALM weight changes are part of this source revision.

## Published and hosted verification — 2026-10-21

**Guarded deployment PASS:** [Hugging Face Space Deploy Request #39673337508](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39673337508) completed success, request SHA `91698305e7e68fb5fe243997da5965ca4853bcbc`. Workflow selected and uploaded immutable `SOURCE_REF=0c34ecf36bc0e8a1c64b03cd036060610cc70c32` to existing `kamiloki/Swyrlz`. Its release checkpoint recorded new Space revision `ffc9d264e3ae7f9df8edca5cc878fd2c8587f9fc` with previous `2b9475e46675932d2651d2c899ea6efdee629779` retained as rollback. Rollback artifact `12380498777`, release checkpoint artifact `12379109578`.

**Actual hosted HTTP PASS:** [PR #289](https://github.com/kaministrator999-ui/Swrlzkamico/pull/289) and [live run #39674127790](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39674127790) independently checked the live Hugging Face metadata revision and served Chat HTML. Exact Space SHA matched the deployment receipt; HTML returned HTTP 200 with `swrlz-chat-version=1.1.19`, JS Chat version 1.1.19, desktop 560px card CSS at 761px viewport, original first-run renderer and reduced-transparency CSS. `/api/hf/models` returned HTTP 200 and five models. Test scripts `scripts/verify_chat_welcome_v294_live.py` and `.github/workflows/chat-welcome-v294-live.yml` merged to `main` at `bb44ecddff4738a332ee6cf7eda63d1208a55ef0`. No authenticated account state or model-generation call was accessed.

**Version authority:** Deployed UI/first-run layout advances canonical `runtime` Web Chat `1.5.156 → 1.5.157`; governed Repository Work `1.0.233 → 1.0.234`. Both changes were applied atomically in `runtime` commit `b46cf40f7be3fcefe3af14d978d86c0bde840942`. Server Runtime unchanged `2.3.439`, LALM Engine unchanged `2.1.201`, §E unchanged. Chat local version 1.1.19.

**Remaining acceptance:** The public hosted CSS and release revision are verified, and Chromium responsive layout was tested with the real stylesheet in an isolated first-run DOM fixture. The user's actual signed-in first-conversation card on their PC/device was **not** directly observed after publication, and is not falsely called verified.

## Version/verification follow-up
Before the new guarded publication: Repository Work `1.0.233`, Web Chat `1.5.156`, Server Runtime `2.3.439`, LALM Engine `2.1.201`. Post-release affected registries advanced with receipts above. Direct physical PC browser acceptance under the owner's signed-in account remains unobserved; public live CSS evidence and mock-context Chromium metrics are independent checks, not substitutes for that acceptance.
