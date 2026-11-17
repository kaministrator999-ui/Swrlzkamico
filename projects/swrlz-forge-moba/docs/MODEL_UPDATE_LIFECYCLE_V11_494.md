# §E v11.494 — model update experience

User request (2026-11-17): Make My Projects > Update Model communicate progress clearly, remove avoidable delays, and open the selected updated project as soon as its save succeeds. The same user also wants Sorting Hat mouth relief reduced so the existing texture defines the expression.

## Changes
- Per-card update launches a prominent, accessible progress surface with six **actual stages**: read model ZIP/JSON, read account revision, validate identity + mesh/UV/rig, archive previous revision, commit the new revision, and open updated project. An indeterminate transfer bar and elapsed time show ongoing activity without fabricated percentages.
- After §C confirms `cloud.save` durably with matching original project ID and exactly the next revision, §E reuses a one-use copy of those exact saved bytes for the **canonical authenticated native `loadCloud`** path. No redundant second download. The in-memory copy is discarded whether opening succeeds, fails, or is cancelled.
- The old unconditional project-list refresh after save was on the critical path. The new path invalidates its in-memory cache and updates card revision immediately; a later My Projects refresh can fetch updated records.
- The canonical loader retains native scene rollback, dirty-scene confirmation, link persistence and camera workspace restoration. Failure to auto-open does not falsely report a failed save or trigger a second write.
- Local updates likewise keep previous revision history before opening the saved result.
- ZIP signature recognition from v11.493 remains, including browser file pickers with misleading filenames.

## Geometry artifact
`The-Sorting-Hat-Mesh-Fix-v4.zip` is a **separate owner-supplied model update**; never change the user's saved account bytes without their explicit file selection. The single-mesh v4 data uses the v3 texture, rig, skin weights, and UV coordinates unchanged and blends only exaggerated mouth positions back toward the original cloth surface (a texture-first expression).

## Safety and acceptance
Do not auto-retry ambiguous cloud.save outcomes, bypass account identity/CAS, drop revision history, mutate a different open project without confirmation, or replace a native scene before the server confirms its save. Verify by Android test: upload v4 ZIP on the selected Sorting Hat project, observe all six stages, confirm revision increment, and see the updated project open without manually tapping Open project.
