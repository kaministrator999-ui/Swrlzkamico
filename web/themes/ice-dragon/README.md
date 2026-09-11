# SWRLZ Ice Dragon Chat Theme ❄️🐉

Repo-aware overlay theme for `kaministrator999-ui/Swrlzkamico`.

## Integration

The current `web/chat.html` remains untouched. The existing `web/chat_account.js` bootstrap loads:

- `/themes/ice-dragon/ice-dragon-theme.css`
- `/themes/ice-dragon/ice-dragon-theme.js`

The controller mounts a compact theme selector into `.topbar-right` with two choices:

- `Default`
- `❄ Ice Dragon`

Default remains the first-load behavior. The user's explicit selection persists in:

```text
localStorage['swrlz.chat.theme']
```

## Activation contract

Ice Dragon styling is scoped behind:

```html
<body data-swrlz-theme="ice-dragon">
```

The controller API is also available:

```js
IceDragonTheme.enable();
IceDragonTheme.disable();
IceDragonTheme.toggle();
IceDragonTheme.set('ice-dragon');
IceDragonTheme.set('default');
```

## Included

- `ice-dragon-theme.css`
- `ice-dragon-theme.js`
- `assets/ice-dragon-sigil.svg`
- `assets/ice-shards.svg`
- `manifest.json`

## Design behavior

The overlay preserves chat logic, streaming, account identity, LALM routing, evidence tooling, and layout architecture while styling the visible shell with deep glacier/navy surfaces, crystalline bubbles, frost accents, local dragon artwork, composer/send treatment, enhancement panels, and mobile states.

### Mobile sidebar contract

The theme explicitly keeps the sidebar bright and undimmed when opened. Dimming remains isolated to the background workspace/scrim layer.

## Dependencies

None. All artwork is local SVG; no CDN, remote font, remote image, paid asset, or runtime service is required.
