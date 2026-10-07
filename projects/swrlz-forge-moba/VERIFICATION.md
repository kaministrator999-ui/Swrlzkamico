# Embervault Atelier v8.0 verification

Verified on 2026-10-07 in Chromium desktop Play and the native editor. The project contains 167 authored actors, three editor layers, three physical tiers, and six persistent stations.

| Check | Evidence / outcome |
|---|---|
| Native authoring | Reusable prefabs were spawned, positioned, grouped, assigned to layers, configured as stations/signs, and saved with the editor. |
| Walking between tiers | Actual WASD input reached the upper study via the east ramp, crossed both bays, ascended/descended the council connector, and descended the west ramp. Feet tracked the supported mesh tops. |
| Lower circulation | Actual walking reached both workshop stations and the hearth. Side rails blocked attempts to cut across a ramp side; walking through the open mouths completed the route. |
| Bridge clearance | Walking beneath the study bridge remained on the lower floor; upstairs geometry did not pull the visitor upward. |
| Station interaction | E opened Code Studio, Archive Garden, World Forge, Prototype Court, Dragon Council, and the AI Hearth from their actual walk-up positions. |
| Documents | Native New file, text/notes editing, individual download, workspace export/import, and Save Project/reload preserved the expected contents. Temporary verification documents are excluded from the starter. |
| Runtime restoration | Stop restored the visitor spawn while retaining document edits. Opening/closing a station restored the prior pause state. |
| Layer history | Visibility toggle, Undo, and Redo preserved layer state and independent authored actor visibility. |
| Signs | Both faces use their own orientation and remain readable. Text/size updates refresh both faces; shared resources are disposed once. |
| Contact regressions | Physical floor and dragon-contact rays exclude station Sprite labels and editor helpers. Movement checks include grouped/transformed surfaces, rail height filtering, hidden ancestors, edited geometry, and passages below decks. |
| Release gates | The governed builder checks the exact manifest bytes/hash; Node checks the generated module. Deployment checks the live marker and exact artifact SHA-256. |

The headless worker renders with software WebGL. Some walking measurements suppressed raster drawing to keep automation responsive; native input, animation ticks, movement, collisions, support queries, and station logic continued unchanged. Arrival/editor screenshots use normal rendering. This verifies desktop behavior; headset rendering, controller input, spatial comfort, in-room inference, and execution of project code require future implementation and device testing.

The exact production receipt is the Actions run whose head SHA matches the final v8.0 DEPLOY_REQUEST commit, plus the served SOURCE.json and exact live HTML hash. Repository content is finalized before that trigger; the final delivery supplies its run/live links.
