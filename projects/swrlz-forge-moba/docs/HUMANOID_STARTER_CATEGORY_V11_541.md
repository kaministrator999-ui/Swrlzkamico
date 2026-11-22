# §E v11.541 — Futuristic Humanoid Starter Models visibility

**Root cause:** v11.540 changed the mannequin's visible template tag to "ONE UV BODY · FIVE FINGERS PER HAND", removing the "STARTER MODEL" category keyword. The existing v11.285 native Projects sorter uses explicit model template IDs and a fallback regex on the category badge. The stable mannequin ID `robotic-humanoid-mannequin` was absent from the explicit modelIds set. As a result, the Projects menu could place the card under **Starter Games**, leaving it missing from **Starter Models**.

**Correction:** register that stable ID in the existing modelIds category set, restore the "STARTER MODEL" badge prefix, and synchronize the immersive library display name to "Futuristic Humanoid · Detailed Hands". No geometry, UV asset, account data, save format, project ID, card handler or other starter is changed.

**Validation:** `node tests/humanoid_starter_category_v11_541.cjs <assembled index.html>` executes the actual extracted native Projects category classifier from the assembled HTML and confirms the mannequin is classified as a model even without its label, existing model starters remain models, and a known game remains a game. The v11.541 release verifier and static packaging checks must pass before Hugging Face publication.

**Owner acceptance:** in §E choose Projects → Starter Projects → Starter Models and find "Futuristic Humanoid · Detailed Hands". Opening the card should show the existing one-piece, five-digit T-pose with UV material. Previously saved model copies are preserved.
