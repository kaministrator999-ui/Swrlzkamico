# §E v11.182 UI design and overlap remediation

## Scope
Professionalize the editor UI while preserving existing architecture. This release is additive CSS and a read-only audit, not a redesign of underlying scene and modeling workflows.

## Verified browser cases

| Viewport | Result |
|---|---|
| 390×844 phone portrait | PASS |
| 430×932 wide phone portrait | PASS |
| 844×390 phone landscape | PASS |
| 980×680 Quest-sized flat browser window | PASS |
| 1280×800 desktop | PASS |

Each case verifies native app readiness, baseline chrome noncollision, toolbar scrollability, Projects window bounds and hit-testability of the close button. No unexpected JS page errors. The tests intentionally dismiss the native release-notes dialog after stable boot, since native modal dialogs correctly have foreground priority.

## Defects and decisions

- v11.182's first styling draft enlarged the toolbar to 56px while the app's native grid reserved 48px. Chromium detected a genuine 8px intersection with the canvas at 844×390. Reduced toolbar height/padding to fit the canonical grid row without moving game camera or canvas.
- Portrait editor toolbar and viewport share a 1px rendered boundary due to native browser rounding. The audit ignores intersections no wider/taller than 3px to avoid counting adjacent layers as true occlusion.
- Projects close was initially hit-tested beneath a still-open release-notes dialog. That was correct native-modal behavior, not a project/Chat stacking failure. A stable hydrated browser test closes release notes before testing Projects.
- Project modal remains body-portaled with the previously validated z-index above Chat and docks; true modal top layer remains authoritative.

## Source and acceptance

Version v11.182; 214 ordered patches; 68 assets; 7,094,717 HTML bytes; SHA-256 0b4af9562ac14811d597938d75e716a39110ce1849929bb3a8599b78370b4f25.

Physical Android and Quest interaction acceptance is not simulated by a desktop Chromium viewport; future user findings can be addressed with focused follow-up patches.
