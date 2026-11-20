# §C Chat 1.0.60 — UI audit and design contract

**Canonical owner:** `chat/§wyrlz/index.html` (not legacy `web/chat.html`)  
**Release intent:** Professional, orderly interface refinement without changing chat, account, or model authority.  
**Host:** existing Hugging Face Space `kamiloki/Swyrlz`; this source branch is **not** a live deployment.

## Baseline audit (1.0.59)

The canonical source has a 60 KB+ inline CSS layer plus successive Tier A–G overrides, a first-paint wallpaper, one integrated behavior script, and two local artwork assets. Existing functional areas include top status and title, Work surface, side drawer with threads and Google account, message list, expandable composer, and a settings sheet containing eleven sections. Controls and network routes are directly bound to fixed DOM IDs; replacing the HTML shell would risk transport/auth/thread regressions.

Observed implementation-level design debt:
- Top bar, menu trigger, Work button, status chip, and thread title used overlapping visual emphasis rather than a clear hierarchy.
- Composer used decorative polygon clipping that competed with form boundaries. Spacing and widths diverged from the conversation column.
- Threads, version data, and account information shared the same drawer without a well-defined flex/scroll hierarchy.
- Eleven settings sections were presented as a flat menu, with no categories to help navigate the information architecture.
- Messages, code artifacts, action buttons, and forms had inconsistent radius, shadow, padding, and hover behavior across old CSS tiers.
- Mobile and landscape widths needed explicit containment rules, while motion preferences had to remain authoritative.

## 1.0.60 implementation

- **Unified design tokens:** Ice Dragon-adjacent navy glass, pale cyan action accent, restrained violet elsewhere, typography, surfaces, border/spacing/radius/easing tokens. Existing artwork and product identity stay intact.
- **Top bar:** coherent alignment for menu, identity, conversation title, authentic runtime status and Work. No invented model readiness or tool activity.
- **Conversation:** wider but bounded reading column; refined message rhythm, assistant/user bubble hierarchy, scrolling code artifacts and tab controls, copy/pin affordances, and first-run welcome.
- **Composer:** centered to the conversation column, clear send affordance and accessible focus state; persistent existing grow/collapse and send/stop interaction bindings. Anchoring remains `bottom:0`.
- **Drawer:** flexible thread list gets the scroll budget; account and collapsed versions occupy purposeful lower regions. Existing Google auth and thread actions remain unchanged.
- **Settings:** four presentational categories (Conversation, Identity, Memory & permissions, Interface) around the existing eleven functional tabs. Tablet uses two-column sheet; mobile uses horizontally scrollable tabs inside a full-viewport panel.
- **Work surface:** same evidence/action truth boundary and APIs, but aligned visual panels and headings.
- **Motion and accessibility:** bounded enter/hover/pane transitions only. OS reduced-motion and existing Reduced/Off settings disable animation. Existing opacity/contrast settings remain effective. No new animation loop, polling, model call, or dependencies.
- **Event behavior:** Escape now closes the conversation drawer and returns focus to its button.

## Acceptance and risks

`tests/test_chat_ui_professional_v1060.py` checks all eleven pane/navigation pairs, unique canonical IDs, thread/send/composer/Work/settings bindings, responsive rules and version parity. `tests/verify_chat_ui_geometry.cjs` uses Chromium at 320, 390, 768, and 1440 px to check viewport containment, bottom-anchored composer, drawer/settings geometry, and reduced motion. CI saves representative screenshots for visual review.

This is a presentation-only branch; passing static/browser geometry does not establish live account, token-stream, or HF deployment acceptance. The guarded Space deployment lane requires its own pinned-source and snapshot/approval process. Before declaring live completion, verify authenticated threads, streaming stop/continue, keyboard up/down on Android, input auto-grow, and no console or layout regressions in the actual Space.

**Rollback:** revert the 1.0.60 branch commit or restore the previous 1.0.59 canonical index and VERSION.txt; no schema migration was introduced.
