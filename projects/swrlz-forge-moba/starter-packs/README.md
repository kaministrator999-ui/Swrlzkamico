# §E Starter Packs — source-only validation lane

This folder is for bounded, reviewed `swyrl-engine-starter-pack-v1` descriptors created by the account-owned §wyrlz GitHub pack workbench. A descriptor is paired with a real `../scenes/<id>.swyrl.json`. The draft descriptor is provenance and validation data, **not** a plugin, automatic Projects menu registration, new game mode, or deployment instruction.

## Validate

From the repository root:

```sh
python projects/swrlz-forge-moba/tools/validate_starter_packs.py --scene sheep-tag-meadow
python -m unittest discover -s projects/swrlz-forge-moba/tests -p test_starter_pack_validation_v216.py -v
python projects/swrlz-forge-moba/tools/validate_starter_packs.py --pack my-meadow
```

The last command requires the reviewed `scenes/my-meadow.swyrl.json` and `starter-packs/my-meadow.starter.json` pair to exist in the checkout. `--pack` checks the file digest/size, scene ID, source Git identities, actor and layer counts, mode type and the `draft-unregistered` lifecycle marker. A passing check does **not** confirm authoring controls, asset packaging or engine Play.

In §wyrlz Chat, an account-connected user can request `@GitHub engine pack sheep-tag-meadow as my-meadow on feature/my-meadow`, review the two-file proposal, explicitly confirm it, then use `@GitHub engine pack verify my-meadow on feature/my-meadow`. All mutations stay on a feature branch until human review. A new feature branch can be prepared through the existing approved branch-creation command. No tool auto-merges or triggers the dedicated §E deployment.

## From draft to playable starter

After source validation, add an intentional Projects card/loader, mode-specific gameplay and prefab/editor tools when needed, deterministic `build_space.py` bundling, an ordered governed patch and sealed manifest checksum, tests for Save/Load/Undo/Redo and Play/Pause/Stop on desktop/mobile, a draft PR and the independent §E guarded deployment only after approval. Keep §E full game editor separate from each game-specific simplified map builder and from the game hub launcher.

Read `§tart_§E.md` and `docs/engineering/SWRLZ_ENGINE_PACK_AUTHORING_V215.md` for the authoritative full engineering ladder.
