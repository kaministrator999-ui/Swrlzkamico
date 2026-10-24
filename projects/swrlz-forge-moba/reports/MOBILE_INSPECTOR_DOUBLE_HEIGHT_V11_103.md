# §E v11.103 · Double-height mobile floating inspector

## User request
On Android after v11.102, the owner confirmed the floating window is better but asked for **twice its current height**. No width, drag, or touch gesture changes requested.

## Change
Only the mobile inspector height is overridden, with matching specificity and placement after the prior v11.102 panel styles:
- Default from min(34dvh,350px) to min(68dvh,700px).
- Expanded from min(43dvh,440px) to min(78dvh,800px), so Expand still increases size.
- Width, position, drag CSS-variable handling, scroll gutters, hold-to-edit keypad, brush logic, assets and old model files unchanged.

## Build integrity
- 135 ordered patches, 68 existing assets.
- HTML bytes: 6526071
- SHA-256: `7ce2d65c328d3c14f417062daaeb6f37f30b592c8f0b99f5cb305fd3bf1ee395`
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V11_103_DOUBLE_INSPECTOR_HEIGHT`
- Build checksum obtained in a fail-closed preflight; final independent hosted verification required before declaring live.

## Owner acceptance
Inspect height and remaining canvas visibility at original phone browser scale; verify manual dragging, internal scrolling and numeric press-hold still work.
