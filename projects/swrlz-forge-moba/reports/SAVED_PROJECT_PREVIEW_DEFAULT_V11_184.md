# §E v11.184: Saved-project preview cards and default startup

## Design
- Native Projects → My Projects lists **on-device** and **connected account** projects using visual cards, stored names, revision information, Open action and a separate accessible default checkbox.
- New local saved snapshots include a small overview calculated from actual actor positions and model parts. Older on-device snapshots lazily render as cards enter the viewport, with concurrency bounded at two reads.
- Account project cards have thematic placeholders and a manual Preview scene action; full cloud scenes are never fetched automatically just for listing.
- A single same-device preference now supports starter defaults or one local/account saved project. No changes to project scene payloads or credentials. URL deep links override.
- Device-local default reads existing IndexedDB project bytes and uses the native importer; account default activates the existing sign-in flow and attempts a native cloud load only after authentication. Timeout fallback preserves continued editing.
- Previous starter checkboxes, Model Atelier, Sheep Tag LAN, VR and Chat authoring remain unchanged.

## Tests and limitations
- JS checks and default/cloud boot mock tests passed.
- Browser default selection, native gallery, imported saved scene and reload checked on phone-sized and Quest-sized viewport using seeded local project records.
- No real connected account or Quest headset end-to-end acceptance included.
- Local preview is a top-down actor overview, not a rendered 3D camera screenshot.
- Startup preference is stored in localStorage on the current browser; not account-synced.

## Release seal
- Version: §wyrl§ Engine v11.184
- Patches: 216
- Assets: 68
- Bytes: 7134586
- SHA-256: `35ba507edf2eedd98a85a49e8ae5e55e5b43f0b78c61139e1b2e6b50e8b95c5b`
