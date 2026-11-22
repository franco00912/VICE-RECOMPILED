# VICE RECOMPILED: a reproducible path from console build to PC research

I am building **VICE RECOMPILED**, an independent local-only toolkit for long-running console-to-PC research builds.

The goal is not to pretend that an incomplete port already boots. VICE RECOMPILED improves the part users can verify today:
long-running Windows build management.

The first working checkpoint provides:

- exact Git revision pinning;
- clean/dirty source detection;
- available-space reporting;
- deterministic mapping of package and per-pack TTPF pools;
- completed/incomplete pool detection from published manifests;
- audio and shader checkpoint reporting;
- explicit detection of the separately supplied game executable;
- human-readable and atomic JSON output;
- immutable revision/toolchain lockfiles;
- checkpoint comparison with automatic regression detection;
- synthetic tests containing no game data.

On the development machine it correctly tracked a resumed export from **40/57 to 41/57 completed texture pools**
while preserving the existing outputs. The current suite passes **2/2** synthetic tests. The pinned runtime checkpoint
passes **1,171/1,171 shader semantic tests**, **30/30 viewer tests** and **65/65 enabled runtime tests**.

VICE RECOMPILED contains no game archives, executable, shaders, models, textures, audio, keys, decryption or online-service
access. It does not distribute generated output. It does not claim to make an incomplete game port playable.

Next milestones: validated selective resume, immutable build lockfiles, structured test-gate reports and a local
progress dashboard.
