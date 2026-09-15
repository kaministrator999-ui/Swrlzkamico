# Server 2.3.167 — Chat Mask refresh + dialog containment repair

**Server Runtime:** 2.3.167  
**Web Chat:** 1.5.34  
**Runtime manifest:** 102  
**Deployment / restart:** NONE — runtime-hot event.

## Trigger

Android Chat evidence showed two independent Mask defects while failed assistant turns were being displayed: Bridge settings/runtime diagnostic text could escape into the conversation viewport and remained interactive, and canonical same-tab account-state reconciliation produced refresh-like whole-Chat rerender behavior after sends.

## Change

- `web/chat_same_tab_canonical_reconcile_v1.js` advances its internal contract to v2. It no longer fabricates a `storage` event in the same document. It adopts the authoritative cached snapshot directly into Chat's live state, renders without forced scrolling, emits a narrow `swrlz:canonical-state-adopted` receipt, and retains requestId-first terminal reconciliation.
- `web/chat_user_settings_v2.css` explicitly removes closed dialogs from layout/hit testing and adds a defensive closed-state containment rule for `#settingsDialog`, preventing Bridge settings/runtime diagnostic content from leaking into the conversation or intercepting taps.
- `runtime_pages/manifest.json` advances to 102 so the updated runtime assets are cache-busted into fresh Chat loads.

## Authority boundaries

This is a Mask-only repair. It does not change server/account authority, canonical persistence semantics, request identity, LALM cognition, R39 inference, or authentication.

## Verification

Repository/source verification is complete after commit. Live Android behavioral acceptance remains pending a fresh manifest-102 page load and send. The separate `No committed assistant text was received` / R39 generation failure is intentionally not declared fixed by this event; it requires its own evidence-backed LALM event if it persists on the fresh test.
