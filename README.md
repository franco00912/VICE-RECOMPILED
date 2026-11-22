# VICE RECOMPILED

VICE RECOMPILED is a local-only Windows toolkit for auditing and resuming long console-to-PC research builds without
packaging or publishing any game content.

The first release provides a deterministic status report:

- pins the exact source revision;
- reports clean/dirty source state and available disk space;
- maps package and per-pack TTPF pools to their expected output folders;
- identifies completed and incomplete pools from completion manifests;
- records audio and shader checkpoints;
- reports whether the separately supplied game executable is present;
- emits human-readable output or atomic JSON for dashboards and CI.
- writes a source/toolchain lockfile for reproducible checkpoints;
- compares reports and fails automatically if a completed pool regresses.

It does **not** contain GTA VI files, shaders, models, textures, keys, executable code from the game, decryption,
online-service access or instructions for obtaining restricted files. It does not claim that GTA VI currently boots.

## Example

```powershell
python vice_recompiled.py `
  --game "D:\path\to\your\readable-package" `
  --work "D:\build-work" `
  --repo "D:\ProjectSource" `
  --write-report "D:\build-work\vice-recompiled-status.json" `
  --write-lock "D:\build-work\vice-recompiled.lock.json"

# On a later run, compare against the previous report:
python vice_recompiled.py `
  --game "D:\path\to\your\readable-package" `
  --work "D:\build-work" `
  --repo "D:\ProjectSource" `
  --baseline "D:\build-work\previous-status.json"
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

All fixtures are synthetic and contain no game data.

## Project boundaries

VICE RECOMPILED is an independent research tool and is not affiliated with Rockstar Games or Take-Two Interactive. It
focuses on repeatable Windows build operations and evidence-based status reporting.
