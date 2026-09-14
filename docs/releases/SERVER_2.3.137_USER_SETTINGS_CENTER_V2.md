# Server 2.3.137 — User Settings Center v2

**Status:** source complete; browser visual acceptance pending  
**Server Runtime:** 2.3.137  
**Web Chat:** 1.5.14  
**Web Frontend:** 1.0.3 unchanged  
**LALM/R39:** unchanged  
**Deployment:** NONE  
**Restart:** NONE

## What changed

- Upgraded the existing account/user settings surface in place instead of replacing the Chat page.
- Expanded the settings navigation from Profile, Data & privacy, Personalization and Security to include Appearance, Conversation, Accessibility and Advanced.
- Added a larger responsive desktop settings workspace and mobile horizontal section navigation, clearer section hierarchy, card-based controls, stronger spacing, cleaner typography and account/device scope labeling.
- Added account-scoped device UI preferences for interface density, Chat text size, reduced motion, high contrast, larger controls, Enter-to-send behavior, local scroll behavior and composer helper visibility.
- Added an Appearance theme selector that reuses the existing authoritative Chat theme controller instead of introducing a competing theme engine.
- Added Advanced utilities that reuse the existing Bridge Settings and Chat export actions.
- Added a non-secret diagnostics copy action containing only factual local UI/account-scope/context-estimate information. It does not include access tokens, Google credential tokens, conversation text or hidden server secrets.
- Added an interface-preference reset that resets only the new UI preference namespace and does not delete conversation history, account profile preferences or server state.

## Mask / Human / Brain boundary

This event is presentation/client behavior only. The Mask owns display, local interaction preferences and relay controls; it does not invent server capacity, readiness or authorization state and it does not add client-side semantic reasoning. The Advanced conversation context readout is explicitly an estimate from the existing local context-capacity component rather than a declaration of server writability or a hard server limit.

## Source ownership

- `web/chat_user_settings_v2.js` — settings augmentation and client-owned UI preference behavior.
- `web/chat_user_settings_v2.css` — responsive visual treatment and accessibility presentation states.
- `runtime_pages/manifest.json` v46 — activates both assets for `/chat` after the existing account/theme layers.
- Existing Profile, Data & privacy, Personalization, Security, Google account scoping, Bridge Settings and Chat export implementations remain the underlying owners of their existing behavior.

## Verification

- Confirmed both new runtime assets exist on the `runtime` branch after publication.
- Confirmed manifest v46 references `web/chat_user_settings_v2.css` and `web/chat_user_settings_v2.js` on `/chat`.
- Confirmed authoritative versions were re-read immediately before assignment and remained Server 2.3.136 / Web Chat 1.5.13, then advanced to Server 2.3.137 / Web Chat 1.5.14.
- No stable API, middleware, authentication, loader, build or deployment configuration changed.
- Final browser visual/interaction acceptance is still pending a user refresh/open of the Settings dialog.

## Rollback

Remove the two v2 settings assets from manifest loading and restore manifest v45 behavior. The existing account settings implementation remains intact underneath, so rollback does not require data migration, deployment or restart.
